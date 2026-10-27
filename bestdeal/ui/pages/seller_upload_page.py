"""Halaman Seller: form upload game ke katalog BestDeal."""

import os
import tkinter as tk
from datetime import date
from tkinter import filedialog, messagebox, ttk

from bestdeal.models.produk import Game
from bestdeal.services.seller import LayananSeller
from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import KartuProduk, ScrollFrame, TombolFlat


class SellerUploadPage(Halaman):
    GALAT = "#b91c1c"
    LEBAR_PRATINJAU = 300
    # teks + tujuan yang bisa diganti subclass (mis. SellerEditPage) -- Polymorphism
    JUDUL = "Upload Game"
    SUBJUDUL = "Isi detail game lalu publikasikan. Game langsung tampil di toko untuk semua customer."
    TEKS_KIRIM = "Publikasikan Game"
    TEKS_RESET = "Kosongkan form"
    HALAMAN_SETELAH = "dashboard"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)
        self._after = None
        self._cover = ""

    def saat_ditampilkan(self):
        self.bangun()           # form selalu mulai dalam keadaan kosong

    def segarkan(self):
        pass                    # jangan hapus isi form saat resize / refresh_semua

    def destroy(self):
        if self._after:
            self.after_cancel(self._after)
            self._after = None
        super().destroy()

    # ---------- susunan halaman ----------
    def bangun(self):
        if self._after:
            self.after_cancel(self._after)
            self._after = None
        self._cover = self._cover_awal()
        self.scroll.kosongkan()
        self.scroll.ke_atas()
        isi = self.scroll.isi
        self.judul(isi, self.JUDUL)
        tk.Label(isi, text=self.SUBJUDUL, fg=Tema.REDUP, bg=Tema.BG,
                 font=(Tema.FONT, 10)).pack(anchor="w", padx=32, pady=(0, 14))

        badan = tk.Frame(isi, bg=Tema.BG)
        badan.pack(fill="x", padx=32, pady=(0, 28))
        badan.columnconfigure(0, weight=1)
        form = tk.Frame(badan, bg=Tema.PANEL, padx=28, pady=22,
                        highlightthickness=1, highlightbackground=Tema.GARIS)
        form.grid(row=0, column=0, sticky="new", padx=(0, 18))
        kanan = tk.Frame(badan, bg=Tema.BG)
        kanan.grid(row=0, column=1, sticky="n")
        self._susun_form(form)
        self._susun_pratinjau(kanan)
        self._pratinjau()

    # ---------- komponen form ----------
    def _label(self, parent, teks, pady=(14, 4)):
        tk.Label(parent, text=teks, fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w", pady=pady)

    def _entry(self, parent):
        e = tk.Entry(parent, bg=Tema.KARTU, fg=Tema.TEKS, insertbackground=Tema.TEKS,
                     relief="flat", font=(Tema.FONT, 11), highlightthickness=1,
                     highlightbackground=Tema.GARIS, highlightcolor=Tema.aksen)
        e.bind("<KeyRelease>", lambda ev: self._jadwalkan_pratinjau())
        e.pack(fill="x", ipady=8)
        return e

    def _dua_kolom(self, form):
        baris = tk.Frame(form, bg=Tema.PANEL)
        baris.pack(fill="x")
        baris.columnconfigure(0, weight=1, uniform="f")
        baris.columnconfigure(1, weight=1, uniform="f")
        kiri = tk.Frame(baris, bg=Tema.PANEL)
        kiri.grid(row=0, column=0, sticky="new", padx=(0, 8))
        kanan = tk.Frame(baris, bg=Tema.PANEL)
        kanan.grid(row=0, column=1, sticky="new", padx=(8, 0))
        return kiri, kanan

    def _susun_form(self, form):
        self._label(form, "Judul game", pady=(0, 4))
        self._nama = self._entry(form)

        kiri, kanan = self._dua_kolom(form)
        self._label(kiri, "Kategori")
        gaya = ttk.Style(self)
        gaya.configure("Seller.TCombobox", arrowcolor=Tema.REDUP, bordercolor=Tema.GARIS,
                       lightcolor=Tema.KARTU, darkcolor=Tema.KARTU)
        gaya.map("Seller.TCombobox", fieldbackground=[("readonly", Tema.KARTU)],
                 background=[("readonly", Tema.KARTU), ("active", Tema.CHIP)],
                 foreground=[("readonly", Tema.TEKS)],
                 selectbackground=[("readonly", Tema.KARTU)],
                 selectforeground=[("readonly", Tema.TEKS)])
        self._kategori = ttk.Combobox(kiri, values=LayananSeller.KATEGORI, state="readonly",
                                      style="Seller.TCombobox", font=(Tema.FONT, 11))
        self._kategori.pack(fill="x", ipady=5)
        self._kategori.bind("<<ComboboxSelected>>", lambda e: self._jadwalkan_pratinjau())
        self._label(kanan, "Tahun / tanggal rilis")
        self._rilis = self._entry(kanan)
        self._rilis.insert(0, str(date.today().year))

        kiri, kanan = self._dua_kolom(form)
        self._label(kiri, "Harga (Rp)")
        self._harga = self._entry(kiri)
        tk.Label(kiri, text="Angka saja, mis. 150000. Isi 0 untuk gratis.", fg=Tema.REDUP,
                 bg=Tema.PANEL, font=(Tema.FONT, 8)).pack(anchor="w", pady=(3, 0))
        self._label(kanan, "Diskon (%)")
        self._diskon = self._entry(kanan)
        self._diskon.insert(0, "0")

        self._label(form, "Deskripsi")
        self._deskripsi = tk.Text(form, height=6, wrap="word", bg=Tema.KARTU, fg=Tema.TEKS,
                                  insertbackground=Tema.TEKS, relief="flat",
                                  font=(Tema.FONT, 11), highlightthickness=1,
                                  highlightbackground=Tema.GARIS, highlightcolor=Tema.aksen)
        self._deskripsi.pack(fill="x")
        self._deskripsi.bind("<KeyRelease>", lambda ev: self._jadwalkan_pratinjau())
        self._hitung = tk.Label(form, text="", fg=Tema.REDUP, bg=Tema.PANEL,
                                font=(Tema.FONT, 8))
        self._hitung.pack(anchor="w", pady=(3, 0))

        self._label(form, "Cover game")
        cov = tk.Frame(form, bg=Tema.PANEL)
        cov.pack(fill="x")
        TombolFlat(cov, "Pilih gambar\u2026", self._pilih_cover, bg=Tema.KARTU, fg=Tema.TEKS,
                   font=(Tema.FONT, 9, "bold"), padx=14, pady=6).pack(side="left")
        self._nama_cover = tk.Label(cov, text="Belum dipilih (pakai placeholder)",
                                    fg=Tema.REDUP, bg=Tema.PANEL, font=(Tema.FONT, 9))
        self._nama_cover.pack(side="left", padx=10)
        self._hapus_cover = tk.Label(cov, text="Hapus", fg=Tema.AKSEN_TEKS, bg=Tema.PANEL,
                                     cursor="hand2", font=(Tema.FONT, 9, "bold"))
        self._hapus_cover.bind("<Button-1>", lambda e: self._atur_cover(""))
        tk.Label(form, text="Rasio 16:9 (mis. 1280\u00d7720) paling pas. PNG, JPG, WEBP, GIF, "
                            "atau BMP, maksimal 10 MB.", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 8)).pack(anchor="w", pady=(4, 0))

        self._galat = tk.Label(form, text="", fg=self.GALAT, bg=Tema.PANEL, justify="left",
                               wraplength=480, font=(Tema.FONT, 9, "bold"))
        self._galat.pack(anchor="w", pady=(14, 0))
        tombol = tk.Frame(form, bg=Tema.PANEL)
        tombol.pack(fill="x", pady=(10, 0))
        TombolFlat(tombol, self.TEKS_KIRIM, self._kirim, padx=24, pady=11).pack(side="left")
        TombolFlat(tombol, self.TEKS_RESET, self.bangun, bg=Tema.CHIP, fg=Tema.TEKS,
                   padx=18, pady=11).pack(side="left", padx=10)
        self._tombol_ekstra(tombol)
        self._isi_awal()
        self._nama.focus_set()

    # ---------- hook untuk subclass ----------
    def _cover_awal(self):
        return ""

    def _isi_awal(self):
        """Isi form dengan data awal (kosong untuk upload baru)."""

    def _tombol_ekstra(self, tombol):
        """Tombol tambahan di samping tombol kirim / reset."""

    def _simpan(self):
        """Kirim isi form ke service. Return (ok, pesan, game)."""
        return self._app.seller.upload_game(
            self._nama.get(), self._kategori.get(), self._harga.get(), self._diskon.get(),
            self._rilis.get(), self._deskripsi.get("1.0", "end"), self._cover)

    def _susun_pratinjau(self, parent):
        tk.Label(parent, text="Pratinjau di toko", fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 12, "bold")).pack(anchor="w", pady=(0, 8))
        self._wadah = tk.Frame(parent, bg=Tema.BG)
        self._wadah.pack(anchor="w")
        tk.Label(parent, text="Begini kartu game-mu akan tampil di halaman Toko.",
                 fg=Tema.REDUP, bg=Tema.BG, wraplength=self.LEBAR_PRATINJAU, justify="left",
                 font=(Tema.FONT, 9)).pack(anchor="w", pady=(8, 0))

    # ---------- pratinjau langsung ----------
    def _jadwalkan_pratinjau(self):
        if self._after:
            self.after_cancel(self._after)
        self._after = self.after(250, self._pratinjau)

    def _pratinjau(self):
        self._after = None
        for w in self._wadah.winfo_children():
            w.destroy()
        harga = LayananSeller.ke_angka(self._harga.get()) or 0
        diskon = min(100, LayananSeller.ke_angka(self._diskon.get()) or 0)
        game = Game("PRATINJAU", self._nama.get().strip()[:LayananSeller.JUDUL_MAKS] or "Judul game",
                    harga, self._kategori.get() or "Kategori", self._app.seller.get_seller(), "",
                    diskon=diskon, ulasan=0, gambar=self._cover or None)
        KartuProduk(self._wadah, game, None, self.LEBAR_PRATINJAU, lambda p: None).pack()
        n = len(self._deskripsi.get("1.0", "end").strip())
        self._hitung.configure(
            text=f"{n} / {LayananSeller.DESKRIPSI_MAKS} karakter (minimal {LayananSeller.DESKRIPSI_MIN})")

    # ---------- cover ----------
    def _pilih_cover(self):
        path = filedialog.askopenfilename(
            parent=self, title="Pilih cover game",
            filetypes=[("Gambar", "*.png *.jpg *.jpeg *.webp *.gif *.bmp"), ("Semua file", "*.*")])
        if not path:
            return
        ok, pesan = LayananSeller.cek_cover(path)
        if not ok:
            self._galat.configure(text=pesan)
            return
        self._galat.configure(text="")
        self._atur_cover(path)

    def _atur_cover(self, path):
        self._cover = path
        self._tampil_cover()
        self._pratinjau()

    def _tampil_cover(self):
        path = self._cover
        if path:
            self._nama_cover.configure(text=os.path.basename(path), fg=Tema.TEKS)
            self._hapus_cover.pack(side="left")
        else:
            self._nama_cover.configure(text="Belum dipilih (pakai placeholder)", fg=Tema.REDUP)
            self._hapus_cover.pack_forget()

    # ---------- kirim ----------
    def _kirim(self):
        ok, pesan, game = self._simpan()
        if not ok:
            self._galat.configure(text=pesan)
            return
        messagebox.showinfo("Berhasil", pesan, parent=self)
        self._app.refresh_semua()
        self._app.buka(self.HALAMAN_SETELAH)
