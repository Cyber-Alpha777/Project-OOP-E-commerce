"""Halaman Dompet: saldo, top up dengan pilihan metode pembayaran, dan riwayat mutasi."""

import tkinter as tk
from tkinter import messagebox

from bestdeal.services.dompet import DompetService
from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import ScrollFrame, TombolFlat
from bestdeal.utils import rupiah

MAKS_RIWAYAT = 30


class DompetPage(Halaman):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)
        # disimpan di sini (bukan di bangun) supaya isian tidak hilang saat halaman digambar ulang
        self._nominal = tk.StringVar(value="100.000")
        self._metode = tk.StringVar(value=list(DompetService.daftar_metode())[0])
        self._lb_rincian = None
        self._lb_catatan = None

    def _kartu(self, parent, judul):
        k = tk.Frame(parent, bg=Tema.PANEL)
        tk.Label(k, text=judul, fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 12, "bold")).pack(anchor="w", padx=20, pady=(16, 8))
        return k

    def bangun(self):
        self.scroll.kosongkan()
        isi = self.scroll.isi
        customer = self._app.toko.get_customer()
        dompet = DompetService(customer)
        self.judul(isi, "Dompet")

        grid = tk.Frame(isi, bg=Tema.BG)
        grid.pack(fill="x", padx=32)
        grid.columnconfigure(0, weight=2, uniform="d")
        grid.columnconfigure(1, weight=3, uniform="d")

        self._bangun_saldo(grid, customer, dompet)
        self._bangun_topup(grid, dompet)

        self.judul(isi, "Riwayat Dompet", pad=(6, 10))
        self._bangun_riwayat(isi, customer)
        tk.Frame(isi, bg=Tema.BG, height=30).pack()
        self._hitung()

    # ---------- kartu saldo ----------
    def _bangun_saldo(self, grid, customer, dompet):
        ks = self._kartu(grid, "Saldo BestDeal")
        ks.grid(row=0, column=0, sticky="nsew", padx=(0, 9), pady=(0, 18))
        tk.Label(ks, text=rupiah(customer.get_saldo()), fg=Tema.HIJAU, bg=Tema.PANEL,
                 font=(Tema.FONT, 26, "bold")).pack(anchor="w", padx=20)
        tk.Label(ks, text="Saldo yang bisa dipakai untuk membeli game", fg=Tema.REDUP,
                 bg=Tema.PANEL, font=(Tema.FONT, 10)).pack(anchor="w", padx=20, pady=(0, 14))
        masuk, keluar, jumlah = dompet.ringkasan()
        tk.Label(ks, text=f"Total top up    : {rupiah(masuk)}\n"
                          f"Total belanja   : {rupiah(keluar)}\n"
                          f"Jumlah mutasi   : {jumlah}",
                 fg=Tema.REDUP, bg=Tema.PANEL, justify="left",
                 font=("Consolas", 10)).pack(anchor="w", padx=20, pady=(0, 18))

    # ---------- kartu top up ----------
    def _bangun_topup(self, grid, dompet):
        kt = self._kartu(grid, "Top Up Saldo")
        kt.grid(row=0, column=1, sticky="nsew", padx=(9, 0), pady=(0, 18))

        tk.Label(kt, text="Nominal", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9)).pack(anchor="w", padx=20)
        baris = tk.Frame(kt, bg=Tema.PANEL)
        baris.pack(anchor="w", padx=20, pady=(4, 6))
        tk.Label(baris, text="Rp", fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 12, "bold")).pack(side="left", padx=(0, 6))
        e = tk.Entry(baris, textvariable=self._nominal, bg=Tema.KARTU, fg=Tema.TEKS,
                     insertbackground=Tema.TEKS, relief="flat", width=16, font=(Tema.FONT, 12))
        e.pack(side="left", ipady=6)
        e.bind("<KeyRelease>", lambda ev: self._hitung())

        chip = tk.Frame(kt, bg=Tema.PANEL)
        chip.pack(anchor="w", padx=20, pady=(0, 10))
        for n in DompetService.NOMINAL_CEPAT:
            TombolFlat(chip, rupiah(n).replace("Rp", ""), lambda x=n: self._set_nominal(x),
                       bg=Tema.CHIP, fg=Tema.TEKS, padx=10, pady=5,
                       font=(Tema.FONT, 9, "bold")).pack(side="left", padx=(0, 6))

        tk.Label(kt, text="Metode pembayaran", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9)).pack(anchor="w", padx=20, pady=(4, 2))
        grid_m = tk.Frame(kt, bg=Tema.PANEL)
        grid_m.pack(anchor="w", padx=16)
        for i, (nama, kelas) in enumerate(dompet.daftar_metode().items()):
            tk.Radiobutton(grid_m, text=f"{nama}  \u2022  admin {kelas.label_tarif()}",
                           value=nama, variable=self._metode, command=self._hitung,
                           bg=Tema.PANEL, fg=Tema.TEKS, activebackground=Tema.PANEL,
                           activeforeground=Tema.TEKS, selectcolor=Tema.KARTU,
                           highlightthickness=0, bd=0, font=(Tema.FONT, 10), cursor="hand2",
                           anchor="w", width=26).grid(row=i // 2, column=i % 2, sticky="w")

        self._lb_catatan = tk.Label(kt, text="", fg=Tema.REDUP, bg=Tema.PANEL, justify="left",
                                    wraplength=420, font=(Tema.FONT, 9))
        self._lb_catatan.pack(anchor="w", padx=20, pady=(8, 0))
        self._lb_rincian = tk.Label(kt, text="", fg=Tema.TEKS, bg=Tema.PANEL, justify="left",
                                    font=("Consolas", 10))
        self._lb_rincian.pack(anchor="w", padx=20, pady=(8, 10))
        TombolFlat(kt, "Top Up Sekarang", self._topup, padx=26, pady=10).pack(
            anchor="w", padx=20, pady=(0, 18))

    # ---------- riwayat ----------
    def _bangun_riwayat(self, isi, customer):
        mutasi = customer.get_mutasi()
        if not mutasi:
            tk.Label(isi, text="Belum ada mutasi. Top up atau pembelianmu akan muncul di sini.",
                     fg=Tema.REDUP, bg=Tema.BG, font=(Tema.FONT, 10)).pack(anchor="w", padx=32)
            return
        for m in reversed(mutasi[-MAKS_RIWAYAT:]):
            k = tk.Frame(isi, bg=Tema.PANEL)
            k.pack(fill="x", padx=32, pady=(0, 8))
            kiri = tk.Frame(k, bg=Tema.PANEL)
            kiri.pack(side="left", padx=18, pady=12)
            tk.Label(kiri, text=m.get_keterangan(), fg=Tema.TEKS, bg=Tema.PANEL,
                     font=(Tema.FONT, 10, "bold")).pack(anchor="w")
            tk.Label(kiri, text=f"{m.get_jenis()}  \u2022  {m.get_waktu()}", fg=Tema.REDUP,
                     bg=Tema.PANEL, font=(Tema.FONT, 9)).pack(anchor="w")
            kanan = tk.Frame(k, bg=Tema.PANEL)
            kanan.pack(side="right", padx=18, pady=12)
            warna = Tema.HIJAU if m.masuk() else Tema.MERAH
            tanda = "+" if m.masuk() else "-"
            tk.Label(kanan, text=f"{tanda}{rupiah(abs(m.get_jumlah()))}", fg=warna,
                     bg=Tema.PANEL, font=(Tema.FONT, 11, "bold")).pack(anchor="e")
            tk.Label(kanan, text=f"Saldo {rupiah(m.get_saldo_akhir())}", fg=Tema.REDUP,
                     bg=Tema.PANEL, font=(Tema.FONT, 9)).pack(anchor="e")
        if len(mutasi) > MAKS_RIWAYAT:
            tk.Label(isi, text=f"Menampilkan {MAKS_RIWAYAT} mutasi terakhir.", fg=Tema.REDUP,
                     bg=Tema.BG, font=(Tema.FONT, 9)).pack(anchor="w", padx=32)

    # ---------- aksi ----------
    def _set_nominal(self, n):
        self._nominal.set(f"{n:,}".replace(",", "."))
        self._hitung()

    def _hitung(self):
        """Perbarui rincian biaya sesuai nominal dan metode yang dipilih."""
        if self._lb_rincian is None or self._lb_catatan is None:
            return
        dompet = DompetService(self._app.toko.get_customer())
        nama = self._metode.get()
        nominal = DompetService.baca_nominal(self._nominal.get())
        self._lb_catatan.configure(text=dompet.daftar_metode()[nama].catatan())
        ok, pesan = dompet.validasi(nominal)
        if not ok:
            self._lb_rincian.configure(text=pesan, fg=Tema.MERAH, font=(Tema.FONT, 10))
            return
        admin, total = dompet.rincian(nominal, nama)
        self._lb_rincian.configure(
            text=(f"Saldo masuk : {rupiah(nominal)}\nAdmin       : {rupiah(admin)}\n"
                  f"Total bayar : {rupiah(total)}"),
            fg=Tema.TEKS, font=("Consolas", 10))

    def _topup(self):
        root = self._app.root
        dompet = DompetService(self._app.toko.get_customer())
        nama = self._metode.get()
        nominal = DompetService.baca_nominal(self._nominal.get())
        ok, pesan = dompet.validasi(nominal)
        if not ok:
            messagebox.showwarning("Nominal tidak valid", pesan, parent=root)
            return
        if self._app.pengaturan.get_konfirmasi():
            _, total = dompet.rincian(nominal, nama)
            if not messagebox.askyesno(
                    "Konfirmasi", f"Top up {rupiah(nominal)} via {nama}?\n"
                                  f"Total bayar {rupiah(total)}.", parent=root):
                return
        ok, pesan = dompet.topup(nominal, nama)
        if not ok:
            messagebox.showwarning("Gagal", pesan, parent=root)
            return
        messagebox.showinfo("Top up berhasil", pesan, parent=root)
        self._app.refresh_semua()