"""Dialog ulasan: DialogTulisUlasan (customer menulis/mengubah) dan DialogDaftarUlasan (baca)."""

import tkinter as tk
from tkinter import messagebox

from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import ScrollFrame, TombolFlat
from bestdeal.utils import campur


class _DialogDasar(tk.Toplevel):
    """Dasar dialog modal: transient, di tengah jendela utama, mengembalikan grab ke induk."""

    def __init__(self, app, induk, judul):
        super().__init__(app.root, bg=Tema.BG)
        self._app = app
        self._induk = induk
        self.title(judul)
        self.resizable(False, False)
        self.transient(app.root)
        self.protocol("WM_DELETE_WINDOW", self._tutup)

    def _tampilkan(self):
        self.update_idletasks()
        r = self._app.root
        x = r.winfo_x() + (r.winfo_width() - self.winfo_reqwidth()) // 2
        y = r.winfo_y() + (r.winfo_height() - self.winfo_reqheight()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.wait_visibility()
        self.grab_set()

    def _tutup(self):
        self.destroy()
        if self._induk is not None:             # dialog induk (mis. detail produk) jadi modal lagi
            try:
                self._induk.grab_set()
            except tk.TclError:
                pass


def tampilkan_rekomendasi(parent, bg, rekomendasi, ukuran=9):
    """Label '✓ Direkomendasikan' (hijau) / '✕ Tidak direkomendasikan' (merah)."""
    teks, warna = (("\u2713 Direkomendasikan", Tema.HIJAU) if rekomendasi
                   else ("\u2715 Tidak direkomendasikan", Tema.MERAH))
    return tk.Label(parent, text=teks, fg=warna, bg=bg, font=(Tema.FONT, ukuran, "bold"))


class DialogTulisUlasan(_DialogDasar):
    """Form ulasan satu game. Kalau customer sudah punya ulasan, form berisi ulasan lama (edit)."""

    def __init__(self, app, game, saat_selesai=None, induk=None):
        super().__init__(app, induk, f"Ulasan \u2014 {game.get_nama_produk()}")
        self._game = game
        self._saat_selesai = saat_selesai
        self._toko = app.toko
        lama = self._toko.ulasan_saya(game)
        self._pilihan = lama.get_rekomendasi() if lama else None

        kartu = tk.Frame(self, bg=Tema.BG, padx=28, pady=24)
        kartu.pack()
        tk.Label(kartu, text="Ubah ulasan" if lama else "Tulis ulasan", fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 16, "bold")).pack(anchor="w")
        tk.Label(kartu, text=game.get_nama_produk(), fg=Tema.REDUP, bg=Tema.BG,
                 font=(Tema.FONT, 10)).pack(anchor="w", pady=(2, 14))

        tk.Label(kartu, text="Apakah kamu merekomendasikan game ini?", fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 10, "bold")).pack(anchor="w")
        baris = tk.Frame(kartu, bg=Tema.BG)
        baris.pack(anchor="w", pady=(8, 14))
        self._tombol = {}
        for nilai, teks in ((True, "\u2713  Ya, rekomendasi"), (False, "\u2715  Tidak")):
            t = TombolFlat(baris, teks, lambda v=nilai: self._pilih(v), bg=Tema.CHIP,
                           font=(Tema.FONT, 10, "bold"), padx=18, pady=8)
            t.pack(side="left", padx=(0, 8))
            self._tombol[nilai] = t
        self._pilih(self._pilihan)

        tk.Label(kartu, text=f"Komentar (min. {self._toko.KOMENTAR_MIN} karakter)",
                 fg=Tema.TEKS, bg=Tema.BG, font=(Tema.FONT, 10, "bold")).pack(anchor="w")
        self._teks = tk.Text(kartu, width=52, height=7, wrap="word", bg=Tema.KARTU, fg=Tema.TEKS,
                             insertbackground=Tema.TEKS, relief="flat", font=(Tema.FONT, 10),
                             highlightthickness=1, highlightbackground=Tema.GARIS,
                             highlightcolor=Tema.aksen, padx=8, pady=6)
        self._teks.pack(pady=(6, 2))
        if lama:
            self._teks.insert("1.0", lama.get_komentar())
        self._hitung = tk.Label(kartu, text="", fg=Tema.REDUP, bg=Tema.BG, font=(Tema.FONT, 9))
        self._hitung.pack(anchor="e")
        self._teks.bind("<KeyRelease>", lambda e: (self._perbarui_hitung(),
                                                   self._galat.configure(text="")))
        self._perbarui_hitung()

        self._galat = tk.Label(kartu, text="", fg="#b91c1c", bg=Tema.BG, justify="left",
                               wraplength=400, font=(Tema.FONT, 9, "bold"))
        self._galat.pack(anchor="w", pady=(4, 0))

        aksi = tk.Frame(kartu, bg=Tema.BG)
        aksi.pack(fill="x", pady=(12, 0))
        TombolFlat(aksi, "Simpan ulasan" if lama else "Kirim ulasan", self._kirim,
                   padx=22, pady=9).pack(side="left")
        TombolFlat(aksi, "Batal", self._tutup, bg=Tema.CHIP, padx=18, pady=9).pack(
            side="left", padx=8)
        if lama:
            TombolFlat(aksi, "Hapus", self._hapus, bg=Tema.CHIP, fg=Tema.MERAH,
                       padx=18, pady=9).pack(side="right")
        self._tampilkan()
        self._teks.focus_set()

    def _pilih(self, nilai):
        self._pilihan = nilai
        if hasattr(self, "_galat"):             # pesan galat lama tidak relevan lagi
            self._galat.configure(text="")
        for v, t in self._tombol.items():
            warna = Tema.aksen if v == nilai else Tema.CHIP
            t._normal = warna
            t._hover = campur(warna, "#ffffff", 0.18)
            t.configure(bg=warna)

    def _perbarui_hitung(self):
        n = len(self._teks.get("1.0", "end").strip())
        warna = Tema.MERAH if n > self._toko.KOMENTAR_MAKS else Tema.REDUP
        self._hitung.configure(text=f"{n}/{self._toko.KOMENTAR_MAKS}", fg=warna)

    def _selesai(self, pesan):
        messagebox.showinfo("Ulasan", pesan, parent=self)
        self._tutup()
        if self._saat_selesai:
            self._saat_selesai()

    def _kirim(self):
        ok, pesan, _ = self._toko.kirim_ulasan(self._game, self._pilihan,
                                               self._teks.get("1.0", "end"))
        if not ok:
            self._galat.configure(text=pesan)
            return
        self._selesai(pesan)

    def _hapus(self):
        if not messagebox.askyesno("Hapus ulasan", "Hapus ulasanmu untuk game ini?", parent=self):
            return
        ok, pesan = self._toko.hapus_ulasan(self._game)
        if not ok:
            self._galat.configure(text=pesan)
            return
        self._selesai(pesan)


class DialogDaftarUlasan(_DialogDasar):
    """Daftar semua ulasan pengguna untuk satu game (hanya baca)."""

    def __init__(self, app, game, induk=None):
        super().__init__(app, induk, f"Ulasan \u2014 {game.get_nama_produk()}")
        atas = tk.Frame(self, bg=Tema.BG, padx=24, pady=18)
        atas.pack(fill="x")
        tk.Label(atas, text=game.get_nama_produk(), fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 15, "bold")).pack(anchor="w")
        tk.Label(atas, text=game.teks_ulasan(), fg=Tema.REDUP, bg=Tema.BG,
                 font=(Tema.FONT, 10)).pack(anchor="w", pady=(2, 0))

        daftar = ScrollFrame(self, bg=Tema.PANEL)
        daftar.pack(fill="both", expand=True)
        daftar.canvas.configure(width=520, height=340)
        ulasan = game.daftar_ulasan()
        if not ulasan:
            tk.Label(daftar.isi, text="Belum ada ulasan dari pengguna.\nJadilah yang pertama "
                                      "setelah memiliki game ini.", fg=Tema.REDUP, bg=Tema.PANEL,
                     justify="left", font=(Tema.FONT, 10)).pack(anchor="w", padx=24, pady=24)
        saya = app.toko.get_customer().get_id_user()
        for u in ulasan:
            kartu = tk.Frame(daftar.isi, bg=Tema.KARTU, highlightthickness=1,
                             highlightbackground=Tema.GARIS)
            kartu.pack(fill="x", padx=16, pady=(10, 0))
            kepala = tk.Frame(kartu, bg=Tema.KARTU)
            kepala.pack(fill="x", padx=14, pady=(10, 2))
            nama = u.get_nama_customer() + ("  (kamu)" if u.get_id_customer() == saya else "")
            tk.Label(kepala, text=nama, fg=Tema.TEKS, bg=Tema.KARTU,
                     font=(Tema.FONT, 10, "bold")).pack(side="left")
            tk.Label(kepala, text=u.teks_tanggal(), fg=Tema.REDUP, bg=Tema.KARTU,
                     font=(Tema.FONT, 9)).pack(side="right")
            tampilkan_rekomendasi(kartu, Tema.KARTU, u.get_rekomendasi()).pack(
                anchor="w", padx=14)
            tk.Label(kartu, text=u.get_komentar(), fg=Tema.TEKS, bg=Tema.KARTU, justify="left",
                     wraplength=470, font=(Tema.FONT, 10)).pack(anchor="w", padx=14, pady=(4, 12))
        tk.Frame(daftar.isi, bg=Tema.PANEL, height=14).pack()

        bawah = tk.Frame(self, bg=Tema.BG, padx=24, pady=12)
        bawah.pack(fill="x")
        TombolFlat(bawah, "Tutup", self._tutup, bg=Tema.CHIP, padx=22, pady=8).pack(side="right")
        self._tampilkan()
