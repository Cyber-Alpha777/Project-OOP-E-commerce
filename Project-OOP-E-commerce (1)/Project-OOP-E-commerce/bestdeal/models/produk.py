"""Domain 2 : Produk  (Abstraction + Inheritance + Polymorphism)."""

from abc import ABC, abstractmethod

from bestdeal.utils import rupiah


class Produk(ABC):
    """Produk abstrak: Game, DLC, Bundle punya aturan harga & beli sendiri-sendiri."""

    def __init__(self, id_produk, nama_produk, harga, stok, kategori, seller=None,
                 deskripsi="", gambar=None):
        self.__id_produk = id_produk
        self.__nama_produk = nama_produk
        self.__harga = harga
        self.__stok = stok
        self.__kategori = kategori
        self.__seller = seller
        self.__deskripsi = deskripsi
        self.__gambar = gambar

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

    def get_gambar(self):
        return self.__gambar

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

    def set_gambar(self, gambar):
        path = str(gambar).strip() if gambar else ""
        self.__gambar = path or None

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
    def __init__(self, id_produk, nama, harga, kategori, seller, deskripsi, 
                 diskon=0, rilis="2025", ulasan=85, gambar=None):
        super().__init__(id_produk, nama, harga, 9999, kategori, seller, deskripsi, gambar)
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
    def __init__(self, id_produk, nama, harga, game_induk, deskripsi, gambar=None):
        super().__init__(id_produk, nama, harga, 9999, "DLC", game_induk.get_seller(),
                         deskripsi, gambar)
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
    def __init__(self, id_produk, nama, daftar_game, seller, deskripsi, potongan=0.15,
                 gambar=None):
        total_normal = sum(g.get_harga() for g in daftar_game)
        super().__init__(id_produk, nama, total_normal, 9999, "Paket", seller, deskripsi,
                         gambar)
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
