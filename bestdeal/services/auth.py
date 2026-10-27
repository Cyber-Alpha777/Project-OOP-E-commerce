"""Autentikasi: daftar akun, masuk, keluar (disimpan di memori)."""

from bestdeal.models.user import Customer


class AuthService:
    """Mengelola akun Customer + Seller dan siapa yang sedang login.

    Data hanya tersimpan selama aplikasi berjalan (belum ada database / file).
    """
    MIN_PASSWORD = 6

    def __init__(self, daftar_customer=(), daftar_seller=()):
        self.__akun = {}            
        self.__aktif = None
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
