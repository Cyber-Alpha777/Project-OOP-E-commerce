"""
BestDeal - Aplikasi Desktop Toko Game (tema putih-orange) berbasis Tkinter, rasio 16:9.

Cara jalan:  python bestdeal.py   (Python 3.9+, tanpa library tambahan)

Penerapan 4 pilar OOP
---------------------
1. ENCAPSULATION : atribut private (__x) / protected (_x) + getter/setter dengan validasi
                   (Customer.__saldo, Produk.__harga, Pengaturan.__aksen, dst).
2. INHERITANCE   : User -> Customer, Seller | Produk -> Game, DLC, Bundle
                   Pembayaran -> PembayaranSaldo, PembayaranQRIS, PembayaranKartu
                   Halaman -> HomePage, LibraryPage, AkunPage, SettingPage
3. POLYMORPHISM  : method yang sama, perilaku beda di tiap subclass:
                   tampilkan_profil(), harga_akhir(), bisa_dibeli_oleh(), berikan_ke(),
                   tarif_admin(), proses(), bangun()
4. ABSTRACTION   : User, Produk, Pembayaran, Halaman = abstract class (ABC) dengan
                   @abstractmethod; TokoGame = facade yang menyembunyikan alur
                   Pesanan -> Pembayaran -> Pengiriman dari GUI.
"""

import hashlib
import random
import string
import tkinter as tk
import tkinter.font as tkfont
from abc import ABC, abstractmethod
from datetime import date
from tkinter import messagebox, ttk


# ======================================================================
# UTIL
# ======================================================================
def rupiah(n):
    return "Rp" + f"{int(n):,}".replace(",", ".")


def campur(a, b, t):
    """Campur dua warna hex (#rrggbb). t=0 -> a, t=1 -> b."""
    ar, ag, ab = int(a[1:3], 16), int(a[3:5], 16), int(a[5:7], 16)
    br, bg, bb = int(b[1:3], 16), int(b[3:5], 16), int(b[5:7], 16)
    return "#%02x%02x%02x" % (
        int(ar + (br - ar) * t), int(ag + (bg - ag) * t), int(ab + (bb - ab) * t))


# ======================================================================
# DOMAIN 1 : USER  (Abstraction + Inheritance + Polymorphism)
# ======================================================================
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

    def tambah_saldo(self, jumlah):
        if jumlah > 0:
            self.__saldo += jumlah
            return True
        return False

    def kurangi_saldo(self, jumlah):
        if 0 <= jumlah <= self.__saldo:
            self.__saldo -= jumlah
            return True
        return False

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


# ======================================================================
# DOMAIN 2 : PRODUK  (Abstraction + Inheritance + Polymorphism)
# ======================================================================
class Produk(ABC):
    """Produk abstrak: Game, DLC, Bundle punya aturan harga & beli sendiri-sendiri."""

    def __init__(self, id_produk, nama_produk, harga, stok, kategori, seller=None,
                 deskripsi="", warna=("#2f8cff", "#0b1017")):
        self.__id_produk = id_produk
        self.__nama_produk = nama_produk
        self.__harga = harga
        self.__stok = stok
        self.__kategori = kategori
        self.__seller = seller
        self.__deskripsi = deskripsi
        self.__warna = warna

    # ==== Getter ====
    def get_id_produk(self):
        return self.__id_produk

    def get_nama_produk(self):
        return self.__nama_produk

    def get_harga(self):
        return self.__harga

    def get_stok(self):
        return self.__stok

    def get_kategori(self):
        return self.__kategori

    def get_seller(self):
        return self.__seller

    def get_deskripsi(self):
        return self.__deskripsi

    def get_warna(self):
        return self.__warna

    # ==== Setter ====
    def set_id_produk(self, id_produk):
        if str(id_produk).strip():
            self.__id_produk = id_produk

    def set_nama_produk(self, nama_produk):
        if nama_produk.strip():
            self.__nama_produk = nama_produk.strip()

    def set_harga(self, harga):
        if harga >= 0:
            self.__harga = harga

    def set_stok(self, stok):
        if stok >= 0:
            self.__stok = stok

    def set_kategori(self, kategori):
        self.__kategori = kategori

    def set_seller(self, seller):
        self.__seller = seller

    def kurangi_stok(self, jumlah):
        if jumlah <= self.__stok:
            self.__stok -= jumlah
            return True
        return False

    # ==== Abstract / Polymorphic ====
    @abstractmethod
    def label_tipe(self):
        ...

    @abstractmethod
    def harga_akhir(self):
        ...

    @abstractmethod
    def bisa_dibeli_oleh(self, customer):
        """Return (bool, pesan)."""

    @abstractmethod
    def berikan_ke(self, customer):
        """Masukkan produk ke library customer setelah pembayaran sukses."""

    # ==== Default (boleh di-override) ====
    def diskon_persen(self):
        return 0

    def bisa_dimainkan(self):
        return False

    def info_tambahan(self):
        """Info khusus tipe produk; di-override subclass."""
        return ""

    def dimiliki_oleh(self, customer):
        return customer.punya(self)

    def nama_publisher(self):
        return self.__seller.get_nama_toko() if self.__seller else "Tanpa Seller"

    def tampilkan_produk(self):
        return (f"{self.__nama_produk} | {rupiah(self.harga_akhir())} | "
                f"{self.label_tipe()} | Dijual oleh: {self.nama_publisher()}")


class Game(Produk):
    def __init__(self, id_produk, nama, harga, kategori, seller, deskripsi, warna,
                 diskon=0, rilis="2025", ulasan=85):
        super().__init__(id_produk, nama, harga, 9999, kategori, seller, deskripsi, warna)
        self.__diskon = diskon
        self.__rilis = rilis
        self.__ulasan = ulasan

    def get_rilis(self):
        return self.__rilis

    def get_ulasan(self):
        return self.__ulasan

    def label_tipe(self):
        return "Game"

    def bisa_dimainkan(self):
        return True

    def diskon_persen(self):
        return self.__diskon

    def harga_akhir(self):
        return self.get_harga() * (100 - self.__diskon) // 100

    def bisa_dibeli_oleh(self, customer):
        if customer.punya(self):
            return False, "Game ini sudah ada di library kamu."
        return True, ""

    def berikan_ke(self, customer):
        customer.tambah_ke_library(self)


class DLC(Produk):
    def __init__(self, id_produk, nama, harga, game_induk, deskripsi, warna):
        super().__init__(id_produk, nama, harga, 9999, "DLC", game_induk.get_seller(),
                         deskripsi, warna)
        self.__game_induk = game_induk

    def get_game_induk(self):
        return self.__game_induk

    def label_tipe(self):
        return "DLC"

    def info_tambahan(self):
        return f"Butuh game: {self.__game_induk.get_nama_produk()}"

    def harga_akhir(self):
        return self.get_harga()          # DLC tidak kena diskon

    def bisa_dibeli_oleh(self, customer):
        if customer.punya(self):
            return False, "DLC ini sudah kamu miliki."
        if not customer.punya(self.__game_induk):
            return False, f"Butuh game '{self.__game_induk.get_nama_produk()}' dulu."
        return True, ""

    def berikan_ke(self, customer):
        customer.tambah_ke_library(self)


class Bundle(Produk):
    def __init__(self, id_produk, nama, daftar_game, seller, deskripsi, warna, potongan=0.15):
        total_normal = sum(g.get_harga() for g in daftar_game)
        super().__init__(id_produk, nama, total_normal, 9999, "Paket", seller, deskripsi, warna)
        self.__daftar_game = daftar_game
        self.__potongan = potongan

    def get_daftar_game(self):
        return list(self.__daftar_game)

    def label_tipe(self):
        return "Paket"

    def info_tambahan(self):
        isi = ", ".join(g.get_nama_produk() for g in self.__daftar_game)
        return f"Isi paket: {isi}"

    def harga_akhir(self):
        total = sum(g.harga_akhir() for g in self.__daftar_game) * (1 - self.__potongan)
        return int(round(total / 1000.0) * 1000)

    def diskon_persen(self):
        return max(0, 100 - self.harga_akhir() * 100 // self.get_harga())

    def dimiliki_oleh(self, customer):
        return all(customer.punya(g) for g in self.__daftar_game)

    def bisa_dibeli_oleh(self, customer):
        if self.dimiliki_oleh(customer):
            return False, "Semua game di paket ini sudah kamu miliki."
        return True, ""

    def berikan_ke(self, customer):
        for g in self.__daftar_game:
            customer.tambah_ke_library(g)


# ======================================================================
# DOMAIN 3 : PESANAN, PEMBAYARAN, PENGIRIMAN
# ======================================================================
class DetailPesanan:
    def __init__(self, id_detail, produk, jumlah):
        self.__id_detail = id_detail
        self.__produk = produk
        self.__jumlah = jumlah
        self.__subtotal = produk.harga_akhir() * jumlah

    def get_id_detail(self):
        return self.__id_detail

    def get_produk(self):
        return self.__produk

    def get_jumlah(self):
        return self.__jumlah

    def get_subtotal(self):
        return self.__subtotal

    def set_id_detail(self, id_detail):
        self.__id_detail = id_detail

    def set_produk(self, produk):
        self.__produk = produk
        self.__subtotal = produk.harga_akhir() * self.__jumlah

    def set_jumlah(self, jumlah):
        self.__jumlah = jumlah
        self.__subtotal = self.__produk.harga_akhir() * jumlah

    def tampilkan_detail(self):
        return f"{self.__produk.get_nama_produk()} x {self.__jumlah} = {rupiah(self.__subtotal)}"


class Pesanan:
    def __init__(self, id_pesanan, customer, tanggal_pesanan):
        self.__id_pesanan = id_pesanan
        self.__customer = customer
        self.__tanggal_pesanan = tanggal_pesanan
        self.__status = "Diproses"
        self.__detail_pesanan = []

    def get_id_pesanan(self):
        return self.__id_pesanan

    def get_customer(self):
        return self.__customer

    def get_tanggal_pesanan(self):
        return self.__tanggal_pesanan

    def get_status(self):
        return self.__status

    def get_detail_pesanan(self):
        return list(self.__detail_pesanan)

    def set_id_pesanan(self, id_pesanan):
        self.__id_pesanan = id_pesanan

    def set_customer(self, customer):
        self.__customer = customer

    def set_tanggal_pesanan(self, tanggal):
        self.__tanggal_pesanan = tanggal

    def set_status(self, status):
        self.__status = status

    def tambah_produk(self, id_detail, produk, jumlah):
        if produk.kurangi_stok(jumlah):
            self.__detail_pesanan.append(DetailPesanan(id_detail, produk, jumlah))
            return True
        return False

    def hitung_total(self):
        return sum(d.get_subtotal() for d in self.__detail_pesanan)

    def get_pesanan(self):
        baris = [f"ID Pesanan : {self.__id_pesanan}",
                 f"Tanggal    : {self.__tanggal_pesanan}",
                 f"Status     : {self.__status}", "Detail:"]
        baris += ["  " + d.tampilkan_detail() for d in self.__detail_pesanan]
        baris.append(f"Total      : {rupiah(self.hitung_total())}")
        return "\n".join(baris)


class Pembayaran(ABC):
    """Abstract: tiap metode bayar punya biaya admin & cara proses sendiri."""

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
    @classmethod
    def tarif_admin(cls, subtotal):
        return 0

    def proses(self):
        customer = self.get_pesanan().get_customer()
        total = self.total_tagihan()
        if customer.kurangi_saldo(total):
            self._lunas(total)
            return True, "Pembayaran saldo berhasil."
        return False, f"Saldo tidak cukup. Kurang {rupiah(total - customer.get_saldo())}."


class PembayaranQRIS(Pembayaran):
    @classmethod
    def tarif_admin(cls, subtotal):
        return int(round(subtotal * 0.007))

    def proses(self):
        self._lunas(self.total_tagihan())
        return True, "Pembayaran QRIS berhasil."


class PembayaranKartu(Pembayaran):
    @classmethod
    def tarif_admin(cls, subtotal):
        return int(round(subtotal * 0.025))

    def proses(self):
        self._lunas(self.total_tagihan())
        return True, "Pembayaran kartu kredit berhasil."


class Pengiriman:
    """Untuk produk digital: 'pengiriman' = kirim kunci lisensi ke email customer."""
    nama_platform = "BestDeal"
    jumlah_pengiriman = 0

    def __init__(self, id_pengiriman, pesanan, nomor_resi, jasa_ekspedisi, biaya_kirim,
                 estimasi_sampai):
        self.__id_pengiriman = id_pengiriman
        self.__pesanan = pesanan
        self.__nomor_resi = nomor_resi
        self.__alamat_tujuan = pesanan.get_customer().get_email()
        self.__jasa_ekspedisi = jasa_ekspedisi
        self.__status_pengiriman = "Sedang Diproses"
        self.__biaya_kirim = biaya_kirim
        self.__estimasi_sampai = estimasi_sampai
        Pengiriman.jumlah_pengiriman += 1

    def get_kunci(self):
        return self.__nomor_resi

    def get_status(self):
        return self.__status_pengiriman

    def get_alamat_tujuan(self):
        return self.__alamat_tujuan

    def get_jasa(self):
        return self.__jasa_ekspedisi

    def get_biaya(self):
        return self.__biaya_kirim

    def get_estimasi(self):
        return self.__estimasi_sampai

    def ubah_status(self, status_baru):
        self.__status_pengiriman = status_baru

    @staticmethod
    def buat_kunci():
        def blok():
            return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return "-".join(blok() for _ in range(3))


# ======================================================================
# DOMAIN 4 : TOKO (Facade - menyembunyikan alur beli dari GUI)
# ======================================================================
class TokoGame:
    METODE = {
        "Saldo BestDeal": PembayaranSaldo,
        "QRIS": PembayaranQRIS,
        "Kartu Kredit": PembayaranKartu,
    }

    def __init__(self, customer):
        self.__customer = customer
        self.__riwayat = []         # list (Pesanan, Pembayaran, Pengiriman)
        self.__no = 0
        self.__katalog = []
        self.__unggulan = []
        self.__isi_katalog()

    # ---------- data demo ----------
    def __isi_katalog(self):
        nova = Seller("S001", "Nova Studio", "hi@novastudio.id", "081200000001", "Jakarta", 4.8)
        iron = Seller("S002", "Ironclad Games", "hi@ironclad.id", "081200000002", "Bandung", 4.5)
        lantern = Seller("S003", "Lantern Works", "hi@lantern.id", "081200000003", "Surabaya", 4.6)
        barn = Seller("S004", "Pixel Barn", "hi@pixelbarn.id", "081200000004", "Yogyakarta", 4.9)
        resmi = Seller("S000", "BestDeal Official", "cs@bestdeal.id", "081200000000", "Jakarta", 5.0)

        def g(*a, **k):
            return Game(*a, **k)

        g1 = g("G001", "Eclipse Warden", 549000, "RPG", nova,
               "RPG dunia terbuka: jadi penjaga terakhir kerajaan saat gerhana abadi menelan langit.",
               ("#6a3df0", "#10002b"), diskon=25, rilis="2025", ulasan=94)
        g2 = g("G002", "Neon Circuit", 399000, "Balapan", barn,
               "Balapan malam hari di kota neon dengan drift ekstrem dan mobil bisa dimodif.",
               ("#00e5ff", "#1a0033"), diskon=40, rilis="2026", ulasan=88)
        g3 = g("G003", "Iron Frontier", 299000, "Strategi", iron,
               "Bangun koloni di perbatasan baru, kelola sumber daya, dan pertahankan dari serangan.",
               ("#c97b2d", "#2b1608"), rilis="2024", ulasan=91)
        g4 = g("G004", "Hollow Lantern", 249000, "Horor", lantern,
               "Telusuri hutan berkabut dengan satu lentera. Jangan biarkan apinya padam.",
               ("#2e8b57", "#02120a"), diskon=50, rilis="2025", ulasan=86)
        g5 = g("G005", "Pixel Harvest", 129000, "Indie", barn,
               "Simulasi bertani santai bergaya pixel art. Tanam, panen, dan dekor rumahmu.",
               ("#ffd166", "#ef476f"), rilis="2023", ulasan=97)
        g6 = g("G006", "Skyforge Legends", 599000, "Aksi", nova,
               "Aksi hack-and-slash di kota melayang, dengan combo tanpa batas dan bos raksasa.",
               ("#ff6b35", "#1b1b3a"), diskon=15, rilis="2026", ulasan=90)
        g7 = g("G007", "Void Raiders", 459000, "Tembak", iron,
               "Shooter co-op 4 pemain: rebut kapal alien terbengkalai dan bawa pulang hartanya.",
               ("#3a86ff", "#000814"), diskon=30, rilis="2026", ulasan=84)
        g8 = g("G008", "Mythic Tactics", 349000, "Strategi", iron,
               "Strategi turn-based dengan pasukan mitologi dan pohon skill yang dalam.",
               ("#e0aaff", "#240046"), diskon=20, rilis="2025", ulasan=89)
        g9 = g("G009", "Drift Kings", 279000, "Balapan", barn,
               "Arcade racing kompetitif online. Naik peringkat dan jadi raja drift.",
               ("#f72585", "#3a0ca3"), rilis="2024", ulasan=82)
        g10 = g("G010", "Last Signal", 219000, "Horor", lantern,
                "Horor survival di stasiun radio terpencil. Sinyal terakhir bukan dari manusia.",
                ("#9ca3af", "#111827"), diskon=35, rilis="2024", ulasan=87)
        g11 = g("G011", "Tiny Kingdoms", 99000, "Indie", barn,
                "Kerajaan mungil, keputusan besar. Puzzle-strategi singkat yang bikin ketagihan.",
                ("#80ed99", "#22577a"), diskon=10, rilis="2023", ulasan=93)
        g12 = g("G012", "Blade of Ashes", 649000, "Aksi", nova,
                "Samurai di dunia pasca-perang: duel presisi, cerita kelam, visual memukau.",
                ("#ef233c", "#2b2d42"), rilis="2026", ulasan=92)

        d1 = DLC("D001", "Eclipse Warden: Shadow Realm", 189000, g1,
                 "Ekspansi wilayah baru, 12 jam cerita tambahan, dan senjata legendaris.",
                 ("#9d4edd", "#10002b"))
        d2 = DLC("D002", "Neon Circuit: Turbo Pack", 99000, g2,
                 "10 mobil baru, 4 trek malam hari, dan kustomisasi neon ekstra.",
                 ("#00b4d8", "#03045e"))
        b1 = Bundle("B001", "Paket Horor Malam", [g4, g10], resmi,
                    "Dua game horor sekaligus dengan harga hemat. Jangan main sendirian.",
                    ("#52796f", "#0b090a"))
        b2 = Bundle("B002", "Paket Strategi Raja", [g3, g8], resmi,
                    "Dua strategi terbaik dalam satu paket untuk para ahli taktik.",
                    ("#b08968", "#1d1308"))

        self.__katalog = [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12, d1, d2, b1, b2]
        self.__unggulan = [g1, g2, g6, g7, g12]

        # library awal + jam main
        for game, jam in ((g3, 42.5), (g5, 18.0), (g9, 7.5)):
            self.__customer.tambah_ke_library(game)
            self.__customer.tambah_jam_main(game, jam)

    # ---------- akses ----------
    def get_customer(self):
        return self.__customer

    def get_katalog(self):
        return list(self.__katalog)

    def get_unggulan(self):
        return list(self.__unggulan)

    def get_riwayat(self):
        return list(self.__riwayat)

    def daftar_kategori(self):
        urut = ["Semua", "Aksi", "RPG", "Strategi", "Balapan", "Horor", "Indie", "Tembak",
                "DLC", "Paket"]
        return urut

    def cari(self, query="", kategori="Semua"):
        q = query.strip().lower()
        hasil = []
        for p in self.__katalog:
            if kategori != "Semua" and p.get_kategori() != kategori:
                continue
            if q and q not in p.get_nama_produk().lower() \
                    and q not in p.get_kategori().lower() \
                    and q not in p.nama_publisher().lower():
                continue
            hasil.append(p)
        return hasil

    def library_game(self):
        return [p for p in self.__customer.get_library() if p.bisa_dimainkan()]

    # ---------- transaksi ----------
    def beli(self, produk, nama_metode):
        ok, pesan = produk.bisa_dibeli_oleh(self.__customer)
        if not ok:
            return False, pesan, None

        self.__no += 1
        pesanan = Pesanan(f"ORD{self.__no:03d}", self.__customer,
                          date.today().strftime("%d-%m-%Y"))
        pesanan.tambah_produk("D001", produk, 1)

        pembayaran = self.METODE[nama_metode](f"PAY{self.__no:03d}", pesanan, nama_metode)
        ok, pesan = pembayaran.proses()
        if not ok:
            produk.set_stok(produk.get_stok() + 1)   # kembalikan stok
            return False, pesan, None

        produk.berikan_ke(self.__customer)
        pesanan.set_status("Selesai")
        pengiriman = Pengiriman(f"SHP{self.__no:03d}", pesanan, Pengiriman.buat_kunci(),
                                "Pengiriman Digital", 0, "Instan")
        pengiriman.ubah_status("Terkirim")
        self.__riwayat.append((pesanan, pembayaran, pengiriman))
        return True, "Pembelian berhasil!", pengiriman


class Pengaturan:
    def __init__(self):
        self.__autoplay = True
        self.__konfirmasi = True
        self.__layar_penuh = False
        self.__aksen = "Oranye"

    def get_autoplay(self):
        return self.__autoplay

    def set_autoplay(self, v):
        self.__autoplay = bool(v)

    def get_konfirmasi(self):
        return self.__konfirmasi

    def set_konfirmasi(self, v):
        self.__konfirmasi = bool(v)

    def get_layar_penuh(self):
        return self.__layar_penuh

    def set_layar_penuh(self, v):
        self.__layar_penuh = bool(v)

    def get_aksen(self):
        return self.__aksen

    def set_aksen(self, nama):
        if Tema.terapkan_aksen(nama):
            self.__aksen = nama


# ======================================================================
# GUI : TEMA & KOMPONEN KECIL
# ======================================================================
class Tema:
    BG = "#ffffff"
    NAV = "#ffffff"
    PANEL = "#fff4ea"
    PANEL2 = "#fff8f2"
    KARTU = "#ffffff"
    KARTU_HOVER = "#fff3e8"
    CHIP = "#f6f1ec"
    GARIS = "#efe6dd"
    TEKS = "#1c1410"
    REDUP = "#6b5d52"
    NONAKTIF = "#a8998c"
    HIJAU = "#1a8f4a"
    DISKON_BG = "#ff7a1a"
    DISKON_FG = "#1c1410"
    AKSEN_TEKS = "#c2410c"
    FONT = "Segoe UI"
    AKSEN = {"Oranye": "#ff7a1a", "Biru": "#2f8cff", "Hijau": "#1db954", "Ungu": "#8b5cf6"}
    aksen = "#ff7a1a"

    @classmethod
    def terapkan_aksen(cls, nama):
        if nama in cls.AKSEN:
            cls.aksen = cls.AKSEN[nama]
            return True
        return False


def lukis_art(c, w, h, produk, badge=True):
    """Gambar cover game prosedural (gradien + bentuk + monogram) di Canvas."""
    c1, c2 = produk.get_warna()
    n = 28
    for i in range(n):
        c.create_rectangle(0, h * i // n, w, h * (i + 1) // n + 1,
                           fill=campur(c1, c2, i / (n - 1)), outline="")
    rnd = random.Random(produk.get_id_produk())
    for _ in range(4):
        r = rnd.randint(int(h * 0.12), int(h * 0.35))
        x, y = rnd.randint(0, w), rnd.randint(0, int(h * 0.6))
        c.create_oval(x - r, y - r, x + r, y + r, outline="",
                      fill=campur(c1, "#ffffff", rnd.uniform(0.08, 0.3)))
    inisial = "".join(k[0] for k in produk.get_nama_produk().replace(":", "").split()[:2]).upper()
    c.create_text(w // 2, int(h * 0.42), text=inisial, anchor="center",
                  fill=campur(c1, "#ffffff", 0.55), font=(Tema.FONT, -int(h * 0.38), "bold"))
    for lapis, gelap in ((0.62, 0.35), (0.80, 0.6)):
        pts = [0, h]
        for k in range(7):
            pts += [w * k // 6, int(h * lapis) + rnd.randint(-int(h * 0.1), int(h * 0.1))]
        pts += [w, h]
        c.create_polygon(pts, fill=campur(c2, "#000000", gelap), outline="")
    if badge and produk.label_tipe() != "Game":
        teks = produk.label_tipe().upper()
        c.create_rectangle(8, 8, 16 + len(teks) * 8, 28, fill=Tema.aksen, outline="")
        c.create_text(12, 18, text=teks, anchor="w", fill=Tema.TEKS,
                      font=(Tema.FONT, 8, "bold"))


class TombolFlat(tk.Label):
    def __init__(self, parent, teks, perintah, bg=None, fg="#1c1410", font=None,
                 padx=16, pady=8):
        warna = bg or Tema.aksen
        super().__init__(parent, text=teks, bg=warna, fg=fg, padx=padx, pady=pady,
                         font=font or (Tema.FONT, 10, "bold"), cursor="hand2")
        self._normal = warna
        self._hover = campur(warna, "#ffffff", 0.18)
        self._perintah = perintah
        self.bind("<Enter>", lambda e: self.configure(bg=self._hover))
        self.bind("<Leave>", lambda e: self.configure(bg=self._normal))
        self.bind("<Button-1>", lambda e: self._perintah())


class InputCari(tk.Frame):
    def __init__(self, parent, placeholder, saat_ubah, lebar=30, bg=None):
        bg = bg or Tema.KARTU
        super().__init__(parent, bg=bg, highlightthickness=1,
                         highlightbackground=Tema.GARIS, highlightcolor=Tema.aksen)
        self._placeholder = placeholder
        self._saat_ubah = saat_ubah
        self._aktif_ph = False
        self._after = None
        tk.Label(self, text="🔍", bg=bg, fg=Tema.REDUP, font=(Tema.FONT, 10)).pack(
            side="left", padx=(10, 0))
        self._entry = tk.Entry(self, bg=bg, fg=Tema.TEKS, insertbackground=Tema.TEKS,
                               relief="flat", width=lebar, font=(Tema.FONT, 11),
                               highlightthickness=0)
        self._entry.pack(side="left", padx=8, pady=7)
        self._tampil_ph()
        self._entry.bind("<FocusIn>", self._fokus_masuk)
        self._entry.bind("<FocusOut>", self._fokus_keluar)
        self._entry.bind("<KeyRelease>", self._ketik)
        self._entry.bind("<Return>", lambda e: self._kirim())

    def _tampil_ph(self):
        self._entry.delete(0, "end")
        self._entry.insert(0, self._placeholder)
        self._entry.configure(fg=Tema.REDUP)
        self._aktif_ph = True

    def _fokus_masuk(self, _):
        if self._aktif_ph:
            self._entry.delete(0, "end")
            self._entry.configure(fg=Tema.TEKS)
            self._aktif_ph = False

    def _fokus_keluar(self, _):
        if not self._entry.get():
            self._tampil_ph()

    def _ketik(self, _):
        if self._after:
            self.after_cancel(self._after)
        self._after = self.after(200, self._kirim)

    def _kirim(self):
        self._after = None
        self._saat_ubah(self.get_teks())

    def nonaktifkan(self):
        self._entry.configure(state="disabled", disabledforeground=Tema.REDUP,
                              disabledbackground=self.cget("bg"))

    def get_teks(self):
        return "" if self._aktif_ph else self._entry.get()


class ScrollFrame(tk.Frame):
    """Area yang bisa di-scroll (mouse wheel + scrollbar). Isi taruh di .isi"""

    def __init__(self, parent, bg=Tema.BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, yscrollincrement=20)
        self._sb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                 style="Game.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=self._sb.set)
        self._sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.isi = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.isi, anchor="nw")
        self.isi.bind("<Configure>",
                      lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self._win, width=e.width))

    def gulir(self, arah):
        if self.canvas.yview() != (0.0, 1.0):
            self.canvas.yview_scroll(arah * 3, "units")

    def ke_atas(self):
        self.canvas.yview_moveto(0)

    def posisi(self):
        return self.canvas.yview()[0]

    def pulihkan(self, frac):
        self.after(40, lambda: self.canvas.yview_moveto(frac))

    def kosongkan(self):
        for w in self.isi.winfo_children():
            w.destroy()


def baris_harga(parent, produk, customer, bg, ukuran=11):
    f = tk.Frame(parent, bg=bg)
    if produk.dimiliki_oleh(customer):
        tk.Label(f, text="✓ Di Library", fg=Tema.HIJAU, bg=bg,
                 font=(Tema.FONT, ukuran, "bold")).pack(side="left")
        return f
    harga = produk.harga_akhir()
    d = produk.diskon_persen()
    if d > 0:
        b = tk.Label(f, text=f"-{d}%", bg=Tema.DISKON_BG, fg=Tema.DISKON_FG, padx=5,
                     font=(Tema.FONT, ukuran - 1, "bold"))
        b._tetap = True
        b.pack(side="left", padx=(0, 8))
        coret = tkfont.Font(family=Tema.FONT, size=ukuran - 2, overstrike=True)
        lc = tk.Label(f, text=rupiah(produk.get_harga()), fg=Tema.REDUP, bg=bg, font=coret)
        lc._font = coret
        lc.pack(side="left", padx=(0, 8))
    tk.Label(f, text="Gratis" if harga == 0 else rupiah(harga), fg=Tema.TEKS, bg=bg,
             font=(Tema.FONT, ukuran, "bold")).pack(side="left")
    return f


class KartuProduk(tk.Frame):
    def __init__(self, parent, produk, customer, lebar, saat_klik):
        super().__init__(parent, bg=Tema.KARTU, cursor="hand2", highlightthickness=1,
                         highlightbackground=Tema.GARIS)
        tinggi = int(lebar * 9 / 16)
        art = tk.Canvas(self, width=lebar, height=tinggi, highlightthickness=0, bg=Tema.KARTU)
        art.pack()
        lukis_art(art, lebar, tinggi, produk)
        body = tk.Frame(self, bg=Tema.KARTU)
        body.pack(fill="both", expand=True, padx=12, pady=(10, 12))
        tk.Label(body, text=produk.get_nama_produk(), fg=Tema.TEKS, bg=Tema.KARTU,
                 font=(Tema.FONT, 11, "bold"), anchor="w", justify="left",
                 wraplength=lebar - 28).pack(anchor="w")
        tk.Label(body, text=f"{produk.get_kategori()}  •  {produk.nama_publisher()}",
                 fg=Tema.REDUP, bg=Tema.KARTU, font=(Tema.FONT, 9)).pack(anchor="w", pady=(2, 8))
        baris_harga(body, produk, customer, Tema.KARTU).pack(anchor="w", side="bottom")
        self._ikat(self, lambda e: saat_klik(produk))
        self._ikat_hover(self)

    def _ikat(self, w, fn):
        w.bind("<Button-1>", fn, add="+")
        for c in w.winfo_children():
            self._ikat(c, fn)

    def _ikat_hover(self, w):
        w.bind("<Enter>", lambda e: self._warna(self, Tema.KARTU_HOVER), add="+")
        w.bind("<Leave>", self._keluar, add="+")
        for c in w.winfo_children():
            self._ikat_hover(c)

    def _keluar(self, _):
        try:
            w = self.winfo_containing(*self.winfo_pointerxy())
        except (KeyError, tk.TclError):
            w = None
        while w is not None:
            if w is self:
                return
            w = w.master
        self._warna(self, Tema.KARTU)

    def _warna(self, w, warna):
        if not getattr(w, "_tetap", False) and not isinstance(w, tk.Canvas):
            w.configure(bg=warna)
        for c in w.winfo_children():
            self._warna(c, warna)


# ======================================================================
# GUI : NAVBAR
# ======================================================================
class NavBar(tk.Frame):
    """Navbar BestDeal. Menu selain TOKO dan kolom cari hanya tampilan (belum bisa diklik)."""
    MENU = (("home", "TOKO"), ("library", "LIBRARY"), ("akun", "AKUN"), ("setting", "SETTING"))
    AKTIF = ("home",)

    def __init__(self, parent, app):
        super().__init__(parent, bg=Tema.NAV, height=72)
        self.pack_propagate(False)
        self._app = app

        logo = tk.Frame(self, bg=Tema.NAV)
        logo.pack(side="left", padx=(32, 36))
        ic = tk.Canvas(logo, width=36, height=36, bg=Tema.NAV, highlightthickness=0)
        ic.pack(side="left")
        ic.create_oval(0, 0, 36, 36, fill=Tema.aksen, outline="")
        ic.create_text(18, 18, text="B", fill=Tema.TEKS, font=(Tema.FONT, 14, "bold"))
        tk.Label(logo, text="BestDeal", fg=Tema.TEKS, bg=Tema.NAV,
                 font=(Tema.FONT, 18, "bold")).pack(side="left", padx=(10, 0))

        for kunci, teks in self.MENU:
            aktif = kunci in self.AKTIF
            f = tk.Frame(self, bg=Tema.NAV)
            f.pack(side="left", fill="y", padx=4)
            tk.Label(f, text=teks, fg=Tema.TEKS if aktif else Tema.NONAKTIF, bg=Tema.NAV,
                     font=(Tema.FONT, 10, "bold"), padx=12).pack(expand=True)
            tk.Frame(f, bg=Tema.aksen if aktif else Tema.NAV, height=3).pack(
                fill="x", side="bottom")

        self._avatar = tk.Canvas(self, width=40, height=40, bg=Tema.NAV, highlightthickness=0)
        self._avatar.pack(side="right", padx=(12, 32))
        self._saldo = tk.Label(self, fg="#9a3d00", bg="#fff1e4", padx=12, pady=5,
                               font=(Tema.FONT, 10, "bold"))
        self._saldo.pack(side="right", padx=8)
        self.cari = InputCari(self, "Cari game, genre, publisher...", lambda q: None,
                              lebar=28, bg=Tema.CHIP)
        self.cari.nonaktifkan()
        self.cari.pack(side="right", padx=16)
        self.perbarui()

    def perbarui(self):
        c = self._app.toko.get_customer()
        self._saldo.configure(text=rupiah(c.get_saldo()))
        a = self._avatar
        a.delete("all")
        a.create_oval(2, 2, 38, 38, fill=Tema.TEKS, outline="")
        a.create_text(20, 20, text=c.get_nama()[:1].upper(), fill="#ffffff",
                      font=(Tema.FONT, 13, "bold"))

    def set_aktif(self, kunci):
        pass    # hanya Home yang aktif untuk saat ini


# ======================================================================
# GUI : HALAMAN  (Abstraction + Inheritance + Polymorphism)
# ======================================================================
class Halaman(tk.Frame, ABC):
    """Kelas abstrak untuk semua halaman. Subclass wajib implement bangun()."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=Tema.BG)
        self._app = app
        self._kotor = True

    @abstractmethod
    def bangun(self):
        ...

    def segarkan(self):
        self.bangun()
        self._kotor = False

    def tandai_kotor(self):
        self._kotor = True

    def saat_ditampilkan(self):
        if self._kotor:
            self.segarkan()

    def judul(self, parent, teks, aksi_teks=None, aksi=None, pad=(24, 12)):
        f = tk.Frame(parent, bg=Tema.BG)
        f.pack(fill="x", padx=32, pady=pad)
        tk.Label(f, text=teks, fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 16, "bold")).pack(side="left")
        if aksi_teks:
            lb = tk.Label(f, text=aksi_teks, fg=Tema.AKSEN_TEKS, bg=Tema.BG, cursor="hand2",
                          font=(Tema.FONT, 10, "bold"))
            lb.pack(side="right")
            lb.bind("<Button-1>", lambda e: aksi())
        return f


class HomePage(Halaman):
    GAP = 20

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)
        self._query = ""
        self._kategori = "Semua"
        self._idx = 0
        self._after_id = None
        self._unggulan = []
        self._art = None
        self._info = None
        self._dots = None
        self._ukuran = (0, 0)

    # ---------- kontrol ----------
    def atur_pencarian(self, q):
        self._query = q
        self.scroll.ke_atas()
        self.bangun()

    def atur_kategori(self, k):
        self._kategori = k
        self.scroll.ke_atas()
        self.bangun()

    def segarkan(self):
        frac = self.scroll.posisi()
        super().segarkan()
        self.scroll.pulihkan(frac)

    def destroy(self):
        self._hentikan_autoplay()
        super().destroy()

    # ---------- build ----------
    def bangun(self):
        self._hentikan_autoplay()
        self._art = None
        self.scroll.kosongkan()
        isi = self.scroll.isi
        toko = self._app.toko
        lebar = self._app.lebar_konten()
        mode_cari = bool(self._query.strip()) or self._kategori != "Semua"

        if not mode_cari:
            self._hero(isi, lebar)
        self._chips(isi)

        if mode_cari:
            hasil = toko.cari(self._query, self._kategori)
            self.judul(isi, f"Hasil ({len(hasil)})", pad=(8, 12))
            if hasil:
                self._grid(isi, hasil, lebar)
            else:
                tk.Label(isi, text="Tidak ada produk yang cocok.", fg=Tema.REDUP,
                         bg=Tema.BG, font=(Tema.FONT, 11)).pack(anchor="w", padx=32, pady=20)
            return

        katalog = toko.get_katalog()
        panas = sorted([p for p in katalog if p.bisa_dimainkan() and p.diskon_persen() > 0],
                       key=lambda p: -p.diskon_persen())[:self._kolom(lebar)]
        self.judul(isi, "Deal terpanas")
        self._grid(isi, panas, lebar)
        self._panel_bawah(isi)
        self.judul(isi, "Semua game", pad=(32, 12))
        self._grid(isi, [p for p in katalog if p.bisa_dimainkan()], lebar)
        self.judul(isi, "DLC & paket hemat")
        self._grid(isi, [p for p in katalog if not p.bisa_dimainkan()], lebar)
        tk.Label(isi, text="BestDeal  •  Toko game digital", fg=Tema.REDUP, bg=Tema.BG,
                 font=(Tema.FONT, 9)).pack(pady=(10, 28))

    def _kolom(self, lebar):
        return max(2, (lebar + self.GAP) // (230 + self.GAP))

    def _grid(self, parent, items, lebar):
        kolom = self._kolom(lebar)
        lebar_kartu = (lebar - self.GAP * (kolom - 1)) // kolom
        f = tk.Frame(parent, bg=Tema.BG)
        f.pack(fill="x", padx=32)
        customer = self._app.toko.get_customer()
        for i, p in enumerate(items):
            KartuProduk(f, p, customer, lebar_kartu, self._app.buka_produk).grid(
                row=i // kolom, column=i % kolom, sticky="nsew",
                padx=(0, self.GAP if i % kolom != kolom - 1 else 0), pady=(0, self.GAP))

    def _chips(self, parent):
        f = tk.Frame(parent, bg=Tema.BG)
        f.pack(fill="x", padx=32, pady=(18, 4))
        for k in self._app.toko.daftar_kategori():
            aktif = k == self._kategori
            TombolFlat(f, k, lambda kk=k: self.atur_kategori(kk),
                       bg=Tema.aksen if aktif else Tema.CHIP,
                       fg=Tema.TEKS if aktif else "#4a3d33",
                       font=(Tema.FONT, 9, "bold"), padx=16, pady=7).pack(
                side="left", padx=(0, 8))

    # ---------- hero ----------
    def _hero(self, parent, lebar):
        self._unggulan = self._app.toko.get_unggulan()
        wrap = tk.Frame(parent, bg=Tema.PANEL)
        wrap.pack(fill="x", padx=32, pady=(16, 4))

        kiri = tk.Frame(wrap, bg=Tema.PANEL)
        kiri.pack(side="left", fill="both", expand=True, padx=(44, 20), pady=36)
        tk.Label(kiri, text="  DEAL HARI INI  ", bg=Tema.TEKS, fg="#ffffff", pady=3,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w")
        tk.Label(kiri, text="Game terbaik,", fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 34, "bold")).pack(anchor="w", pady=(16, 0))
        tk.Label(kiri, text="harga terbaik.", fg=Tema.AKSEN_TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 34, "bold")).pack(anchor="w")
        tk.Label(kiri, text="Diskon sampai 50% untuk game pilihan. Bayar lewat saldo, QRIS, "
                            "atau kartu, kunci lisensi langsung terkirim.",
                 fg="#5a4c41", bg=Tema.PANEL, justify="left", wraplength=400,
                 font=(Tema.FONT, 11)).pack(anchor="w", pady=(12, 20))
        TombolFlat(kiri, "Lihat detail unggulan",
                   lambda: self._app.buka_produk(self._unggulan[self._idx]),
                   padx=24, pady=11).pack(anchor="w")
        st = tk.Frame(kiri, bg=Tema.PANEL)
        st.pack(anchor="w", pady=(26, 0))
        for angka, ket in (("16", "produk"), ("5", "publisher"), ("Instan", "kunci lisensi")):
            k = tk.Frame(st, bg=Tema.PANEL)
            k.pack(side="left", padx=(0, 28))
            tk.Label(k, text=angka, fg=Tema.TEKS, bg=Tema.PANEL,
                     font=(Tema.FONT, 16, "bold")).pack(anchor="w")
            tk.Label(k, text=ket, fg=Tema.REDUP, bg=Tema.PANEL,
                     font=(Tema.FONT, 9)).pack(anchor="w")

        kanan = tk.Frame(wrap, bg=Tema.PANEL)
        kanan.pack(side="right", padx=(0, 44), pady=28)
        w = max(360, min(500, int(lebar * 0.40)))
        h = int(w * 10 / 16)
        self._ukuran = (w, h)
        kartu = tk.Frame(kanan, bg=Tema.KARTU, padx=10, pady=10)
        kartu.pack()
        self._art = tk.Canvas(kartu, width=w, height=h, highlightthickness=0,
                              bg=Tema.KARTU, cursor="hand2")
        self._art.pack()
        self._art.bind("<Button-1>", lambda e: self._app.buka_produk(self._unggulan[self._idx]))
        self._info = tk.Frame(kartu, bg=Tema.KARTU)
        self._info.pack(fill="x", pady=(10, 2))
        self._dots = tk.Frame(kanan, bg=Tema.PANEL)
        self._dots.pack(pady=(10, 0))
        self._idx = min(self._idx, len(self._unggulan) - 1)
        self._tampil_banner()
        self._jadwal_autoplay()

    def _tampil_banner(self):
        w, h = self._ukuran
        p = self._unggulan[self._idx]
        self._art.delete("all")
        lukis_art(self._art, w, h, p, badge=False)
        if p.diskon_persen() > 0:
            self._art.create_rectangle(12, 12, 78, 38, fill=Tema.aksen, outline="")
            self._art.create_text(45, 25, text=f"-{p.diskon_persen()}%", fill=Tema.TEKS,
                                  font=(Tema.FONT, 11, "bold"))
        for x in self._info.winfo_children():
            x.destroy()
        kiri = tk.Frame(self._info, bg=Tema.KARTU)
        kiri.pack(side="left")
        tk.Label(kiri, text=p.get_nama_produk(), fg=Tema.TEKS, bg=Tema.KARTU,
                 font=(Tema.FONT, 15, "bold")).pack(anchor="w")
        tk.Label(kiri, text=f"{p.get_kategori()}  •  {p.nama_publisher()}  •  "
                            f"{p.get_ulasan()}% positif",
                 fg=Tema.REDUP, bg=Tema.KARTU, font=(Tema.FONT, 9)).pack(anchor="w")
        baris_harga(self._info, p, self._app.toko.get_customer(), Tema.KARTU, 12).pack(
            side="right")

        for x in self._dots.winfo_children():
            x.destroy()
        TombolFlat(self._dots, "‹", lambda: self._geser(-1), bg=Tema.KARTU, padx=10,
                   pady=1).pack(side="left", padx=6)
        for i in range(len(self._unggulan)):
            d = tk.Label(self._dots, text="●", cursor="hand2", bg=Tema.PANEL,
                         fg=Tema.aksen if i == self._idx else "#e8dcd1", font=(Tema.FONT, 10))
            d.pack(side="left", padx=2)
            d.bind("<Button-1>", lambda e, k=i: self._ke(k))
        TombolFlat(self._dots, "›", lambda: self._geser(1), bg=Tema.KARTU, padx=10,
                   pady=1).pack(side="left", padx=6)

    def _ke(self, i):
        self._idx = i
        self._tampil_banner()
        self._jadwal_autoplay()

    def _geser(self, arah):
        self._ke((self._idx + arah) % len(self._unggulan))

    def _jadwal_autoplay(self):
        self._hentikan_autoplay()
        if self._app.pengaturan.get_autoplay() and self._art is not None:
            self._after_id = self.after(5000, self._auto)

    def _auto(self):
        self._after_id = None
        if self.winfo_exists() and self._art is not None and self._art.winfo_exists():
            self._geser(1)

    def _hentikan_autoplay(self):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    # ---------- panel library & paket ----------
    def _panel_bawah(self, parent):
        toko = self._app.toko
        customer = toko.get_customer()
        f = tk.Frame(parent, bg=Tema.BG)
        f.pack(fill="x", padx=32, pady=(10, 0))
        f.columnconfigure(0, weight=6, uniform="p")
        f.columnconfigure(1, weight=5, uniform="p")

        kiri = self._panel(f, "Lanjut main", Tema.PANEL2)
        kiri.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        game = toko.library_game()[:3]
        if not game:
            tk.Label(kiri, text="Belum ada game di library.", fg=Tema.REDUP, bg=Tema.PANEL2,
                     font=(Tema.FONT, 10)).pack(anchor="w", padx=22, pady=(4, 18))
        for g in game:
            self._baris(kiri, g, f"{customer.get_jam_main(g):.1f} jam dimainkan")
        tk.Frame(kiri, bg=Tema.PANEL2, height=18).pack()

        kanan = self._panel(f, "Paket hemat", Tema.PANEL)
        kanan.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        for p in [x for x in toko.get_katalog() if x.get_kategori() == "Paket"]:
            r = self._baris(kanan, p, p.info_tambahan().replace("Isi paket: ", ""))
            baris_harga(r, p, customer, Tema.KARTU, 11).pack(side="right", padx=12)
            r.configure(cursor="hand2")
            self._klik(r, p)
        tk.Frame(kanan, bg=Tema.PANEL, height=18).pack()

    def _panel(self, parent, judul, bg):
        p = tk.Frame(parent, bg=bg)
        tk.Label(p, text=judul, fg=Tema.TEKS, bg=bg,
                 font=(Tema.FONT, 15, "bold")).pack(anchor="w", padx=22, pady=(18, 4))
        return p

    def _baris(self, panel, produk, sub):
        r = tk.Frame(panel, bg=Tema.KARTU)
        r.pack(fill="x", padx=18, pady=(8, 0))
        c = tk.Canvas(r, width=96, height=54, highlightthickness=0, bg=Tema.KARTU)
        c.pack(side="left", padx=8, pady=8)
        lukis_art(c, 96, 54, produk, badge=False)
        t = tk.Frame(r, bg=Tema.KARTU)
        t.pack(side="left")
        tk.Label(t, text=produk.get_nama_produk(), fg=Tema.TEKS, bg=Tema.KARTU,
                 font=(Tema.FONT, 11, "bold")).pack(anchor="w")
        tk.Label(t, text=sub, fg=Tema.REDUP, bg=Tema.KARTU,
                 font=(Tema.FONT, 9)).pack(anchor="w")
        return r

    def _klik(self, w, produk):
        w.bind("<Button-1>", lambda e: self._app.buka_produk(produk), add="+")
        for c in w.winfo_children():
            self._klik(c, produk)


class LibraryPage(Halaman):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._terpilih = None
        self._filter = ""
        self._status = None

        kiri = tk.Frame(self, bg=Tema.PANEL, width=340)
        kiri.pack(side="left", fill="y")
        kiri.pack_propagate(False)
        self._judul = tk.Label(kiri, text="", fg=Tema.TEKS, bg=Tema.PANEL,
                               font=(Tema.FONT, 13, "bold"))
        self._judul.pack(anchor="w", padx=18, pady=(18, 10))
        InputCari(kiri, "Cari di library...", self.atur_filter, lebar=26,
                  bg=Tema.KARTU).pack(fill="x", padx=18, pady=(0, 10))
        self.daftar = ScrollFrame(kiri, bg=Tema.PANEL)
        self.daftar.pack(fill="both", expand=True)
        self.detail = ScrollFrame(self)
        self.detail.pack(side="left", fill="both", expand=True)

    def atur_filter(self, q):
        self._filter = q.strip().lower()
        self.bangun()

    def pilih(self, game):
        self._terpilih = game
        self.bangun()

    def bangun(self):
        toko = self._app.toko
        semua = toko.library_game()
        game = [g for g in semua if self._filter in g.get_nama_produk().lower()]
        self._judul.configure(text=f"LIBRARY  ({len(semua)})")

        if self._terpilih is None or not any(
                g.get_id_produk() == self._terpilih.get_id_produk() for g in semua):
            self._terpilih = semua[0] if semua else None

        self.daftar.kosongkan()
        for g in game:
            self._baris(g)
        if not game:
            tk.Label(self.daftar.isi, text="Tidak ada game.", fg=Tema.REDUP, bg=Tema.PANEL,
                     font=(Tema.FONT, 10)).pack(padx=18, pady=16, anchor="w")
        self._detail()

    def _baris(self, g):
        aktif = self._terpilih is not None and g.get_id_produk() == self._terpilih.get_id_produk()
        bg = Tema.KARTU_HOVER if aktif else Tema.PANEL
        f = tk.Frame(self.daftar.isi, bg=bg, cursor="hand2")
        f.pack(fill="x", padx=10, pady=2)
        c = tk.Canvas(f, width=80, height=45, highlightthickness=0, bg=bg)
        c.pack(side="left", padx=8, pady=6)
        lukis_art(c, 80, 45, g)
        kol = tk.Frame(f, bg=bg)
        kol.pack(side="left", fill="x", expand=True)
        tk.Label(kol, text=g.get_nama_produk(), fg=Tema.TEKS, bg=bg,
                 font=(Tema.FONT, 10, "bold")).pack(anchor="w")
        jam = self._app.toko.get_customer().get_jam_main(g)
        tk.Label(kol, text=f"{g.get_kategori()} • {jam:.1f} jam", fg=Tema.REDUP, bg=bg,
                 font=(Tema.FONT, 9)).pack(anchor="w")
        for w in (f, c, kol) + tuple(kol.winfo_children()):
            w.bind("<Button-1>", lambda e, gg=g: self.pilih(gg))

    def _detail(self):
        self.detail.kosongkan()
        isi = self.detail.isi
        g = self._terpilih
        if g is None:
            tk.Label(isi, text="Library masih kosong.\nBeli game dulu di halaman Toko.",
                     fg=Tema.REDUP, bg=Tema.BG, font=(Tema.FONT, 13)).pack(padx=40, pady=60)
            return
        customer = self._app.toko.get_customer()
        lebar = max(420, min(720, self._app.lebar() - 340 - 100))
        tinggi = int(lebar * 9 / 16)
        c = tk.Canvas(isi, width=lebar, height=tinggi, highlightthickness=0, bg=Tema.BG)
        c.pack(anchor="w", padx=32, pady=(28, 16))
        lukis_art(c, lebar, tinggi, g)
        tk.Label(isi, text=g.get_nama_produk(), fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 24, "bold")).pack(anchor="w", padx=32)
        tk.Label(isi, text=f"{g.get_kategori()}  •  {g.nama_publisher()}  •  Rilis {g.get_rilis()}",
                 fg=Tema.REDUP, bg=Tema.BG, font=(Tema.FONT, 10)).pack(anchor="w", padx=32,
                                                                      pady=(2, 12))
        baris = tk.Frame(isi, bg=Tema.BG)
        baris.pack(anchor="w", padx=32, pady=(0, 14))
        TombolFlat(baris, "▶  MAIN", lambda: self._main(g), bg="#2ea043",
                   font=(Tema.FONT, 12, "bold"), padx=36, pady=10).pack(side="left")
        self._status = tk.Label(baris, text="", fg=Tema.HIJAU, bg=Tema.BG,
                                font=(Tema.FONT, 10, "bold"))
        self._status.pack(side="left", padx=16)

        tk.Label(isi, text=g.get_deskripsi(), fg=Tema.TEKS, bg=Tema.BG, justify="left",
                 wraplength=lebar, font=(Tema.FONT, 11)).pack(anchor="w", padx=32, pady=(0, 14))
        info = (f"Waktu bermain : {customer.get_jam_main(g):.1f} jam\n"
                f"Ulasan        : {g.get_ulasan()}% positif\n"
                f"Publisher     : {g.nama_publisher()}  (★ {g.get_seller().get_rating()})")
        tk.Label(isi, text=info, fg=Tema.REDUP, bg=Tema.PANEL, justify="left",
                 font=("Consolas", 10), padx=16, pady=12).pack(anchor="w", padx=32)
        dlc = [p for p in customer.get_library()
               if isinstance(p, DLC) and p.get_game_induk().get_id_produk() == g.get_id_produk()]
        if dlc:
            tk.Label(isi, text="DLC dimiliki", fg=Tema.TEKS, bg=Tema.BG,
                     font=(Tema.FONT, 12, "bold")).pack(anchor="w", padx=32, pady=(16, 4))
            for d in dlc:
                tk.Label(isi, text="✓ " + d.get_nama_produk(), fg=Tema.HIJAU, bg=Tema.BG,
                         font=(Tema.FONT, 10)).pack(anchor="w", padx=32)
        tk.Frame(isi, bg=Tema.BG, height=30).pack()

    def _main(self, g):
        self._app.toko.get_customer().tambah_jam_main(g, 0.5)
        self._status.configure(text=f"Menjalankan {g.get_nama_produk()}... (simulasi)")
        self.after(1600, self.bangun)
        self._app.perbarui_navbar()
        self._app.halaman_tandai_kotor("home")


class AkunPage(Halaman):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)

    def _kartu(self, parent, judul):
        k = tk.Frame(parent, bg=Tema.PANEL)
        tk.Label(k, text=judul, fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 12, "bold")).pack(anchor="w", padx=20, pady=(16, 8))
        return k

    def bangun(self):
        self.scroll.kosongkan()
        isi = self.scroll.isi
        toko = self._app.toko
        c = toko.get_customer()
        self.judul(isi, "Akun Saya")

        grid = tk.Frame(isi, bg=Tema.BG)
        grid.pack(fill="x", padx=32)
        grid.columnconfigure(0, weight=1, uniform="k")
        grid.columnconfigure(1, weight=1, uniform="k")

        # --- profil ---
        kp = self._kartu(grid, "Profil")
        kp.grid(row=0, column=0, sticky="nsew", padx=(0, 9), pady=(0, 18))
        av = tk.Canvas(kp, width=84, height=84, bg=Tema.PANEL, highlightthickness=0)
        av.pack(anchor="w", padx=20)
        av.create_oval(2, 2, 82, 82, fill=Tema.aksen, outline="")
        av.create_text(42, 42, text=c.get_nama()[:1].upper(), fill="#fff",
                       font=(Tema.FONT, 30, "bold"))
        tk.Label(kp, text=f"{c.get_nama()}  ({c.peran()})", fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 15, "bold")).pack(anchor="w", padx=20, pady=(10, 6))
        tk.Label(kp, text=c.tampilkan_profil(), fg=Tema.REDUP, bg=Tema.PANEL, justify="left",
                 font=("Consolas", 10)).pack(anchor="w", padx=20)
        ubah = tk.Frame(kp, bg=Tema.PANEL)
        ubah.pack(anchor="w", padx=20, pady=(14, 18))
        e = tk.Entry(ubah, bg=Tema.KARTU, fg=Tema.TEKS, insertbackground=Tema.TEKS,
                     relief="flat", font=(Tema.FONT, 11), width=18)
        e.insert(0, c.get_nama())
        e.pack(side="left", ipady=6, padx=(0, 8))
        TombolFlat(ubah, "Ubah Nama", lambda: self._ubah_nama(e.get()), pady=6).pack(side="left")

        # --- saldo & statistik ---
        ks = self._kartu(grid, "Dompet & Statistik")
        ks.grid(row=0, column=1, sticky="nsew", padx=(9, 0), pady=(0, 18))
        tk.Label(ks, text=rupiah(c.get_saldo()), fg=Tema.HIJAU, bg=Tema.PANEL,
                 font=(Tema.FONT, 26, "bold")).pack(anchor="w", padx=20)
        tk.Label(ks, text="Saldo BestDeal", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 10)).pack(anchor="w", padx=20, pady=(0, 10))
        tp = tk.Frame(ks, bg=Tema.PANEL)
        tp.pack(anchor="w", padx=20, pady=(0, 14))
        for n in (100_000, 500_000, 1_000_000):
            TombolFlat(tp, f"+ {rupiah(n)}", lambda x=n: self._topup(x), pady=6,
                       font=(Tema.FONT, 9, "bold")).pack(side="left", padx=(0, 8))
        game = toko.library_game()
        total_jam = sum(c.get_jam_main(g) for g in game)
        tk.Label(ks, text=f"Game di library : {len(game)}\nTotal jam main  : {total_jam:.1f} jam\n"
                          f"Total pesanan   : {len(toko.get_riwayat())}",
                 fg=Tema.REDUP, bg=Tema.PANEL, justify="left",
                 font=("Consolas", 10)).pack(anchor="w", padx=20, pady=(0, 18))

        # --- riwayat ---
        self.judul(isi, "Riwayat Pesanan", pad=(6, 10))
        riwayat = toko.get_riwayat()
        if not riwayat:
            tk.Label(isi, text="Belum ada pesanan. Pembelian kamu akan muncul di sini.",
                     fg=Tema.REDUP, bg=Tema.BG, font=(Tema.FONT, 10)).pack(anchor="w", padx=32)
        for pesanan, bayar, kirim in reversed(riwayat):
            k = tk.Frame(isi, bg=Tema.PANEL)
            k.pack(fill="x", padx=32, pady=(0, 10))
            teks = (pesanan.get_pesanan() +
                    f"\nMetode     : {bayar.get_metode()} (admin {rupiah(bayar.biaya_admin())})"
                    f"\nDibayar    : {rupiah(bayar.get_jumlah_bayar())}  [{bayar.get_status()}]"
                    f"\nKunci      : {kirim.get_kunci()}  [{kirim.get_status()} ke "
                    f"{kirim.get_alamat_tujuan()}]"
                    f"\nPengiriman : {kirim.get_jasa()} • {kirim.get_estimasi()} • "
                    f"ongkir {rupiah(kirim.get_biaya())}")
            tk.Label(k, text=teks, fg=Tema.TEKS, bg=Tema.PANEL, justify="left",
                     font=("Consolas", 10), padx=18, pady=14).pack(anchor="w")
        tk.Frame(isi, bg=Tema.BG, height=30).pack()

    def _ubah_nama(self, nama):
        if not nama.strip():
            messagebox.showwarning("Nama kosong", "Nama tidak boleh kosong.")
            return
        self._app.toko.get_customer().set_nama(nama)
        self._app.refresh_semua()

    def _topup(self, jumlah):
        self._app.toko.get_customer().tambah_saldo(jumlah)
        self._app.refresh_semua()


class SettingPage(Halaman):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)

    def _baris(self, judul, ket):
        f = tk.Frame(self.scroll.isi, bg=Tema.PANEL)
        f.pack(fill="x", padx=32, pady=(0, 10))
        kiri = tk.Frame(f, bg=Tema.PANEL)
        kiri.pack(side="left", padx=20, pady=16)
        tk.Label(kiri, text=judul, fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 11, "bold")).pack(anchor="w")
        tk.Label(kiri, text=ket, fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9)).pack(anchor="w")
        kanan = tk.Frame(f, bg=Tema.PANEL)
        kanan.pack(side="right", padx=20)
        return kanan

    def _cek(self, parent, var, cmd):
        return tk.Checkbutton(parent, variable=var, command=cmd, bg=Tema.PANEL,
                              activebackground=Tema.PANEL, selectcolor=Tema.KARTU,
                              fg=Tema.TEKS, highlightthickness=0, bd=0, cursor="hand2")

    def bangun(self):
        self.scroll.kosongkan()
        p = self._app.pengaturan
        self.judul(self.scroll.isi, "Pengaturan")

        v1 = tk.BooleanVar(value=p.get_autoplay())
        self._cek(self._baris("Banner otomatis", "Banner unggulan di halaman Toko geser tiap 5 detik."),
                  v1, lambda: p.set_autoplay(v1.get())).pack()

        v2 = tk.BooleanVar(value=p.get_konfirmasi())
        self._cek(self._baris("Konfirmasi sebelum membeli", "Tampilkan dialog konfirmasi saat checkout."),
                  v2, lambda: p.set_konfirmasi(v2.get())).pack()

        v3 = tk.BooleanVar(value=p.get_layar_penuh())

        def layar():
            p.set_layar_penuh(v3.get())
            self._app.atur_layar_penuh(v3.get())
        self._cek(self._baris("Layar penuh", "Tekan Esc untuk keluar dari mode layar penuh."),
                  v3, layar).pack()

        kanan = self._baris("Warna aksen", "Ganti warna utama aplikasi.")
        for nama, hex_ in Tema.AKSEN.items():
            aktif = nama == p.get_aksen()
            TombolFlat(kanan, ("✓ " if aktif else "") + nama, lambda n=nama: self._ganti(n),
                       bg=hex_, padx=12, pady=6, font=(Tema.FONT, 9, "bold")).pack(
                side="left", padx=4)

        self._baris("Tentang", "BestDeal v1.0 • Tkinter • Proyek PBO")
        tk.Frame(self.scroll.isi, bg=Tema.BG, height=30).pack()

    def _ganti(self, nama):
        self._app.pengaturan.set_aksen(nama)
        self._app.bangun_ulang("setting")


# ======================================================================
# GUI : DIALOG DETAIL / BELI
# ======================================================================
class DialogProduk(tk.Toplevel):
    def __init__(self, app, produk):
        super().__init__(app.root, bg=Tema.BG)
        self._app = app
        self._produk = produk
        self.title(produk.get_nama_produk())
        self.resizable(False, False)
        self.transient(app.root)

        toko = app.toko
        customer = toko.get_customer()
        lebar_art = 520
        tinggi_art = int(lebar_art * 9 / 16)

        kiri = tk.Frame(self, bg=Tema.BG)
        kiri.grid(row=0, column=0, padx=(24, 12), pady=24, sticky="n")
        art = tk.Canvas(kiri, width=lebar_art, height=tinggi_art, highlightthickness=0, bg=Tema.BG)
        art.pack()
        lukis_art(art, lebar_art, tinggi_art, produk)
        tk.Label(kiri, text=produk.get_nama_produk(), fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 18, "bold"), wraplength=lebar_art, justify="left").pack(
            anchor="w", pady=(14, 2))
        tk.Label(kiri, text=f"{produk.label_tipe()} • {produk.get_kategori()}",
                 fg=Tema.aksen, bg=Tema.BG, font=(Tema.FONT, 9, "bold")).pack(anchor="w")
        tk.Label(kiri, text=produk.get_deskripsi(), fg=Tema.TEKS, bg=Tema.BG, justify="left",
                 wraplength=lebar_art, font=(Tema.FONT, 10)).pack(anchor="w", pady=(10, 6))
        seller = produk.get_seller()
        tk.Label(kiri, text=f"Publisher: {produk.nama_publisher()}"
                            + (f"  (★ {seller.get_rating()})" if seller else ""),
                 fg=Tema.REDUP, bg=Tema.BG, font=(Tema.FONT, 9)).pack(anchor="w")
        info = produk.info_tambahan()      # polymorphism, tanpa isinstance
        if info:
            tk.Label(kiri, text=info, fg=Tema.REDUP, bg=Tema.BG, wraplength=lebar_art,
                     justify="left", font=(Tema.FONT, 9)).pack(anchor="w")

        kanan = tk.Frame(self, bg=Tema.PANEL, width=300)
        kanan.grid(row=0, column=1, padx=(12, 24), pady=24, sticky="ns")
        kanan.grid_propagate(False)
        kanan.configure(height=tinggi_art + 150)
        tk.Label(kanan, text="Beli", fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 14, "bold")).pack(anchor="w", padx=20, pady=(20, 6))
        baris_harga(kanan, produk, customer, Tema.PANEL, 13).pack(anchor="w", padx=20)

        ok, alasan = produk.bisa_dibeli_oleh(customer)
        if not ok:
            tk.Label(kanan, text=alasan, fg=Tema.REDUP, bg=Tema.PANEL, wraplength=260,
                     justify="left", font=(Tema.FONT, 10)).pack(anchor="w", padx=20, pady=18)
            TombolFlat(kanan, "Tutup", self.destroy, bg=Tema.KARTU).pack(
                anchor="w", padx=20)
        else:
            tk.Label(kanan, text="Metode pembayaran", fg=Tema.REDUP, bg=Tema.PANEL,
                     font=(Tema.FONT, 9)).pack(anchor="w", padx=20, pady=(16, 4))
            self._metode = tk.StringVar(value=list(toko.METODE)[0])
            for nama in toko.METODE:
                tk.Radiobutton(kanan, text=nama, value=nama, variable=self._metode,
                               command=self._hitung, bg=Tema.PANEL, fg=Tema.TEKS,
                               activebackground=Tema.PANEL, activeforeground=Tema.TEKS,
                               selectcolor=Tema.KARTU, highlightthickness=0, bd=0,
                               font=(Tema.FONT, 10), cursor="hand2").pack(anchor="w", padx=18)
            self._rincian = tk.Label(kanan, text="", fg=Tema.TEKS, bg=Tema.PANEL, justify="left",
                                     font=("Consolas", 10))
            self._rincian.pack(anchor="w", padx=20, pady=14)
            TombolFlat(kanan, "Beli Sekarang", self._beli, padx=26, pady=10).pack(
                anchor="w", padx=20)
            self._hitung()

        self._pusatkan()
        self.wait_visibility()
        self.grab_set()

    def _pusatkan(self):
        self.update_idletasks()
        r = self._app.root
        x = r.winfo_x() + (r.winfo_width() - self.winfo_reqwidth()) // 2
        y = r.winfo_y() + (r.winfo_height() - self.winfo_reqheight()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    def _hitung(self):
        toko = self._app.toko
        kelas = toko.METODE[self._metode.get()]
        sub = self._produk.harga_akhir()
        admin = kelas.tarif_admin(sub)          # polymorphism
        self._rincian.configure(text=f"Harga   : {rupiah(sub)}\nAdmin   : {rupiah(admin)}\n"
                                     f"Total   : {rupiah(sub + admin)}")

    def _beli(self):
        app = self._app
        if app.pengaturan.get_konfirmasi() and not messagebox.askyesno(
                "Konfirmasi", f"Beli '{self._produk.get_nama_produk()}'?", parent=self):
            return
        ok, pesan, kirim = app.toko.beli(self._produk, self._metode.get())
        if not ok:
            messagebox.showwarning("Gagal", pesan, parent=self)
            return
        messagebox.showinfo("Berhasil", f"{pesan}\n\nKunci lisensi:\n{kirim.get_kunci()}\n\n"
                                        f"Game sudah ada di Library kamu.", parent=self)
        self.destroy()
        app.refresh_semua()


# ======================================================================
# APLIKASI UTAMA
# ======================================================================
class AplikasiBestDeal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BestDeal — Toko Game")
        self.root.configure(bg=Tema.BG)
        sh = self.root.winfo_screenheight()
        w, h = (1280, 720) if sh >= 800 else (1152, 648)
        x = (self.root.winfo_screenwidth() - w) // 2
        y = max(0, (sh - h) // 2 - 20)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(1024, 576)
        self._lebar = w
        self._after_resize = None

        customer = Customer("C001", "Arya", "password123", "arya@email.com",
                            "081234567890", "Surabaya", saldo=1_500_000)
        self.toko = TokoGame(customer)
        self.pengaturan = Pengaturan()
        self._gaya()

        self.navbar = None
        self.halaman = {}
        self._aktif = None
        self._bangun_ui("home")

        self.root.bind("<Configure>", self._saat_resize)
        self.root.bind_all("<MouseWheel>", self._wheel)
        self.root.bind_all("<Button-4>", self._wheel)
        self.root.bind_all("<Button-5>", self._wheel)
        self.root.bind("<Escape>", lambda e: self.atur_layar_penuh(False))

    # ---------- util ----------
    def _gaya(self):
        s = ttk.Style(self.root)
        s.theme_use("clam")
        s.configure("Game.Vertical.TScrollbar", background=Tema.GARIS, troughcolor=Tema.BG,
                    bordercolor=Tema.BG, arrowcolor=Tema.BG, lightcolor=Tema.GARIS,
                    darkcolor=Tema.GARIS, gripcount=0, arrowsize=1)
        s.map("Game.Vertical.TScrollbar", background=[("active", Tema.REDUP)])

    def lebar(self):
        return self._lebar

    def lebar_konten(self):
        return max(600, self._lebar - 16 - 64)

    def aktif(self):
        return self._aktif

    def _bangun_ui(self, awal):
        for w in self.root.winfo_children():
            w.destroy()
        self.navbar = NavBar(self.root, self)
        self.navbar.pack(fill="x")
        tk.Frame(self.root, bg=Tema.GARIS, height=1).pack(fill="x")
        wadah = tk.Frame(self.root, bg=Tema.BG)
        wadah.pack(fill="both", expand=True)
        self.halaman = {
            "home": HomePage(wadah, self),
            "library": LibraryPage(wadah, self),
            "akun": AkunPage(wadah, self),
            "setting": SettingPage(wadah, self),
        }
        self._aktif = None
        self.buka(awal)

    def bangun_ulang(self, awal="home"):
        self._bangun_ui(awal)

    # ---------- navigasi ----------
    def buka(self, nama):
        if self._aktif:
            self.halaman[self._aktif].pack_forget()
        self._aktif = nama
        h = self.halaman[nama]
        h.pack(fill="both", expand=True)
        h.saat_ditampilkan()
        self.navbar.set_aktif(nama)

    def buka_library(self, game):
        self.buka("library")
        self.halaman["library"].pilih(game)

    def buka_produk(self, produk):
        DialogProduk(self, produk)

    def cari(self, query):
        self.buka("home")
        self.halaman["home"].atur_pencarian(query)

    # ---------- refresh ----------
    def perbarui_navbar(self):
        self.navbar.perbarui()

    def halaman_tandai_kotor(self, nama):
        if nama != self._aktif:
            self.halaman[nama].tandai_kotor()

    def refresh_semua(self):
        self.navbar.perbarui()
        for nama, h in self.halaman.items():
            if nama == self._aktif:
                h.segarkan()
            else:
                h.tandai_kotor()

    # ---------- event ----------
    def atur_layar_penuh(self, aktif):
        self.pengaturan.set_layar_penuh(aktif)
        self.root.attributes("-fullscreen", aktif)

    def _saat_resize(self, e):
        if e.widget is not self.root or abs(e.width - self._lebar) < 40:
            return
        self._lebar = e.width
        if self._after_resize:
            self.root.after_cancel(self._after_resize)
        self._after_resize = self.root.after(250, self._resize_selesai)

    def _resize_selesai(self):
        self._after_resize = None
        for nama, h in self.halaman.items():
            if nama == self._aktif:
                h.segarkan()
            else:
                h.tandai_kotor()

    def _wheel(self, e):
        if getattr(e, "num", 0) == 4:
            arah = -1
        elif getattr(e, "num", 0) == 5:
            arah = 1
        else:
            arah = -1 if e.delta > 0 else 1
        try:
            w = self.root.winfo_containing(e.x_root, e.y_root)
        except (KeyError, tk.TclError):
            return
        while w is not None:
            if isinstance(w, ScrollFrame):
                w.gulir(arah)
                return
            w = w.master

    def jalankan(self):
        self.root.mainloop()


if __name__ == "__main__":
    AplikasiBestDeal().jalankan()
