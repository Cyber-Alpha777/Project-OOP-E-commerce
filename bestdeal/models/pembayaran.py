"""Domain 3b : Pembayaran (abstract) dan turunannya."""

from abc import ABC, abstractmethod

from bestdeal.utils import rupiah


class Pembayaran(ABC):
    """Abstract: tiap metode bayar punya biaya admin & cara proses sendiri."""

    eksternal = True        # True = dibayar lewat pihak luar (bisa juga dipakai untuk top up)

    def __init__(self, id_pembayaran, pesanan, metode_pembayaran):
        self.__id_pembayaran = id_pembayaran
        self.__pesanan = pesanan
        self._metode_pembayaran = metode_pembayaran
        self._status_pembayaran = "Belum Dibayar"
        self.__jumlah_bayar = 0

    def get_pesanan(self):
        return self.__pesanan

    def get_status(self):
        return self._status_pembayaran

    def get_metode(self):
        return self._metode_pembayaran

    def get_jumlah_bayar(self):
        return self.__jumlah_bayar

    @classmethod
    @abstractmethod
    def tarif_admin(cls, subtotal):
        ...

    @classmethod
    def label_tarif(cls):
        """Teks singkat tarif admin untuk ditampilkan di GUI (mis. '0,7%')."""
        return ""

    @classmethod
    def catatan(cls):
        """Petunjuk singkat cara bayar untuk ditampilkan di GUI."""
        return ""

    @abstractmethod
    def proses(self):
        """Return (bool, pesan)."""

    def biaya_admin(self):
        return self.tarif_admin(self.__pesanan.hitung_total())

    def total_tagihan(self):
        return self.__pesanan.hitung_total() + self.biaya_admin()

    def _lunas(self, jumlah):
        self.__jumlah_bayar = jumlah
        self._status_pembayaran = "Lunas"


class PembayaranSaldo(Pembayaran):
    eksternal = False       # memotong saldo dompet, jadi tidak bisa dipakai untuk top up

    @classmethod
    def tarif_admin(cls, subtotal):
        return 0

    @classmethod
    def label_tarif(cls):
        return "Gratis"

    @classmethod
    def catatan(cls):
        return "Dipotong langsung dari saldo dompet BestDeal."

    def proses(self):
        customer = self.get_pesanan().get_customer()
        total = self.total_tagihan()
        nama = ", ".join(d.get_produk().get_nama_produk()
                         for d in self.get_pesanan().get_detail_pesanan())
        if customer.kurangi_saldo(total, f"Beli {nama}"):
            self._lunas(total)
            return True, "Pembayaran saldo berhasil."
        return False, f"Saldo tidak cukup. Kurang {rupiah(total - customer.get_saldo())}."


class PembayaranBerPersen(Pembayaran):
    """Metode eksternal dengan biaya admin berupa persentase dari subtotal.

    Subclass cukup mengisi PERSEN (dan CATATAN); proses simulasi sudah disediakan di sini.
    """
    PERSEN = 0.0
    CATATAN = ""

    @classmethod
    def tarif_admin(cls, subtotal):
        return int(round(subtotal * cls.PERSEN))

    @classmethod
    def label_tarif(cls):
        return f"{cls.PERSEN * 100:g}%".replace(".", ",")

    @classmethod
    def catatan(cls):
        return cls.CATATAN

    def proses(self):
        self._lunas(self.total_tagihan())
        return True, f"Pembayaran {self._metode_pembayaran} berhasil."


class PembayaranQRIS(PembayaranBerPersen):
    PERSEN = 0.007
    CATATAN = "Scan kode QR dari aplikasi bank atau e-wallet apa pun (simulasi)."


class PembayaranKartu(PembayaranBerPersen):
    PERSEN = 0.025
    CATATAN = "Kartu kredit / debit Visa dan Mastercard (simulasi)."


class PembayaranEWallet(PembayaranBerPersen):
    """Induk e-wallet. Tiap aplikasi cukup menimpa PERSEN."""
    PERSEN = 0.015
    CATATAN = "Pembayaran lewat aplikasi e-wallet (simulasi)."


class PembayaranGoPay(PembayaranEWallet):
    PERSEN = 0.015


class PembayaranOVO(PembayaranEWallet):
    PERSEN = 0.015


class PembayaranDANA(PembayaranEWallet):
    PERSEN = 0.01


class PembayaranTransferBank(Pembayaran):
    """Transfer ke virtual account: biaya admin tetap (flat), bukan persentase."""
    BIAYA_TETAP = 4000

    @classmethod
    def tarif_admin(cls, subtotal):
        return cls.BIAYA_TETAP

    @classmethod
    def label_tarif(cls):
        return rupiah(cls.BIAYA_TETAP)

    @classmethod
    def catatan(cls):
        return "Transfer ke virtual account bank (simulasi)."

    def proses(self):
        self._lunas(self.total_tagihan())
        return True, "Pembayaran transfer bank berhasil."


# Urutan di sini = urutan tampil di dialog beli dan di halaman Dompet.
DAFTAR_METODE = {
    "Saldo BestDeal": PembayaranSaldo,
    "QRIS": PembayaranQRIS,
    "GoPay": PembayaranGoPay,
    "OVO": PembayaranOVO,
    "DANA": PembayaranDANA,
    "Transfer Bank": PembayaranTransferBank,
    "Kartu Kredit": PembayaranKartu,
}
