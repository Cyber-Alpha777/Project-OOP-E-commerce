"""Beranda (landing page) untuk pengunjung yang belum login."""

import tkinter as tk

from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import KartuProduk, ScrollFrame, TombolFlat, baris_harga, lukis_art


class LandingPage(Halaman):
    GAP = 20

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)

    def segarkan(self):
        frac = self.scroll.posisi()
        super().segarkan()
        self.scroll.pulihkan(frac)

    def bangun(self):
        self.scroll.kosongkan()
        isi = self.scroll.isi
        lebar = self._app.lebar_konten()
        self._hero(isi, lebar)
        self._deal(isi, lebar)
        self._keunggulan(isi)
        self._ajakan(isi)
        tk.Label(isi, text="BestDeal  \u2022  Toko game digital", fg=Tema.REDUP, bg=Tema.BG,
                 font=(Tema.FONT, 9)).pack(pady=(10, 28))

    # ---------- hero ----------
    def _hero(self, parent, lebar):
        app = self._app
        katalog = app.katalog
        publisher = {p.nama_publisher() for p in katalog}
        diskon_maks = max([p.diskon_persen() for p in katalog] or [0])

        wrap = tk.Frame(parent, bg=Tema.PANEL)
        wrap.pack(fill="x", padx=32, pady=(24, 8))

        kiri = tk.Frame(wrap, bg=Tema.PANEL)
        kiri.pack(side="left", fill="both", expand=True, padx=(44, 20), pady=36)
        tk.Label(kiri, text="  SELAMAT DATANG  ", bg=Tema.TEKS, fg="#ffffff", pady=3,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w")
        tk.Label(kiri, text="Game favoritmu,", fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 34, "bold")).pack(anchor="w", pady=(16, 0))
        tk.Label(kiri, text="harga terbaik.", fg=Tema.AKSEN_TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 34, "bold")).pack(anchor="w")
        tk.Label(kiri, text=f"Jelajahi game, DLC, dan paket hemat dengan diskon sampai "
                            f"{diskon_maks}%. Daftar gratis, bayar lewat saldo, QRIS, atau kartu, "
                            f"kunci lisensi langsung terkirim.",
                 fg="#5a4c41", bg=Tema.PANEL, justify="left", wraplength=400,
                 font=(Tema.FONT, 11)).pack(anchor="w", pady=(12, 20))
        tombol = tk.Frame(kiri, bg=Tema.PANEL)
        tombol.pack(anchor="w")
        TombolFlat(tombol, "Masuk", app.tampilkan_login, padx=28, pady=11).pack(
            side="left", padx=(0, 10))
        TombolFlat(tombol, "Daftar Gratis", app.tampilkan_daftar, bg=Tema.CHIP,
                   fg=Tema.TEKS, padx=24, pady=11).pack(side="left")
        st = tk.Frame(kiri, bg=Tema.PANEL)
        st.pack(anchor="w", pady=(26, 0))
        for angka, ket in ((str(len(katalog)), "produk"), (str(len(publisher)), "publisher"),
                           ("Instan", "kunci lisensi")):
            k = tk.Frame(st, bg=Tema.PANEL)
            k.pack(side="left", padx=(0, 28))
            tk.Label(k, text=angka, fg=Tema.TEKS, bg=Tema.PANEL,
                     font=(Tema.FONT, 16, "bold")).pack(anchor="w")
            tk.Label(k, text=ket, fg=Tema.REDUP, bg=Tema.PANEL,
                     font=(Tema.FONT, 9)).pack(anchor="w")

        if not app.unggulan:
            return
        produk = app.unggulan[0]
        kanan = tk.Frame(wrap, bg=Tema.PANEL)
        kanan.pack(side="right", padx=(0, 44), pady=28)
        w = max(360, min(500, int(lebar * 0.40)))
        h = int(w * 10 / 16)
        kartu = tk.Frame(kanan, bg=Tema.KARTU, padx=10, pady=10)
        kartu.pack()
        art = tk.Canvas(kartu, width=w, height=h, highlightthickness=0, bg=Tema.KARTU,
                        cursor="hand2")
        art.pack()
        lukis_art(art, w, h, produk, badge=False)
        art.bind("<Button-1>", lambda e: app.minta_login(produk))
        info = tk.Frame(kartu, bg=Tema.KARTU)
        info.pack(fill="x", pady=(10, 2))
        tk.Label(info, text=produk.get_nama_produk(), fg=Tema.TEKS, bg=Tema.KARTU,
                 font=(Tema.FONT, 13, "bold")).pack(anchor="w")
        baris_harga(info, produk, None, Tema.KARTU, 12).pack(anchor="w", pady=(4, 0))

    # ---------- deal terpanas ----------
    def _kolom(self, lebar):
        return max(2, (lebar + self.GAP) // (230 + self.GAP))

    def _deal(self, parent, lebar):
        kolom = self._kolom(lebar)
        panas = sorted([p for p in self._app.katalog if p.bisa_dimainkan() and p.diskon_persen() > 0],
                       key=lambda p: -p.diskon_persen())[:kolom * 2]
        self.judul(parent, "Deal terpanas", "Masuk untuk membeli \u2192", self._app.tampilkan_login,
                   pad=(28, 12))
        lebar_kartu = (lebar - self.GAP * (kolom - 1)) // kolom
        f = tk.Frame(parent, bg=Tema.BG)
        f.pack(fill="x", padx=32)
        for i, p in enumerate(panas):
            KartuProduk(f, p, None, lebar_kartu, self._app.minta_login).grid(
                row=i // kolom, column=i % kolom, sticky="nsew",
                padx=(0, self.GAP if i % kolom != kolom - 1 else 0), pady=(0, self.GAP))

    # ---------- keunggulan ----------
    def _keunggulan(self, parent):
        self.judul(parent, "Kenapa BestDeal?", pad=(12, 12))
        grid = tk.Frame(parent, bg=Tema.BG)
        grid.pack(fill="x", padx=32)
        data = (("%", "Harga hemat", "Diskon rutin untuk game, DLC, dan paket bundel."),
                ("\u2713", "Kunci instan", "Bayar lewat saldo, QRIS, atau kartu. Kunci lisensi "
                                         "langsung terkirim ke email."),
                ("\u2605", "Library pribadi", "Semua game yang kamu beli tersimpan rapi di "
                                              "Library akunmu."))
        for i, (simbol, judul, ket) in enumerate(data):
            grid.columnconfigure(i, weight=1, uniform="u")
            k = tk.Frame(grid, bg=Tema.PANEL)
            k.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 9, 0 if i == 2 else 9))
            ic = tk.Canvas(k, width=44, height=44, bg=Tema.PANEL, highlightthickness=0)
            ic.pack(anchor="w", padx=22, pady=(22, 10))
            ic.create_oval(2, 2, 42, 42, fill=Tema.aksen, outline="")
            ic.create_text(22, 22, text=simbol, fill=Tema.TEKS, font=(Tema.FONT, 14, "bold"))
            tk.Label(k, text=judul, fg=Tema.TEKS, bg=Tema.PANEL,
                     font=(Tema.FONT, 12, "bold")).pack(anchor="w", padx=22)
            tk.Label(k, text=ket, fg=Tema.REDUP, bg=Tema.PANEL, justify="left", wraplength=240,
                     font=(Tema.FONT, 10)).pack(anchor="w", padx=22, pady=(4, 22))

    # ---------- ajakan ----------
    def _ajakan(self, parent):
        b = tk.Frame(parent, bg=Tema.TEKS)
        b.pack(fill="x", padx=32, pady=(32, 8))
        tk.Label(b, text="Siap berburu deal?", fg="#ffffff", bg=Tema.TEKS,
                 font=(Tema.FONT, 18, "bold")).pack(side="left", padx=36, pady=28)
        kanan = tk.Frame(b, bg=Tema.TEKS)
        kanan.pack(side="right", padx=36)
        TombolFlat(kanan, "Masuk", self._app.tampilkan_login, bg=Tema.CHIP, fg=Tema.TEKS,
                   padx=24, pady=10).pack(side="left", padx=(0, 10))
        TombolFlat(kanan, "Daftar Gratis", self._app.tampilkan_daftar, padx=24, pady=10).pack(
            side="left")
