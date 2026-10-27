"""LaporanPenjualan: buku besar penjualan bersama + agregasi statistik per seller."""

from datetime import date, timedelta

from bestdeal.models.penjualan import CatatanPenjualan


class LaporanPenjualan:
    """Satu objek dipakai bersama (shared) oleh semua sesi customer dan seller.

    TokoGame mencatat setiap pembelian ke sini; LayananSeller membacanya untuk statistik.
    Data hanya tersimpan di memori selama aplikasi berjalan.
    """

    def __init__(self):
        self.__catatan = []

    def catat(self, produk, id_customer, tanggal=None, nominal=None):
        c = CatatanPenjualan(tanggal or date.today(), produk,
                             produk.harga_akhir() if nominal is None else nominal, id_customer)
        self.__catatan.append(c)
        return c

    def get_catatan(self):
        return list(self.__catatan)

    # ---------- agregasi per seller ----------
    def _bagian_seller(self, seller):
        """Yield (catatan, game, nominal) untuk bagian penjualan milik seller ini."""
        id_seller = seller.get_id_user()
        for c in self.__catatan:
            for game, nominal in c.rincian():
                pemilik = game.get_seller()
                if pemilik is not None and pemilik.get_id_user() == id_seller:
                    yield c, game, nominal

    def statistik_produk(self, seller):
        """dict id_produk -> (unit terjual, pendapatan)."""
        hasil = {}
        for _, game, nominal in self._bagian_seller(seller):
            unit, uang = hasil.get(game.get_id_produk(), (0, 0))
            hasil[game.get_id_produk()] = (unit + 1, uang + nominal)
        return hasil

    def total(self, seller):
        """(total unit terjual, total pendapatan)."""
        unit = uang = 0
        for _, _, nominal in self._bagian_seller(seller):
            unit += 1
            uang += nominal
        return unit, uang

    def harian(self, seller, hari=14, akhir=None):
        """[(tanggal, unit, pendapatan)] untuk `hari` hari berakhir di `akhir` (default hari ini)."""
        akhir = akhir or date.today()
        awal = akhir - timedelta(days=hari - 1)
        per_hari = {awal + timedelta(days=i): [0, 0] for i in range(hari)}
        for c, _, nominal in self._bagian_seller(seller):
            if c.get_tanggal() in per_hari:
                per_hari[c.get_tanggal()][0] += 1
                per_hari[c.get_tanggal()][1] += nominal
        return [(tgl, v[0], v[1]) for tgl, v in per_hari.items()]

    def terbaru(self, seller, jumlah=8):
        """[(tanggal, game, nominal, produk_dibeli)] terbaru dulu.

        produk_dibeli berbeda dari game kalau penjualannya lewat paket.
        """
        baris = [(c.get_tanggal(), game, nominal, c.get_produk())
                 for c, game, nominal in self._bagian_seller(seller)]
        baris.reverse()                                 # catatan terakhir dulu
        baris.sort(key=lambda b: b[0], reverse=True)    # sort stabil: urut catat dipertahankan
        return baris[:jumlah]
