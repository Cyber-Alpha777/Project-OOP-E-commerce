"""Komponen visual tambahan (kartu, pil, ubin metode bayar, bilah progres) untuk tampilan yang lebih rapi."""

import tkinter as tk
import tkinter.font as tkfont

from bestdeal.ui.tema import Tema
from bestdeal.utils import campur


def kotak_bulat(c, x1, y1, x2, y2, r=12, **kw):
    """Persegi panjang sudut membulat di Canvas."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    p = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2,
         x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(p, smooth=True, **kw)


class Pil(tk.Canvas):
    """Tombol pilihan berbentuk pil (dipakai untuk nominal cepat, filter periode, dsb)."""

    def __init__(self, parent, teks, perintah, terpilih=False, bg=None, font=None, padx=16,
                 tinggi=32):
        self._teks, self._perintah, self._terpilih = teks, perintah, terpilih
        self._font = font or (Tema.FONT, 9, "bold")
        lebar = tkfont.Font(family=self._font[0], size=self._font[1],
                            weight="bold").measure(teks) + padx * 2
        super().__init__(parent, width=lebar, height=tinggi, bg=bg or Tema.BG,
                         highlightthickness=0, cursor="hand2")
        self._lebar, self._tinggi = lebar, tinggi
        self._hover = False
        self.bind("<Button-1>", lambda e: self._perintah())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self._gambar()

    def _set_hover(self, v):
        self._hover = v
        self._gambar()

    def atur(self, terpilih):
        self._terpilih = terpilih
        self._gambar()

    def _gambar(self):
        self.delete("all")
        if self._terpilih:
            isi, garis, fg = Tema.aksen, Tema.aksen, "#ffffff"
        else:
            isi = Tema.KARTU_HOVER if self._hover else Tema.KARTU
            garis, fg = Tema.GARIS, Tema.TEKS
        kotak_bulat(self, 1, 1, self._lebar - 1, self._tinggi - 1, r=self._tinggi / 2,
                    fill=isi, outline=garis)
        self.create_text(self._lebar / 2, self._tinggi / 2, text=self._teks, fill=fg,
                         font=self._font)


def lencana(parent, teks, warna, fg="#ffffff", bg=None, font=None, padx=12, tinggi=24):
    """Lencana kecil berwarna (mis. status, nama bank)."""
    f = font or (Tema.FONT, 8, "bold")
    lebar = tkfont.Font(family=f[0], size=f[1], weight="bold").measure(teks) + padx * 2
    c = tk.Canvas(parent, width=lebar, height=tinggi, bg=bg or Tema.BG, highlightthickness=0)
    kotak_bulat(c, 0, 0, lebar, tinggi, r=tinggi / 2, fill=warna, outline="")
    c.create_text(lebar / 2, tinggi / 2, text=teks, fill=fg, font=f)
    return c


def lencana_bank(parent, bank, lebar=64, tinggi=40, bg=None):
    """Logo teks bank (BCA / Mandiri / BNI) dengan warna khas bank."""
    c = tk.Canvas(parent, width=lebar, height=tinggi, bg=bg or Tema.BG, highlightthickness=0)
    kotak_bulat(c, 0, 0, lebar, tinggi, r=10, fill=bank.WARNA, outline="")
    ukuran = 13 if len(bank.NAMA) <= 3 else 10
    c.create_text(lebar / 2, tinggi / 2, text=bank.NAMA.upper(), fill=bank.WARNA_TEKS,
                  font=(Tema.FONT, ukuran, "bold"))
    return c


def ikon_metode(c, nama, cx, cy, r=18, bg=None):
    """Gambar ikon sederhana untuk metode pembayaran di Canvas c."""
    bg = bg or Tema.PANEL
    nama = nama.lower()
    if "qris" in nama:
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#e11d48", outline="")
        s = r * 0.42
        for dx, dy in ((-1, -1), (1, -1), (-1, 1)):
            x, y = cx + dx * r * 0.45, cy + dy * r * 0.45
            c.create_rectangle(x - s, y - s, x + s, y + s, fill="#ffffff", outline="")
            c.create_rectangle(x - s * 0.4, y - s * 0.4, x + s * 0.4, y + s * 0.4,
                               fill="#e11d48", outline="")
        c.create_rectangle(cx + r * 0.1, cy + r * 0.1, cx + r * 0.7, cy + r * 0.7,
                           fill="#ffffff", outline="")
    elif "transfer" in nama or "bank" in nama:
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#2563eb", outline="")
        k = r * 0.55
        c.create_polygon(cx - k, cy - k * 0.3, cx, cy - k, cx + k, cy - k * 0.3,
                         fill="#ffffff", outline="")
        for dx in (-0.6, 0, 0.6):
            c.create_rectangle(cx + dx * k - 2, cy - k * 0.1, cx + dx * k + 2, cy + k * 0.6,
                               fill="#ffffff", outline="")
        c.create_rectangle(cx - k, cy + k * 0.7, cx + k, cy + k * 0.9, fill="#ffffff", outline="")
    elif "kartu" in nama:
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#7c3aed", outline="")
        c.create_rectangle(cx - r * 0.6, cy - r * 0.4, cx + r * 0.6, cy + r * 0.4,
                           fill="#ffffff", outline="")
        c.create_rectangle(cx - r * 0.6, cy - r * 0.2, cx + r * 0.6, cy, fill="#7c3aed",
                           outline="")
    elif "saldo" in nama:
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=Tema.aksen, outline="")
        c.create_rectangle(cx - r * 0.6, cy - r * 0.4, cx + r * 0.6, cy + r * 0.45,
                           fill="#ffffff", outline="")
        c.create_oval(cx + r * 0.25, cy - r * 0.08, cx + r * 0.45, cy + r * 0.12,
                      fill=Tema.aksen, outline="")
    else:       # e-wallet (GoPay, OVO, DANA, ...)
        warna = {"gopay": "#00aa13", "ovo": "#4c3494", "dana": "#118eea"}.get(nama, "#475569")
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=warna, outline="")
        c.create_text(cx, cy, text=nama[:1].upper(), fill="#ffffff",
                      font=(Tema.FONT, int(r * 0.8), "bold"))


class UbinMetode(tk.Canvas):
    """Ubin metode pembayaran yang bisa dipilih: ikon + nama + biaya admin."""

    def __init__(self, parent, nama, keterangan, perintah, terpilih=False, lebar=210,
                 tinggi=62, bg=None, kompak=False):
        super().__init__(parent, width=lebar, height=tinggi, bg=bg or Tema.PANEL,
                         highlightthickness=0, cursor="hand2")
        self._kompak = kompak
        self._nama, self._ket, self._perintah = nama, keterangan, perintah
        self._terpilih, self._hover = terpilih, False
        self._lebar, self._tinggi = lebar, tinggi
        self.bind("<Button-1>", lambda e: self._perintah())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self._gambar()

    def _set_hover(self, v):
        self._hover = v
        self._gambar()

    def atur(self, terpilih):
        self._terpilih = terpilih
        self._gambar()

    def _gambar(self):
        self.delete("all")
        w, h = self._lebar, self._tinggi
        if self._terpilih:
            kotak_bulat(self, 1, 1, w - 1, h - 1, r=14, fill="#fff7ef", outline=Tema.aksen,
                        width=2)
        else:
            isi = Tema.KARTU_HOVER if self._hover else Tema.KARTU
            kotak_bulat(self, 1, 1, w - 1, h - 1, r=14, fill=isi, outline=Tema.GARIS, width=1)
        if self._kompak:
            ikon_metode(self, self._nama, 24, h / 2, r=12, bg=Tema.KARTU)
            self.create_text(44, h / 2, text=self._nama, anchor="w", fill=Tema.TEKS,
                             font=(Tema.FONT, 9, "bold"))
            return
        ikon_metode(self, self._nama, 32, h / 2, r=17, bg=Tema.KARTU)
        self.create_text(60, h / 2 - 9, text=self._nama, anchor="w", fill=Tema.TEKS,
                         font=(Tema.FONT, 10, "bold"))
        self.create_text(60, h / 2 + 10, text=self._ket, anchor="w", fill=Tema.REDUP,
                         font=(Tema.FONT, 8))
        if self._terpilih:
            self.create_oval(w - 28, h / 2 - 9, w - 10, h / 2 + 9, fill=Tema.aksen, outline="")
            self.create_text(w - 19, h / 2 - 1, text="\u2713", fill="#ffffff",
                             font=(Tema.FONT, 9, "bold"))


class BilahProgres(tk.Canvas):
    """Bilah progres tipis (dipakai untuk hitung mundur batas bayar)."""

    def __init__(self, parent, lebar, tinggi=8, bg=None):
        super().__init__(parent, width=lebar, height=tinggi, bg=bg or Tema.BG,
                         highlightthickness=0)
        self._lebar, self._tinggi = lebar, tinggi
        self.atur(1.0)

    def atur(self, pecahan, warna=None):
        pecahan = max(0.0, min(1.0, pecahan))
        self.delete("all")
        kotak_bulat(self, 0, 0, self._lebar, self._tinggi, r=self._tinggi / 2,
                    fill=Tema.GARIS, outline="")
        if pecahan > 0:
            kotak_bulat(self, 0, 0, max(self._tinggi, self._lebar * pecahan), self._tinggi,
                        r=self._tinggi / 2, fill=warna or Tema.aksen, outline="")


def nomor_langkah(parent, angka, bg):
    """Lingkaran bernomor untuk daftar langkah."""
    c = tk.Canvas(parent, width=24, height=24, bg=bg, highlightthickness=0)
    c.create_oval(1, 1, 23, 23, fill=campur(Tema.aksen, "#ffffff", 0.82), outline="")
    c.create_text(12, 12, text=str(angka), fill=Tema.AKSEN_TEKS, font=(Tema.FONT, 9, "bold"))
    return c


def kartu_statistik(parent, label, nilai, sub, warna=None, bg=None):
    """Kartu angka dengan aksen warna di sisi kiri."""
    bg = bg or Tema.PANEL
    luar = tk.Frame(parent, bg=bg)
    tk.Frame(luar, bg=warna or Tema.aksen, width=5).pack(side="left", fill="y")
    isi = tk.Frame(luar, bg=bg)
    isi.pack(side="left", fill="both", expand=True)
    tk.Label(isi, text=label, fg=Tema.REDUP, bg=bg, font=(Tema.FONT, 10)).pack(
        anchor="w", padx=16, pady=(14, 0))
    tk.Label(isi, text=nilai, fg=Tema.TEKS, bg=bg, font=(Tema.FONT, 20, "bold")).pack(
        anchor="w", padx=16)
    tk.Label(isi, text=sub, fg=Tema.REDUP, bg=bg, font=(Tema.FONT, 9)).pack(
        anchor="w", padx=16, pady=(0, 14))
    return luar


def pemisah(parent, bg=None):
    return tk.Frame(parent, bg=bg or Tema.GARIS, height=1)
