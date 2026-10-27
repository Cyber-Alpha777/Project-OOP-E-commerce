"""Domain 1 : User  (Abstraction + Inheritance + Polymorphism)."""

import hashlib
from abc import ABC, abstractmethod

from bestdeal.models.dompet import Mutasi


class User(ABC):
    """Superclass abstrak. Tidak bisa di-instantiate langsung."""

    def __init__(self, id_user, nama, email, no_telepon, alamat):
        self.__id_user = id_user
        self.__nama = nama
        self.__email = email
        self.__no_telepon = no_telepon
        self.__alamat = alamat

    # ==== Getter ====
    def get_id_user(self):
        return self.__id_user

    def get_nama(self):
        return self.__nama

    def get_email(self):
        return self.__email

    def get_no_telepon(self):
        return self.__no_telepon

    def get_alamat(self):
        return self.__alamat

    # ==== Setter ====
    def set_id_user(self, id_user):
        self.__id_user = id_user

    def set_nama(self, nama):
        if nama.strip():
            self.__nama = nama.strip()

    def set_email(self, email):
        if "@" in email and "." in email.split("@")[-1]:
            self.__email = email

    def set_no_telepon(self, no_telepon):
        digit = no_telepon.replace("+", "").replace(" ", "")
        if digit.isdigit() and 8 <= len(digit) <= 15:
            self.__no_telepon = no_telepon

    def set_alamat(self, alamat):
        self.__alamat = alamat

    # ==== Abstract: wajib di-override subclass ====
    @abstractmethod
    def peran(self):
        ...

    @abstractmethod
    def tampilkan_profil(self):
        ...


class Customer(User):
    def __init__(self, id_customer, nama, password, email, no_telepon, alamat, saldo=0):
        super().__init__(id_customer, nama, email, no_telepon, alamat)
        self.__password = self._hash(password)
        self.__saldo = saldo
        self.__mutasi = []       # list Mutasi (riwayat dompet)
        if saldo > 0:
            self.__catat("Saldo Awal", "Saldo awal akun", saldo)
        self.__library = []      # list Produk yang sudah dibeli
        self.__jam_main = {}     # id_produk -> jam main

    def peran(self):
        return "Customer"

    # ==== Password ====
    @staticmethod
    def _hash(password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def set_password(self, password):
        if len(password) >= 6:
            self.__password = self._hash(password)

    def cek_password(self, password):
        return self.__password == self._hash(password)

    # ==== Saldo (dilindungi, hanya lewat method) ====
    def get_saldo(self):
        return self.__saldo

    def tambah_saldo(self, jumlah, keterangan="Top up saldo"):
        if jumlah > 0:
            self.__saldo += jumlah
            self.__catat("Top Up", keterangan, jumlah)
            return True
        return False

    def kurangi_saldo(self, jumlah, keterangan="Pembelian"):
        if 0 <= jumlah <= self.__saldo:
            self.__saldo -= jumlah
            if jumlah > 0:
                self.__catat("Pembelian", keterangan, -jumlah)
            return True
        return False

    def get_mutasi(self):
        return list(self.__mutasi)

    def __catat(self, jenis, keterangan, jumlah):
        self.__mutasi.append(Mutasi(jenis, keterangan, jumlah, self.__saldo))

    # ==== Library ====
    def get_library(self):
        return list(self.__library)

    def punya(self, produk):
        return any(p.get_id_produk() == produk.get_id_produk() for p in self.__library)

    def tambah_ke_library(self, produk):
        if not self.punya(produk):
            self.__library.append(produk)

    def get_jam_main(self, produk):
        return self.__jam_main.get(produk.get_id_produk(), 0.0)

    def tambah_jam_main(self, produk, jam):
        if jam > 0:
            self.__jam_main[produk.get_id_produk()] = self.get_jam_main(produk) + jam

    # Method Overriding dari User
    def tampilkan_profil(self):
        return (f"Customer : {self.get_nama()}\nEmail    : {self.get_email()}\n"
                f"Telepon  : {self.get_no_telepon()}\nAlamat   : {self.get_alamat()}")

    get_tampilkan_customer = tampilkan_profil   # nama lama dari nomor_2.py


class Seller(User):
    def __init__(self, id_seller, nama_toko, email, no_telepon, alamat, rating=5.0):
        super().__init__(id_seller, nama_toko, email, no_telepon, alamat)
        self.__nama_toko = nama_toko
        self.__rating = rating

    def peran(self):
        return "Publisher"

    def get_nama_toko(self):
        return self.__nama_toko

    def set_nama_toko(self, nama_toko):
        self.__nama_toko = nama_toko
        self.set_nama(nama_toko)  # sinkron dengan atribut parent

    def get_rating(self):
        return self.__rating

    def set_rating(self, rating):
        if 0 <= rating <= 5:
            self.__rating = rating

    # Method Overriding dari User
    def tampilkan_profil(self):
        return (f"Toko     : {self.__nama_toko}\nEmail    : {self.get_email()}\n"
                f"Telepon  : {self.get_no_telepon()}\nAlamat   : {self.get_alamat()}\n"
                f"Rating   : {self.__rating}")

    get_tampilkan_seller = tampilkan_profil     # nama lama dari nomor_2.py
