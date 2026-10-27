"""Domain 4 : TokoGame (Facade - menyembunyikan alur beli dari GUI)."""

from datetime import date

from bestdeal.models.pembayaran import DAFTAR_METODE
from bestdeal.models.pengiriman import Pengiriman
from bestdeal.models.pesanan import Pesanan


class TokoGame:
    """Facade: menyembunyikan alur Pesanan -> Pembayaran -> Pengiriman dari GUI.

    Satu objek TokoGame mewakili satu sesi belanja seorang customer.
    Katalog dipakai bersama (shared) oleh semua sesi.
    """
    METODE = DAFTAR_METODE

    def __init__(self, customer, katalog, unggulan, laporan=None):
        self.__customer = customer
        self.__riwayat = []         
        self.__no = 0
        self.__katalog = katalog
        self.__unggulan = unggulan
        self.__laporan = laporan  
        
    def get_customer(self):
        return self.__customer

    def get_katalog(self):
        return list(self.__katalog)

    def get_unggulan(self):
        return list(self.__unggulan)

    def get_riwayat(self):
        return list(self.__riwayat)

    def daftar_kategori(self):
        urut = ["Semua", "Aksi", "RPG", "Strategi", "Balapan", "Horor", "Indie", "Tembak", "Petualangan",
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
        if self.__laporan is not None:      # untuk statistik seller
            self.__laporan.catat(produk, self.__customer.get_id_user())
        return True, "Pembelian berhasil!", pengiriman
