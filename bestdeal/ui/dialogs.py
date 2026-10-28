"""Dialog detail / beli produk."""

import tkinter as tk
from tkinter import messagebox

from bestdeal.ui.dialog_bayar import DialogBayar, perlu_halaman_bayar
from bestdeal.ui.dialog_ulasan import DialogDaftarUlasan
from bestdeal.ui.hias import UbinMetode
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import TombolFlat, baris_harga, lukis_art
from bestdeal.utils import rupiah


class DialogProduk(tk.Toplevel):
    def __init__(self, app, produk):
        super().__init__(app.root, bg=Tema.BG)
        self._app = app
        self._produk = produk
        self.title(produk.get_nama_produk())
        self.resizable(False, False)
        self.transient(app.root)

        toko = app.toko
        customer = toko.get_customer()
        lebar_art = 520
        tinggi_art = int(lebar_art * 9 / 16)

        kiri = tk.Frame(self, bg=Tema.BG)
        kiri.grid(row=0, column=0, padx=(24, 12), pady=24, sticky="n")
        art = tk.Canvas(kiri, width=lebar_art, height=tinggi_art, highlightthickness=0, bg=Tema.BG)
        art.pack()
        lukis_art(art, lebar_art, tinggi_art, produk)
        tk.Label(kiri, text=produk.get_nama_produk(), fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 18, "bold"), wraplength=lebar_art, justify="left").pack(
            anchor="w", pady=(14, 2))
        tk.Label(kiri, text=f"{produk.label_tipe()} • {produk.get_kategori()}",
                 fg=Tema.aksen, bg=Tema.BG, font=(Tema.FONT, 9, "bold")).pack(anchor="w")
        tk.Label(kiri, text=produk.get_deskripsi(), fg=Tema.TEKS, bg=Tema.BG, justify="left",
                 wraplength=lebar_art, font=(Tema.FONT, 10)).pack(anchor="w", pady=(10, 6))
        seller = produk.get_seller()
        tk.Label(kiri, text=f"Publisher: {produk.nama_publisher()}"
                            + (f"  (★ {seller.get_rating()})" if seller else ""),
                 fg=Tema.REDUP, bg=Tema.BG, font=(Tema.FONT, 9)).pack(anchor="w")
        if produk.bisa_diulas():            # polymorphism: hanya Game yang punya ulasan
            baris_ulasan = tk.Frame(kiri, bg=Tema.BG)
            baris_ulasan.pack(anchor="w")
            tk.Label(baris_ulasan, text=f"Ulasan: {produk.teks_ulasan()}", fg=Tema.REDUP,
                     bg=Tema.BG, font=(Tema.FONT, 9)).pack(side="left")
            lihat = tk.Label(baris_ulasan, text="  Lihat ulasan", fg=Tema.AKSEN_TEKS, bg=Tema.BG,
                             cursor="hand2", font=(Tema.FONT, 9, "bold"))
            lihat.pack(side="left")
            lihat.bind("<Button-1>", lambda e: DialogDaftarUlasan(app, produk, induk=self))
        info = produk.info_tambahan()      # polymorphism, tanpa isinstance
        if info:
            tk.Label(kiri, text=info, fg=Tema.REDUP, bg=Tema.BG, wraplength=lebar_art,
                     justify="left", font=(Tema.FONT, 9)).pack(anchor="w")

        kanan = tk.Frame(self, bg=Tema.PANEL, width=300)
        kanan.grid(row=0, column=1, padx=(12, 24), pady=24, sticky="ns")
        kanan.grid_propagate(False)
        kanan.configure(height=tinggi_art + 240)
        tk.Label(kanan, text="Beli", fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 14, "bold")).pack(anchor="w", padx=20, pady=(20, 6))
        baris_harga(kanan, produk, customer, Tema.PANEL, 13).pack(anchor="w", padx=20)

        ok, alasan = produk.bisa_dibeli_oleh(customer)
        if not ok:
            tk.Label(kanan, text=alasan, fg=Tema.REDUP, bg=Tema.PANEL, wraplength=260,
                     justify="left", font=(Tema.FONT, 10)).pack(anchor="w", padx=20, pady=18)
            TombolFlat(kanan, "Tutup", self.destroy, bg=Tema.KARTU).pack(
                anchor="w", padx=20)
        else:
            tk.Label(kanan, text="Metode pembayaran", fg=Tema.REDUP, bg=Tema.PANEL,
                     font=(Tema.FONT, 9)).pack(anchor="w", padx=20, pady=(16, 4))
            self._metode = tk.StringVar(value=list(toko.METODE)[0])
            grid_m = tk.Frame(kanan, bg=Tema.PANEL)
            grid_m.pack(anchor="w", padx=14)
            self._ubin = {}
            for i, nama in enumerate(toko.METODE):
                u = UbinMetode(grid_m, nama, "", lambda n=nama: self._pilih(n),
                               terpilih=(i == 0), lebar=132, tinggi=44, kompak=True,
                               bg=Tema.PANEL)
                u.grid(row=i // 2, column=i % 2, padx=2, pady=2)
                self._ubin[nama] = u
            self._catatan = tk.Label(kanan, text="", fg=Tema.REDUP, bg=Tema.PANEL,
                                     justify="left", wraplength=260, font=(Tema.FONT, 9))
            self._catatan.pack(anchor="w", padx=20, pady=(8, 0))
            self._rincian = tk.Label(kanan, text="", fg=Tema.TEKS, bg=Tema.PANEL, justify="left",
                                     font=("Consolas", 10))
            self._rincian.pack(anchor="w", padx=20, pady=12)
            TombolFlat(kanan, "Beli Sekarang", self._beli, padx=26, pady=10).pack(
                anchor="w", padx=20)
            self._hitung()

        self._pusatkan()
        self.wait_visibility()
        self.grab_set()

    def _pusatkan(self):
        self.update_idletasks()
        r = self._app.root
        x = r.winfo_x() + (r.winfo_width() - self.winfo_reqwidth()) // 2
        y = r.winfo_y() + (r.winfo_height() - self.winfo_reqheight()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    def _pilih(self, nama):
        self._metode.set(nama)
        for k, u in self._ubin.items():
            u.atur(k == nama)
        self._hitung()

    def _hitung(self):
        toko = self._app.toko
        kelas = toko.METODE[self._metode.get()]
        sub = self._produk.harga_akhir()
        admin = kelas.tarif_admin(sub)          # polymorphism
        total = sub + admin
        teks = f"Harga   : {rupiah(sub)}\nAdmin   : {rupiah(admin)}\nTotal   : {rupiah(total)}"
        catatan = kelas.catatan()
        if not kelas.eksternal:                 # metode saldo: tampilkan sisa saldo
            saldo = toko.get_customer().get_saldo()
            teks += f"\nSaldo   : {rupiah(saldo)}"
            if saldo < total:
                catatan = "Saldo tidak cukup. Klik saldo di navbar untuk top up."
        self._rincian.configure(text=teks)
        self._catatan.configure(text=catatan)

    def _bayar_lewat_halaman(self, nama, kelas):
        """QRIS / Transfer Bank: tampilkan kode QR atau virtual account dulu."""
        app = self._app
        hasil = {}

        def bayar(tagihan):
            ok, pesan, kirim = app.toko.beli(self._produk, nama)
            if ok:
                hasil["kirim"] = kirim
            return ok, pesan

        def selesai(pesan):
            messagebox.showinfo(
                "Berhasil", f"{pesan}\n\nKunci lisensi:\n{hasil['kirim'].get_kunci()}\n\n"
                            f"Game sudah ada di Library kamu.", parent=self)
            self.destroy()
            app.refresh_semua()

        DialogBayar(app, self, f"Beli {self._produk.get_nama_produk()}", nama, kelas,
                    self._produk.harga_akhir(), "Harga", "ORD", bayar, selesai)

    def _beli(self):
        app = self._app
        nama = self._metode.get()
        kelas = app.toko.METODE[nama]
        if perlu_halaman_bayar(nama) and self._produk.harga_akhir() > 0:
            self._bayar_lewat_halaman(nama, kelas)
            return
        if app.pengaturan.get_konfirmasi() and not messagebox.askyesno(
                "Konfirmasi", f"Beli '{self._produk.get_nama_produk()}'?", parent=self):
            return
        ok, pesan, kirim = app.toko.beli(self._produk, self._metode.get())
        if not ok:
            messagebox.showwarning("Gagal", pesan, parent=self)
            return
        messagebox.showinfo("Berhasil", f"{pesan}\n\nKunci lisensi:\n{kirim.get_kunci()}\n\n"
                                        f"Game sudah ada di Library kamu.", parent=self)
        self.destroy()
        app.refresh_semua()
