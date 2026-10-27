"""Aplikasi utama: jendela, navigasi antar halaman, alur masuk / keluar."""

import tkinter as tk
from tkinter import messagebox, ttk

from bestdeal.data.katalog_demo import (buat_customer_demo, buat_katalog_demo,
                                        buat_penjualan_demo)
from bestdeal.services.auth import AuthService
from bestdeal.services.pengaturan import Pengaturan
from bestdeal.services.penjualan import LaporanPenjualan
from bestdeal.services.seller_kelola import LayananSellerLengkap
from bestdeal.services.toko import TokoGame
from bestdeal.ui.dialogs import DialogProduk
from bestdeal.ui.navbar import NavBar, NavBarSeller, NavBarTamu
from bestdeal.ui.pages.akun_page import AkunPage
from bestdeal.ui.pages.auth_pages import DaftarPage, LoginPage
from bestdeal.ui.pages.home_page import HomePage
from bestdeal.ui.pages.landing_page import LandingPage
from bestdeal.ui.pages.library_page import LibraryPage
from bestdeal.ui.pages.seller_dashboard_page import SellerDashboardPage
from bestdeal.ui.pages.seller_edit_page import SellerEditPage
from bestdeal.ui.pages.seller_kelola_page import SellerKelolaPage
from bestdeal.ui.pages.seller_penjualan_page import SellerPenjualanPage
from bestdeal.ui.pages.seller_upload_page import SellerUploadPage
from bestdeal.ui.pages.setting_page import SettingPage
from bestdeal.ui.pages.dompet_page import DompetPage
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import ScrollFrame


class AplikasiBestDeal:
    # halaman yang tersedia sebelum dan sesudah login
    HALAMAN_TAMU = {"landing": LandingPage, "login": LoginPage, "daftar": DaftarPage}
    HALAMAN_MEMBER = {"home": HomePage, "library": LibraryPage, "akun": AkunPage,
                      "setting": SettingPage, "dompet": DompetPage}
    HALAMAN_SELLER = {"dashboard": SellerDashboardPage, "upload": SellerUploadPage,
                      "kelola": SellerKelolaPage, "penjualan": SellerPenjualanPage,
                      "edit": SellerEditPage}

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BestDeal \u2014 Toko Game")
        self.root.configure(bg=Tema.BG)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = (1280, 720) if sh >= 800 else (1152, 648)
        x = (sw - w) // 2
        y = max(0, (sh - h) // 2 - 20)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(1024, 576)
        self._lebar = sw
        self._after_resize = None

        self.katalog, self.unggulan, library_awal, akun_seller = buat_katalog_demo()
        self.auth = AuthService([buat_customer_demo(library_awal)], akun_seller)
        self.laporan = LaporanPenjualan()       # buku besar penjualan, dipakai semua sesi
        buat_penjualan_demo(self.katalog, self.laporan)     # data simulasi awal (hapus = mulai nol)
        self.pengaturan = Pengaturan()
        self.toko = None            # TokoGame milik customer yang sedang login (None = bukan customer)
        self.seller = None          # LayananSeller milik seller yang sedang login (None = bukan seller)
        self._sesi_toko = {}        # id customer -> TokoGame (riwayat tetap ada setelah keluar-masuk)
        self._gaya()

        self.navbar = None
        self.halaman = {}
        self._aktif = None
        self.atur_layar_penuh(True)
        self.tampilkan_landing()

        self.root.bind("<Configure>", self._saat_resize)
        self.root.bind_all("<MouseWheel>", self._wheel)
        self.root.bind_all("<Button-4>", self._wheel)
        self.root.bind_all("<Button-5>", self._wheel)
        self.root.bind("<Escape>", lambda e: self.atur_layar_penuh(False))
        self.root.bind("<F11>", lambda e: self.toggle_layar_penuh())

    # ---------- util ----------
    def _gaya(self):
        s = ttk.Style(self.root)
        s.theme_use("clam")
        s.configure("Game.Vertical.TScrollbar", background=Tema.GARIS, troughcolor=Tema.BG,
                    bordercolor=Tema.BG, arrowcolor=Tema.BG, lightcolor=Tema.GARIS,
                    darkcolor=Tema.GARIS, gripcount=0, arrowsize=1)
        s.map("Game.Vertical.TScrollbar", background=[("active", Tema.REDUP)])

    def lebar(self):
        return self._lebar

    def lebar_konten(self):
        return max(600, self._lebar - 16 - 64)

    def aktif(self):
        return self._aktif

    def _bangun_ui(self, kelas_navbar, kelas_halaman, awal):
        for w in self.root.winfo_children():
            w.destroy()
        self.navbar = kelas_navbar(self.root, self)
        self.navbar.pack(fill="x")
        tk.Frame(self.root, bg=Tema.GARIS, height=1).pack(fill="x")
        wadah = tk.Frame(self.root, bg=Tema.BG)
        wadah.pack(fill="both", expand=True)
        self.halaman = {nama: kelas(wadah, self) for nama, kelas in kelas_halaman.items()}
        self._aktif = None
        self.buka(awal)

    def _bangun_ui_tamu(self, awal="landing"):
        self._bangun_ui(NavBarTamu, self.HALAMAN_TAMU, awal)

    def _bangun_ui_member(self, awal="home"):
        self._bangun_ui(NavBar, self.HALAMAN_MEMBER, awal)

    def _bangun_ui_seller(self, awal="dashboard"):
        self._bangun_ui(NavBarSeller, self.HALAMAN_SELLER, awal)

    def bangun_ulang(self, awal="home"):
        """Bangun ulang seluruh UI (mis. setelah ganti warna aksen)."""
        if self.seller is not None:
            self._bangun_ui_seller(awal if awal in self.HALAMAN_SELLER else "dashboard")
        elif self.toko is None:
            self._bangun_ui_tamu(awal if awal in self.HALAMAN_TAMU else "landing")
        else:
            self._bangun_ui_member(awal if awal in self.HALAMAN_MEMBER else "home")

    # ---------- alur sebelum login ----------
    def tampilkan_landing(self):
        if self.toko is None and "landing" in self.halaman:
            self.buka("landing")
        else:
            self._bangun_ui_tamu("landing")

    def tampilkan_login(self, pesan=""):
        self.halaman["login"].atur_pesan(pesan)
        self.buka("login")

    def tampilkan_daftar(self):
        self.buka("daftar")

    def minta_login(self, produk=None):
        """Dipanggil saat tamu mencoba membeli / membuka produk."""
        if produk is not None:
            pesan = f"Masuk dulu untuk membeli '{produk.get_nama_produk()}'."
        else:
            pesan = "Masuk dulu untuk melanjutkan."
        self.tampilkan_login(pesan)

    # ---------- masuk / keluar ----------
    def masuk(self, user):
        """Arahkan user yang baru login ke tampilan sesuai perannya."""
        {"Customer": self.masuk_toko, "Publisher": self.masuk_seller}[user.peran()](user)

    def masuk_toko(self, customer):
        kunci = customer.get_id_user()
        if kunci not in self._sesi_toko:
            self._sesi_toko[kunci] = TokoGame(customer, self.katalog, self.unggulan, self.laporan)
        self.toko = self._sesi_toko[kunci]
        self.seller = None
        self._bangun_ui_member("home")

    def masuk_seller(self, seller):
        self.toko = None
        self.seller = LayananSellerLengkap(seller, self.katalog, self.laporan)
        self._bangun_ui_seller("dashboard")

    def keluar(self):
        if not messagebox.askyesno("Keluar", "Keluar dari akun BestDeal?", parent=self.root):
            return
        self.auth.keluar()
        self.toko = None
        self.seller = None
        self._bangun_ui_tamu("landing")

    # ---------- navigasi ----------
    def buka(self, nama):
        if self._aktif:
            self.halaman[self._aktif].pack_forget()
        self._aktif = nama
        h = self.halaman[nama]
        h.pack(fill="both", expand=True)
        h.saat_ditampilkan()
        self.navbar.set_aktif(nama)

    def buka_library(self, game):
        self.buka("library")
        self.halaman["library"].pilih(game)

    def buka_edit(self, game):
        """Buka form edit untuk game milik seller yang sedang login."""
        self.halaman["edit"].atur_game(game)
        self.buka("edit")

    def buka_produk(self, produk):
        DialogProduk(self, produk)

    def cari(self, query):
        self.buka("home")
        self.halaman["home"].atur_pencarian(query)

    # ---------- refresh ----------
    def perbarui_navbar(self):
        self.navbar.perbarui()

    def halaman_tandai_kotor(self, nama):
        if nama != self._aktif:
            self.halaman[nama].tandai_kotor()

    def refresh_semua(self):
        self.navbar.perbarui()
        for nama, h in self.halaman.items():
            if nama == self._aktif:
                h.segarkan()
            else:
                h.tandai_kotor()

    # ---------- event ----------
    def atur_layar_penuh(self, aktif):
        self.pengaturan.set_layar_penuh(aktif)
        self.root.attributes("-fullscreen", aktif)

    def toggle_layar_penuh(self):
        self.atur_layar_penuh(not self.pengaturan.get_layar_penuh())

    def _saat_resize(self, e):
        if e.widget is not self.root or abs(e.width - self._lebar) < 40:
            return
        self._lebar = e.width
        if self._after_resize:
            self.root.after_cancel(self._after_resize)
        self._after_resize = self.root.after(250, self._resize_selesai)

    def _resize_selesai(self):
        self._after_resize = None
        for nama, h in self.halaman.items():
            if nama == self._aktif:
                h.segarkan()
            else:
                h.tandai_kotor()

    def _wheel(self, e):
        if getattr(e, "num", 0) == 4:
            arah = -1
        elif getattr(e, "num", 0) == 5:
            arah = 1
        else:
            arah = -1 if e.delta > 0 else 1
        try:
            w = self.root.winfo_containing(e.x_root, e.y_root)
        except (KeyError, tk.TclError):
            return
        while w is not None:
            if isinstance(w, ScrollFrame):
                w.gulir(arah)
                return
            w = w.master

    def jalankan(self):
        self.root.mainloop()
