"""Halaman Toko (setelah login)."""

import tkinter as tk

from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import KartuProduk, ScrollFrame, TombolFlat, baris_harga, lukis_art


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
                            f"{p.teks_ulasan()}",
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
            r = self._baris(kiri, g, f"{customer.get_jam_main(g):.1f} jam dimainkan")
            r.configure(cursor="hand2")
            self._klik(r, g, self._app.buka_library)
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

    def _klik(self, w, produk, aksi=None):
        aksi = aksi or self._app.buka_produk
        w.bind("<Button-1>", lambda e: aksi(produk), add="+")
        for c in w.winfo_children():
            self._klik(c, produk, aksi)
