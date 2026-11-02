"""SYMULATOR PIZZERII – realistyczny, w pełni powtarzalny świat, z którego biorą się dane.

Wszystko jest losowe, ale z ukrytymi regułami (pogoda, święta, mecze, wypłaty, promocje,
sezon, trend, dzielnice). Model prognozy musi te reguły sam odkryć.

Powtarzalność i izolacja:
* ten sam (ziarno, tydzień) => bajt w bajt te same pliki (sprawdzalne odciskiem SHA-256),
* każdy rodzaj losowości ma własny, niezależny strumień (SeedSequence) – np. zmiana liczby
  kurierów nie zmienia pogody ani zamówień, a zamówienia z danego dnia nie zależą od tego,
  jaki zakres dat generujemy,
* każde ziarno ląduje w osobnym folderze `<baza>/ziarno_<N>_<tydzień>/` z plikiem metadane.json
  – symulowane dane nigdy nie mieszają się z prawdziwymi danymi w `dane/`.

Uruchomienie z wiersza poleceń:
    python -m grafik_kurierow.generator --ziarno 42 --tydzien 2026-10-19
"""
import argparse
import hashlib
import json
import math
import os
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

WERSJA_GENERATORA = "3.1"

# identyfikatory niezależnych strumieni losowości
STRUMIEN = {"pogoda": 1, "mecze": 2, "kurierzy": 3, "prognoza_pogody": 7, "zamowienia": 100}

DNI_TYG = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nd"]

# ---------- ukryte reguły świata (prawdziwe efekty – model ich nie zna) ----------
# KROK 1 – UKRYTE REGUŁY ŚWIATA
# To jest „prawda”, której nie zna reszta programu. Wartość 0.70 = +70% zamówień, -0.25 = -25%.
# Model prognozy ma te liczby odkryć sam z danych – na końcu porównujemy jego wynik z tym słownikiem.
PRAWDZIWE_EFEKTY = {
    "deszcz (na każde 5 mm/h)": 0.30,
    "zimno (na każde 10°C poniżej 5°C)": 0.18,
    "upał (na każde 10°C powyżej 25°C)": -0.20,
    "godzina przed meczem": 0.70,
    "w trakcie meczu": -0.25,
    "po meczu": 0.35,
    "2 dni po wypłacie": 0.12,
    "promocja Wtorek 2 za 1": 0.40,
    "święto – dzień wolny": 0.35,
    "święto rodzinne": -0.60,
    "wakacje – pora lunchu": 0.15,
}
SEZON = [1.10, 1.06, 1.00, 0.95, 0.93, 0.90, 0.85, 0.87, 0.97, 1.03, 1.08, 1.12]   # sty..gru
TREND_ROCZNY = 0.25                     # +25% rocznie (nowa aplikacja, rosnąca baza klientów)

# profil bazowy: wszystkie zamówienia (dostawa + odbiór) na godzinę, dzień tygodnia × godzina 11..22
# Bazowa liczba wszystkich zamówień w godzinach 11..22 (12 liczb) dla każdego dnia tygodnia.
PROFIL = {
    "Pon": [4, 7, 8, 6, 5, 6, 10, 15, 16, 12, 7, 4],
    "Wt":  [4, 7, 8, 6, 5, 6, 10, 15, 16, 12, 7, 4],
    "Śr":  [4, 7, 8, 6, 5, 6, 11, 16, 17, 13, 8, 4],
    "Czw": [4, 7, 9, 6, 5, 7, 11, 17, 18, 14, 9, 5],
    "Pt":  [5, 8, 9, 7, 6, 9, 15, 22, 24, 20, 14, 8],
    "Sob": [6, 8, 10, 9, 8, 11, 16, 23, 25, 21, 15, 9],
    "Nd":  [7, 11, 15, 13, 11, 12, 17, 23, 22, 17, 11, 5],
}
GODZINY = list(range(11, 23))

# dzielnice fikcyjnego miasta (km od pizzerii w (0,0)): nazwa, x, y, rozrzut, waga, kiedy częściej
# x, y = środek dzielnicy w km od pizzerii (0, 0); rozrzut = jak bardzo adresy są rozsiane; waga = udział zamówień.
DZIELNICE = [
    ("Centrum",            0.4,  0.3, 0.55, 0.28, None),
    ("Osiedle Słoneczne",  2.3, -1.1, 0.50, 0.22, "wieczór"),
    ("Stare Miasto",      -1.3,  0.9, 0.40, 0.14, None),
    ("Kampus",             1.4,  2.2, 0.45, 0.13, "noc"),
    ("Strefa Przemysłowa",-2.9, -2.1, 0.60, 0.10, "lunch"),
    ("Wille Zielone",      3.8,  2.6, 0.80, 0.08, "weekend"),
    ("Nowe Bloki",        -0.8, -3.4, 0.55, 0.05, None),
]

SWIETA_2026 = {  # data: (nazwa, typ)  wolne = więcej pizzy, rodzinne = mniej
    date(2026, 1, 1): ("Nowy Rok", "wolne"), date(2026, 1, 6): ("Trzech Króli", "wolne"),
    date(2026, 4, 5): ("Wielkanoc", "rodzinne"), date(2026, 4, 6): ("Poniedziałek Wielkanocny", "wolne"),
    date(2026, 5, 1): ("Święto Pracy", "wolne"), date(2026, 5, 3): ("Święto Konstytucji 3 Maja", "wolne"),
    date(2026, 5, 24): ("Zielone Świątki", "wolne"), date(2026, 6, 4): ("Boże Ciało", "wolne"),
    date(2026, 8, 15): ("Wniebowzięcie NMP", "wolne"), date(2026, 11, 1): ("Wszystkich Świętych", "rodzinne"),
    date(2026, 11, 11): ("Narodowe Święto Niepodległości", "wolne"), date(2026, 12, 24): ("Wigilia", "rodzinne"),
    date(2026, 12, 25): ("Boże Narodzenie", "rodzinne"), date(2026, 12, 26): ("Drugi dzień świąt", "wolne"),
}
WAKACJE = (date(2026, 6, 27), date(2026, 8, 31))
PROMOCJA_OD = date(2026, 9, 1)          # "Wtorek 2 za 1"

IMIONA = ["Adam", "Bartek", "Celina", "Damian", "Ewa", "Filip", "Gosia", "Hubert", "Iga", "Jakub", "Kasia",
          "Łukasz", "Marta", "Natalia", "Oskar", "Patryk", "Roksana", "Szymon", "Tomek", "Wiktoria", "Zuzia",
          "Kacper", "Ola", "Mateusz", "Julka", "Wojtek", "Paulina", "Dawid", "Nikola", "Kuba"]
NAZWISKA = "ABCDEFGHJKLMNOPRSTWZ"


class Swiat:
    """Fikcyjna pizzeria w fikcyjnym mieście. Ten sam seed = ten sam świat."""

    def __init__(self, od=date(2026, 1, 1), do=date(2026, 12, 31), seed=2026):
        if not isinstance(seed, (int, np.integer)) or seed < 0:
            raise ValueError("Ziarno musi być nieujemną liczbą całkowitą, np. 2026")
        self.od, self.do, self.seed = od, do, int(seed)
        self._pogoda()
        self._mecze()

    # ----- pogoda godzinowa: temperatura z sezonem i dobowym cyklem, deszcz z łańcucha Markowa -----
    # KROK 2 – ZIARNO I STRUMIENIE LOSOWOŚCI
    # default_rng([ziarno, nr_strumienia, klucz]) tworzy generator liczb losowych z całej listy liczb (SeedSequence).
    # Różne listy = statystycznie niezależne ciągi. Dzięki temu np. dodanie kuriera nie zmienia pogody.
    def _strumien(self, nazwa, *klucz):
        """Niezależny generator liczb losowych dla (ziarno, rodzaj losowości, klucz)."""
        return np.random.default_rng([self.seed, STRUMIEN[nazwa], *[int(k) for k in klucz]])

    # KROK 3 – POGODA GODZINA PO GODZINIE
    # Temperatura: sinusoida roczna (min. ok. 22 stycznia, max. ok. 22 lipca) + szum AR(1), który ma „pamięć”
    # (szum[i] = 0,75 · szum[i-1] + losowe), więc ciepłe i zimne okresy trwają kilka dni.
    # Deszcz: łańcuch Markowa – po deszczowym dniu szansa na deszcz 55%, po suchym 22%.
    def _pogoda(self):
        rng = self._strumien("pogoda")
        dni = pd.date_range(self.od, self.do, freq="D")
        doy = dni.dayofyear.values
        t_dzien = 8.5 + 11.5 * np.sin(2 * np.pi * (doy - 112) / 365)
        szum = np.zeros(len(dni))
        for i in range(1, len(dni)):
            szum[i] = 0.75 * szum[i - 1] + rng.normal(0, 2.2)
        t_dzien = t_dzien + szum
        deszczowy = np.zeros(len(dni), bool)
        for i in range(1, len(dni)):
            p = 0.55 if deszczowy[i - 1] else 0.22
            deszczowy[i] = rng.random() < p
        wiersze = []
        for i, d in enumerate(dni):
            start_d = rng.integers(8, 20) if deszczowy[i] else 99
            dl = rng.integers(2, 9)
            sila = rng.gamma(1.6, 1.8) if deszczowy[i] else 0
            for h in range(0, 24):
                temp = t_dzien[i] + 4.0 * np.sin(2 * np.pi * (h - 9) / 24)
                mm = max(0.0, sila * rng.uniform(0.4, 1.3)) if start_d <= h < start_d + dl else 0.0
                wiersze.append((d.date(), h, round(temp, 1), round(mm, 1)))
        self.pogoda = pd.DataFrame(wiersze, columns=["data", "godzina", "temp_c", "deszcz_mm"])
        self._pog = {(r[0], r[1]): (r[2], r[3]) for r in wiersze}

    # ----- mecze w TV: 2–4 w miesiącu, wieczorami; w planowanym tygodniu zawsze jakiś będzie -----
    # KROK 4 – MECZE W TV: losowo 2–4 w miesiącu, częściej we wtorki i środy (Liga Mistrzów).
    def _mecze(self):
        rng = self._strumien("mecze")
        nazwy = ["Liga Mistrzów", "Ekstraklasa – derby", "Reprezentacja Polski", "Liga Europy", "Mecz o Superpuchar"]
        mecze = []
        d = self.od
        while d <= self.do:
            if rng.random() < 0.09 or (d.weekday() in (1, 2) and rng.random() < 0.12):
                mecze.append({"data": d, "start": int(rng.choice([18, 20, 20, 21])),
                              "opis": str(rng.choice(nazwy))})
            d += timedelta(days=1)
        self.mecze = pd.DataFrame(mecze)
        self._indeks_meczow()

    def _indeks_meczow(self):
        self._mecze_dzien = {}
        for _, r in self.mecze.iterrows():
            self._mecze_dzien.setdefault(r.data, []).append(int(r.start))

    def dodaj_mecz(self, d, start=20, opis="Reprezentacja Polski"):
        self.mecze = self.mecze[self.mecze.data != d]
        self.mecze = pd.concat([self.mecze, pd.DataFrame([{"data": d, "start": start, "opis": opis}])], ignore_index=True)
        self._indeks_meczow()

    # ----- kalendarz zdarzeń znanych z wyprzedzeniem (to widzi model prognozy) -----
    # Kalendarz = wszystko, co da się wiedzieć z wyprzedzeniem (święta, wypłaty, promocje, mecze).
    # Tylko to dostaje model prognozy – nie zna np. przyszłego „poziomu dnia”.
    def kalendarz(self, od, do):
        rows = []
        d = od
        while d <= do:
            if d in SWIETA_2026:
                rows.append({"data": d, "typ": "święto_" + SWIETA_2026[d][1], "godzina": "", "opis": SWIETA_2026[d][0]})
            if self._po_wyplacie(d):
                rows.append({"data": d, "typ": "po_wyplacie", "godzina": "", "opis": "1–2 dni po wypłacie"})
            if d.weekday() == 1 and d >= PROMOCJA_OD:
                rows.append({"data": d, "typ": "promocja", "godzina": "", "opis": "Wtorek 2 za 1"})
            d += timedelta(days=1)
        m = self.mecze[(self.mecze.data >= od) & (self.mecze.data <= do)]
        for _, r in m.iterrows():
            rows.append({"data": r.data, "typ": "mecz", "godzina": int(r.start), "opis": r.opis})
        return pd.DataFrame(rows, columns=["data", "typ", "godzina", "opis"]).sort_values("data").reset_index(drop=True)

    @staticmethod
    def _dzien_wyplaty(rok, mies):
        ost = (date(rok, mies % 12 + 1, 1) if mies < 12 else date(rok + 1, 1, 1)) - timedelta(days=1)
        while ost.weekday() >= 5:
            ost -= timedelta(days=1)
        dziesiaty = date(rok, mies, 10)
        while dziesiaty.weekday() >= 5:
            dziesiaty -= timedelta(days=1)
        return [dziesiaty, ost]

    def _po_wyplacie(self, d):
        for delta in (0, 1):
            dd = d - timedelta(days=delta)
            if dd in self._dzien_wyplaty(dd.year, dd.month):
                return True
        return False

    # ----- prawdziwa intensywność zamówień w danej godzinie (wszystkie kanały) -----
    # KROK 5 – SERCE GENERATORA: oczekiwana liczba zamówień w godzinie h dnia d.
    # Profil × sezon × trend × pogoda × mecz × wypłata × promocja × święto × wakacje.
    # Efekty pogody są „na jednostkę”: exp(log(1+efekt) · ilość) – np. 10 mm deszczu = 1,3² zamiast 1,3.
    def intensywnosc(self, d: date, h: int):
        dzien = DNI_TYG[d.weekday()]
        lam = PROFIL[dzien][h - 11]
        lam *= SEZON[d.month - 1] * (1 + TREND_ROCZNY * (d - self.od).days / 365)
        temp, mm = self._pog.get((d, h), (10, 0))
        E = PRAWDZIWE_EFEKTY
        lam *= math.exp(math.log1p(E["deszcz (na każde 5 mm/h)"]) * min(mm, 8) / 5)
        lam *= math.exp(math.log1p(E["zimno (na każde 10°C poniżej 5°C)"]) * max(0, 5 - temp) / 10)
        lam *= math.exp(math.log1p(E["upał (na każde 10°C powyżej 25°C)"]) * max(0, temp - 25) / 10)
        for start in self._mecze_dzien.get(d, []):
            if h == start - 1:
                lam *= 1 + E["godzina przed meczem"]
            elif start <= h < start + 2:
                lam *= 1 + E["w trakcie meczu"]
            elif h == start + 2:
                lam *= 1 + E["po meczu"]
        if self._po_wyplacie(d):
            lam *= 1 + E["2 dni po wypłacie"]
        if d.weekday() == 1 and d >= PROMOCJA_OD:
            lam *= 1 + E["promocja Wtorek 2 za 1"]
        if d in SWIETA_2026:
            lam *= 1 + (E["święto – dzień wolny"] if SWIETA_2026[d][1] == "wolne" else E["święto rodzinne"])
        if WAKACJE[0] <= d <= WAKACJE[1] and 12 <= h <= 14:
            lam *= 1 + E["wakacje – pora lunchu"]
        return lam

    # ----- zamówienia jedno po drugim: czas, kanał, adres, dzielnica, strefa, wartość, czas przygotowania -----
    # KROK 6 – POJEDYNCZE ZAMÓWIENIA
    # Dla każdej godziny: liczba ~ Poisson(intensywność × poziom dnia), a potem dla każdego zamówienia
    # dzielnica, adres, droga, strefa, dostawa/odbiór, kanał, koszyk i czas przygotowania.
    def zamowienia(self, od: date, do: date, seed_offset=0):
        """seed_offset=0: historia; inna wartość: „alternatywna rzeczywistość” (np. 999 = tydzień do symulacji)."""
        nazwy = [z[0] for z in DZIELNICE]
        rows = []
        d = od
        while d <= do:
            rng = self._strumien("zamowienia", seed_offset, (d - self.od).days + 10_000)
            # Wspólny mnożnik całego dnia (średnio 1, ok. ±15%): bywają po prostu „dobre” i „słabe” dni.
            poziom_dnia = rng.gamma(40, 1 / 40)            # „dziwny dzień” – wspólny dla wszystkich godzin
            for h in GODZINY:
                n = rng.poisson(self.intensywnosc(d, h) * poziom_dnia)
                if n == 0:
                    continue
                temp, mm = self._pog.get((d, h), (10, 0))
                p_dost = 0.86 if mm > 0.5 else (0.70 if temp > 22 else 0.78)
                # Wagi dzielnic zależą od pory: strefa przemysłowa w lunch, kampus nocą, wille w weekend.
                wagi = np.array([z[4] for z in DZIELNICE])
                for i, z in enumerate(DZIELNICE):
                    if z[5] == "lunch" and 12 <= h <= 14 and d.weekday() < 5:
                        wagi[i] *= 3.5
                    if z[5] == "lunch" and (h >= 17 or d.weekday() >= 5):
                        wagi[i] *= 0.3
                    if z[5] == "wieczór" and h >= 17:
                        wagi[i] *= 1.4
                    if z[5] == "noc" and h >= 20:
                        wagi[i] *= 2.2
                    if z[5] == "weekend" and d.weekday() >= 5:
                        wagi[i] *= 2.0
                wagi /= wagi.sum()
                ktore = rng.choice(len(DZIELNICE), size=n, p=wagi)
                minuty = np.sort(rng.integers(0, 60, size=n))
                for j in range(n):
                    z = DZIELNICE[ktore[j]]
                    x, y = rng.normal(z[1], z[3]), rng.normal(z[2], z[3])
                    # Droga po ulicach ≈ odległość w linii prostej × 1,35; strefa A ≤ 2,5 km, B ≤ 4,5 km, dalej C.
                    km = min(7.5, math.hypot(x, y) * 1.35)   # 1,35 = ulice nie są prostą linią
                    dostawa = rng.random() < p_dost
                    rows.append((datetime(d.year, d.month, d.day, h, int(minuty[j])), DNI_TYG[d.weekday()],
                                 "tak" if dostawa else "nie",
                                 rng.choice(["aplikacja", "www", "telefon"], p=[0.56, 0.26, 0.18]),
                                 nazwy[ktore[j]], round(x, 3), round(y, 3), round(km, 2),
                                 "A" if km <= 2.5 else ("B" if km <= 4.5 else "C"),
                                 round(float(np.clip(rng.lognormal(4.15, 0.38), 25, 320)), 2),
                                 int(rng.integers(1, 6)), int(np.clip(rng.normal(13, 2.5), 8, 25))))
            d += timedelta(days=1)
        return pd.DataFrame(rows, columns=["czas", "dzien", "dostawa", "kanal", "dzielnica", "x_km", "y_km",
                                           "droga_km", "strefa", "wartosc_zl", "pozycji", "przygotowanie_min"])

    # ----- prognoza pogody na planowany tydzień = prawda + błąd prognozy -----
    # Prognoza pogody = prawdziwa pogoda + błąd (±1,5°C, ±40% opadu, czasem fałszywy deszcz) – jak w życiu.
    def prognoza_pogody(self, od, do):
        rng = self._strumien("prognoza_pogody", (od - self.od).days + 10_000)
        p = self.pogoda[(self.pogoda.data >= od) & (self.pogoda.data <= do)].copy()
        p["temp_c"] = (p["temp_c"] + rng.normal(0, 1.5, len(p))).round(1)
        p["deszcz_mm"] = np.clip(p["deszcz_mm"] * rng.uniform(0.6, 1.4, len(p)) + (rng.random(len(p)) < 0.03) * 1.0, 0, None).round(1)
        return p

    # ----- zespół kurierów: studenci, pełne etaty, weekendowi, poranni -----
    # KROK 7 – ZESPÓŁ KURIERÓW
    # Profil (student / etat / weekend / dzienny) decyduje o dostępności i limicie godzin.
    def kurierzy(self, n, poniedzialek):
        rng = self._strumien("kurierzy", n)
        profile = [("student", 0.40), ("etat", 0.25), ("weekend", 0.20), ("dzienny", 0.15)]
        imiona = rng.choice(IMIONA, size=n, replace=False)
        rows = []
        for i in range(n):
            prof = rng.choice([p[0] for p in profile], p=[p[1] for p in profile])
            auto = rng.random() < (0.55 if prof == "etat" else 0.35)
            skuter = rng.random() < 0.6 or not auto
            rower = (not auto and not skuter) or rng.random() < 0.15
            if prof == "student":
                dost = {d: ("16-23" if rng.random() < 0.8 else "") for d in DNI_TYG[:5]}
                dost.update({d: ("11-23" if rng.random() < 0.6 else "") for d in DNI_TYG[5:]})
                limit = int(rng.choice([16, 20, 24]))
            elif prof == "etat":
                wolne = set(rng.choice(7, size=2, replace=False))
                dost = {d: ("" if k in wolne else "11-23") for k, d in enumerate(DNI_TYG)}
                limit = 40
            elif prof == "weekend":
                dost = {d: "" for d in DNI_TYG[:4]}
                dost.update({"Pt": "16-23", "Sob": "11-23", "Nd": "11-23"})
                limit = int(rng.choice([16, 20, 24]))
            else:
                dost = {d: ("11-18" if rng.random() < 0.85 else "") for d in DNI_TYG}
                limit = int(rng.choice([24, 30, 32]))
            sanepid = poniedzialek + timedelta(days=int(rng.integers(40, 500)))
            bhp = poniedzialek + timedelta(days=int(rng.integers(60, 600)))
            rows.append({"imie": f"{imiona[i]} {rng.choice(list(NAZWISKA))}.", "aktywny": "tak",
                         "auto": "tak" if auto else "nie", "skuter": "tak" if skuter else "nie",
                         "rower": "tak" if rower else "nie", "terminal": "tak" if rng.random() < 0.55 else "nie",
                         "limit_h": limit, "stawka_h": round(float(rng.choice([31.4, 31.4, 32, 33, 34, 35])), 2),
                         "sanepid_do": sanepid.isoformat(), "bhp_do": bhp.isoformat(), "profil": prof, **dost})
        # realizm: jednemu kończy się sanepid w środę planowanego tygodnia, jednemu już się skończył
        # Celowo: jednemu sanepid kończy się w środę, drugiemu już się skończył – żeby było widać alerty.
        rows[1]["sanepid_do"] = (poniedzialek + timedelta(days=2)).isoformat()
        rows[2]["sanepid_do"] = (poniedzialek - timedelta(days=20)).isoformat()
        return pd.DataFrame(rows)


# KROK 8 – ODCISK, IZOLACJA, ZAPIS
# SHA-256 to „odcisk palca” pliku: zmiana jednego bajtu daje zupełnie inny skrót.
# Ten sam odcisk = identyczne dane, więc łatwo udowodnić powtarzalność.
def odcisk_pliku(sciezka):
    h = hashlib.sha256()
    with open(sciezka, "rb") as f:
        for kawalek in iter(lambda: f.read(1 << 16), b""):
            h.update(kawalek)
    return h.hexdigest()


def odcisk_danych(folder, pliki):
    """Jeden odcisk całego zestawu danych (SHA-256 z odcisków plików, w stałej kolejności)."""
    h = hashlib.sha256()
    for nazwa in sorted(pliki):
        h.update(nazwa.encode() + b":" + odcisk_pliku(os.path.join(folder, nazwa)).encode() + b"\n")
    return h.hexdigest()


def folder_ziarna(baza, seed, poniedzialek):
    return os.path.join(baza, f"ziarno_{int(seed)}_{poniedzialek:%Y-%m-%d}")


PLIKI_SWIATA = ["historia_zamowien.csv", "pogoda_historia.csv", "prognoza_pogody.csv", "kalendarz.csv", "kurierzy.csv"]


def zbuduj_swiat(baza, poniedzialek, seed=2026, liczba_kurierow=18, nadpisz=False):
    """Tworzy (albo wczytuje) izolowany zestaw danych dla danego ziarna i tygodnia.

    Zwraca (swiat, folder, metadane). Jeśli folder już istnieje i jego metadane pasują
    (to samo ziarno, tydzień, liczba kurierów, wersja generatora) – nic nie jest liczone od nowa.
    """
    if poniedzialek.weekday() != 0:
        raise ValueError(f"{poniedzialek} to nie poniedziałek – tydzień musi zaczynać się w poniedziałek")
    # Każda para (ziarno, tydzień) ma własny folder – różne ziarna nigdy się nie nadpisują.
    folder = folder_ziarna(baza, seed, poniedzialek)
    os.makedirs(folder, exist_ok=True)
    plik_meta = os.path.join(folder, "metadane.json")
    oczekiwane = {"ziarno": int(seed), "tydzien": poniedzialek.isoformat(),
                  "liczba_kurierow": int(liczba_kurierow), "wersja_generatora": WERSJA_GENERATORA}

    swiat = Swiat(od=date(2026, 1, 1), do=poniedzialek + timedelta(days=20), seed=seed)
    # w planowanym tygodniu zawsze jest mecz w czwartek (żeby było co pokazać)
    czw = poniedzialek + timedelta(days=3)
    if not ((swiat.mecze.data == czw).any() if len(swiat.mecze) else False):
        swiat.dodaj_mecz(czw, 20, "Reprezentacja Polski – eliminacje")

    # Jeśli dane już są i metadane się zgadzają – wczytujemy z dysku zamiast liczyć od nowa.
    if not nadpisz and os.path.exists(plik_meta):
        with open(plik_meta, encoding="utf-8") as f:
            meta = json.load(f)
        if all(meta.get(k) == v for k, v in oczekiwane.items()) and \
                all(os.path.exists(os.path.join(folder, p)) for p in PLIKI_SWIATA):
            meta["wczytano_z_dysku"] = True
            return swiat, folder, meta

    koniec_hist = poniedzialek - timedelta(days=1)
    pliki = {
        "historia_zamowien.csv": lambda: swiat.zamowienia(date(2026, 1, 1), koniec_hist),
        "pogoda_historia.csv": lambda: swiat.pogoda[(swiat.pogoda.data <= koniec_hist) & swiat.pogoda.godzina.between(11, 22)],
        "prognoza_pogody.csv": lambda: swiat.prognoza_pogody(poniedzialek, poniedzialek + timedelta(days=6)).query("11 <= godzina <= 22"),
        "kalendarz.csv": lambda: swiat.kalendarz(date(2026, 1, 1), poniedzialek + timedelta(days=6)),
        "kurierzy.csv": lambda: swiat.kurierzy(liczba_kurierow, poniedzialek),
    }
    for nazwa, f in pliki.items():
        # lineterminator='\n' – ten sam zapis na Windows i Linux, więc i ten sam odcisk.
        f().to_csv(os.path.join(folder, nazwa), index=False, lineterminator="\n")
    meta = {**oczekiwane,
            "odcisk": odcisk_danych(folder, PLIKI_SWIATA),
            "odciski_plikow": {p: odcisk_pliku(os.path.join(folder, p)) for p in PLIKI_SWIATA},
            "ukryte_efekty": PRAWDZIWE_EFEKTY,
            "utworzono": datetime.now().isoformat(timespec="seconds"),
            "wczytano_z_dysku": False}
    with open(plik_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return swiat, folder, meta


# Wywołanie z terminala: python -m grafik_kurierow.generator --ziarno 42 --tydzien 2026-10-19
def _main(argv=None):
    p = argparse.ArgumentParser(description="Generator danych wirtualnej pizzerii (powtarzalny z ziarna).")
    p.add_argument("--ziarno", type=int, default=2026, help="ziarno losowości (ten sam = te same dane)")
    p.add_argument("--tydzien", type=str, required=True, help="poniedziałek planowanego tygodnia, RRRR-MM-DD")
    p.add_argument("--kurierzy", type=int, default=18, help="liczba kurierów")
    p.add_argument("--folder", type=str, default="dane_symulowane", help="folder bazowy na dane")
    p.add_argument("--nadpisz", action="store_true", help="wygeneruj od nowa, nawet jeśli dane istnieją")
    a = p.parse_args(argv)
    _, folder, meta = zbuduj_swiat(a.folder, date.fromisoformat(a.tydzien), a.ziarno, a.kurierzy, a.nadpisz)
    print(f"Folder: {folder}")
    print(f"Odcisk danych (SHA-256): {meta['odcisk']}")
    print("Wczytano istniejące dane." if meta.get("wczytano_z_dysku") else "Wygenerowano nowe dane.")


if __name__ == "__main__":
    _main()
