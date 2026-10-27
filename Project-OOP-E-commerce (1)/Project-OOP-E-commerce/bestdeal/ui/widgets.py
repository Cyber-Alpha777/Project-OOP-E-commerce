"""Komponen GUI kecil yang dipakai ulang di banyak halaman."""

import tkinter as tk
import tkinter.font as tkfont
from PIL import Image, ImageOps, ImageTk
from tkinter import ttk

from bestdeal.config import resolve_gambar
from bestdeal.ui.tema import Tema
from bestdeal.utils import campur, rupiah


def lukis_art(c, w, h, produk, badge=True):
    """Gambar placeholder cover produk di Canvas."""
    latar = "#f3f4f6"
    garis = "#d1d5db"
    ikon = "#9ca3af"
    c.create_rectangle(0, 0, w, h, fill=latar, outline="")

    path_gambar = produk.get_gambar()
    gambar_dimuat = False
    if path_gambar:
        path = resolve_gambar(path_gambar)
        try:
            with Image.open(path) as sumber:
                gambar = ImageOps.contain(sumber.convert("RGB"), (w, h))
                kanvas_gambar = Image.new("RGB", (w, h), latar)
                posisi = ((w - gambar.width) // 2, (h - gambar.height) // 2)
                kanvas_gambar.paste(gambar, posisi)
            foto = ImageTk.PhotoImage(kanvas_gambar, master=c)
        except (OSError, tk.TclError) as err:
            c.create_text(w / 2, h / 2, text=f"Gagal memuat gambar:\n{err}",
                          fill="#6b7280", font=(Tema.FONT, max(7, min(10, int(h * 0.12)))))
        else:
            c.create_image(w / 2, h / 2, image=foto)
            c.gambar_produk = foto
            gambar_dimuat = True

    if not path_gambar:
        ukuran_ikon = max(6, min(w * 0.09, h * 0.22))
        tengah_x = w / 2
        tengah_y = h * (0.40 if h >= 64 else 0.5)
        kiri = tengah_x - ukuran_ikon
        kanan = tengah_x + ukuran_ikon
        atas = tengah_y - ukuran_ikon * 0.7
        bawah = tengah_y + ukuran_ikon * 0.7
        c.create_rectangle(kiri, atas, kanan, bawah, outline=ikon, width=2)
        c.create_oval(kiri + ukuran_ikon * 0.2, atas + ukuran_ikon * 0.15,
                      kiri + ukuran_ikon * 0.6, atas + ukuran_ikon * 0.55,
                      fill=ikon, outline="")
        c.create_polygon(kiri + ukuran_ikon * 0.1, bawah - ukuran_ikon * 0.1,
                         kiri + ukuran_ikon * 0.48, atas + ukuran_ikon * 0.55,
                         kanan - ukuran_ikon * 0.1, bawah - ukuran_ikon * 0.1,
                         fill=ikon, outline=ikon)
        if h >= 64:
            c.create_text(w / 2, h * 0.78, text="Placeholder gambar",
                          fill="#6b7280", font=(Tema.FONT, max(8, min(11, int(h * 0.08)))))
    elif gambar_dimuat:
        c.create_rectangle(1, 1, w - 1, h - 1, outline=garis)

    if badge and produk.label_tipe() != "Game":
        teks = produk.label_tipe().upper()
        c.create_rectangle(8, 8, 16 + len(teks) * 8, 28, fill=Tema.aksen, outline="")
        c.create_text(12, 18, text=teks, anchor="w", fill=Tema.TEKS,
                      font=(Tema.FONT, 8, "bold"))


class TombolFlat(tk.Label):
    def __init__(self, parent, teks, perintah, bg=None, fg="#1c1410", font=None,
                 padx=16, pady=8):
        warna = bg or Tema.aksen
        super().__init__(parent, text=teks, bg=warna, fg=fg, padx=padx, pady=pady,
                         font=font or (Tema.FONT, 10, "bold"), cursor="hand2")
        self._normal = warna
        self._hover = campur(warna, "#ffffff", 0.18)
        self._perintah = perintah
        self.bind("<Enter>", lambda e: self.configure(bg=self._hover))
        self.bind("<Leave>", lambda e: self.configure(bg=self._normal))
        self.bind("<Button-1>", lambda e: self._perintah())


class InputCari(tk.Frame):
    def __init__(self, parent, placeholder, saat_ubah, lebar=30, bg=None):
        bg = bg or Tema.KARTU
        super().__init__(parent, bg=bg, highlightthickness=1,
                         highlightbackground=Tema.GARIS, highlightcolor=Tema.aksen)
        self._placeholder = placeholder
        self._saat_ubah = saat_ubah
        self._aktif_ph = False
        self._after = None
        tk.Label(self, text="🔍", bg=bg, fg=Tema.REDUP, font=(Tema.FONT, 10)).pack(
            side="left", padx=(10, 0))
        self._entry = tk.Entry(self, bg=bg, fg=Tema.TEKS, insertbackground=Tema.TEKS,
                               relief="flat", width=lebar, font=(Tema.FONT, 11),
                               highlightthickness=0)
        self._entry.pack(side="left", padx=8, pady=7)
        self._tampil_ph()
        self._entry.bind("<FocusIn>", self._fokus_masuk)
        self._entry.bind("<FocusOut>", self._fokus_keluar)
        self._entry.bind("<KeyRelease>", self._ketik)
        self._entry.bind("<Return>", lambda e: self._kirim())

    def _tampil_ph(self):
        self._entry.delete(0, "end")
        self._entry.insert(0, self._placeholder)
        self._entry.configure(fg=Tema.REDUP)
        self._aktif_ph = True

    def _fokus_masuk(self, _):
        if self._aktif_ph:
            self._entry.delete(0, "end")
            self._entry.configure(fg=Tema.TEKS)
            self._aktif_ph = False

    def _fokus_keluar(self, _):
        if not self._entry.get():
            self._tampil_ph()

    def _ketik(self, _):
        if self._after:
            self.after_cancel(self._after)
        self._after = self.after(200, self._kirim)

    def _kirim(self):
        self._after = None
        self._saat_ubah(self.get_teks())

    def nonaktifkan(self):
        self._entry.configure(state="disabled", disabledforeground=Tema.REDUP,
                              disabledbackground=self.cget("bg"))

    def get_teks(self):
        return "" if self._aktif_ph else self._entry.get()


class ScrollFrame(tk.Frame):
    """Area yang bisa di-scroll (mouse wheel + scrollbar). Isi taruh di .isi"""

    def __init__(self, parent, bg=Tema.BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, yscrollincrement=20)
        self._sb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                 style="Game.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=self._sb.set)
        self._sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.isi = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.isi, anchor="nw")
        self.isi.bind("<Configure>",
                      lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self._win, width=e.width))

    def gulir(self, arah):
        if self.canvas.yview() != (0.0, 1.0):
            self.canvas.yview_scroll(arah * 3, "units")

    def ke_atas(self):
        self.canvas.yview_moveto(0)

    def posisi(self):
        return self.canvas.yview()[0]

    def pulihkan(self, frac):
        self.after(40, lambda: self.canvas.yview_moveto(frac))

    def kosongkan(self):
        for w in self.isi.winfo_children():
            w.destroy()


def baris_harga(parent, produk, customer, bg, ukuran=11):
    f = tk.Frame(parent, bg=bg)
    if customer is not None and produk.dimiliki_oleh(customer):   # tamu: customer = None
        tk.Label(f, text="✓ Di Library", fg=Tema.HIJAU, bg=bg,
                 font=(Tema.FONT, ukuran, "bold")).pack(side="left")
        return f
    harga = produk.harga_akhir()
    d = produk.diskon_persen()
    if d > 0:
        b = tk.Label(f, text=f"-{d}%", bg=Tema.DISKON_BG, fg=Tema.DISKON_FG, padx=5,
                     font=(Tema.FONT, ukuran - 1, "bold"))
        b._tetap = True
        b.pack(side="left", padx=(0, 8))
        coret = tkfont.Font(family=Tema.FONT, size=ukuran - 2, overstrike=True)
        lc = tk.Label(f, text=rupiah(produk.get_harga()), fg=Tema.REDUP, bg=bg, font=coret)
        lc._font = coret
        lc.pack(side="left", padx=(0, 8))
    tk.Label(f, text="Gratis" if harga == 0 else rupiah(harga), fg=Tema.TEKS, bg=bg,
             font=(Tema.FONT, ukuran, "bold")).pack(side="left")
    return f


class KartuProduk(tk.Frame):
    def __init__(self, parent, produk, customer, lebar, saat_klik):
        super().__init__(parent, bg=Tema.KARTU, cursor="hand2", highlightthickness=1,
                         highlightbackground=Tema.GARIS)
        tinggi = int(lebar * 9 / 16)
        art = tk.Canvas(self, width=lebar, height=tinggi, highlightthickness=0, bg=Tema.KARTU)
        art.pack()
        lukis_art(art, lebar, tinggi, produk)
        body = tk.Frame(self, bg=Tema.KARTU)
        body.pack(fill="both", expand=True, padx=12, pady=(10, 12))
        tk.Label(body, text=produk.get_nama_produk(), fg=Tema.TEKS, bg=Tema.KARTU,
                 font=(Tema.FONT, 11, "bold"), anchor="w", justify="left",
                 wraplength=lebar - 28).pack(anchor="w")
        tk.Label(body, text=f"{produk.get_kategori()}  •  {produk.nama_publisher()}",
                 fg=Tema.REDUP, bg=Tema.KARTU, font=(Tema.FONT, 9)).pack(anchor="w", pady=(2, 8))
        baris_harga(body, produk, customer, Tema.KARTU).pack(anchor="w", side="bottom")
        self._ikat(self, lambda e: saat_klik(produk))
        self._ikat_hover(self)

    def _ikat(self, w, fn):
        w.bind("<Button-1>", fn, add="+")
        for c in w.winfo_children():
            self._ikat(c, fn)

    def _ikat_hover(self, w):
        w.bind("<Enter>", lambda e: self._warna(self, Tema.KARTU_HOVER), add="+")
        w.bind("<Leave>", self._keluar, add="+")
        for c in w.winfo_children():
            self._ikat_hover(c)

    def _keluar(self, _):
        try:
            w = self.winfo_containing(*self.winfo_pointerxy())
        except (KeyError, tk.TclError):
            w = None
        while w is not None:
            if w is self:
                return
            w = w.master
        self._warna(self, Tema.KARTU)

    def _warna(self, w, warna):
        if not getattr(w, "_tetap", False) and not isinstance(w, tk.Canvas):
            w.configure(bg=warna)
        for c in w.winfo_children():
            self._warna(c, warna)
