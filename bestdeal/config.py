"""Konfigurasi path proyek."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent     # folder yang berisi main.py
GAMBAR_DIR = ROOT_DIR / "Gambar"


def resolve_gambar(path_gambar):
    """Ubah path gambar relatif (mis. "Gambar/cs2.png") menjadi path absolut.

    Tahan terhadap perbedaan pemisah (\\ atau /) dan huruf besar/kecil nama file,
    supaya proyek juga jalan di Linux/macOS, bukan hanya Windows.
    """
    p = Path(str(path_gambar).replace("\\", "/"))
    if not p.is_absolute():
        p = ROOT_DIR / p
    if p.exists() or not p.parent.is_dir():
        return p
    for f in p.parent.iterdir():
        if f.name.lower() == p.name.lower():
            return f
    return p
