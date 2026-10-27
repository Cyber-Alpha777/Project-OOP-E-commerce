"""Domain 7 : Tagihan pembayaran (instruksi bayar QRIS / virtual account + batas waktu)."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta


def _tlv(tag, nilai):
    return f"{tag}{len(nilai):02d}{nilai}"


def _crc16(teks):
    """CRC-16/CCITT-FALSE, sama seperti yang dipakai standar QRIS (EMVCo)."""
    crc = 0xFFFF
    for b in teks.encode("ascii"):
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return f"{crc:04X}"


class Tagihan(ABC):
    """Abstract: satu tagihan yang harus dibayar dalam batas waktu tertentu."""
    DURASI_DETIK = 15 * 60
    MENUNGGU, LUNAS, KEDALUWARSA = "Menunggu Pembayaran", "Lunas", "Kedaluwarsa"
    _urut = 0

    def __init__(self, referensi, nominal, admin, dibuat=None):
        self.__referensi = referensi
        self.__nominal = nominal
        self.__admin = admin
        self.__dibuat = dibuat or datetime.now()
        self.__lunas = False

    @classmethod
    def buat_referensi(cls, awalan):
        Tagihan._urut += 1
        return f"{awalan}{datetime.now():%y%m%d%H%M%S}{Tagihan._urut:03d}"

    def get_referensi(self):
        return self.__referensi

    def get_nominal(self):
        return self.__nominal

    def get_admin(self):
        return self.__admin

    def total(self):
        return self.__nominal + self.__admin

    def sisa_detik(self, sekarang=None):
        batas = self.__dibuat + timedelta(seconds=self.DURASI_DETIK)
        return max(0, int((batas - (sekarang or datetime.now())).total_seconds()))

    def kedaluwarsa(self, sekarang=None):
        return not self.__lunas and self.sisa_detik(sekarang) <= 0

    def tandai_lunas(self):
        """Return False kalau tagihan sudah lewat batas waktu."""
        if self.kedaluwarsa():
            return False
        self.__lunas = True
        return True

    def get_status(self):
        if self.__lunas:
            return self.LUNAS
        return self.KEDALUWARSA if self.kedaluwarsa() else self.MENUNGGU

    @abstractmethod
    def judul(self):
        ...

    @abstractmethod
    def kode_bayar(self):
        """Isi kode QR (QRIS) atau nomor virtual account (transfer bank)."""

    @abstractmethod
    def langkah(self):
        ...


class TagihanQRIS(Tagihan):
    """Payload meniru format QRIS statis/dinamis (EMVCo) -- SIMULASI, bukan merchant sungguhan."""

    def __init__(self, referensi, nominal, admin, dibuat=None):
        super().__init__(referensi, nominal, admin, dibuat)
        isi = (_tlv("00", "01") + _tlv("01", "12")
               + _tlv("26", _tlv("00", "ID.CO.BESTDEAL.WWW") + _tlv("01", "ID1000000000001")
                      + _tlv("02", "BESTDEAL SIMULASI"))
               + _tlv("52", "5816") + _tlv("53", "360") + _tlv("54", str(self.total()))
               + _tlv("58", "ID") + _tlv("59", "BESTDEAL") + _tlv("60", "JAKARTA")
               + _tlv("62", _tlv("01", referensi)) + "6304")
        self.__payload = isi + _crc16(isi)

    def judul(self):
        return "QRIS"

    def kode_bayar(self):
        return self.__payload

    def langkah(self):
        return ["Buka aplikasi bank atau e-wallet yang mendukung QRIS.",
                "Pilih Scan / Bayar, lalu arahkan kamera ke kode QR.",
                "Periksa nominal di layar, lalu konfirmasi pembayaran.",
                "Kembali ke sini dan tekan 'Saya Sudah Bayar'."]


class TagihanVA(Tagihan):
    """Transfer ke nomor virtual account milik salah satu bank."""

    def __init__(self, bank, id_customer, referensi, nominal, admin, dibuat=None):
        super().__init__(referensi, nominal, admin, dibuat)
        self.__bank = bank
        self.__nomor = bank.buat_nomor_va(id_customer, referensi)

    def get_bank(self):
        return self.__bank

    def judul(self):
        return f"Transfer {self.__bank.NAMA}"

    def kode_bayar(self):
        return self.__nomor

    def langkah(self):
        return self.__bank.langkah_bayar() + ["Kembali ke sini dan tekan 'Saya Sudah Bayar'."]
