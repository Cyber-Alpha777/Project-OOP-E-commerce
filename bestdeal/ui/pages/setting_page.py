"""Halaman Pengaturan."""

import tkinter as tk

from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import ScrollFrame, TombolFlat


class SettingPage(Halaman):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)

    def _baris(self, judul, ket):
        f = tk.Frame(self.scroll.isi, bg=Tema.PANEL)
        f.pack(fill="x", padx=32, pady=(0, 10))
        kiri = tk.Frame(f, bg=Tema.PANEL)
        kiri.pack(side="left", padx=20, pady=16)
        tk.Label(kiri, text=judul, fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 11, "bold")).pack(anchor="w")
        tk.Label(kiri, text=ket, fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9)).pack(anchor="w")
        kanan = tk.Frame(f, bg=Tema.PANEL)
        kanan.pack(side="right", padx=20)
        return kanan

    def _cek(self, parent, var, cmd):
        return tk.Checkbutton(parent, variable=var, command=cmd, bg=Tema.PANEL,
                              activebackground=Tema.PANEL, selectcolor=Tema.KARTU,
                              fg=Tema.TEKS, highlightthickness=0, bd=0, cursor="hand2")

    def bangun(self):
        self.scroll.kosongkan()
        p = self._app.pengaturan
        self.judul(self.scroll.isi, "Pengaturan")

        v1 = tk.BooleanVar(value=p.get_autoplay())
        self._cek(self._baris("Banner otomatis", "Banner unggulan di halaman Toko geser tiap 5 detik."),
                  v1, lambda: p.set_autoplay(v1.get())).pack()

        v2 = tk.BooleanVar(value=p.get_konfirmasi())
        self._cek(self._baris("Konfirmasi sebelum membeli", "Tampilkan dialog konfirmasi saat checkout."),
                  v2, lambda: p.set_konfirmasi(v2.get())).pack()

        v3 = tk.BooleanVar(value=p.get_layar_penuh())

        def layar():
            p.set_layar_penuh(v3.get())
            self._app.atur_layar_penuh(v3.get())
        self._cek(self._baris("Layar penuh", "Tekan Esc untuk keluar dari mode layar penuh."),
                  v3, layar).pack()

        kanan = self._baris("Warna aksen", "Ganti warna utama aplikasi.")
        for nama, hex_ in Tema.AKSEN.items():
            aktif = nama == p.get_aksen()
            TombolFlat(kanan, ("✓ " if aktif else "") + nama, lambda n=nama: self._ganti(n),
                       bg=hex_, padx=12, pady=6, font=(Tema.FONT, 9, "bold")).pack(
                side="left", padx=4)

        self._baris("Tentang", "BestDeal v1.0 • Tkinter • Proyek PBO")
        tk.Frame(self.scroll.isi, bg=Tema.BG, height=30).pack()

    def _ganti(self, nama):
        if Tema.terapkan_aksen(nama):          # warna = urusan UI, pilihan = urusan Pengaturan
            self._app.pengaturan.set_aksen(nama)
        self._app.bangun_ulang("setting")
