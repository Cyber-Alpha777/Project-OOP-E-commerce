"""
BestDeal - Aplikasi Desktop Toko Game (tema putih-orange) berbasis Tkinter, rasio 16:9.

Alur aplikasi
-------------
Pengunjung  : LandingPage (beranda sebelum login) -> LoginPage / DaftarPage
Member      : HomePage (toko), LibraryPage, AkunPage, SettingPage  (+ tombol Keluar)

Penerapan 4 pilar OOP
---------------------
1. ENCAPSULATION : atribut private (__x) / protected (_x) + getter/setter dengan validasi
                   (Customer.__saldo, Produk.__harga, Pengaturan.__aksen, dst).
2. INHERITANCE   : User -> Customer, Seller | Produk -> Game, DLC, Bundle
                   Pembayaran -> PembayaranSaldo, PembayaranQRIS, PembayaranKartu
                   Halaman -> LandingPage, LoginPage, DaftarPage,
                              HomePage, LibraryPage, AkunPage, SettingPage
3. POLYMORPHISM  : method yang sama, perilaku beda di tiap subclass:
                   tampilkan_profil(), harga_akhir(), bisa_dibeli_oleh(), berikan_ke(),
                   tarif_admin(), proses(), bangun()
4. ABSTRACTION   : User, Produk, Pembayaran, Halaman = abstract class (ABC) dengan
                   @abstractmethod; TokoGame = facade yang menyembunyikan alur
                   Pesanan -> Pembayaran -> Pengiriman dari GUI.
"""
