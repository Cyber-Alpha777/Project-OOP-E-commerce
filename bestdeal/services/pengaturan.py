"""Pengaturan aplikasi (Encapsulation: atribut private + getter/setter)."""


class Pengaturan:
    def __init__(self):
        self.__autoplay = True
        self.__konfirmasi = True
        self.__layar_penuh = True
        self.__aksen = "Oranye"

    def get_autoplay(self):
        return self.__autoplay

    def set_autoplay(self, v):
        self.__autoplay = bool(v)

    def get_konfirmasi(self):
        return self.__konfirmasi

    def set_konfirmasi(self, v):
        self.__konfirmasi = bool(v)

    def get_layar_penuh(self):
        return self.__layar_penuh

    def set_layar_penuh(self, v):
        self.__layar_penuh = bool(v)

    def get_aksen(self):
        return self.__aksen

    def set_aksen(self, nama):
        """Simpan nama aksen. Penerapan warnanya ada di lapisan UI (Tema)."""
        if isinstance(nama, str) and nama.strip():
            self.__aksen = nama
