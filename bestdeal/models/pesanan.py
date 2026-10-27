"""Domain 3a : Pesanan dan DetailPesanan."""

from bestdeal.utils import rupiah


class DetailPesanan:
    def __init__(self, id_detail, produk, jumlah):
        self.__id_detail = id_detail
        self.__produk = produk
        self.__jumlah = jumlah
        self.__subtotal = produk.harga_akhir() * jumlah

    def get_id_detail(self):
        return self.__id_detail

    def get_produk(self):
        return self.__produk

    def get_jumlah(self):
        return self.__jumlah

    def get_subtotal(self):
        return self.__subtotal

    def set_id_detail(self, id_detail):
        self.__id_detail = id_detail

    def set_produk(self, produk):
        self.__produk = produk
        self.__subtotal = produk.harga_akhir() * self.__jumlah

    def set_jumlah(self, jumlah):
        self.__jumlah = jumlah
        self.__subtotal = self.__produk.harga_akhir() * jumlah

    def tampilkan_detail(self):
        return f"{self.__produk.get_nama_produk()} x {self.__jumlah} = {rupiah(self.__subtotal)}"


class Pesanan:
    def __init__(self, id_pesanan, customer, tanggal_pesanan):
        self.__id_pesanan = id_pesanan
        self.__customer = customer
        self.__tanggal_pesanan = tanggal_pesanan
        self.__status = "Diproses"
        self.__detail_pesanan = []

    def get_id_pesanan(self):
        return self.__id_pesanan

    def get_customer(self):
        return self.__customer

    def get_tanggal_pesanan(self):
        return self.__tanggal_pesanan

    def get_status(self):
        return self.__status

    def get_detail_pesanan(self):
        return list(self.__detail_pesanan)

    def set_id_pesanan(self, id_pesanan):
        self.__id_pesanan = id_pesanan

    def set_customer(self, customer):
        self.__customer = customer

    def set_tanggal_pesanan(self, tanggal):
        self.__tanggal_pesanan = tanggal

    def set_status(self, status):
        self.__status = status

    def tambah_produk(self, id_detail, produk, jumlah):
        if produk.kurangi_stok(jumlah):
            self.__detail_pesanan.append(DetailPesanan(id_detail, produk, jumlah))
            return True
        return False

    def hitung_total(self):
        return sum(d.get_subtotal() for d in self.__detail_pesanan)

    def get_pesanan(self):
        baris = [f"ID Pesanan : {self.__id_pesanan}",
                 f"Tanggal    : {self.__tanggal_pesanan}",
                 f"Status     : {self.__status}", "Detail:"]
        baris += ["  " + d.tampilkan_detail() for d in self.__detail_pesanan]
        baris.append(f"Total      : {rupiah(self.hitung_total())}")
        return "\n".join(baris)
