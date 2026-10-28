"""Halaman Login dan Daftar (form di tengah layar)."""

import tkinter as tk
from abc import abstractmethod

from bestdeal.data.katalog_demo import DEMO_EMAIL, DEMO_PASSWORD,AKUN_SELLER_DEMO,DEMO_SELLER_PASSWORD
from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import ScrollFrame, TombolFlat


class AuthPageBase(Halaman):
    """Dasar halaman form. Subclass mengisi form di bangun() (Polymorphism)."""
    GALAT = "#b91c1c"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)
        self._pesan = ""

    def atur_pesan(self, teks):
        """Pesan info yang tampil sekali di atas form (mis. 'Masuk dulu untuk membeli ...')."""
        self._pesan = teks

    def saat_ditampilkan(self):
        self.bangun()           # form selalu mulai dalam keadaan kosong

    def segarkan(self):
        pass                    # ukuran kartu tetap, tidak perlu dibangun ulang saat resize

    # ---------- komponen form ----------
    def _kartu(self, judul, sub):
        self.scroll.kosongkan()
        self.scroll.ke_atas()
        kartu = tk.Frame(self.scroll.isi, bg=Tema.PANEL, padx=40, pady=30)
        kartu.pack(pady=(40, 40))
        kembali = tk.Label(kartu, text="\u2190 Kembali ke beranda", fg=Tema.AKSEN_TEKS,
                           bg=Tema.PANEL, cursor="hand2", font=(Tema.FONT, 9, "bold"))
        kembali.pack(anchor="w")
        kembali.bind("<Button-1>", lambda e: self._app.tampilkan_landing())
        tk.Label(kartu, text=judul, fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 22, "bold")).pack(anchor="w", pady=(14, 2))
        tk.Label(kartu, text=sub, fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 10)).pack(anchor="w")
        if self._pesan:
            tk.Label(kartu, text=self._pesan, fg=Tema.AKSEN_TEKS, bg="#ffe9d6", padx=12, pady=8,
                     justify="left", wraplength=340,
                     font=(Tema.FONT, 10, "bold")).pack(fill="x", pady=(14, 0))
            self._pesan = ""
        return kartu

    def _field(self, kartu, label, sembunyi=False):
        tk.Label(kartu, text=label, fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w", pady=(14, 4))
        e = tk.Entry(kartu, bg=Tema.KARTU, fg=Tema.TEKS, insertbackground=Tema.TEKS,
                     relief="flat", font=(Tema.FONT, 11), width=36, show="\u2022" if sembunyi else "",
                     highlightthickness=1, highlightbackground=Tema.GARIS,
                     highlightcolor=Tema.aksen)
        e.pack(fill="x", ipady=8)
        e.bind("<Return>", lambda ev: self._kirim())
        return e

    def _label_galat(self, kartu):
        return tk.Label(kartu, text="", fg=self.GALAT, bg=Tema.PANEL, justify="left",
                        wraplength=340, font=(Tema.FONT, 9, "bold"))

    def _tautan(self, kartu, teks, aksi_teks, aksi):
        f = tk.Frame(kartu, bg=Tema.PANEL)
        f.pack(pady=(16, 0))
        tk.Label(f, text=teks, fg=Tema.REDUP, bg=Tema.PANEL, font=(Tema.FONT, 10)).pack(side="left")
        lb = tk.Label(f, text=aksi_teks, fg=Tema.AKSEN_TEKS, bg=Tema.PANEL, cursor="hand2",
                      font=(Tema.FONT, 10, "bold"))
        lb.pack(side="left")
        lb.bind("<Button-1>", lambda e: aksi())

    @abstractmethod
    def _kirim(self):
        ...


class LoginPage(AuthPageBase):
    def bangun(self):
        kartu = self._kartu("Masuk ke BestDeal", "Lanjutkan belanja game favoritmu.")
        self._email = self._field(kartu, "Email")
        self._sandi = self._field(kartu, "Kata sandi", sembunyi=True)
        self._galat = self._label_galat(kartu)
        self._galat.pack(anchor="w", pady=(10, 0))
        TombolFlat(kartu, "Masuk", self._kirim, padx=24, pady=11).pack(fill="x", pady=(14, 0))
        self._tautan(kartu, "Belum punya akun?  ", "Daftar", self._app.tampilkan_daftar)

        demo = tk.Frame(kartu, bg=Tema.CHIP)
        demo.pack(fill="x", pady=(22, 0))
        tk.Label(demo, text="Akun demo Customer", fg=Tema.TEKS, bg=Tema.CHIP,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w", padx=14, pady=(10, 0))
        tk.Label(demo, text=f"{DEMO_EMAIL}  \u2022  {DEMO_PASSWORD}", fg=Tema.REDUP, bg=Tema.CHIP,
                 font=("Consolas", 9)).pack(anchor="w", padx=14)
        TombolFlat(demo, "Isi otomatis", self._isi_demo_cust, bg=Tema.KARTU, fg=Tema.TEKS,
                 font=(Tema.FONT, 9, "bold"), padx=12, pady=5).pack(anchor="w", padx=14, pady=10)
        tk.Label(demo, text="Akun Seller", fg=Tema.TEKS, bg=Tema.CHIP,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w", padx=14, pady=(10, 0))
        tk.Label(demo, text=f"{AKUN_SELLER_DEMO}  \u2022  {DEMO_SELLER_PASSWORD}", fg=Tema.REDUP, bg=Tema.CHIP,
                 font=("Consolas", 9)).pack(anchor="w", padx=14)
        TombolFlat(demo, "Isi otomatis", self._isi_demo_seller, bg=Tema.KARTU, fg=Tema.TEKS,
                   font=(Tema.FONT, 9, "bold"), padx=12, pady=5).pack(anchor="w", padx=14, pady=10)
        self._email.focus_set()

    def _isi_demo_cust(self):
        for e, teks in ((self._email, DEMO_EMAIL), (self._sandi, DEMO_PASSWORD)):
            e.delete(0, "end")
            e.insert(0, teks)

    def _isi_demo_seller(self):
        for e, teks in ((self._email, AKUN_SELLER_DEMO), (self._sandi, DEMO_SELLER_PASSWORD)):
            e.delete(0, "end")
            e.insert(0, teks)

    def _kirim(self):
        ok, pesan, user = self._app.auth.masuk(self._email.get(), self._sandi.get())
        if not ok:
            self._galat.configure(text=pesan)
            self._sandi.delete(0, "end")
            return
        self._app.masuk(user)  


class DaftarPage(AuthPageBase):
    """Daftar akun baru, sebagai Pembeli (Customer) atau Seller (Publisher)."""
    PERAN = (("Customer", "Pembeli"), ("Publisher", "Seller"))

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._peran = "Customer"
        self._isian = {}

    def saat_ditampilkan(self):
        self._peran = "Customer"        # setiap kali dibuka mulai sebagai Pembeli, form kosong
        self._isian = {}
        self.bangun()

    def bangun(self):
        seller = self._peran == "Publisher"
        kartu = self._kartu("Daftar sebagai Seller" if seller else "Buat akun baru",
                            "Jual gamemu di BestDeal. Gratis." if seller
                            else "Gratis. Cukup beberapa detik.")
        self._pilih_peran(kartu)
        self._nama = self._field(kartu, "Nama toko / publisher" if seller else "Nama")
        self._email = self._field(kartu, "Email")
        self._sandi = self._field(kartu, "Kata sandi (min. 6 karakter)", sembunyi=True)
        self._konfirmasi = self._field(kartu, "Ulangi kata sandi", sembunyi=True)
        self._galat = self._label_galat(kartu)
        self._galat.pack(anchor="w", pady=(10, 0))
        TombolFlat(kartu, "Daftar sebagai Seller" if seller else "Daftar", self._kirim,
                   padx=24, pady=11).pack(fill="x", pady=(14, 0))
        self._tautan(kartu, "Sudah punya akun?  ", "Masuk", self._app.tampilkan_login)
        for kunci, entry in self._entri().items():      # pulihkan isian saat ganti peran
            entry.insert(0, self._isian.get(kunci, ""))
        self._nama.focus_set()

    def _entri(self):
        return {"nama": self._nama, "email": self._email, "sandi": self._sandi,
                "konfirmasi": self._konfirmasi}

    def _pilih_peran(self, kartu):
        """Dua tombol pilihan peran; yang aktif berwarna aksen."""
        baris = tk.Frame(kartu, bg=Tema.PANEL)
        baris.pack(fill="x", pady=(16, 0))
        tk.Label(baris, text="Daftar sebagai", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w", pady=(0, 4))
        for i, (peran, teks) in enumerate(self.PERAN):
            aktif = peran == self._peran
            TombolFlat(baris, teks, lambda p=peran: self._ganti_peran(p),
                       bg=Tema.aksen if aktif else Tema.CHIP, padx=20, pady=8).pack(
                side="left", fill="x", expand=True,
                padx=(0, 6) if i < len(self.PERAN) - 1 else 0)

    def _ganti_peran(self, peran):
        if peran == self._peran:
            return
        self._isian = {k: e.get() for k, e in self._entri().items()}
        self._peran = peran
        self.bangun()                   # _kartu() mengosongkan lalu membangun ulang form

    def _kirim(self):
        daftar = (self._app.auth.daftar_seller if self._peran == "Publisher"
                  else self._app.auth.daftar)
        ok, pesan, user = daftar(self._nama.get(), self._email.get(), self._sandi.get(),
                                 self._konfirmasi.get())
        if not ok:
            self._galat.configure(text=pesan)
            return
        self._app.auth.masuk(self._email.get(), self._sandi.get())
        self._app.masuk(user)           # Customer -> toko, Seller -> dashboard seller
