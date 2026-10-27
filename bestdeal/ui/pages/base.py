"""Kelas abstrak Halaman (Abstraction + Inheritance + Polymorphism)."""

import tkinter as tk
from abc import ABC, abstractmethod

from bestdeal.ui.tema import Tema


class Halaman(tk.Frame, ABC):
    """Kelas abstrak untuk semua halaman. Subclass wajib implement bangun()."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=Tema.BG)
        self._app = app
        self._kotor = True

    @abstractmethod
    def bangun(self):
        ...

    def segarkan(self):
        self.bangun()
        self._kotor = False

    def tandai_kotor(self):
        self._kotor = True

    def saat_ditampilkan(self):
        if self._kotor:
            self.segarkan()

    def judul(self, parent, teks, aksi_teks=None, aksi=None, pad=(24, 12)):
        f = tk.Frame(parent, bg=Tema.BG)
        f.pack(fill="x", padx=32, pady=pad)
        tk.Label(f, text=teks, fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 16, "bold")).pack(side="left")
        if aksi_teks:
            lb = tk.Label(f, text=aksi_teks, fg=Tema.AKSEN_TEKS, bg=Tema.BG, cursor="hand2",
                          font=(Tema.FONT, 10, "bold"))
            lb.pack(side="right")
            lb.bind("<Button-1>", lambda e: aksi())
        return f
