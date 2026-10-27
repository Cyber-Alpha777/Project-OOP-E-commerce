"""Domain 5 : CatatanPenjualan (satu baris transaksi untuk laporan seller)."""


class CatatanPenjualan:
    """Satu produk yang terjual pada satu tanggal. Hanya baca (tanpa setter)."""

    def __init__(self, tanggal, produk, nominal, id_customer):
        self.__tanggal = tanggal
        self.__produk = produk
        self.__nominal = nominal            # harga jual setelah diskon (tanpa biaya admin)
        self.__id_customer = id_customer

    def get_tanggal(self):
        return self.__tanggal

    def get_produk(self):
        return self.__produk

    def get_nominal(self):
        return self.__nominal

    def get_id_customer(self):
        return self.__id_customer

    def rincian(self):
        """[(game, nominal)] - siapa dapat berapa (paket dibagi ke game isinya)."""
        return self.__produk.rincian_pendapatan(self.__nominal)
