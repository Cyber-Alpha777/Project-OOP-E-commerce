"""Pembuat kode QR sederhana tanpa library luar (byte mode, koreksi error level M, versi 1-10).

Dipakai halaman pembayaran QRIS untuk menggambar kode QR di Canvas.
Pemakaian:  matriks = buat_matriks("teks")   ->  list baris, tiap sel True = modul gelap.
"""

# versi -> (jumlah byte koreksi error per blok, [(jumlah blok, byte data per blok), ...])
_TABEL_M = {
    1: (10, [(1, 16)]),
    2: (16, [(1, 28)]),
    3: (26, [(1, 44)]),
    4: (18, [(2, 32)]),
    5: (24, [(2, 43)]),
    6: (16, [(4, 27)]),
    7: (18, [(4, 31)]),
    8: (22, [(2, 38), (2, 39)]),
    9: (22, [(3, 36), (2, 37)]),
    10: (26, [(4, 43), (1, 44)]),
}
_ALIGN = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34],
          7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]}
KAPASITAS_MAKS = 213        # byte maksimum (versi 10, level M)


# ---------- aritmetika GF(256) + Reed-Solomon ----------
def _tabel_gf():
    exp, log, x = [0] * 512, [0] * 256, 1
    for i in range(255):
        exp[i], log[x] = x, i
        x <<= 1
        if x & 0x100:
            x ^= 0x11D
    for i in range(255, 512):
        exp[i] = exp[i - 255]
    return exp, log


_EXP, _LOG = _tabel_gf()


def _kali(a, b):
    return 0 if a == 0 or b == 0 else _EXP[_LOG[a] + _LOG[b]]


def _generator(derajat):
    g = [1]
    for i in range(derajat):
        baru = [0] * (len(g) + 1)
        for j, c in enumerate(g):
            baru[j] ^= c
            baru[j + 1] ^= _kali(c, _EXP[i])
        g = baru
    return g


def _sisa_rs(data, derajat):
    g = _generator(derajat)
    sisa = [0] * derajat
    for b in data:
        faktor = b ^ sisa[0]
        sisa = sisa[1:] + [0]
        for i in range(derajat):
            sisa[i] ^= _kali(g[i + 1], faktor)
    return sisa


# ---------- pengkodean data -> codeword ----------
def _jumlah_data(versi):
    return sum(n * d for n, d in _TABEL_M[versi][1])


def _pilih_versi(panjang):
    for v in range(1, 11):
        if 4 + (8 if v < 10 else 16) + 8 * panjang <= _jumlah_data(v) * 8:
            return v
    raise ValueError(f"Teks terlalu panjang untuk kode QR (maks {KAPASITAS_MAKS} byte).")


def _kodekan(data, versi):
    bits = []

    def tambah(nilai, panjang):
        bits.extend((nilai >> i) & 1 for i in range(panjang - 1, -1, -1))

    tambah(0b0100, 4)
    tambah(len(data), 8 if versi < 10 else 16)
    for b in data:
        tambah(b, 8)
    kapasitas = _jumlah_data(versi) * 8
    tambah(0, min(4, kapasitas - len(bits)))
    while len(bits) % 8:
        bits.append(0)
    i = 0
    while len(bits) < kapasitas:
        tambah((0xEC, 0x11)[i % 2], 8)
        i += 1
    kata = [int("".join(map(str, bits[k:k + 8])), 2) for k in range(0, len(bits), 8)]

    ec_len, grup = _TABEL_M[versi]
    blok, pos = [], 0
    for n, d in grup:
        for _ in range(n):
            blok.append(kata[pos:pos + d])
            pos += d
    ec = [_sisa_rs(b, ec_len) for b in blok]
    hasil = []
    for i in range(max(len(b) for b in blok)):
        hasil.extend(b[i] for b in blok if i < len(b))
    for i in range(ec_len):
        hasil.extend(e[i] for e in ec)
    return hasil


# ---------- penggambaran matriks ----------
def _bch(nilai, generator, bit_sisa, bit_geser):
    sisa = nilai
    for _ in range(bit_geser):
        sisa = (sisa << 1) ^ ((sisa >> (bit_sisa - 1)) * generator)
    return sisa


def _mask_aktif(mask, x, y):
    return (
        (x + y) % 2 == 0, y % 2 == 0, x % 3 == 0, (x + y) % 3 == 0,
        (x // 3 + y // 2) % 2 == 0, x * y % 2 + x * y % 3 == 0,
        (x * y % 2 + x * y % 3) % 2 == 0, ((x + y) % 2 + x * y % 3) % 2 == 0,
    )[mask]


def _penalti(m):
    n = len(m)
    skor = 0
    for susun in (m, [list(k) for k in zip(*m)]):          # baris lalu kolom
        for baris in susun:
            jalan = 1
            for i in range(1, n):
                if baris[i] == baris[i - 1]:
                    jalan += 1
                else:
                    skor += 3 + (jalan - 5) if jalan >= 5 else 0
                    jalan = 1
            skor += 3 + (jalan - 5) if jalan >= 5 else 0
            teks = "".join("1" if s else "0" for s in baris)
            for pola in ("10111010000", "00001011101"):
                skor += 40 * sum(teks.startswith(pola, i) for i in range(n - 10))
    for y in range(n - 1):
        for x in range(n - 1):
            if m[y][x] == m[y][x + 1] == m[y + 1][x] == m[y + 1][x + 1]:
                skor += 3
    gelap = sum(sum(baris) for baris in m)
    total = n * n
    skor += (-(-abs(gelap * 20 - total * 10) // total) - 1) * 10
    return skor


def buat_matriks(teks):
    """Ubah teks menjadi matriks QR (list of list bool). ValueError kalau terlalu panjang."""
    data = teks.encode("utf-8")
    versi = _pilih_versi(len(data))
    kata = _kodekan(data, versi)
    n = 17 + 4 * versi
    m = [[False] * n for _ in range(n)]
    fn = [[False] * n for _ in range(n)]      # True = modul fungsi (bukan data)

    def atur(x, y, gelap):
        m[y][x] = gelap
        fn[y][x] = True

    def finder(cx, cy):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                x, y = cx + dx, cy + dy
                if 0 <= x < n and 0 <= y < n:
                    atur(x, y, max(abs(dx), abs(dy)) not in (2, 4))

    def format_bit(mask):
        data_f = (0 << 3) | mask                         # level M = 00
        bits = ((data_f << 10) | _bch(data_f, 0x537, 10, 10)) ^ 0x5412
        b = lambda i: ((bits >> i) & 1) == 1
        for i in range(6):
            atur(8, i, b(i))
        atur(8, 7, b(6))
        atur(8, 8, b(7))
        atur(7, 8, b(8))
        for i in range(9, 15):
            atur(14 - i, 8, b(i))
        for i in range(8):
            atur(n - 1 - i, 8, b(i))
        for i in range(8, 15):
            atur(8, n - 15 + i, b(i))
        atur(8, n - 8, True)                             # modul gelap tetap

    for i in range(n):                                   # garis timing
        atur(6, i, i % 2 == 0)
        atur(i, 6, i % 2 == 0)
    finder(3, 3)
    finder(n - 4, 3)
    finder(3, n - 4)
    pos = _ALIGN[versi]
    for i, cy in enumerate(pos):
        for j, cx in enumerate(pos):
            if (i == 0 and j == 0) or (i == 0 and j == len(pos) - 1) or \
                    (i == len(pos) - 1 and j == 0):
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    atur(cx + dx, cy + dy, max(abs(dx), abs(dy)) != 1)
    format_bit(0)
    if versi >= 7:
        bits = (versi << 12) | _bch(versi, 0x1F25, 12, 12)
        for i in range(18):
            gelap = ((bits >> i) & 1) == 1
            a, b = n - 11 + i % 3, i // 3
            atur(a, b, gelap)
            atur(b, a, gelap)

    # isi codeword zig-zag
    i, total_bit = 0, len(kata) * 8
    for kanan in range(n - 1, 0, -2):
        if kanan == 6:
            kanan = 5
        for vert in range(n):
            for j in range(2):
                x = kanan - j
                naik = ((kanan + 1) & 2) == 0
                y = n - 1 - vert if naik else vert
                if not fn[y][x] and i < total_bit:
                    m[y][x] = ((kata[i >> 3] >> (7 - (i & 7))) & 1) == 1
                    i += 1

    def terapkan(mask):
        for y in range(n):
            for x in range(n):
                if not fn[y][x] and _mask_aktif(mask, x, y):
                    m[y][x] = not m[y][x]

    terbaik = None
    for mask in range(8):
        terapkan(mask)
        format_bit(mask)
        skor = _penalti(m)
        if terbaik is None or skor < terbaik[0]:
            terbaik = (skor, mask)
        terapkan(mask)                                   # batalkan
    terapkan(terbaik[1])
    format_bit(terbaik[1])
    return m
