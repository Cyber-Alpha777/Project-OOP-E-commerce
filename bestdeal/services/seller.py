"""LayananSeller (Facade): upload game dan statistik penjualan untuk satu seller."""

import os
import re
from collections import namedtuple
from datetime import date

from PIL import Image

from bestdeal.models.produk import Game

BarisStatistik = namedtuple("BarisStatistik", "produk terjual pendapatan")
Ringkasan = namedtuple("Ringkasan", "jumlah_judul terjual pendapatan rata_ulasan")


class LayananSeller:
    """Satu objek mewakili satu sesi seller yang sedang login.

    Katalog dan laporan penjualan dipakai bersama (shared) dengan sesi customer,
    jadi game yang diupload langsung muncul di toko dan pembelian customer langsung
    masuk ke statistik.
    """
    # sama dengan filter di TokoGame.daftar_kategori() tanpa "Semua", "DLC", "Paket"
    KATEGORI = ("Aksi", "RPG", "Strategi", "Balapan", "Horor", "Indie", "Tembak", "Petualangan")
    JUDUL_MAKS = 60
    DESKRIPSI_MIN = 20
    DESKRIPSI_MAKS = 1000
    HARGA_MAKS = 10_000_000
    COVER_MAKS_MB = 10
    EKSTENSI_COVER = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")

    def __init__(self, seller, katalog, laporan):
        self.__seller = seller
        self.__katalog = katalog        # list yang SAMA dengan milik TokoGame (bukan salinan)
        self.__laporan = laporan

    def get_seller(self):
        return self.__seller

    def kategori_game(self):
        return list(self.KATEGORI)

    # ---------- statistik ----------
    def daftar_produk(self):
        """Semua produk di katalog yang penjualnya seller ini."""
        id_seller = self.__seller.get_id_user()
        return [p for p in self.__katalog
                if p.get_seller() is not None and p.get_seller().get_id_user() == id_seller]

    def statistik(self):
        """[BarisStatistik] per produk, pendapatan terbesar dulu."""
        per_produk = self.__laporan.statistik_produk(self.__seller)
        baris = [BarisStatistik(p, *per_produk.get(p.get_id_produk(), (0, 0)))
                 for p in self.daftar_produk()]
        baris.sort(key=lambda b: (-b.pendapatan, b.produk.get_nama_produk().lower()))
        return baris

    def ringkasan(self):
        produk = self.daftar_produk()
        terjual, pendapatan = self.__laporan.total(self.__seller)
        skor = [s for s in (p.skor_ulasan() for p in produk) if s is not None]
        rata = round(sum(skor) / len(skor)) if skor else None
        return Ringkasan(len(produk), terjual, pendapatan, rata)

    def penjualan_harian(self, hari=14):
        return self.__laporan.harian(self.__seller, hari)

    def penjualan_terbaru(self, jumlah=8):
        return self.__laporan.terbaru(self.__seller, jumlah)

    # ---------- upload ----------
    @staticmethod
    def ke_angka(teks):
        """'Rp 150.000' -> 150000. Return None kalau bukan angka."""
        t = re.sub(r"(?i)rp|[.,\s]", "", str(teks))
        return int(t) if t.isascii() and t.isdigit() else None

    @classmethod
    def cek_cover(cls, path):
        """Validasi file cover. Return (ok, pesan). Path kosong dianggap valid (pakai placeholder)."""
        if not path:
            return True, ""
        if not os.path.isfile(path):
            return False, "File cover tidak ditemukan."
        if os.path.splitext(path)[1].lower() not in cls.EKSTENSI_COVER:
            return False, "Format cover harus PNG, JPG, WEBP, GIF, atau BMP."
        if os.path.getsize(path) > cls.COVER_MAKS_MB * 1024 * 1024:
            return False, f"Ukuran cover maksimal {cls.COVER_MAKS_MB} MB."
        try:
            with Image.open(path) as gambar:
                gambar.verify()
        except (OSError, SyntaxError, ValueError, Image.DecompressionBombError):
            return False, "File cover bukan gambar yang valid."
        return True, ""

    def _id_berikutnya(self):
        angka = [int(p.get_id_produk()[1:]) for p in self.__katalog
                 if p.get_id_produk().startswith("G") and p.get_id_produk()[1:].isdigit()]
        return f"G{max(angka, default=0) + 1:03d}"

    def upload_game(self, nama, kategori, harga, diskon, rilis, deskripsi, cover=""):
        """Validasi form lalu tambahkan Game ke katalog. Return (ok, pesan, game)."""
        nama = nama.strip()
        if not nama:
            return False, "Judul game tidak boleh kosong.", None
        if len(nama) > self.JUDUL_MAKS:
            return False, f"Judul maksimal {self.JUDUL_MAKS} karakter.", None
        if any(p.get_nama_produk().strip().lower() == nama.lower() for p in self.__katalog):
            return False, f"Judul '{nama}' sudah ada di katalog.", None
        if kategori not in self.KATEGORI:
            return False, "Pilih kategori game.", None

        harga_int = self.ke_angka(harga)
        if harga_int is None:
            return False, "Harga harus berupa angka (isi 0 untuk gratis).", None
        if harga_int > self.HARGA_MAKS:
            return False, f"Harga maksimal Rp{self.HARGA_MAKS:,}.".replace(",", "."), None

        diskon_int = 0 if not str(diskon).strip() else self.ke_angka(diskon)
        if diskon_int is None or not 0 <= diskon_int <= 100:
            return False, "Diskon harus angka 0 sampai 100.", None

        rilis = rilis.strip() or str(date.today().year)
        if len(rilis) > 30:
            return False, "Teks rilis maksimal 30 karakter.", None

        deskripsi = deskripsi.strip()
        if len(deskripsi) < self.DESKRIPSI_MIN:
            return False, f"Deskripsi minimal {self.DESKRIPSI_MIN} karakter.", None
        if len(deskripsi) > self.DESKRIPSI_MAKS:
            return False, f"Deskripsi maksimal {self.DESKRIPSI_MAKS} karakter.", None

        ok, pesan = self.cek_cover(cover)
        if not ok:
            return False, pesan, None

        game = Game(self._id_berikutnya(), nama, harga_int, kategori, self.__seller, deskripsi,
                    diskon=diskon_int, rilis=rilis, ulasan=0,
                    gambar=os.path.abspath(cover) if cover else None)
        self.__katalog.append(game)
        return True, f"'{nama}' berhasil dipublikasikan dan sudah tampil di toko.", game
