"""Halaman Library."""

import tkinter as tk

from bestdeal.models.produk import DLC
from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import InputCari, ScrollFrame, TombolFlat, lukis_art


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
        bg = Tema.KARTU if aktif else Tema.PANEL
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
        TombolFlat(baris, "▶  MAIN", lambda: self._main(g), bg=Tema.aksen,
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
