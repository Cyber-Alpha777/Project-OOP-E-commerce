"""Halaman Seller: edit informasi game yang sudah dipublikasikan."""

import tkinter as tk

from bestdeal.ui.pages.seller_upload_page import SellerUploadPage
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import TombolFlat


class SellerEditPage(SellerUploadPage):
    """Form yang sama dengan upload, tapi terisi data game dan menyimpan lewat edit_game()."""
    JUDUL = "Edit Game"
    SUBJUDUL = "Ubah judul, harga, diskon, deskripsi, atau cover. Perubahan langsung tampil di toko."
    TEKS_KIRIM = "Simpan Perubahan"
    TEKS_RESET = "Kembalikan data awal"
    HALAMAN_SETELAH = "kelola"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._game = None

    def atur_game(self, game):
        self._game = game

    def _cover_awal(self):
        return (self._game.get_gambar() or "") if self._game else ""

    def _isi_awal(self):
        g = self._game
        if g is None:
            return
        self._nama.insert(0, g.get_nama_produk())
        self._kategori.set(g.get_kategori())
        self._rilis.delete(0, "end")
        self._rilis.insert(0, g.get_rilis())
        self._harga.insert(0, str(g.get_harga()))
        self._diskon.delete(0, "end")
        self._diskon.insert(0, str(g.diskon_persen()))
        self._deskripsi.insert("1.0", g.get_deskripsi())
        self._tampil_cover()

    def _tombol_ekstra(self, tombol):
        TombolFlat(tombol, "Batal", lambda: self._app.buka("kelola"), bg=Tema.CHIP,
                   fg=Tema.TEKS, padx=18, pady=11).pack(side="left")

    def _simpan(self):
        if self._game is None:
            return False, "Pilih game dari menu Kelola Game dulu.", None
        return self._app.seller.edit_game(
            self._game, self._nama.get(), self._kategori.get(), self._harga.get(),
            self._diskon.get(), self._rilis.get(), self._deskripsi.get("1.0", "end"),
            self._cover)
