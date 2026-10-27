"""LayananSellerLengkap: LayananSeller + edit info game + riwayat penjualan & pemasukan.

Subclass dari LayananSeller (Inheritance), jadi upload_game / statistik lama tidak berubah.
"""

import os
from collections import namedtuple
from datetime import date, timedelta

from bestdeal.services.seller import LayananSeller

BarisPenjualan = namedtuple("BarisPenjualan", "tanggal game nominal dibeli id_customer")
RingkasanPeriode = namedtuple("RingkasanPeriode", "hari_ini minggu bulan semua")   # tiap isi (unit, uang)


class LayananSellerLengkap(LayananSeller):
    def __init__(self, seller, katalog, laporan):
        super().__init__(seller, katalog, laporan)
        self._katalog = katalog
        self._laporan = laporan

    # ---------- edit info game ----------
    def milik_saya(self, produk):
        id_seller = self.get_seller().get_id_user()
        pemilik = produk.get_seller()
        return pemilik is not None and pemilik.get_id_user() == id_seller

    def daftar_game_edit(self):
        return [p for p in self.daftar_produk() if p.bisa_diedit()]

    def edit_game(self, game, nama, kategori, harga, diskon, rilis, deskripsi, cover=""):
        """Validasi form lalu simpan perubahan ke game. Return (ok, pesan, game)."""
        if game not in self._katalog or not self.milik_saya(game):
            return False, "Game ini bukan milik tokomu.", None
        if not game.bisa_diedit():
            return False, "Jenis produk ini tidak bisa diedit.", None

        nama = nama.strip()
        if not nama:
            return False, "Judul game tidak boleh kosong.", None
        if len(nama) > self.JUDUL_MAKS:
            return False, f"Judul maksimal {self.JUDUL_MAKS} karakter.", None
        if any(p is not game and p.get_nama_produk().strip().lower() == nama.lower()
               for p in self._katalog):
            return False, f"Judul '{nama}' sudah dipakai produk lain.", None
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

        rilis = rilis.strip() or game.get_rilis()
        if len(rilis) > 30:
            return False, "Teks rilis maksimal 30 karakter.", None

        deskripsi = deskripsi.strip()
        if len(deskripsi) < self.DESKRIPSI_MIN:
            return False, f"Deskripsi minimal {self.DESKRIPSI_MIN} karakter.", None
        if len(deskripsi) > self.DESKRIPSI_MAKS:
            return False, f"Deskripsi maksimal {self.DESKRIPSI_MAKS} karakter.", None

        cover_lama = game.get_gambar() or ""
        if cover != cover_lama:             # cover tidak diganti = tidak perlu dicek ulang
            ok, pesan = self.cek_cover(cover)
            if not ok:
                return False, pesan, None
            cover = os.path.abspath(cover) if cover else ""

        game.set_nama_produk(nama)
        game.set_kategori(kategori)
        game.set_harga(harga_int)
        game.set_diskon(diskon_int)
        game.set_rilis(rilis)
        game.set_deskripsi(deskripsi)
        game.set_gambar(cover)
        return True, f"Perubahan '{nama}' berhasil disimpan.", game

    # ---------- riwayat penjualan & pemasukan ----------
    def riwayat_penjualan(self, hari=None, id_produk=None, akhir=None):
        """[BarisPenjualan] terbaru dulu. hari=None -> semua waktu; id_produk=None -> semua game."""
        akhir = akhir or date.today()
        sejak = None if hari is None else akhir - timedelta(days=hari - 1)
        id_seller = self.get_seller().get_id_user()
        baris = []
        for c in self._laporan.get_catatan():
            if sejak is not None and c.get_tanggal() < sejak:
                continue
            for game, nominal in c.rincian():
                pemilik = game.get_seller()
                if pemilik is None or pemilik.get_id_user() != id_seller:
                    continue
                if id_produk is not None and game.get_id_produk() != id_produk:
                    continue
                baris.append(BarisPenjualan(c.get_tanggal(), game, nominal, c.get_produk(),
                                            c.get_id_customer()))
        baris.reverse()
        baris.sort(key=lambda b: b.tanggal, reverse=True)       # sort stabil
        return baris

    @staticmethod
    def jumlahkan(baris):
        """(unit, total uang) dari daftar BarisPenjualan."""
        return len(baris), sum(b.nominal for b in baris)

    def ringkasan_periode(self):
        return RingkasanPeriode(
            self.jumlahkan(self.riwayat_penjualan(1)),
            self.jumlahkan(self.riwayat_penjualan(7)),
            self.jumlahkan(self.riwayat_penjualan(30)),
            self.jumlahkan(self.riwayat_penjualan()))
