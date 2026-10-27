"""Domain 3c : Pengiriman (kunci lisensi produk digital)."""

import random
import string


class Pengiriman:
    """Untuk produk digital: 'pengiriman' = kirim kunci lisensi ke email customer."""
    nama_platform = "BestDeal"
    jumlah_pengiriman = 0

    def __init__(self, id_pengiriman, pesanan, nomor_resi, jasa_ekspedisi, biaya_kirim,
                 estimasi_sampai):
        self.__id_pengiriman = id_pengiriman
        self.__pesanan = pesanan
        self.__nomor_resi = nomor_resi
        self.__alamat_tujuan = pesanan.get_customer().get_email()
        self.__jasa_ekspedisi = jasa_ekspedisi
        self.__status_pengiriman = "Sedang Diproses"
        self.__biaya_kirim = biaya_kirim
        self.__estimasi_sampai = estimasi_sampai
        Pengiriman.jumlah_pengiriman += 1

    def get_kunci(self):
        return self.__nomor_resi

    def get_status(self):
        return self.__status_pengiriman

    def get_alamat_tujuan(self):
        return self.__alamat_tujuan

    def get_jasa(self):
        return self.__jasa_ekspedisi

    def get_biaya(self):
        return self.__biaya_kirim

    def get_estimasi(self):
        return self.__estimasi_sampai

    def ubah_status(self, status_baru):
        self.__status_pengiriman = status_baru

    @staticmethod
    def buat_kunci():
        def blok():
            return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return "-".join(blok() for _ in range(3))
