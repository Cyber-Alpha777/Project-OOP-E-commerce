"""Halaman Seller: daftar game milik seller + tombol edit."""

import tkinter as tk

from bestdeal.ui.hias import lencana
from bestdeal.ui.pages.base import Halaman
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import ScrollFrame, TombolFlat, lukis_art
from bestdeal.utils import campur, rupiah


class SellerKelolaPage(Halaman):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)

    def saat_ditampilkan(self):
        Halaman.segarkan(self)      # data bisa berubah (habis edit / upload), selalu bangun ulang
        self.scroll.ke_atas()

    def segarkan(self):
        frac = self.scroll.posisi()
        super().segarkan()
        self.scroll.pulihkan(frac)

    def bangun(self):
        self.scroll.kosongkan()
        isi = self.scroll.isi
        layanan = self._app.seller
        baris = layanan.statistik()
        self.judul(isi, f"Kelola Game \u2022 {layanan.get_seller().get_nama_toko()}",
                   "+ Upload Game", lambda: self._app.buka("upload"))
        if not baris:
            self._kosong(isi)
            return
        tk.Label(isi, text=f"{len(baris)} produk di tokomu. Klik Edit untuk mengubah judul, "
                           f"harga, diskon, deskripsi, atau cover.", fg=Tema.REDUP, bg=Tema.BG,
                 font=(Tema.FONT, 10)).pack(anchor="w", padx=32, pady=(0, 14))
        for b in baris:
            self._kartu(isi, b)
        tk.Frame(isi, bg=Tema.BG, height=24).pack()

    def _kosong(self, isi):
        k = tk.Frame(isi, bg=Tema.PANEL)
        k.pack(fill="x", padx=32, pady=(0, 24))
        tk.Label(k, text="Belum ada game di tokomu", fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 15, "bold")).pack(anchor="w", padx=28, pady=(26, 4))
        tk.Label(k, text="Upload game pertamamu agar bisa dikelola di sini.", fg=Tema.REDUP,
                 bg=Tema.PANEL, font=(Tema.FONT, 10)).pack(anchor="w", padx=28)
        TombolFlat(k, "Upload Game Pertama", lambda: self._app.buka("upload"),
                   padx=24, pady=10).pack(anchor="w", padx=28, pady=(16, 26))

    def _kartu(self, isi, b):
        p = b.produk
        k = tk.Frame(isi, bg=Tema.KARTU, highlightthickness=1, highlightbackground=Tema.GARIS)
        k.pack(fill="x", padx=32, pady=(0, 10))

        art = tk.Canvas(k, width=128, height=72, highlightthickness=0, bg=Tema.KARTU)
        lukis_art(art, 128, 72, p, badge=False)
        art.pack(side="left", padx=14, pady=14)

        info = tk.Frame(k, bg=Tema.KARTU)
        info.pack(side="left", fill="y", pady=14)
        tk.Label(info, text=p.get_nama_produk(), fg=Tema.TEKS, bg=Tema.KARTU,
                 font=(Tema.FONT, 12, "bold")).pack(anchor="w")
        tag = tk.Frame(info, bg=Tema.KARTU)
        tag.pack(anchor="w", pady=(6, 6))
        lencana(tag, p.label_tipe(), campur(Tema.aksen, "#ffffff", 0.82), Tema.AKSEN_TEKS,
                bg=Tema.KARTU).pack(side="left", padx=(0, 6))
        lencana(tag, p.get_kategori(), Tema.CHIP, Tema.REDUP, bg=Tema.KARTU).pack(side="left")
        harga = "Gratis" if p.harga_akhir() == 0 else rupiah(p.harga_akhir())
        if p.diskon_persen() > 0:
            harga += f"   (-{p.diskon_persen()}% dari {rupiah(p.get_harga())})"
        tk.Label(info, text=harga, fg=Tema.TEKS, bg=Tema.KARTU,
                 font=(Tema.FONT, 10, "bold")).pack(anchor="w")

        aksi = tk.Frame(k, bg=Tema.KARTU)
        aksi.pack(side="right", padx=18)
        if p.bisa_diedit():
            TombolFlat(aksi, "Edit", lambda g=p: self._app.buka_edit(g), padx=26,
                       pady=9).pack()
        else:
            tk.Label(aksi, text="Dikelola otomatis", fg=Tema.NONAKTIF, bg=Tema.KARTU,
                     font=(Tema.FONT, 9)).pack()

        for judul, nilai in (("Pendapatan", rupiah(b.pendapatan)),
                             ("Terjual", f"{b.terjual:,}".replace(",", "."))):
            s = tk.Frame(k, bg=Tema.KARTU)
            s.pack(side="right", padx=22)
            tk.Label(s, text=judul, fg=Tema.REDUP, bg=Tema.KARTU,
                     font=(Tema.FONT, 9)).pack(anchor="e")
            tk.Label(s, text=nilai, fg=Tema.TEKS, bg=Tema.KARTU,
                     font=(Tema.FONT, 12, "bold")).pack(anchor="e")
