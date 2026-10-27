"""Halaman Seller: dashboard statistik penjualan game."""

import tkinter as tk

from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import ScrollFrame, TombolFlat, lukis_art
from bestdeal.utils import rupiah, rupiah_singkat


def langkah_rapi(nilai):
    """Pembulatan 'enak dibaca' untuk skala sumbu grafik (mis. 585000 -> 600000)."""
    if nilai <= 0:
        return 250_000
    pangkat = 10 ** (len(str(int(nilai))) - 1)
    for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if nilai <= m * pangkat:
            return int(m * pangkat)
    return int(10 * pangkat)


class SellerDashboardPage(Halaman):
    HARI_GRAFIK = 14
    CATATAN = ("Statistik dihitung dari pembelian di aplikasi ini ditambah data penjualan "
               "simulasi awal. Semua data tersimpan di memori dan hilang saat aplikasi ditutup.")

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)

    def saat_ditampilkan(self):
        Halaman.segarkan(self)      # data penjualan bisa berubah, selalu hitung ulang
        self.scroll.ke_atas()

    def segarkan(self):             # saat resize: bangun ulang tapi pertahankan posisi scroll
        frac = self.scroll.posisi()
        super().segarkan()
        self.scroll.pulihkan(frac)

    def bangun(self):
        self.scroll.kosongkan()
        isi = self.scroll.isi
        layanan = self._app.seller
        seller = layanan.get_seller()
        self.judul(isi, f"Dashboard \u2022 {seller.get_nama_toko()}", "+ Upload Game",
                   lambda: self._app.buka("upload"))
        if not layanan.daftar_produk():
            self._kosong(isi)
            return
        self._kartu_ringkasan(isi, layanan.ringkasan(), seller)
        self._grafik(isi, layanan, self._app.lebar_konten())
        self._tabel(isi, layanan)
        self._terbaru(isi, layanan)
        tk.Label(isi, text=self.CATATAN, fg=Tema.NONAKTIF, bg=Tema.BG, justify="left",
                 wraplength=self._app.lebar_konten(), font=(Tema.FONT, 8)).pack(
            anchor="w", padx=32, pady=(4, 28))

    # ---------- kondisi kosong ----------
    def _kosong(self, isi):
        k = tk.Frame(isi, bg=Tema.PANEL)
        k.pack(fill="x", padx=32, pady=(0, 24))
        tk.Label(k, text="Belum ada game di tokomu", fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 15, "bold")).pack(anchor="w", padx=28, pady=(26, 4))
        tk.Label(k, text="Upload game pertamamu. Setelah dipublikasikan, game langsung tampil "
                         "di toko dan statistik penjualannya muncul di sini.",
                 fg=Tema.REDUP, bg=Tema.PANEL, justify="left", wraplength=560,
                 font=(Tema.FONT, 10)).pack(anchor="w", padx=28)
        TombolFlat(k, "Upload Game Pertama", lambda: self._app.buka("upload"),
                   padx=24, pady=10).pack(anchor="w", padx=28, pady=(16, 26))

    # ---------- kartu ringkasan ----------
    def _kartu_ringkasan(self, isi, r, seller):
        ulasan = f"{r.rata_ulasan}%" if r.rata_ulasan is not None else "\u2014"
        item = (
            ("Judul dipublikasi", str(r.jumlah_judul), "game & DLC milikmu"),
            ("Unit terjual", f"{r.terjual:,}".replace(",", "."), "total semua penjualan"),
            ("Pendapatan", rupiah(r.pendapatan), "harga jual setelah diskon"),
            ("Ulasan rata-rata", ulasan, f"rating toko \u2605 {seller.get_rating()}"),
        )
        grid = tk.Frame(isi, bg=Tema.BG)
        grid.pack(fill="x", padx=32, pady=(0, 18))
        for i, (label, nilai, sub) in enumerate(item):
            grid.columnconfigure(i, weight=1, uniform="stat")
            k = tk.Frame(grid, bg=Tema.PANEL)
            k.grid(row=0, column=i, sticky="nsew",
                   padx=(0 if i == 0 else 9, 0 if i == len(item) - 1 else 9))
            tk.Label(k, text=label, fg=Tema.REDUP, bg=Tema.PANEL,
                     font=(Tema.FONT, 10)).pack(anchor="w", padx=18, pady=(14, 0))
            tk.Label(k, text=nilai, fg=Tema.TEKS, bg=Tema.PANEL,
                     font=(Tema.FONT, 20, "bold")).pack(anchor="w", padx=18)
            tk.Label(k, text=sub, fg=Tema.REDUP, bg=Tema.PANEL,
                     font=(Tema.FONT, 9)).pack(anchor="w", padx=18, pady=(0, 14))

    # ---------- grafik batang pendapatan harian ----------
    def _grafik(self, isi, layanan, lebar):
        data = layanan.penjualan_harian(self.HARI_GRAFIK)
        ringkas = (f"{sum(u for _, u, _ in data)} unit \u2022 "
                   f"{rupiah(sum(r for _, _, r in data))}")
        kartu = tk.Frame(isi, bg=Tema.PANEL)
        kartu.pack(fill="x", padx=32, pady=(0, 18))
        kepala = tk.Frame(kartu, bg=Tema.PANEL)
        kepala.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(kepala, text=f"Pendapatan {self.HARI_GRAFIK} hari terakhir", fg=Tema.TEKS,
                 bg=Tema.PANEL, font=(Tema.FONT, 12, "bold")).pack(side="left")
        info = tk.Label(kepala, text=ringkas, fg=Tema.REDUP, bg=Tema.PANEL,
                        font=(Tema.FONT, 10))
        info.pack(side="right")
        w, h = lebar - 40, 230
        c = tk.Canvas(kartu, width=w, height=h, bg=Tema.PANEL, highlightthickness=0)
        c.pack(padx=20, pady=(8, 16))
        self._lukis_grafik(c, w, h, data, info, ringkas)

    def _lukis_grafik(self, c, w, h, data, info, ringkas):
        kiri, kanan, atas, bawah = 64, 8, 14, 28
        area_w, area_h = w - kiri - kanan, h - atas - bawah
        maks = max(r for _, _, r in data)
        langkah = langkah_rapi(maks / 4)
        puncak = langkah * 4
        for i in range(5):
            y = atas + area_h - area_h * i / 4
            c.create_line(kiri, y, w - kanan, y, fill=Tema.GARIS)
            c.create_text(kiri - 8, y, text="0" if i == 0 else rupiah_singkat(langkah * i),
                          anchor="e", fill=Tema.REDUP, font=(Tema.FONT, 8))
        slot = area_w / len(data)
        lebar_batang = slot * 0.55
        for i, (tgl, _, rp) in enumerate(data):
            x0 = kiri + slot * i + (slot - lebar_batang) / 2
            tinggi = area_h * rp / puncak
            if tinggi > 0:
                c.create_rectangle(x0, atas + area_h - tinggi, x0 + lebar_batang, atas + area_h,
                                   fill=Tema.aksen, outline="")
            c.create_text(x0 + lebar_batang / 2, h - bawah / 2 + 2, text=tgl.strftime("%d/%m"),
                          fill=Tema.REDUP, font=(Tema.FONT, 8))
        if maks == 0:
            c.create_text(kiri + area_w / 2, atas + area_h / 2,
                          text="Belum ada penjualan pada periode ini.", fill=Tema.REDUP,
                          font=(Tema.FONT, 11))

        def sorot(e):       # arahkan mouse ke grafik -> info hari itu tampil di kanan atas
            i = int((e.x - kiri) // slot)
            if kiri <= e.x <= w - kanan and 0 <= i < len(data):
                tgl, unit, rp = data[i]
                info.configure(text=f"{tgl.strftime('%d/%m/%Y')} \u2022 {unit} unit \u2022 {rupiah(rp)}")

        c.bind("<Motion>", sorot)
        c.bind("<Leave>", lambda e: info.configure(text=ringkas))

    # ---------- tabel performa per judul ----------
    def _tabel(self, isi, layanan):
        self.judul(isi, "Performa Game", pad=(6, 10))
        baris = layanan.statistik()
        maks_terjual = max([b.terjual for b in baris] or [0])
        kartu = tk.Frame(isi, bg=Tema.KARTU, highlightthickness=1, highlightbackground=Tema.GARIS)
        kartu.pack(fill="x", padx=32, pady=(0, 18))
        kartu.columnconfigure(1, weight=1)
        for j, minimal in ((2, 190), (3, 130), (4, 150), (5, 80)):
            kartu.columnconfigure(j, minsize=minimal)

        for j, teks in enumerate(("", "Judul", "Harga", "Terjual", "Pendapatan", "Ulasan")):
            tk.Label(kartu, text=teks, fg=Tema.REDUP, bg=Tema.PANEL, anchor="w", padx=12, pady=8,
                     font=(Tema.FONT, 9, "bold")).grid(row=0, column=j, sticky="nsew")

        for i, b in enumerate(baris):
            p = b.produk
            r = 2 * i + 1
            if i:
                tk.Frame(kartu, bg=Tema.GARIS, height=1).grid(row=r - 1, column=0, columnspan=6,
                                                               sticky="ew")
            art = tk.Canvas(kartu, width=64, height=36, highlightthickness=0, bg=Tema.KARTU)
            lukis_art(art, 64, 36, p, badge=False)
            art.grid(row=r, column=0, padx=(12, 4), pady=8)

            nama = tk.Frame(kartu, bg=Tema.KARTU)
            nama.grid(row=r, column=1, sticky="w", padx=12)
            tk.Label(nama, text=p.get_nama_produk(), fg=Tema.TEKS, bg=Tema.KARTU,
                     font=(Tema.FONT, 10, "bold")).pack(anchor="w")
            tk.Label(nama, text=f"{p.label_tipe()} \u2022 {p.get_kategori()}", fg=Tema.REDUP,
                     bg=Tema.KARTU, font=(Tema.FONT, 8)).pack(anchor="w")

            harga = tk.Frame(kartu, bg=Tema.KARTU)
            harga.grid(row=r, column=2, sticky="w", padx=12)
            tk.Label(harga, text="Gratis" if p.harga_akhir() == 0 else rupiah(p.harga_akhir()),
                     fg=Tema.TEKS, bg=Tema.KARTU, font=(Tema.FONT, 10, "bold")).pack(anchor="w")
            if p.diskon_persen() > 0:
                tk.Label(harga, text=f"-{p.diskon_persen()}% dari {rupiah(p.get_harga())}",
                         fg=Tema.REDUP, bg=Tema.KARTU, font=(Tema.FONT, 8)).pack(anchor="w")

            terjual = tk.Frame(kartu, bg=Tema.KARTU)
            terjual.grid(row=r, column=3, sticky="w", padx=12)
            tk.Label(terjual, text=f"{b.terjual:,}".replace(",", "."), fg=Tema.TEKS,
                     bg=Tema.KARTU, font=(Tema.FONT, 11, "bold")).pack(anchor="w")
            if b.terjual:
                tk.Frame(terjual, bg=Tema.aksen, height=4,
                         width=max(3, int(90 * b.terjual / maks_terjual))).pack(anchor="w")

            tk.Label(kartu, text=rupiah(b.pendapatan), fg=Tema.TEKS, bg=Tema.KARTU,
                     font=(Tema.FONT, 10, "bold")).grid(row=r, column=4, sticky="w", padx=12)
            skor = p.skor_ulasan()
            tk.Label(kartu, text=f"{skor}%" if skor is not None else "\u2014", fg=Tema.REDUP,
                     bg=Tema.KARTU, font=(Tema.FONT, 10)).grid(row=r, column=5, sticky="w",
                                                              padx=12)

    # ---------- penjualan terbaru ----------
    def _terbaru(self, isi, layanan):
        self.judul(isi, "Penjualan Terbaru", pad=(6, 10))
        kartu = tk.Frame(isi, bg=Tema.KARTU, highlightthickness=1, highlightbackground=Tema.GARIS)
        kartu.pack(fill="x", padx=32, pady=(0, 18))
        baris = layanan.penjualan_terbaru(8)
        if not baris:
            tk.Label(kartu, text="Belum ada penjualan.", fg=Tema.REDUP, bg=Tema.KARTU,
                     font=(Tema.FONT, 10), pady=14).pack(anchor="w", padx=14)
        for tgl, game, nominal, dibeli in baris:
            f = tk.Frame(kartu, bg=Tema.KARTU)
            f.pack(fill="x")
            tk.Label(f, text=tgl.strftime("%d/%m/%Y"), fg=Tema.REDUP, bg=Tema.KARTU, width=11,
                     anchor="w", font=(Tema.FONT, 10)).pack(side="left", padx=(14, 0), pady=7)
            teks = game.get_nama_produk()
            if dibeli is not game:
                teks += f"  (lewat {dibeli.get_nama_produk()})"
            tk.Label(f, text=teks, fg=Tema.TEKS, bg=Tema.KARTU, anchor="w",
                     font=(Tema.FONT, 10)).pack(side="left", padx=8)
            tk.Label(f, text="+" + rupiah(nominal), fg=Tema.HIJAU, bg=Tema.KARTU,
                     font=(Tema.FONT, 10, "bold")).pack(side="right", padx=14)
