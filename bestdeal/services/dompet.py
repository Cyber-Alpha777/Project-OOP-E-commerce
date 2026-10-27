"""Dompet: top up saldo dengan pilihan metode pembayaran (simulasi, tanpa Tkinter)."""

from bestdeal.models.pembayaran import DAFTAR_METODE
from bestdeal.utils import rupiah


class DompetService:
    """Mengelola saldo satu Customer: validasi nominal, hitung biaya admin, top up, ringkasan."""
    MIN_TOPUP = 10_000
    MAKS_TOPUP = 5_000_000
    NOMINAL_CEPAT = (50_000, 100_000, 250_000, 500_000, 1_000_000)

    def __init__(self, customer):
        self.__customer = customer

    @staticmethod
    def daftar_metode():
        """Metode yang boleh dipakai top up (Saldo tidak termasuk)."""
        return {nama: kelas for nama, kelas in DAFTAR_METODE.items() if kelas.eksternal}

    @staticmethod
    def baca_nominal(teks):
        """'Rp 1.500.000' -> 1500000. Teks tanpa angka -> 0."""
        digit = "".join(ch for ch in str(teks) if ch.isdigit())
        return int(digit) if digit else 0

    def validasi(self, nominal):
        if nominal < self.MIN_TOPUP:
            return False, f"Nominal top up minimal {rupiah(self.MIN_TOPUP)}."
        if nominal > self.MAKS_TOPUP:
            return False, f"Nominal top up maksimal {rupiah(self.MAKS_TOPUP)} per transaksi."
        return True, ""

    def rincian(self, nominal, nama_metode):
        """Return (biaya_admin, total_bayar)."""
        admin = self.daftar_metode()[nama_metode].tarif_admin(nominal)
        return admin, nominal + admin

    def topup(self, nominal, nama_metode):
        """Return (ok, pesan). Pembayaran disimulasikan selalu berhasil."""
        if nama_metode not in self.daftar_metode():
            return False, "Metode pembayaran tidak tersedia."
        ok, pesan = self.validasi(nominal)
        if not ok:
            return False, pesan
        admin, total = self.rincian(nominal, nama_metode)
        ket = f"Top up via {nama_metode}" + (f" (admin {rupiah(admin)})" if admin else "")
        self.__customer.tambah_saldo(nominal, ket)
        return True, f"Top up {rupiah(nominal)} berhasil. Total dibayar {rupiah(total)}."

    def ringkasan(self):
        """Return (total_topup, total_belanja, jumlah_mutasi)."""
        mutasi = self.__customer.get_mutasi()
        masuk = sum(m.get_jumlah() for m in mutasi if m.get_jenis() == "Top Up")
        keluar = sum(-m.get_jumlah() for m in mutasi if m.get_jenis() == "Pembelian")
        return masuk, keluar, len(mutasi)
