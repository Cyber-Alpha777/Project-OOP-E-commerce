"""Warna, font, dan aksen tema aplikasi."""


class Tema:
    BG = "#ffffff"
    NAV = "#ffffff"
    PANEL = "#fff4ea"
    PANEL2 = "#fff8f2"
    KARTU = "#ffffff"
    KARTU_HOVER = "#fff3e8"
    CHIP = "#f6f1ec"
    GARIS = "#efe6dd"
    TEKS = "#1c1410"
    REDUP = "#6b5d52"
    NONAKTIF = "#a8998c"
    HIJAU = "#1a8f4a"
    MERAH = "#d92d20"
    DISKON_BG = "#ff7a1a"
    DISKON_FG = "#1c1410"
    AKSEN_TEKS = "#c2410c"
    FONT = "Segoe UI"
    AKSEN = {"Oranye": "#ff7a1a", "Biru": "#2f8cff", "Hijau": "#1db954", "Ungu": "#8b5cf6"}
    aksen = "#ff7a1a"

    @classmethod
    def terapkan_aksen(cls, nama):
        if nama in cls.AKSEN:
            cls.aksen = cls.AKSEN[nama]
            return True
        return False
