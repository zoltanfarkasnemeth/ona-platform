# ONA — Care that feels human.

Az ONA otthoni gondoskodási szolgáltatás professzionális, több oldalból álló statikus honlapja. Nincs backend, nincs build lépés — tiszta HTML/CSS/JS, bármilyen statikus tárhelyen (pl. GitHub Pages) azonnal működik.

## Oldalak

| Fájl | Tartalom |
|---|---|
| `index.html` | Kezdőlap — hero, szolgáltatás-áttekintő, "hogyan működik" teaser, árazási előnézet |
| `szolgaltatasok.html` | ONA Senior / Recovery / Mama / Care részletesen, fül-navigációval |
| `arazas.html` | Essential / Comfort / Daily Support csomagok, GYIK |
| `hogyan-mukodik.html` | Folyamat segítséget keresőknek és gondozóként jelentkezőknek, biztonsági/megbízhatósági blokk |
| `jelentkezes.html` | Jelentkezési űrlap — "Segítséget keresek" / "Munkát keresek" váltóval, validációval |

## Helyi megtekintés

Nincs szükség build eszközre. Egyszerűen nyisd meg az `index.html`-t böngészőben, vagy indíts egy helyi szervert:

```bash
python3 -m http.server 8000
# majd nyisd meg: http://localhost:8000
```

## Publikálás GitHub Pages-szel

1. Hozz létre egy új (üres) repót a GitHub-on, majd ebben a mappában:
   ```bash
   git remote add origin https://github.com/<felhasznalonev>/<repo-nev>.git
   git branch -M main
   git push -u origin main
   ```
2. A GitHub repóban: **Settings → Pages → Build and deployment → Source: Deploy from a branch**, ág: `main`, mappa: `/ (root)`.
3. Pár perc múlva a repo élesedik ezen a címen: `https://<felhasznalonev>.github.io/<repo-nev>/`

Saját domain esetén a **Settings → Pages → Custom domain** mezőben add meg a domaint, és állítsd be a DNS-t (CNAME rekord) a szolgáltatódnál.

## Adatbázis és párosító motor (`db/`, `tools/`, `matches/`)

A honlap statikus (nincs szerver), ezért a `jelentkezes.html` űrlapja önmagában nem ír adatbázisba — a `db/` és `tools/` mappa egy különálló, admin-oldali eszközkészlet, ami a jelentkezők adatait tárolja és párosítja. Ha a jövőben szeretnéd, hogy az űrlap valóban ide írjon, ehhez egy kis szerver (pl. egy GitHub Actions workflow vagy egy egyszerű Cloudflare Worker / Formspree-webhook) szükséges, ami a beérkező jelentkezéseket ebbe az adatbázisba menti — szólj, ha ezt is szeretnéd, és összekötöm.

**`db/schema.sql`** — két, egymástól elkülönített tábla:
- `keresok` — akik segítséget/szolgáltatást keresnek (név, elérhetőség, kategória, kinek kell, heti óraigény, **havi keret Ft/hó**)
- `munkavallalok` — akik munkát (gondozói megbízást) keresnek (név, elérhetőség, kategória, tapasztalat, heti vállalt óraszám, **havi díjigény Ft/hó**)

A két oldal fizetési mezője szándékosan azonos mértékegységben (Ft/hó) van, hogy összevethető legyen — óradíjas jelentkezésnél ezt a heti óraszámmal átszámolva kell majd betölteni.

**`db/seed_data.py`** — létrehozza a `db/ona.db` SQLite fájlt a sémából, és feltölti 8+8 mintasorral (minden ONA kategóriában, szándékosan van köztük egyező és nem egyező fizetési igényű pár is). Újrafuttatható:
```bash
python3 db/seed_data.py
```

**`tools/match_engine.py`** — beolvassa a `db/ona.db`-t, és minden olyan (kereső, munkavállaló) párost, ahol **azonos a kategória** és a két havi összeg **legfeljebb 20%-kal tér el egymástól** (a képlet: `|munkavállalói díj − kereső kerete| / átlaguk`), kiír a **`matches/talalatok.xlsx`** táblázatba — névvel, elérhetőségekkel, a tényleges eltérés%-kal (élő Excel-képlet, tehát a fájlban is ellenőrizhető) és egy "Állapot" oszloppal, amit az admin manuálisan tud majd frissíteni (pl. "Új" → "Felvéve" → "Lezárva"). Minden futtatáskor a teljes táblázat újragenerálódik a DB aktuális tartalma alapján:
```bash
pip install -r tools/requirements.txt   # csak első alkalommal (openpyxl)
python3 tools/match_engine.py
```

A 20%-os küszöb a `tools/match_engine.py` tetején, a `MATCH_THRESHOLD_PCT` konstansban módosítható.

## Szerkesztés

Minden oldal önálló, teljes HTML fájl (a stílus és a szkriptek inline-ban vannak benne, hogy a fájlok egyenként is hordozhatók legyenek). Ha egy közös elemet (pl. navigáció, lábléc, színek) mindenhol módosítanál, ugyanazt a részt mind az 5 fájlban át kell vezetni — vagy szólj, és összeállítok egy build-scriptet, ami egy közös sablonból generálja újra az oldalakat.

## Jogi megjegyzés

Az ONA nem minősül egészségügyi szolgáltatónak, és nem végez orvosi vagy ápolói beavatkozást (gyógyszerbeadás, sebkezelés). A szolgáltatás otthoni jelenlétet, mindennapi és háztartási segítséget, valamint logisztikai támogatást nyújt.
