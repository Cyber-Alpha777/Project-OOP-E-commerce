"""Domain 5 : Mutasi dompet (catatan keluar-masuk saldo)."""

from datetime import datetime


class Mutasi:
    """Satu baris riwayat saldo. Jumlah positif = uang masuk, negatif = uang keluar."""

    def __init__(self, jenis, keterangan, jumlah, saldo_akhir, waktu=None):
        self.__jenis = jenis
        self.__keterangan = keterangan
        self.__jumlah = jumlah
        self.__saldo_akhir = saldo_akhir
        self.__waktu = waktu or datetime.now().strftime("%d-%m-%Y %H:%M")

    def get_jenis(self):
        return self.__jenis

    def get_keterangan(self):
        return self.__keterangan

    def get_jumlah(self):
        return self.__jumlah

    def get_saldo_akhir(self):
        return self.__saldo_akhir

    def get_waktu(self):
        return self.__waktu

    def masuk(self):
        return self.__jumlah > 0
