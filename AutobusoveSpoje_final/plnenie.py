import sqlite3 as sql
import hashlib
from datetime import datetime, timedelta


databaza = sql.connect("databaza.db")
cursor = databaza.cursor()


# ---------- ZMAZANIE ----------
cursor.execute("DROP TABLE IF EXISTS rezervacie")
cursor.execute("DROP TABLE IF EXISTS prichody")
cursor.execute("DROP TABLE IF EXISTS odchody")
cursor.execute("DROP TABLE IF EXISTS linky")
cursor.execute("DROP TABLE IF EXISTS uzivatelia")


# ---------- VYTVORENIE TABULIEK ----------
cursor.execute("""
CREATE TABLE uzivatelia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meno TEXT UNIQUE NOT NULL,
    heslo TEXT NOT NULL,
    admin INTEGER NOT NULL CHECK(admin IN (0, 1))
)
""")

cursor.execute("""
CREATE TABLE linky (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cislo_linky TEXT NOT NULL UNIQUE,
    ciel TEXT NOT NULL,
    nazov TEXT
)
""")

cursor.execute("""
CREATE TABLE odchody (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_linky INTEGER NOT NULL,
    datum TEXT NOT NULL,
    cas TEXT NOT NULL,
    volne_miesta INTEGER NOT NULL,
    FOREIGN KEY (id_linky) REFERENCES linky(id)
)
""")

cursor.execute("""
CREATE TABLE prichody (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_linky INTEGER NOT NULL,
    datum TEXT NOT NULL,
    cas TEXT NOT NULL,
    volne_miesta INTEGER NOT NULL,
    FOREIGN KEY (id_linky) REFERENCES linky(id)
)
""")

cursor.execute("""
CREATE TABLE rezervacie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pouzivatel INTEGER NOT NULL,
    id_odchodu INTEGER NOT NULL,
    cas_rezervacie TEXT NOT NULL,
    FOREIGN KEY (id_pouzivatel) REFERENCES uzivatelia(id),
    FOREIGN KEY (id_odchodu) REFERENCES odchody(id)
)
""")


def zahashuj_heslo(heslo):
    return hashlib.sha256(heslo.encode()).hexdigest()


def vygeneruj_odchody(cislo_linky, interval_hodin, kapacita=50):
    cursor.execute("SELECT id FROM linky WHERE cislo_linky = ?", (cislo_linky,))
    vysledok = cursor.fetchone()

    if vysledok is None:
        print("Linka s daným číslom neexistuje.")
        return

    id_linky = vysledok[0]

    datum_start = datetime.today()
    dni = 14
    interval = timedelta(minutes=int(interval_hodin * 60))

    cas_zaciatok = datetime.strptime("05:00", "%H:%M")
    cas_koniec = datetime.strptime("23:00", "%H:%M")

    odchody = []

    for d in range(dni):
        datum = (datum_start + timedelta(days=d)).strftime("%Y-%m-%d")
        cas = cas_zaciatok
        while cas <= cas_koniec:
            odchody.append((id_linky, datum, cas.strftime("%H:%M"), kapacita))
            cas += interval

    cursor.executemany(
        "INSERT INTO odchody (id_linky, datum, cas, volne_miesta) VALUES (?, ?, ?, ?)",
        odchody
    )


def vygeneruj_prichody(cislo_linky, interval_hodin, kapacita=50):
    cursor.execute("SELECT id FROM linky WHERE cislo_linky = ?", (cislo_linky,))
    vysledok = cursor.fetchone()

    if vysledok is None:
        print("Linka s daným číslom neexistuje.")
        return

    id_linky = vysledok[0]

    datum_start = datetime.today()
    dni = 14
    interval = timedelta(minutes=int(interval_hodin * 60))

    cas_zaciatok = datetime.strptime("06:00", "%H:%M")
    cas_koniec = datetime.strptime("01:00", "%H:%M") + timedelta(days=1)  # pridanie dna

    prichody = []

    for d in range(dni):
        datum = datum_start + timedelta(days=d)
        cas = cas_zaciatok

        while cas <= cas_koniec:
            aktualny_datum = datum
            if cas.hour < 5:
                aktualny_datum += timedelta(days=1)

            prichody.append((
                id_linky,
                aktualny_datum.strftime("%Y-%m-%d"),
                cas.strftime("%H:%M"),
                kapacita
            ))
            cas += interval

    cursor.executemany(
        "INSERT INTO prichody (id_linky, datum, cas, volne_miesta) VALUES (?, ?, ?, ?)",
        prichody
    )


# ---------- PLNENIE ----------

pouzivatelia = [
    ("admin", zahashuj_heslo("admin"), 1),
    ("user", zahashuj_heslo("user"), 0),
    ("Adrian", zahashuj_heslo("Adrian"), 0)
]

cursor.executemany(
    "INSERT INTO uzivatelia (meno,heslo,admin) VALUES(?,?,?)",
    pouzivatelia
)


linky = [
    ("50", "Košice", "Bratislava ↔ Košice"),
    ("80", "Trnava", "Bratislava ↔ Trnava"),
    ("120", "Žilina", "Bratislava ↔ Žilina"),
    ("150", "Banská Bystrica", "Bratislava ↔ BB"),
    ("200", "Nitra", "Bratislava ↔ Nitra")
]

cursor.executemany(
    "INSERT INTO linky (cislo_linky, ciel, nazov) VALUES (?, ?, ?)",
    linky
)


vygeneruj_odchody(50, 2)
vygeneruj_odchody(80, 1)
vygeneruj_odchody(120, 3)
vygeneruj_odchody(150, 4)
vygeneruj_odchody(200, 1.5)

vygeneruj_prichody(50, 2)
vygeneruj_prichody(80, 1)
vygeneruj_prichody(120, 3)
vygeneruj_prichody(150, 4)
vygeneruj_prichody(200, 1.5)

# ---------- REZERVACIE----------
def vygeneruj_rezervacie(pocet_na_uzivatela=2):
    cursor.execute("SELECT id FROM uzivatelia")
    uzivatelia_ids = [row[0] for row in cursor.fetchall()]

    teraz = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute("""
        SELECT id, volne_miesta FROM odchody
        WHERE datetime(datum || ' ' || cas) >= datetime(?)
        ORDER BY datum, cas
    """, (teraz,))
    vsetky_odchody = cursor.fetchall()

    if not vsetky_odchody:
        print("Žiadne odchody na vytvorenie rezervácií.")
        return

    index = 0
    for id_pouzivatel in uzivatelia_ids:
        pridane = 0
        pokusy = 0
        while pridane < pocet_na_uzivatela and pokusy < len(vsetky_odchody):
            id_odchodu, volne_miesta = vsetky_odchody[index % len(vsetky_odchody)]
            index += 1
            pokusy += 1

            if volne_miesta <= 0:
                continue

            cursor.execute("""
                SELECT COUNT(*) FROM rezervacie
                WHERE id_odchodu = ? AND id_pouzivatel = ?
            """, (id_odchodu, id_pouzivatel))
            if cursor.fetchone()[0] > 0:
                continue

            cursor.execute("""
                INSERT INTO rezervacie (id_pouzivatel, id_odchodu, cas_rezervacie)
                VALUES (?, ?, datetime('now'))
            """, (id_pouzivatel, id_odchodu))

            cursor.execute("""
                UPDATE odchody SET volne_miesta = volne_miesta - 1 WHERE id = ?
            """, (id_odchodu,))

            pridane += 1


vygeneruj_rezervacie(2)


databaza.commit()
databaza.close()

print("Ide to")