"""Domain 6 : Bank (abstract) dan turunannya, untuk pembayaran transfer virtual account."""

import hashlib
from abc import ABC, abstractmethod


class Bank(ABC):
    """Tiap bank punya prefix VA, warna, dan cara bayar sendiri (Polymorphism).

    Kelas ini dipakai sebagai 'kelas' saja (classmethod), tidak perlu di-instantiate.
    """
    NAMA = ""
    NAMA_LENGKAP = ""
    PREFIX = ""
    WARNA = "#444444"           # warna lencana bank
    WARNA_TEKS = "#ffffff"
    PANJANG_VA = 16

    @classmethod
    def buat_nomor_va(cls, id_customer, referensi):
        """Nomor virtual account 16 digit, tetap sama untuk (customer, referensi) yang sama."""
        sisa = cls.PANJANG_VA - len(cls.PREFIX)
        angka = int(hashlib.sha256(f"{cls.NAMA}|{id_customer}|{referensi}".encode()).hexdigest(), 16)
        return cls.PREFIX + f"{angka % 10 ** sisa:0{sisa}d}"

    @staticmethod
    def format_va(nomor):
        """'3900112345678901' -> '3900 1123 4567 8901'."""
        return " ".join(nomor[i:i + 4] for i in range(0, len(nomor), 4))

    @classmethod
    @abstractmethod
    def langkah_bayar(cls):
        """Daftar langkah singkat cara membayar lewat bank ini."""


class BankBCA(Bank):
    NAMA = "BCA"
    NAMA_LENGKAP = "Bank Central Asia"
    PREFIX = "39001"
    WARNA = "#0b5cab"

    @classmethod
    def langkah_bayar(cls):
        return ["Buka aplikasi BCA mobile atau ATM BCA.",
                "Pilih menu m-Transfer > BCA Virtual Account.",
                "Masukkan nomor virtual account di atas.",
                "Periksa nominal, lalu masukkan PIN untuk membayar."]


class BankMandiri(Bank):
    NAMA = "Mandiri"
    NAMA_LENGKAP = "Bank Mandiri"
    PREFIX = "88001"
    WARNA = "#12326b"

    @classmethod
    def langkah_bayar(cls):
        return ["Buka Livin' by Mandiri atau ATM Mandiri.",
                "Pilih Bayar > Multipayment.",
                "Masukkan nomor virtual account di atas.",
                "Periksa nominal, lalu konfirmasi dengan PIN."]


class BankBNI(Bank):
    NAMA = "BNI"
    NAMA_LENGKAP = "Bank Negara Indonesia"
    PREFIX = "8801"
    WARNA = "#e8590c"

    @classmethod
    def langkah_bayar(cls):
        return ["Buka BNI Mobile Banking atau ATM BNI.",
                "Pilih Transfer > Virtual Account Billing.",
                "Masukkan nomor virtual account di atas.",
                "Periksa nominal, lalu masukkan password transaksi."]


# Urutan di sini = urutan tampil di halaman pembayaran.
DAFTAR_BANK = {"BCA": BankBCA, "Mandiri": BankMandiri, "BNI": BankBNI}
