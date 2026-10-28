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
    KOMENTAR_MIN = 10
    KOMENTAR_MAKS = 500

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

    # ---------- ulasan ----------
    def bisa_mengulas(self, produk):
        """Hanya game yang sudah dimiliki customer yang boleh diulas. Return (bool, pesan)."""
        if not produk.bisa_diulas():
            return False, "Hanya game yang bisa diulas."
        if not self.__customer.punya(produk):
            return False, "Beli game ini dulu untuk menulis ulasan."
        return True, ""

    def ulasan_saya(self, produk):
        return produk.ulasan_dari(self.__customer)

    def kirim_ulasan(self, produk, rekomendasi, komentar):
        """Validasi lalu simpan (atau perbarui) ulasan. Return (ok, pesan, ulasan)."""
        ok, pesan = self.bisa_mengulas(produk)
        if not ok:
            return False, pesan, None
        if rekomendasi is None:
            return False, "Pilih dulu: direkomendasikan atau tidak.", None
        komentar = komentar.strip()
        if len(komentar) < self.KOMENTAR_MIN:
            return False, f"Komentar minimal {self.KOMENTAR_MIN} karakter.", None
        if len(komentar) > self.KOMENTAR_MAKS:
            return False, f"Komentar maksimal {self.KOMENTAR_MAKS} karakter.", None
        ulasan, baru = produk.simpan_ulasan(self.__customer, rekomendasi, komentar)
        return True, ("Ulasan terkirim. Terima kasih!" if baru else "Ulasan diperbarui."), ulasan

    def hapus_ulasan(self, produk):
        if produk.bisa_diulas() and produk.hapus_ulasan(self.__customer):
            return True, "Ulasan dihapus."
        return False, "Kamu belum punya ulasan untuk game ini."
