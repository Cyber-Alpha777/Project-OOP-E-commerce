# BestDeal - Toko Game (Proyek PBO)

Aplikasi desktop toko game berbasis **Tkinter** (tema putih-orange) dengan penerapan 4 pilar OOP.

## Cara menjalankan

```bash
pip install -r requirements.txt
python main.py
```

Butuh Python 3.9+ dan Pillow. Akun demo: `arya@email.com` / `password123`
(atau daftar akun baru dari halaman Daftar).

## Alur aplikasi

| Tahap | Halaman |
|-------|---------|
| Sebelum login | `LandingPage` (beranda) -> `LoginPage` / `DaftarPage` |
| Sesudah login | `HomePage` (toko), `LibraryPage`, `AkunPage`, `SettingPage`, tombol **Keluar** di navbar |

Halaman **Daftar** punya pilihan *Pembeli* atau *Seller*. Akun seller baru langsung masuk ke
dashboard seller. Customer bisa menulis **ulasan** (rekomendasi ya/tidak + komentar) untuk game
yang sudah ada di Library lewat halaman Library; ulasan semua pengguna bisa dibaca dari Library
dan dari dialog detail game di Toko.

Akun, ulasan, dan riwayat pesanan hanya disimpan di memori selama aplikasi berjalan.

Aplikasi dibuka dalam mode layar penuh: **F11** untuk toggle, **Esc** untuk keluar. Di navbar, menu **TOKO** dan **LIBRARY** bisa diklik (AKUN & SETTING masih tampilan saja); klik game di panel *Lanjut main* untuk langsung membukanya di Library.

## Struktur folder

```
Project-OOP-E-commerce/
├── main.py                      # titik masuk
├── requirements.txt
├── Gambar/                      # cover game
└── bestdeal/
    ├── config.py                # path proyek + resolve_gambar()
    ├── utils.py                 # rupiah(), campur()
    ├── models/                  # lapisan DOMAIN (tanpa Tkinter)
    │   ├── user.py              #   User (abstract), Customer, Seller
    │   ├── produk.py            #   Produk (abstract), Game, DLC, Bundle
    │   ├── pesanan.py           #   Pesanan, DetailPesanan
    │   ├── ulasan.py            #   Ulasan (rekomendasi + komentar customer)
    │   ├── pembayaran.py        #   Pembayaran (abstract), Saldo, QRIS, Kartu
    │   └── pengiriman.py        #   Pengiriman (kunci lisensi)
    ├── services/                # lapisan LOGIKA APLIKASI (tanpa Tkinter)
    │   ├── toko.py              #   TokoGame (facade: pesan -> bayar -> kirim)
    │   ├── auth.py              #   AuthService (daftar, masuk, keluar)
    │   └── pengaturan.py        #   Pengaturan
    ├── data/
    │   └── katalog_demo.py      # katalog game + akun demo
    └── ui/                      # lapisan TAMPILAN (Tkinter)
        ├── app.py               #   AplikasiBestDeal (jendela + navigasi)
        ├── tema.py              #   warna, font, aksen
        ├── widgets.py           #   TombolFlat, ScrollFrame, KartuProduk, ...
        ├── navbar.py            #   NavBar (member), NavBarTamu (sebelum login)
        ├── dialogs.py           #   DialogProduk
        ├── dialog_ulasan.py     #   DialogTulisUlasan, DialogDaftarUlasan
        └── pages/
            ├── base.py          #   Halaman (abstract)
            ├── landing_page.py  #   beranda sebelum login
            ├── auth_pages.py    #   LoginPage, DaftarPage
            ├── home_page.py     #   toko
            ├── library_page.py
            ├── akun_page.py
            └── setting_page.py
```

Aturan ketergantungan: `ui` -> `services` -> `models`. `models` dan `services` tidak
meng-import Tkinter, jadi bisa diuji tanpa GUI.
