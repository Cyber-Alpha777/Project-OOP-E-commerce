"""Domain 3b : Pembayaran (abstract) dan turunannya."""

from abc import ABC, abstractmethod

from bestdeal.utils import rupiah


class Pembayaran(ABC):
    """Abstract: tiap metode bayar punya biaya admin & cara proses sendiri."""

    def __init__(self, id_pembayaran, pesanan, metode_pembayaran):
        self.__id_pembayaran = id_pembayaran
        self.__pesanan = pesanan
        self._metode_pembayaran = metode_pembayaran
        self._status_pembayaran = "Belum Dibayar"
        self.__jumlah_bayar = 0

    def get_pesanan(self):
        return self.__pesanan

    def get_status(self):
        return self._status_pembayaran

    def get_metode(self):
        return self._metode_pembayaran

    def get_jumlah_bayar(self):
        return self.__jumlah_bayar

    @classmethod
    @abstractmethod
    def tarif_admin(cls, subtotal):
        ...

    @abstractmethod
    def proses(self):
        """Return (bool, pesan)."""

    def biaya_admin(self):
        return self.tarif_admin(self.__pesanan.hitung_total())

    def total_tagihan(self):
        return self.__pesanan.hitung_total() + self.biaya_admin()

    def _lunas(self, jumlah):
        self.__jumlah_bayar = jumlah
        self._status_pembayaran = "Lunas"


class PembayaranSaldo(Pembayaran):
    @classmethod
    def tarif_admin(cls, subtotal):
        return 0

    def proses(self):
        customer = self.get_pesanan().get_customer()
        total = self.total_tagihan()
        if customer.kurangi_saldo(total):
            self._lunas(total)
            return True, "Pembayaran saldo berhasil."
        return False, f"Saldo tidak cukup. Kurang {rupiah(total - customer.get_saldo())}."


class PembayaranQRIS(Pembayaran):
    @classmethod
    def tarif_admin(cls, subtotal):
        return int(round(subtotal * 0.007))

    def proses(self):
        self._lunas(self.total_tagihan())
        return True, "Pembayaran QRIS berhasil."


class PembayaranKartu(Pembayaran):
    @classmethod
    def tarif_admin(cls, subtotal):
        return int(round(subtotal * 0.025))

    def proses(self):
        self._lunas(self.total_tagihan())
        return True, "Pembayaran kartu kredit berhasil."
