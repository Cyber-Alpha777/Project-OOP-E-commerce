"""Autentikasi: daftar akun, masuk, keluar (disimpan di memori)."""

import re

from bestdeal.models.user import Customer, Seller


class AuthService:
    """Mengelola akun Customer + Seller dan siapa yang sedang login.

    Data hanya tersimpan selama aplikasi berjalan (belum ada database / file).
    """
    MIN_PASSWORD = 6
    NAMA_TOKO_MAKS = 40

    def __init__(self, daftar_customer=(), daftar_seller=(), seller_katalog=()):
        """seller_katalog: Seller yang produknya sudah ada di katalog (tanpa akun login).
        Dipakai supaya ID dan nama toko seller baru tidak bentrok dengan mereka."""
        self.__akun = {}
        self.__aktif = None
        self.__seller_dikenal = list(seller_katalog)
        for u in (*daftar_customer, *daftar_seller):
            self.__akun[u.get_email().lower()] = u

    @staticmethod
    def email_valid(email):
        nama, _, domain = email.partition("@")
        return (bool(nama) and " " not in email and "." in domain
                and not domain.startswith(".") and not domain.endswith("."))

    def daftar(self, nama, email, password, konfirmasi):
        """Buat akun baru. Return (ok, pesan, customer)."""
        nama, email = nama.strip(), email.strip()
        if not nama:
            return False, "Nama tidak boleh kosong.", None
        if not self.email_valid(email):
            return False, "Format email tidak valid.", None
        if email.lower() in self.__akun:
            return False, "Email sudah terdaftar. Silakan masuk.", None
        if len(password) < self.MIN_PASSWORD:
            return False, f"Kata sandi minimal {self.MIN_PASSWORD} karakter.", None
        if password != konfirmasi:
            return False, "Konfirmasi kata sandi tidak sama.", None
        jumlah_customer = sum(1 for u in self.__akun.values() if u.peran() == "Customer")
        customer = Customer(f"C{jumlah_customer + 1:03d}", nama, password, email, "-", "-")
        self.__akun[email.lower()] = customer
        return True, "Akun berhasil dibuat.", customer

    # ---------- daftar sebagai Seller ----------
    def _semua_seller(self):
        return [*self.__seller_dikenal, *(u for u in self.__akun.values() if u.peran() == "Publisher")]

    def _id_seller_berikutnya(self):
        """S###, dihitung dari ID terbesar yang sudah dipakai (akun maupun katalog)."""
        angka = [int(m.group(1)) for sel in self._semua_seller()
                 if (m := re.fullmatch(r"S(\d+)", sel.get_id_user()))]
        return f"S{max(angka, default=0) + 1:03d}"

    def daftar_seller(self, nama_toko, email, password, konfirmasi):
        """Buat akun Seller (Publisher) baru. Return (ok, pesan, seller)."""
        nama_toko, email = nama_toko.strip(), email.strip()
        if not nama_toko:
            return False, "Nama toko tidak boleh kosong.", None
        if len(nama_toko) > self.NAMA_TOKO_MAKS:
            return False, f"Nama toko maksimal {self.NAMA_TOKO_MAKS} karakter.", None
        if not self.email_valid(email):
            return False, "Format email tidak valid.", None
        if email.lower() in self.__akun:
            return False, "Email sudah terdaftar. Silakan masuk.", None
        if any(s.get_nama_toko().strip().lower() == nama_toko.lower()
               for s in self._semua_seller()):
            return False, f"Nama toko '{nama_toko}' sudah dipakai.", None
        if len(password) < self.MIN_PASSWORD:
            return False, f"Kata sandi minimal {self.MIN_PASSWORD} karakter.", None
        if password != konfirmasi:
            return False, "Konfirmasi kata sandi tidak sama.", None
        seller = Seller(self._id_seller_berikutnya(), nama_toko, email, "-", "-",
                        password=password)
        self.__akun[email.lower()] = seller
        return True, "Akun seller berhasil dibuat.", seller

    def masuk(self, email, password):
        """Cek email + kata sandi. Return (ok, pesan, user); user = Customer atau Seller."""
        user = self.__akun.get(email.strip().lower())
        if user is None or not user.cek_password(password):
            return False, "Email atau kata sandi salah.", None
        self.__aktif = user
        return True, f"Selamat datang, {user.get_nama()}!", user

    def keluar(self):
        self.__aktif = None

    def get_aktif(self):
        return self.__aktif

    def sudah_masuk(self):
        return self.__aktif is not None
