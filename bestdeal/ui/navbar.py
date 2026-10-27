"""Navbar BestDeal: versi member (sudah login) dan versi tamu."""

import tkinter as tk

from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import InputCari, TombolFlat
from bestdeal.utils import rupiah


def buat_logo(parent, saat_klik=None):
    """Logo BestDeal (lingkaran + teks). Dipakai NavBar dan NavBarTamu."""
    logo = tk.Frame(parent, bg=Tema.NAV)
    logo.pack(side="left", padx=(32, 36))
    ic = tk.Canvas(logo, width=36, height=36, bg=Tema.NAV, highlightthickness=0)
    ic.pack(side="left")
    ic.create_oval(0, 0, 36, 36, fill=Tema.aksen, outline="")
    ic.create_text(18, 18, text="B", fill=Tema.TEKS, font=(Tema.FONT, 14, "bold"))
    teks = tk.Label(logo, text="BestDeal", fg=Tema.TEKS, bg=Tema.NAV,
                    font=(Tema.FONT, 18, "bold"))
    teks.pack(side="left", padx=(10, 0))
    if saat_klik:
        for w in (logo, ic, teks):
            w.configure(cursor="hand2")
            w.bind("<Button-1>", lambda e: saat_klik())
    return logo


class NavBar(tk.Frame):
    """Navbar BestDeal setelah login. Semua menu (TOKO, LIBRARY, AKUN, SETTING) bisa diklik; klik saldo untuk buka Dompet."""
    MENU = (("home", "TOKO"), ("library", "LIBRARY"), ("akun", "AKUN"), ("setting", "SETTING"))
    BISA_DIKLIK = ("home", "library", "akun", "setting")

    def __init__(self, parent, app):
        super().__init__(parent, bg=Tema.NAV, height=72)
        self.pack_propagate(False)
        self._app = app

        buat_logo(self)

        self._item = {}
        for kunci, teks in self.MENU:
            klik = kunci in self.BISA_DIKLIK
            f = tk.Frame(self, bg=Tema.NAV)
            f.pack(side="left", fill="y", padx=4)
            lb = tk.Label(f, text=teks, bg=Tema.NAV, font=(Tema.FONT, 10, "bold"), padx=12,
                          cursor="hand2" if klik else "arrow")
            lb.pack(expand=True)
            garis = tk.Frame(f, bg=Tema.NAV, height=3)
            garis.pack(fill="x", side="bottom")
            self._item[kunci] = (lb, garis)
            if klik:
                lb.bind("<Button-1>", lambda e, k=kunci: self._app.buka(k))
        self.set_aktif(None)

        self._avatar = tk.Canvas(self, width=40, height=40, bg=Tema.NAV, highlightthickness=0)
        TombolFlat(self, "Keluar", self._app.keluar, bg=Tema.CHIP, fg="#4a3d33",
                   font=(Tema.FONT, 9, "bold"), padx=14, pady=6).pack(side="right", padx=(8, 32))
        self._avatar.pack(side="right", padx=(12, 8))
        self._saldo = tk.Label(self, fg="#9a3d00", bg="#fff1e4", padx=12, pady=5,
                               font=(Tema.FONT, 10, "bold"))
        self._saldo.configure(cursor="hand2")          # klik saldo -> halaman Dompet
        self._saldo.bind("<Button-1>", lambda e: self._app.buka("dompet"))
        self._saldo.pack(side="right", padx=8)
        self.cari = InputCari(self, "Cari game, genre, publisher...", self._app.cari,
                              lebar=28, bg=Tema.CHIP)
        self.cari.pack(side="right", padx=16)
        self.perbarui()

    def perbarui(self):
        c = self._app.toko.get_customer()
        self._saldo.configure(text=rupiah(c.get_saldo()))
        a = self._avatar
        a.delete("all")
        a.create_oval(2, 2, 38, 38, fill=Tema.TEKS, outline="")
        a.create_text(20, 20, text=c.get_nama()[:1].upper(), fill="#ffffff",
                      font=(Tema.FONT, 13, "bold"))

    def set_aktif(self, kunci):
        for k, (lb, garis) in self._item.items():
            if k == kunci:
                lb.configure(fg=Tema.TEKS)
                garis.configure(bg=Tema.aksen)
            else:
                lb.configure(fg=Tema.REDUP if k in self.BISA_DIKLIK else Tema.NONAKTIF)
                garis.configure(bg=Tema.NAV)


class NavBarTamu(tk.Frame):
    """Navbar untuk pengunjung yang belum login: logo + tombol Masuk / Daftar."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=Tema.NAV, height=72)
        self.pack_propagate(False)
        self._app = app
        buat_logo(self, saat_klik=app.tampilkan_landing)
        TombolFlat(self, "Daftar", app.tampilkan_daftar, padx=20, pady=8).pack(
            side="right", padx=(8, 32))
        TombolFlat(self, "Masuk", app.tampilkan_login, bg=Tema.CHIP, fg=Tema.TEKS,
                   padx=20, pady=8).pack(side="right", padx=4)

    def perbarui(self):
        pass    # tidak ada saldo / avatar untuk tamu

    def set_aktif(self, kunci):
        pass
