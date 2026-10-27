"""Fungsi bantu kecil yang dipakai di banyak lapisan."""


def rupiah(n):
    return "Rp" + f"{int(n):,}".replace(",", ".")


def rupiah_singkat(n):
    """Rp1,2jt / Rp350rb / Rp900 - untuk label sempit (mis. sumbu grafik)."""
    n = int(n)
    if n >= 1_000_000:
        return ("Rp" + f"{n / 1_000_000:.1f}".rstrip("0").rstrip(".") + "jt").replace(".", ",")
    if n >= 1_000:
        return f"Rp{n // 1000}rb"
    return f"Rp{n}"


def campur(a, b, t):
    """Campur dua warna hex (#rrggbb). t=0 -> a, t=1 -> b."""
    ar, ag, ab = int(a[1:3], 16), int(a[3:5], 16), int(a[5:7], 16)
    br, bg, bb = int(b[1:3], 16), int(b[3:5], 16), int(b[5:7], 16)
    return "#%02x%02x%02x" % (
        int(ar + (br - ar) * t), int(ag + (bg - ag) * t), int(ab + (bb - ab) * t))
