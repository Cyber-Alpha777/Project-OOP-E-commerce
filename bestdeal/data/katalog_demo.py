"""Data demo toko: katalog produk + akun demo."""

from bestdeal.models.produk import Bundle, DLC, Game
from bestdeal.models.user import Customer, Seller


DEMO_EMAIL = "arya@email.com"
DEMO_PASSWORD = "password123"


def buat_katalog_demo():
    """Bangun katalog demo. Return (katalog, unggulan, library_awal)."""
    Valve = Seller("S001", "Valve", "hi@valve.id", "081200000001", "USA", 4.8)
    ParadoxInteractive = Seller("S002", "Paradox Interactive", "hi@ParadoxInteractive.id", "081200000002", "Stockholm", 4.6)
    lantern = Seller("S003", "Lantern Works", "hi@lantern.id", "081200000003", "Surabaya", 4.6)
    ea = Seller("S004", "Ea", "hi@ea.id", "081200000004", "USA", 4.9)
    resmi = Seller("S000", "BestDeal Official", "cs@bestdeal.id", "081200000000", "Jakarta", 5.0)
    bandai = Seller("S005", "Bandai Namco", "cs@bandainamco.id", "081200000005", "Tokyo", 4.7)
    cdpr = Seller("S006", "CD PROJEKT RED", "cs@cdprojektred.id", "081200000006", "Warsaw", 4.5)
    sega = Seller("S007", "SEGA", "hi@sega.id", "081200000007", "Tokyo", 4.6)
    xbox = Seller("S008", "Xbox Game Studios", "hi@xboxgamestudios.id", "081200000008", "Redmond", 4.8)
    capcom = Seller("S009", "Capcom", "hi@capcom.id", "081200000009", "USA", 4.7)
    rockstar = Seller("S010", "Rockstar Games", "hi@rockstargames.id", "081200000005", "USA", 4.7)
    crystaldynamic = Seller("S011", "Crystal dynamic", "hi@crystaldynamic.id", "081200000006", "USA", 4.4)
    ConcernedApe = Seller("S012", "ConcernedApe", "hi@concernedape.id", "081200000006", "USA", 4.4)

    g1 = Game("G001", "Counter Strike 2", 549000, "Tembak", Valve,
           "Tembak-menembak taktis legendaris. Bergabunglah dalam pertempuran tim dengan mekanik smoke dinamis dan sub-tick rate presisi",
            diskon=25, rilis="2025", ulasan=94,gambar="Gambar/CS2.png")
    g2 = Game("G002", "Need for Speed Unbound", 399000, "Balapan", ea,
           "Balapan liar jalanan dengan gaya seni grafiti anime yang unik, kustomisasi mobil mendalam, dan kejar-kejaran polisi yang menegangkan.",
            diskon=75, rilis="2026", ulasan=88,gambar="Gambar/nfs_onbound.png")
    g3 = Game("G003", "Age of Empires IV", 299000, "Strategi", ParadoxInteractive,
           "Pimpin peradaban bersejarah menuju kejayaan melalui perang abad pertengahan, diplomasi, dan manajemen kerajaan.",
            rilis="2024", ulasan=91,gambar="Gambar/aoe4.png")
    g4 = Game("G004", "Resident Evil 4", 249000, "Horor", capcom,
           "Misi penyelamatan menegangkan di desa terpencil yang terinfeksi wabah parasit mematikan.",
            diskon=50, rilis="2025", ulasan=86,gambar="Gambar/ResidentEvil4.png")
    g5 = Game("G005", "Stardew Valley", 115000, "Indie", ConcernedApe,
            "Warisi kebun tua kakekmu, pelajari cara hidup dari tanah, dan ubah ladang terbengkalai menjadi rumah yang makmur.",
            diskon=20, rilis="2016", ulasan=98, gambar="Gambar/stardew_valley.png")
    g6 = Game("G006", "Red Dead Redemption 2", 599000, "Aksi", rockstar,
           "Arthur Morgan and the Van der Linde Gang are outlaws on the run. With federal agents and bounty hunters massing on their heels, the gang must rob, steal, and fight their way across the rugged heartland in order to survive.",
           diskon=30, rilis="December 5, 2019", ulasan=90,gambar="Gambar/RDR2.png")
    g7 = Game("G007", "Rise of the Tomb Raider", 459000, "Petualangan", crystaldynamic,
           "Rise of the Tomb Raider: 20 Year Celebration includes the base game and Season Pass featuring all-new content. Explore Croft Manor in the new “Blood Ties” story, then defend it against a zombie invasion in Lara Nightmare.",
           diskon=30, rilis="January 28, 2016", ulasan=84,gambar="Gambar/TombRaider.png")
    g8 = Game("G008", "Total War Three Kingdoms", 349000, "Strategi", sega,
           "Unite Ancient China under your rule through a thrilling blend of turn-based empire building and real-time battles. Use the Guanxi System and diplomacy to forge alliances, and build powerful armies with hundreds of unique infantry, cavalry and war machine units.",
            diskon=20, rilis="23 May, 2019", ulasan=89, gambar="Gambar/TotalWar.png")
    g9 = Game("G009", "Forza Horizon 6", 879000, "Balapan", xbox,
           "Discover the breathtaking landscapes of Japan in over 550 real-world cars and become a racing Legend in Forza Horizon's biggest open world driving adventure yet.",
            rilis="19 May, 2026", ulasan=82,gambar="Gambar/Forza.png")
    g10 = Game("G010", "Resident Evil Requiem", 819000, "Horor", capcom,
            "Lagu duka bagi yang telah tiada. Mimpi buruk bagi yang masih hidup. Bersiaplah meloloskan diri dari maut dalam pengalaman yang memacu jantung dan membuat Anda gemetar hingga ke tulang.",
             diskon=35, rilis="27 Feb, 2026", ulasan=87,gambar="Gambar/ResidentEvil.png")
    g11 = Game("G011", "Elden Ring", 599000, "RPG", bandai,
            "RPG dunia terbuka dari FromSoftware dan George R.R. Martin. "
            "Jelajahi Lands Between sebagai Tarnished dan jadilah Elden Lord.",
            diskon=30, rilis="2022", ulasan=92, gambar="Gambar/EldenRing.png")
    g12 = Game("G012", "Cyberpunk 2077", 549000, "Aksi", cdpr,
            "RPG aksi dunia terbuka di Night City. Jadi V, tentara bayaran."
            "yang mengejar implan yang menjanjikan keabadian.",
            diskon=50, rilis="2020", ulasan=82, gambar="Gambar/Cyberpunk.png")
    g13 = Game("G013", "Hollow KnIght", 130000, "Indie", xbox,
            "Tentukan jalanmu sendiri di Hollow Knight! Sebuah petualangan aksi epik melintasi kerajaan serangga dan pahlawan yang telah runtuh dan luas. Jelajahi gua-gua yang berliku, lawan makhluk-makhluk yang tercemar, dan jalin persahabatan dengan serangga-serangga unik—semuanya dalam gaya 2D klasik yang digambar dengan tangan.",
            rilis="2017", ulasan=92, gambar="Gambar/HollowKnight.png")
    g14 = Game("G014", "Uncharted 4", 720000, "Petualangan", cdpr,
            "Bermainlah sebagai Nathan Drake dan Chloe Frazer dalam petualangan mandiri mereka masing-masing saat mereka menghadapi masa lalu dan mengukir warisan mereka sendiri.",
            diskon=50, rilis="2022", ulasan=120, gambar="Gambar/Uncharted4.png")
    g15 = Game("G015", "DOOM The Dark Age", 549000, "Tembak", cdpr,
            "Pemain akan mengenakan sepatu bot berlumuran darah milik DOOM Slayer dalam perang abad pertengahan yang kelam dan mengerikan melawan Neraka—sebuah pengalaman yang belum pernah ada sebelumnya.",
            diskon=20, rilis="2025", ulasan=93, gambar="Gambar/Doom.png")
    g16 = Game("G016", "Minecraft", 200000, "Petualangan", cdpr,
            "Pemain akan mengenakan sepatu bot berlumuran darah milik DOOM Slayer dalam perang abad pertengahan yang kelam dan mengerikan melawan Neraka—sebuah pengalaman yang belum pernah ada sebelumnya.",
            diskon=20, rilis="2025", ulasan=93, gambar="Gambar/Doom.png")
         

    d1 = DLC("D001", "Elden Ring: Shadow of the Erdtree", 279000, g11,
             "Ekspansi resmi: masuki Realm of Shadow, hadapi bos baru, "
             "dan temukan senjata serta kelas baru.",
             gambar="Gambar/ShadowOfTheErdtree.png")
    d2 = DLC("D002", "Cyberpunk 2077: Phantom Liberty", 369000, g12,
             "Spionase thriller di distrik Dogtown. Misi baru, "
             "senjata baru, dan cerita bertabur bintang.",
             gambar="Gambar/PhantomLiberty.png")
    b1 = Bundle("B001", "Paket RPG Legendaris", [g11, g12], resmi,
                "Elden Ring dan Cyberpunk 2077 dalam satu paket hemat.",
                gambar="Gambar/Elden&Cyberpunk.png")
    b2 = Bundle("B002", "Paket Aksi Dunia Terbuka", [g12, g6], resmi,
                "Cyberpunk 2077 dan Red Dead Redemption 2 dalam satu paket hemat.",
                gambar="Gambar/RDR&Cyberpunk.png")

    katalog = [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12, g13, g14, g15, g16, d1, d2, b1, b2]
    unggulan = [g2, g4, g12, g14]
    # game yang sudah dimiliki akun demo (produk, jam main)
    library_awal = [(g3, 42.5), (g5, 18.0), (g9, 7.5)]
    return katalog, unggulan, library_awal


def buat_customer_demo(library_awal):
    """Akun demo: arya@email.com / password123 (library awal sudah terisi)."""
    customer = Customer("C001", "Arya", DEMO_PASSWORD, DEMO_EMAIL,
                        "081234567890", "Surabaya", saldo=1_500_000)
    for game, jam in library_awal:
        customer.tambah_ke_library(game)
        customer.tambah_jam_main(game, jam)
    return customer
