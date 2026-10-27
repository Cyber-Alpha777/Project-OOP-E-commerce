"""Halaman Seller: riwayat penjualan lengkap + pemasukan per periode."""

import tkinter as tk
from tkinter import ttk

from bestdeal.ui.hias import Pil, kartu_statistik
from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import ScrollFrame
from bestdeal.utils import rupiah

SEMUA_GAME = "Semua game"


class SellerPenjualanPage(Halaman):
    MAKS_BARIS = 100
    PERIODE = (("7 Hari", 7), ("30 Hari", 30), ("Semua", None))
    CATATAN = ("Pemasukan = harga jual setelah diskon. Biaya admin metode pembayaran ditanggung "
               "pembeli, jadi tidak dipotong dari pemasukanmu. Paket dihitung per game isinya.")

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)
        self._hari = 30
        self._nama_game = SEMUA_GAME

    def saat_ditampilkan(self):
        Halaman.segarkan(self)      # penjualan baru bisa masuk kapan saja
        self.scroll.ke_atas()

    def segarkan(self):
        frac = self.scroll.posisi()
        super().segarkan()
        self.scroll.pulihkan(frac)

    def _ubah(self, hari=None, nama_game=None, ubah_hari=False):
        if ubah_hari:
            self._hari = hari
        if nama_game is not None:
            self._nama_game = nama_game
        frac = self.scroll.posisi()
        self.bangun()
        self.scroll.pulihkan(frac)

    # ---------- susunan halaman ----------
    def bangun(self):
        self.scroll.kosongkan()
        isi = self.scroll.isi
        layanan = self._app.seller
        self.judul(isi, f"Penjualan & Pemasukan \u2022 {layanan.get_seller().get_nama_toko()}")
        self._kartu_ringkasan(isi, layanan)
        self._filter(isi, layanan)
        self._tabel(isi, layanan)
        tk.Label(isi, text=self.CATATAN, fg=Tema.NONAKTIF, bg=Tema.BG, justify="left",
                 wraplength=self._app.lebar_konten(), font=(Tema.FONT, 8)).pack(
            anchor="w", padx=32, pady=(4, 28))

    def _kartu_ringkasan(self, isi, layanan):
        r = layanan.ringkasan_periode()
        item = (("Hari ini", r.hari_ini, "#16a34a"), ("7 hari terakhir", r.minggu, "#2563eb"),
                ("30 hari terakhir", r.bulan, "#7c3aed"), ("Total pemasukan", r.semua, Tema.aksen))
        grid = tk.Frame(isi, bg=Tema.BG)
        grid.pack(fill="x", padx=32, pady=(0, 18))
        for i, (label, (unit, uang), warna) in enumerate(item):
            grid.columnconfigure(i, weight=1, uniform="stat")
            kartu_statistik(grid, label, rupiah(uang), f"{unit} unit terjual", warna).grid(
                row=0, column=i, sticky="nsew",
                padx=(0 if i == 0 else 9, 0 if i == len(item) - 1 else 9))

    def _filter(self, isi, layanan):
        baris = tk.Frame(isi, bg=Tema.BG)
        baris.pack(fill="x", padx=32, pady=(0, 12))
        tk.Label(baris, text="Periode", fg=Tema.REDUP, bg=Tema.BG,
                 font=(Tema.FONT, 9, "bold")).pack(side="left", padx=(0, 10))
        for teks, hari in self.PERIODE:
            Pil(baris, teks, lambda h=hari: self._ubah(h, ubah_hari=True),
                terpilih=(hari == self._hari), bg=Tema.BG).pack(side="left", padx=(0, 6))

        gaya = ttk.Style(self)
        gaya.configure("Seller.TCombobox", arrowcolor=Tema.REDUP, bordercolor=Tema.GARIS,
                       lightcolor=Tema.KARTU, darkcolor=Tema.KARTU)
        gaya.map("Seller.TCombobox", fieldbackground=[("readonly", Tema.KARTU)],
                 background=[("readonly", Tema.KARTU), ("active", Tema.CHIP)],
                 foreground=[("readonly", Tema.TEKS)],
                 selectbackground=[("readonly", Tema.KARTU)],
                 selectforeground=[("readonly", Tema.TEKS)])
        nama = [SEMUA_GAME] + [p.get_nama_produk() for p in layanan.daftar_produk()]
        if self._nama_game not in nama:
            self._nama_game = SEMUA_GAME
        cb = ttk.Combobox(baris, values=nama, state="readonly", style="Seller.TCombobox",
                          width=30, font=(Tema.FONT, 10))
        cb.set(self._nama_game)
        cb.pack(side="right", ipady=3)
        cb.bind("<<ComboboxSelected>>", lambda e: self._ubah(nama_game=cb.get()))
        tk.Label(baris, text="Game", fg=Tema.REDUP, bg=Tema.BG,
                 font=(Tema.FONT, 9, "bold")).pack(side="right", padx=(0, 10))

    def _tabel(self, isi, layanan):
        id_produk = None
        for p in layanan.daftar_produk():
            if p.get_nama_produk() == self._nama_game:
                id_produk = p.get_id_produk()
        data = layanan.riwayat_penjualan(self._hari, id_produk)
        unit, uang = layanan.jumlahkan(data)

        ringkas = tk.Frame(isi, bg=Tema.PANEL)
        ringkas.pack(fill="x", padx=32, pady=(0, 10))
        tk.Label(ringkas, text=f"{unit} transaksi pada filter ini", fg=Tema.REDUP,
                 bg=Tema.PANEL, font=(Tema.FONT, 10)).pack(side="left", padx=18, pady=12)
        tk.Label(ringkas, text=rupiah(uang), fg=Tema.AKSEN_TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 14, "bold")).pack(side="right", padx=18, pady=12)

        kartu = tk.Frame(isi, bg=Tema.KARTU, highlightthickness=1, highlightbackground=Tema.GARIS)
        kartu.pack(fill="x", padx=32, pady=(0, 10))
        kartu.columnconfigure(1, weight=1)
        for j, (teks, rata) in enumerate((("Tanggal", "w"), ("Game", "w"), ("Pembeli", "w"),
                                          ("Pemasukan", "e"))):
            tk.Label(kartu, text=teks, fg=Tema.REDUP, bg=Tema.PANEL, anchor=rata, padx=14,
                     pady=9, font=(Tema.FONT, 9, "bold")).grid(row=0, column=j, sticky="nsew")
        kartu.columnconfigure(0, minsize=120)
        kartu.columnconfigure(2, minsize=120)
        kartu.columnconfigure(3, minsize=160)
        if not data:
            tk.Label(kartu, text="Belum ada penjualan untuk filter ini.", fg=Tema.REDUP,
                     bg=Tema.KARTU, font=(Tema.FONT, 10), pady=22).grid(
                row=1, column=0, columnspan=4)
            return
        for i, b in enumerate(data[:self.MAKS_BARIS]):
            r = i + 1
            bg = Tema.KARTU if i % 2 == 0 else Tema.PANEL2
            teks_game = b.game.get_nama_produk()
            if b.dibeli is not b.game:
                teks_game += f"  (lewat {b.dibeli.get_nama_produk()})"
            for j, (teks, rata, fg, font) in enumerate((
                    (b.tanggal.strftime("%d/%m/%Y"), "w", Tema.REDUP, (Tema.FONT, 10)),
                    (teks_game, "w", Tema.TEKS, (Tema.FONT, 10, "bold")),
                    (str(b.id_customer), "w", Tema.REDUP, (Tema.FONT, 10)),
                    ("+" + rupiah(b.nominal), "e", Tema.HIJAU, (Tema.FONT, 10, "bold")))):
                tk.Label(kartu, text=teks, fg=fg, bg=bg, anchor=rata, padx=14, pady=8,
                         font=font).grid(row=r, column=j, sticky="nsew")
        if len(data) > self.MAKS_BARIS:
            tk.Label(isi, text=f"Menampilkan {self.MAKS_BARIS} dari {len(data)} transaksi "
                               f"terbaru. Persempit periode / game untuk melihat sisanya.",
                     fg=Tema.REDUP, bg=Tema.BG, font=(Tema.FONT, 9)).pack(anchor="w", padx=32)
