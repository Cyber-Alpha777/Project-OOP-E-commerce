"""Halaman Akun."""

import tkinter as tk
from tkinter import messagebox

from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import ScrollFrame, TombolFlat
from bestdeal.utils import rupiah


class AkunPage(Halaman):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)

    def _kartu(self, parent, judul):
        k = tk.Frame(parent, bg=Tema.PANEL)
        tk.Label(k, text=judul, fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 12, "bold")).pack(anchor="w", padx=20, pady=(16, 8))
        return k

    def bangun(self):
        self.scroll.kosongkan()
        isi = self.scroll.isi
        toko = self._app.toko
        c = toko.get_customer()
        self.judul(isi, "Akun Saya")

        grid = tk.Frame(isi, bg=Tema.BG)
        grid.pack(fill="x", padx=32)
        grid.columnconfigure(0, weight=1, uniform="k")
        grid.columnconfigure(1, weight=1, uniform="k")

        # --- profil ---
        kp = self._kartu(grid, "Profil")
        kp.grid(row=0, column=0, sticky="nsew", padx=(0, 9), pady=(0, 18))
        av = tk.Canvas(kp, width=84, height=84, bg=Tema.PANEL, highlightthickness=0)
        av.pack(anchor="w", padx=20)
        av.create_oval(2, 2, 82, 82, fill=Tema.aksen, outline="")
        av.create_text(42, 42, text=c.get_nama()[:1].upper(), fill="#fff",
                       font=(Tema.FONT, 30, "bold"))
        tk.Label(kp, text=f"{c.get_nama()}  ({c.peran()})", fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 15, "bold")).pack(anchor="w", padx=20, pady=(10, 6))
        tk.Label(kp, text=c.tampilkan_profil(), fg=Tema.REDUP, bg=Tema.PANEL, justify="left",
                 font=("Consolas", 10)).pack(anchor="w", padx=20)
        ubah = tk.Frame(kp, bg=Tema.PANEL)
        ubah.pack(anchor="w", padx=20, pady=(14, 18))
        e = tk.Entry(ubah, bg=Tema.KARTU, fg=Tema.TEKS, insertbackground=Tema.TEKS,
                     relief="flat", font=(Tema.FONT, 11), width=18)
        e.insert(0, c.get_nama())
        e.pack(side="left", ipady=6, padx=(0, 8))
        TombolFlat(ubah, "Ubah Nama", lambda: self._ubah_nama(e.get()), pady=6).pack(side="left")

        # --- saldo & statistik ---
        ks = self._kartu(grid, "Dompet & Statistik")
        ks.grid(row=0, column=1, sticky="nsew", padx=(9, 0), pady=(0, 18))
        tk.Label(ks, text=rupiah(c.get_saldo()), fg=Tema.HIJAU, bg=Tema.PANEL,
                 font=(Tema.FONT, 26, "bold")).pack(anchor="w", padx=20)
        tk.Label(ks, text="Saldo BestDeal", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 10)).pack(anchor="w", padx=20, pady=(0, 10))
        tp = tk.Frame(ks, bg=Tema.PANEL)
        tp.pack(anchor="w", padx=20, pady=(0, 14))
        for n in (100_000, 500_000, 1_000_000):
            TombolFlat(tp, f"+ {rupiah(n)}", lambda x=n: self._topup(x), pady=6,
                       font=(Tema.FONT, 9, "bold")).pack(side="left", padx=(0, 8))
        game = toko.library_game()
        total_jam = sum(c.get_jam_main(g) for g in game)
        tk.Label(ks, text=f"Game di library : {len(game)}\nTotal jam main  : {total_jam:.1f} jam\n"
                          f"Total pesanan   : {len(toko.get_riwayat())}",
                 fg=Tema.REDUP, bg=Tema.PANEL, justify="left",
                 font=("Consolas", 10)).pack(anchor="w", padx=20, pady=(0, 18))

        # --- riwayat ---
        self.judul(isi, "Riwayat Pesanan", pad=(6, 10))
        riwayat = toko.get_riwayat()
        if not riwayat:
            tk.Label(isi, text="Belum ada pesanan. Pembelian kamu akan muncul di sini.",
                     fg=Tema.REDUP, bg=Tema.BG, font=(Tema.FONT, 10)).pack(anchor="w", padx=32)
        for pesanan, bayar, kirim in reversed(riwayat):
            k = tk.Frame(isi, bg=Tema.PANEL)
            k.pack(fill="x", padx=32, pady=(0, 10))
            teks = (pesanan.get_pesanan() +
                    f"\nMetode     : {bayar.get_metode()} (admin {rupiah(bayar.biaya_admin())})"
                    f"\nDibayar    : {rupiah(bayar.get_jumlah_bayar())}  [{bayar.get_status()}]"
                    f"\nKunci      : {kirim.get_kunci()}  [{kirim.get_status()} ke "
                    f"{kirim.get_alamat_tujuan()}]"
                    f"\nPengiriman : {kirim.get_jasa()} • {kirim.get_estimasi()} • "
                    f"ongkir {rupiah(kirim.get_biaya())}")
            tk.Label(k, text=teks, fg=Tema.TEKS, bg=Tema.PANEL, justify="left",
                     font=("Consolas", 10), padx=18, pady=14).pack(anchor="w")
        tk.Frame(isi, bg=Tema.BG, height=30).pack()

    def _ubah_nama(self, nama):
        if not nama.strip():
            messagebox.showwarning("Nama kosong", "Nama tidak boleh kosong.")
            return
        self._app.toko.get_customer().set_nama(nama)
        self._app.refresh_semua()

    def _topup(self, jumlah):
        self._app.toko.get_customer().tambah_saldo(jumlah)
        self._app.refresh_semua()
