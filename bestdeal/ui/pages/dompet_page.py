"""Halaman Dompet: kartu saldo, top up (nominal cepat + pilihan metode), dan riwayat mutasi."""

import tkinter as tk
from tkinter import messagebox

from bestdeal.services.dompet import DompetService
from bestdeal.ui.dialog_bayar import DialogBayar, perlu_halaman_bayar
from bestdeal.ui.hias import Pil, UbinMetode, pemisah
from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import ScrollFrame, TombolFlat
from bestdeal.utils import campur, rupiah

MAKS_RIWAYAT = 30


class DompetPage(Halaman):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)
        # disimpan di sini (bukan di bangun) supaya isian tidak hilang saat halaman digambar ulang
        self._nominal = tk.StringVar(value="100.000")
        self._metode = tk.StringVar(value=list(DompetService.daftar_metode())[0])
        self._ubin = {}
        self._pil = {}
        self._v_saldo = self._v_admin = self._v_total = None
        self._lb_catatan = self._lb_galat = None

    def _kartu(self, parent, judul, sub=None):
        k = tk.Frame(parent, bg=Tema.PANEL)
        tk.Label(k, text=judul, fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 13, "bold")).pack(anchor="w", padx=22, pady=(18, 0 if sub else 10))
        if sub:
            tk.Label(k, text=sub, fg=Tema.REDUP, bg=Tema.PANEL,
                     font=(Tema.FONT, 9)).pack(anchor="w", padx=22, pady=(2, 12))
        return k

    def bangun(self):
        self.scroll.kosongkan()
        self._ubin, self._pil = {}, {}
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

    # ---------- kartu saldo (hero) ----------
    def _bangun_saldo(self, grid, customer, dompet):
        warna = Tema.aksen
        redup = campur(warna, "#ffffff", 0.78)
        ks = tk.Frame(grid, bg=warna)
        ks.grid(row=0, column=0, sticky="nsew", padx=(0, 9), pady=(0, 18))
        tk.Label(ks, text="SALDO BESTDEAL", fg=redup, bg=warna,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w", padx=24, pady=(22, 0))
        tk.Label(ks, text=rupiah(customer.get_saldo()), fg="#ffffff", bg=warna,
                 font=(Tema.FONT, 28, "bold")).pack(anchor="w", padx=24, pady=(2, 0))
        tk.Label(ks, text=f"Atas nama {customer.get_nama()}", fg=redup, bg=warna,
                 font=(Tema.FONT, 10)).pack(anchor="w", padx=24, pady=(0, 18))
        masuk, keluar, jumlah = dompet.ringkasan()
        bawah = tk.Frame(ks, bg=campur(warna, "#000000", 0.12))
        bawah.pack(fill="x", side="bottom")
        for i, (label, nilai) in enumerate((("Total top up", rupiah(masuk)),
                                            ("Total belanja", rupiah(keluar)),
                                            ("Mutasi", str(jumlah)))):
            kolom = tk.Frame(bawah, bg=bawah.cget("bg"))
            kolom.pack(side="left", expand=True, fill="x", padx=(18 if i == 0 else 4, 4), pady=12)
            tk.Label(kolom, text=label, fg=redup, bg=bawah.cget("bg"),
                     font=(Tema.FONT, 8)).pack(anchor="w")
            tk.Label(kolom, text=nilai, fg="#ffffff", bg=bawah.cget("bg"),
                     font=(Tema.FONT, 10, "bold")).pack(anchor="w")

    # ---------- kartu top up ----------
    def _bangun_topup(self, grid, dompet):
        kt = self._kartu(grid, "Top Up Saldo", "Isi saldo untuk membeli game lebih cepat.")
        kt.grid(row=0, column=1, sticky="nsew", padx=(9, 0), pady=(0, 18))

        tk.Label(kt, text="Nominal top up", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w", padx=22)
        kotak = tk.Frame(kt, bg=Tema.KARTU, highlightthickness=1,
                         highlightbackground=Tema.GARIS, highlightcolor=Tema.aksen)
        kotak.pack(anchor="w", padx=22, pady=(6, 8))
        tk.Label(kotak, text="Rp", fg=Tema.REDUP, bg=Tema.KARTU,
                 font=(Tema.FONT, 14, "bold")).pack(side="left", padx=(14, 6))
        e = tk.Entry(kotak, textvariable=self._nominal, bg=Tema.KARTU, fg=Tema.TEKS,
                     insertbackground=Tema.TEKS, relief="flat", width=14,
                     font=(Tema.FONT, 16, "bold"), highlightthickness=0)
        e.pack(side="left", ipady=9, padx=(0, 14))
        e.bind("<KeyRelease>", lambda ev: self._hitung())

        chip = tk.Frame(kt, bg=Tema.PANEL)
        chip.pack(anchor="w", padx=22, pady=(0, 14))
        for n in DompetService.NOMINAL_CEPAT:
            p = Pil(chip, rupiah(n).replace("Rp", ""), lambda x=n: self._set_nominal(x),
                    bg=Tema.PANEL)
            p.pack(side="left", padx=(0, 6))
            self._pil[n] = p

        tk.Label(kt, text="Metode pembayaran", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w", padx=22, pady=(2, 6))
        grid_m = tk.Frame(kt, bg=Tema.PANEL)
        grid_m.pack(anchor="w", padx=18)
        for i, (nama, kelas) in enumerate(dompet.daftar_metode().items()):
            ket = f"admin {kelas.label_tarif()}"
            if nama == "Transfer Bank":
                ket += " \u2022 BCA, Mandiri, BNI"
            u = UbinMetode(grid_m, nama, ket, lambda n=nama: self._pilih(n),
                           terpilih=(nama == self._metode.get()), lebar=232, tinggi=60)
            u.grid(row=i // 2, column=i % 2, padx=4, pady=4)
            self._ubin[nama] = u

        self._lb_catatan = tk.Label(kt, text="", fg=Tema.REDUP, bg=Tema.PANEL, justify="left",
                                    wraplength=470, font=(Tema.FONT, 9))
        self._lb_catatan.pack(anchor="w", padx=22, pady=(8, 8))

        rinci = tk.Frame(kt, bg=Tema.KARTU, highlightthickness=1, highlightbackground=Tema.GARIS)
        rinci.pack(fill="x", padx=22, pady=(0, 6))
        self._v_saldo = self._baris_rinci(rinci, "Saldo masuk")
        self._v_admin = self._baris_rinci(rinci, "Biaya admin")
        pemisah(rinci).pack(fill="x", padx=14)
        self._v_total = self._baris_rinci(rinci, "Total bayar", tebal=True)
        self._lb_galat = tk.Label(kt, text="", fg=Tema.MERAH, bg=Tema.PANEL, justify="left",
                                  font=(Tema.FONT, 9, "bold"))
        self._lb_galat.pack(anchor="w", padx=22)
        TombolFlat(kt, "Top Up Sekarang", self._topup, padx=30, pady=12).pack(
            anchor="w", padx=22, pady=(8, 22))

    def _baris_rinci(self, parent, label, tebal=False):
        f = tk.Frame(parent, bg=Tema.KARTU)
        f.pack(fill="x", padx=14, pady=6)
        tk.Label(f, text=label, fg=Tema.TEKS if tebal else Tema.REDUP, bg=Tema.KARTU,
                 font=(Tema.FONT, 10, "bold" if tebal else "normal")).pack(side="left")
        v = tk.Label(f, text="", fg=Tema.AKSEN_TEKS if tebal else Tema.TEKS, bg=Tema.KARTU,
                     font=(Tema.FONT, 12 if tebal else 10, "bold"))
        v.pack(side="right")
        return v

    # ---------- riwayat ----------
    def _ikon_mutasi(self, parent, masuk):
        c = tk.Canvas(parent, width=40, height=40, bg=Tema.PANEL, highlightthickness=0)
        warna = Tema.HIJAU if masuk else Tema.MERAH
        c.create_oval(2, 2, 38, 38, fill=campur(warna, "#ffffff", 0.85), outline="")
        if masuk:       # panah turun (uang masuk)
            c.create_line(20, 11, 20, 27, fill=warna, width=3)
            c.create_polygon(12, 22, 28, 22, 20, 30, fill=warna, outline=warna)
        else:           # panah naik (uang keluar)
            c.create_line(20, 29, 20, 13, fill=warna, width=3)
            c.create_polygon(12, 18, 28, 18, 20, 10, fill=warna, outline=warna)
        return c

    def _bangun_riwayat(self, isi, customer):
        mutasi = customer.get_mutasi()
        if not mutasi:
            k = tk.Frame(isi, bg=Tema.PANEL)
            k.pack(fill="x", padx=32)
            tk.Label(k, text="Belum ada mutasi", fg=Tema.TEKS, bg=Tema.PANEL,
                     font=(Tema.FONT, 12, "bold")).pack(pady=(24, 2))
            tk.Label(k, text="Top up atau pembelianmu akan muncul di sini.", fg=Tema.REDUP,
                     bg=Tema.PANEL, font=(Tema.FONT, 10)).pack(pady=(0, 24))
            return
        for m in reversed(mutasi[-MAKS_RIWAYAT:]):
            k = tk.Frame(isi, bg=Tema.PANEL)
            k.pack(fill="x", padx=32, pady=(0, 8))
            self._ikon_mutasi(k, m.masuk()).pack(side="left", padx=(18, 0), pady=12)
            kiri = tk.Frame(k, bg=Tema.PANEL)
            kiri.pack(side="left", padx=14, pady=12)
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
    def _pilih(self, nama):
        self._metode.set(nama)
        for k, u in self._ubin.items():
            u.atur(k == nama)
        self._hitung()

    def _set_nominal(self, n):
        self._nominal.set(f"{n:,}".replace(",", "."))
        self._hitung()

    def _hitung(self):
        """Perbarui rincian biaya sesuai nominal dan metode yang dipilih."""
        if self._v_total is None or self._lb_catatan is None:
            return
        dompet = DompetService(self._app.toko.get_customer())
        nama = self._metode.get()
        nominal = DompetService.baca_nominal(self._nominal.get())
        self._lb_catatan.configure(text=dompet.daftar_metode()[nama].catatan())
        for n, p in self._pil.items():
            p.atur(n == nominal)
        ok, pesan = dompet.validasi(nominal)
        if not ok:
            self._lb_galat.configure(text=pesan)
            for v in (self._v_saldo, self._v_admin, self._v_total):
                v.configure(text="\u2014")
            return
        self._lb_galat.configure(text="")
        admin, total = dompet.rincian(nominal, nama)
        self._v_saldo.configure(text=rupiah(nominal))
        self._v_admin.configure(text=rupiah(admin))
        self._v_total.configure(text=rupiah(total))

    def _topup(self):
        root = self._app.root
        dompet = DompetService(self._app.toko.get_customer())
        nama = self._metode.get()
        nominal = DompetService.baca_nominal(self._nominal.get())
        ok, pesan = dompet.validasi(nominal)
        if not ok:
            messagebox.showwarning("Nominal tidak valid", pesan, parent=root)
            return

        if perlu_halaman_bayar(nama):        # QRIS / Transfer Bank: tampilkan kode bayar dulu
            def selesai(pesan_ok):
                messagebox.showinfo("Top up berhasil", pesan_ok, parent=root)
                self._app.refresh_semua()

            DialogBayar(self._app, root, "Top Up Saldo BestDeal", nama,
                        dompet.daftar_metode()[nama], nominal, "Saldo masuk", "TOP",
                        lambda tagihan: dompet.topup(nominal, nama), selesai)
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
