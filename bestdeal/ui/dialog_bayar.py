"""Dialog pembayaran: tampilkan kode QRIS atau virtual account bank (BCA, Mandiri, BNI).

Dialog hanya mengatur tampilan + hitung mundur. Transaksi sebenarnya dikerjakan lewat callback
`saat_bayar` (mis. TokoGame.beli atau DompetService.topup), jadi aturan bisnis tidak berubah.
"""

import tkinter as tk
from tkinter import messagebox

from bestdeal import qr
from bestdeal.models.bank import DAFTAR_BANK, Bank
from bestdeal.models.tagihan import Tagihan, TagihanQRIS, TagihanVA
from bestdeal.ui.hias import (BilahProgres, kotak_bulat, lencana_bank, nomor_langkah,
                              pemisah)
from bestdeal.ui.tema import Tema
from bestdeal.ui.widgets import TombolFlat
from bestdeal.utils import rupiah

LEBAR_DIALOG = 700


def format_waktu(detik):
    return f"{detik // 60:02d}:{detik % 60:02d}"


def perlu_halaman_bayar(nama_metode):
    """Hanya QRIS dan Transfer Bank yang memakai halaman instruksi pembayaran."""
    return nama_metode in ("QRIS", "Transfer Bank")


class DialogBayar(tk.Toplevel):
    """saat_bayar(tagihan) -> (ok, pesan);  saat_selesai(pesan) dipanggil setelah dialog tertutup."""

    def __init__(self, app, induk, judul, nama_metode, kelas, nominal, label_nominal, awalan,
                 saat_bayar, saat_selesai):
        super().__init__(induk, bg=Tema.BG)
        self._app, self._induk = app, induk
        self._nama_metode, self._kelas, self._nominal = nama_metode, kelas, nominal
        self._label_nominal, self._awalan = label_nominal, awalan
        self._saat_bayar, self._saat_selesai = saat_bayar, saat_selesai
        self._mode_bank = nama_metode == "Transfer Bank"
        self._admin = kelas.tarif_admin(nominal)
        self._bank = None
        self._cache = {}                # kunci (nama bank / "qris") -> Tagihan
        self._tagihan = None
        self._after_tik = None
        self._after_salin = None
        self._chip_bank = {}

        self.title("Pembayaran")
        self.resizable(False, False)
        self.transient(induk)
        self.protocol("WM_DELETE_WINDOW", self._batal)

        self._susun_kepala(judul)
        if self._mode_bank:
            self._susun_pilih_bank()
        self._badan = tk.Frame(self, bg=Tema.BG)
        self._badan.pack(fill="both", expand=True, padx=24, pady=(14, 0))
        self._badan.columnconfigure(0, minsize=300)
        self._badan.columnconfigure(1, minsize=330)
        self._susun_kaki()

        if self._mode_bank:
            self._pilih_bank(list(DAFTAR_BANK.values())[0])
        else:
            self._muat()

        self._pusatkan()
        self.wait_visibility()
        self.grab_set()
        self._tik()

    # ---------- kerangka ----------
    def _susun_kepala(self, judul):
        kepala = tk.Frame(self, bg=Tema.PANEL)
        kepala.pack(fill="x")
        kiri = tk.Frame(kepala, bg=Tema.PANEL)
        kiri.pack(side="left", padx=24, pady=16)
        tk.Label(kiri, text="SELESAIKAN PEMBAYARAN", fg=Tema.AKSEN_TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 8, "bold")).pack(anchor="w")
        tk.Label(kiri, text=judul, fg=Tema.TEKS, bg=Tema.PANEL, wraplength=380, justify="left",
                 font=(Tema.FONT, 14, "bold")).pack(anchor="w", pady=(2, 0))
        kanan = tk.Frame(kepala, bg=Tema.PANEL)
        kanan.pack(side="right", padx=24, pady=16)
        tk.Label(kanan, text="Total bayar", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9)).pack(anchor="e")
        tk.Label(kanan, text=rupiah(self._nominal + self._admin), fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 20, "bold")).pack(anchor="e")
        bar = tk.Frame(self, bg=Tema.BG)
        bar.pack(fill="x", padx=24, pady=(12, 0))
        self._bar = BilahProgres(bar, LEBAR_DIALOG - 48 - 150, 8)
        self._bar.pack(side="left")
        self._lb_waktu = tk.Label(bar, text="", fg=Tema.REDUP, bg=Tema.BG, width=20,
                                  anchor="e", font=(Tema.FONT, 9, "bold"))
        self._lb_waktu.pack(side="right")

    def _susun_pilih_bank(self):
        baris = tk.Frame(self, bg=Tema.BG)
        baris.pack(fill="x", padx=24, pady=(14, 0))
        tk.Label(baris, text="Pilih bank", fg=Tema.REDUP, bg=Tema.BG,
                 font=(Tema.FONT, 9, "bold")).pack(anchor="w", pady=(0, 6))
        deret = tk.Frame(baris, bg=Tema.BG)
        deret.pack(anchor="w")
        for nama, bank in DAFTAR_BANK.items():
            c = tk.Canvas(deret, width=132, height=54, bg=Tema.BG, highlightthickness=0,
                          cursor="hand2")
            c.pack(side="left", padx=(0, 10))
            c.bind("<Button-1>", lambda e, b=bank: self._pilih_bank(b))
            self._chip_bank[nama] = (c, bank)

    def _gambar_chip(self):
        for nama, (c, bank) in self._chip_bank.items():
            c.delete("all")
            aktif = bank is self._bank
            kotak_bulat(c, 1, 1, 131, 53, r=12, fill="#fff7ef" if aktif else Tema.KARTU,
                        outline=Tema.aksen if aktif else Tema.GARIS, width=2 if aktif else 1)
            kotak_bulat(c, 9, 10, 57, 44, r=8, fill=bank.WARNA, outline="")
            c.create_text(33, 27, text=bank.NAMA.upper(), fill=bank.WARNA_TEKS,
                          font=(Tema.FONT, 10 if len(bank.NAMA) <= 3 else 8, "bold"))
            c.create_text(66, 27, text=bank.NAMA, anchor="w", fill=Tema.TEKS,
                          font=(Tema.FONT, 10, "bold"))

    def _susun_kaki(self):
        kaki = tk.Frame(self, bg=Tema.BG)
        kaki.pack(fill="x", padx=24, pady=(14, 22))
        self._btn_utama = TombolFlat(kaki, "Saya Sudah Bayar", self._utama, padx=30, pady=11)
        self._btn_utama.pack(side="left")
        TombolFlat(kaki, "Batal", self._batal, bg=Tema.CHIP, fg=Tema.TEKS, padx=22,
                   pady=11).pack(side="left", padx=10)
        tk.Label(kaki, text="Simulasi: tekan tombol setelah 'membayar'.", fg=Tema.NONAKTIF,
                 bg=Tema.BG, font=(Tema.FONT, 8)).pack(side="right")

    def _pusatkan(self):
        self.update_idletasks()
        r = self._app.root
        x = r.winfo_x() + (r.winfo_width() - self.winfo_reqwidth()) // 2
        y = r.winfo_y() + (r.winfo_height() - self.winfo_reqheight()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    # ---------- tagihan ----------
    def _baru(self):
        ref = Tagihan.buat_referensi(self._awalan)
        if self._bank is None:
            return TagihanQRIS(ref, self._nominal, self._admin)
        idc = self._app.toko.get_customer().get_id_user()
        return TagihanVA(self._bank, idc, ref, self._nominal, self._admin)

    def _kunci(self):
        return self._bank.NAMA if self._bank else "qris"

    def _pilih_bank(self, bank):
        self._bank = bank
        self._gambar_chip()
        self._muat()

    def _muat(self):
        kunci = self._kunci()
        if kunci not in self._cache:
            self._cache[kunci] = self._baru()
        self._tagihan = self._cache[kunci]
        for w in self._badan.winfo_children():
            w.destroy()
        kiri = tk.Frame(self._badan, bg=Tema.PANEL)
        kiri.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        kanan = tk.Frame(self._badan, bg=Tema.BG)
        kanan.grid(row=0, column=1, sticky="nsew")
        if self._mode_bank:
            self._gambar_va(kiri)
        else:
            self._gambar_qris(kiri)
        self._gambar_rincian(kanan)
        self._gambar_langkah(kanan)
        self._perbarui_waktu()

    # ---------- sisi kiri: QRIS / virtual account ----------
    def _gambar_qris(self, kiri):
        matriks = qr.buat_matriks(self._tagihan.kode_bayar())
        n = len(matriks)
        modul = max(3, 232 // (n + 2))
        sisi = (n + 2) * modul
        lebar, tinggi = max(sisi + 36, 280), sisi + 96
        c = tk.Canvas(kiri, width=lebar, height=tinggi, bg=Tema.PANEL, highlightthickness=0)
        c.pack(padx=10, pady=10)
        kotak_bulat(c, 2, 2, lebar - 2, tinggi - 2, r=18, fill="#ffffff", outline=Tema.GARIS)
        kotak_bulat(c, lebar / 2 - 34, 14, lebar / 2 + 34, 40, r=13, fill="#e11d48", outline="")
        c.create_text(lebar / 2, 27, text="QRIS", fill="#ffffff", font=(Tema.FONT, 11, "bold"))
        x0, y0 = (lebar - sisi) / 2, 50
        for y, baris in enumerate(matriks):
            for x, gelap in enumerate(baris):
                if gelap:
                    px, py = x0 + (x + 1) * modul, y0 + (y + 1) * modul
                    c.create_rectangle(px, py, px + modul, py + modul, fill="#111111", outline="")
        c.create_text(lebar / 2, y0 + sisi + 14, text="BESTDEAL \u2022 SIMULASI",
                      fill=Tema.REDUP, font=(Tema.FONT, 9, "bold"))
        c.create_text(lebar / 2, y0 + sisi + 32, text="Scan dengan aplikasi bank / e-wallet",
                      fill=Tema.NONAKTIF, font=(Tema.FONT, 8))

    def _gambar_va(self, kiri):
        bank = self._bank
        atas = tk.Frame(kiri, bg=Tema.PANEL)
        atas.pack(fill="x", padx=20, pady=(20, 0))
        lencana_bank(atas, bank, bg=Tema.PANEL).pack(side="left")
        nama = tk.Frame(atas, bg=Tema.PANEL)
        nama.pack(side="left", padx=12)
        tk.Label(nama, text=bank.NAMA_LENGKAP, fg=Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 11, "bold")).pack(anchor="w")
        tk.Label(nama, text="Virtual Account", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9)).pack(anchor="w")
        tk.Label(kiri, text="Nomor virtual account", fg=Tema.REDUP, bg=Tema.PANEL,
                 font=(Tema.FONT, 9)).pack(anchor="w", padx=20, pady=(22, 4))
        kotak = tk.Frame(kiri, bg="#ffffff", highlightthickness=1, highlightbackground=Tema.GARIS)
        kotak.pack(fill="x", padx=20)
        tk.Label(kotak, text=Bank.format_va(self._tagihan.kode_bayar()), fg=Tema.TEKS,
                 bg="#ffffff", font=("Consolas", 15, "bold")).pack(padx=14, pady=14)
        self._btn_salin = TombolFlat(kiri, "Salin nomor", self._salin, bg=Tema.CHIP,
                                     fg=Tema.TEKS, padx=18, pady=7,
                                     font=(Tema.FONT, 9, "bold"))
        self._btn_salin.pack(anchor="w", padx=20, pady=(10, 0))
        tk.Label(kiri, text="Atas nama BestDeal (simulasi).\nNominal harus sama persis dengan\n"
                            "total bayar agar pembayaran terdeteksi.",
                 fg=Tema.REDUP, bg=Tema.PANEL, justify="left",
                 font=(Tema.FONT, 8)).pack(anchor="w", padx=20, pady=(14, 20))

    def _salin(self):
        self.clipboard_clear()
        self.clipboard_append(self._tagihan.kode_bayar())
        self._btn_salin.configure(text="Tersalin \u2713")
        if self._after_salin:
            self.after_cancel(self._after_salin)
        self._after_salin = self.after(1500, self._reset_salin)

    def _reset_salin(self):
        self._after_salin = None
        try:
            self._btn_salin.configure(text="Salin nomor")
        except tk.TclError:
            pass

    # ---------- sisi kanan: rincian + langkah ----------
    def _gambar_rincian(self, kanan):
        tk.Label(kanan, text="Rincian pembayaran", fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 11, "bold")).pack(anchor="w")
        kartu = tk.Frame(kanan, bg=Tema.PANEL)
        kartu.pack(fill="x", pady=(8, 0))
        label_admin = f"Biaya admin ({self._kelas.label_tarif()})"
        for teks, nilai, tebal in ((self._label_nominal, rupiah(self._nominal), False),
                                   (label_admin, rupiah(self._admin), False)):
            self._baris(kartu, teks, nilai, tebal)
        pemisah(kartu).pack(fill="x", padx=16, pady=4)
        self._baris(kartu, "Total bayar", rupiah(self._nominal + self._admin), True)
        kartu.pack_configure(pady=(8, 16))

    def _baris(self, parent, teks, nilai, tebal):
        f = tk.Frame(parent, bg=Tema.PANEL)
        f.pack(fill="x", padx=16, pady=5)
        font = (Tema.FONT, 10, "bold") if tebal else (Tema.FONT, 10)
        tk.Label(f, text=teks, fg=Tema.TEKS if tebal else Tema.REDUP, bg=Tema.PANEL,
                 font=font).pack(side="left")
        tk.Label(f, text=nilai, fg=Tema.AKSEN_TEKS if tebal else Tema.TEKS, bg=Tema.PANEL,
                 font=(Tema.FONT, 11 if tebal else 10, "bold")).pack(side="right")

    def _gambar_langkah(self, kanan):
        tk.Label(kanan, text="Cara membayar", fg=Tema.TEKS, bg=Tema.BG,
                 font=(Tema.FONT, 11, "bold")).pack(anchor="w")
        for i, teks in enumerate(self._tagihan.langkah(), 1):
            f = tk.Frame(kanan, bg=Tema.BG)
            f.pack(fill="x", pady=(8, 0))
            nomor_langkah(f, i, Tema.BG).pack(side="left", anchor="n")
            tk.Label(f, text=teks, fg=Tema.TEKS, bg=Tema.BG, justify="left", wraplength=290,
                     font=(Tema.FONT, 9)).pack(side="left", padx=10, anchor="w")

    # ---------- waktu ----------
    def _tik(self):
        self._after_tik = None
        self._perbarui_waktu()
        self._after_tik = self.after(1000, self._tik)

    def _perbarui_waktu(self):
        t = self._tagihan
        if t is None:
            return
        sisa = t.sisa_detik()
        if t.kedaluwarsa():
            self._lb_waktu.configure(text="Tagihan kedaluwarsa", fg=Tema.MERAH)
            self._bar.atur(0)
            self._btn_utama.configure(text="Buat Tagihan Baru")
            return
        warna = Tema.MERAH if sisa < 60 else Tema.aksen
        self._lb_waktu.configure(text=f"Bayar dalam {format_waktu(sisa)}",
                                 fg=Tema.MERAH if sisa < 60 else Tema.REDUP)
        self._bar.atur(sisa / Tagihan.DURASI_DETIK, warna)
        self._btn_utama.configure(text="Saya Sudah Bayar")

    # ---------- aksi ----------
    def _utama(self):
        if self._tagihan.kedaluwarsa():
            self._cache.pop(self._kunci(), None)
            self._muat()
            return
        ok, pesan = self._saat_bayar(self._tagihan)
        if not ok:
            messagebox.showwarning("Pembayaran gagal", pesan, parent=self)
            return
        self._tagihan.tandai_lunas()
        self._tutup()
        self._saat_selesai(pesan)

    def _batal(self):
        self._tutup()

    def _tutup(self):
        for nama in ("_after_tik", "_after_salin"):
            id_after = getattr(self, nama)
            if id_after:
                self.after_cancel(id_after)
                setattr(self, nama, None)
        induk = self._induk
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()
        try:
            induk.grab_set()
        except tk.TclError:
            pass

    def destroy(self):
        for nama in ("_after_tik", "_after_salin"):
            id_after = getattr(self, nama, None)
            if id_after:
                try:
                    self.after_cancel(id_after)
                except tk.TclError:
                    pass
        super().destroy()
