"""Domain 5 : Ulasan (review) game dari customer."""

from datetime import date


class Ulasan:
    """Satu ulasan = satu customer untuk satu game: rekomendasi (ya/tidak) + komentar."""

    def __init__(self, id_customer, nama_customer, rekomendasi, komentar, tanggal=None):
        self.__id_customer = id_customer
        self.__nama_customer = nama_customer
        self.__rekomendasi = bool(rekomendasi)
        self.__komentar = komentar.strip()
        self.__tanggal = tanggal or date.today()
        self.__diedit = False

    # ==== Getter ====
    def get_id_customer(self):
        return self.__id_customer

    def get_nama_customer(self):
        return self.__nama_customer

    def get_rekomendasi(self):
        return self.__rekomendasi

    def get_komentar(self):
        return self.__komentar

    def get_tanggal(self):
        return self.__tanggal

    def sudah_diedit(self):
        return self.__diedit

    # ==== Ubah isi ulasan (tanggal ikut diperbarui, ditandai "diedit") ====
    def ubah(self, rekomendasi, komentar):
        self.__rekomendasi = bool(rekomendasi)
        self.__komentar = komentar.strip()
        self.__tanggal = date.today()
        self.__diedit = True

    def teks_tanggal(self):
        return self.__tanggal.strftime("%d-%m-%Y") + (" (diedit)" if self.__diedit else "")
