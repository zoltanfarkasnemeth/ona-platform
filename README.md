# ONA — Care that feels human.

Az ONA otthoni gondoskodási szolgáltatás professzionális, több oldalból álló statikus honlapja. Az 5 HTML oldal önmagában, backend és build lépés nélkül is működik bármilyen statikus tárhelyen (pl. GitHub Pages); a `backend/` mappában van egy opcionális kis szerver, ami bekapcsolva azt is lehetővé teszi, hogy a jelentkezési űrlap valóban adatbázisba írjon (lásd lejjebb).

## Oldalak

| Fájl | Tartalom |
|---|---|
| `index.html` | Kezdőlap — hero, szolgáltatás-áttekintő, "hogyan működik" teaser, árazási előnézet |
| `szolgaltatasok.html` | ONA Senior / Recovery / Mama / Care részletesen, fül-navigációval |
| `arazas.html` | Essential / Comfort / Daily Support csomagok, GYIK |
| `hogyan-mukodik.html` | Folyamat segítséget keresőknek és gondozóként jelentkezőknek, biztonsági/megbízhatósági blokk |
| `jelentkezes.html` | Jelentkezési űrlap — "Segítséget keresek" / "Munkát keresek" váltóval, validációval, település- és irányítószám-kereséssel |

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

## Jelentkezés → adatbázis: a `backend/` szerver

Alapból (amíg a `backend/` szervert nem telepíted) a `jelentkezes.html` űrlapja csak helyben igazol vissza — ez teszi lehetővé, hogy a honlap pusztán statikus fájlokból (pl. GitHub Pages) is teljes értékűen működjön. Ha szeretnéd, hogy a beküldött jelentkezések **ténylegesen bekerüljenek** a `db/ona.db`-be, telepítened kell a `backend/app.py`-t egy Python-t futtatni képes helyre:

```bash
pip install -r backend/requirements.txt
python3 backend/app.py
# teszt: http://localhost:5000/api/health -> {"status":"ok"}
```

Ez helyben egy `/api/jelentkezes` végpontot indít, ami a `role` mező alapján (`kereso` / `munkavallalo`) beírja a jelentkezést a megfelelő táblába. Éles használathoz telepítsd egy Pythont futtató, tartósan élő szolgáltatóra (pl. Render.com "Web Service", Railway, Fly.io, PythonAnywhere — mindegyiknek van ingyenes csomagja), majd:

1. Másold ki az onnan kapott publikus URL-t (pl. `https://ona-backend.onrender.com`).
2. Írd be a `build_jelentkezes.py` tetején lévő `API_BASE` konstansba.
3. Futtasd újra a build-et (lásd a *Szerkesztés* szakaszt), majd commitold és push-old az újragenerált `jelentkezes.html`-t.

Amíg `API_BASE` üres, a viselkedés pontosan a mostani marad (nincs törés) — az űrlap csak akkor próbál ténylegesen menteni, ha be van állítva egy cím.

Éles telepítés előtt kapcsold ki a `backend/app.py` alján a `debug=True`-t (fejlesztéshez hagytam bekapcsolva), és szűkítsd le az `ALLOWED_ORIGINS` listát a saját GitHub Pages domainedre.

**Fontos korlát:** a `backend/app.py` SQLite-ba (`db/ona.db`) ír, ami egyetlen fájl a szerver lemezén. Ez tökéletes teszteléshez és kis forgalomhoz, hagyományos, tartósan futó szerveren (VPS, Render perzisztens lemezzel stb.) megbízhatóan működik — de "serverless" platformokon (pl. sima Cloudflare Workers) NEM ad tartós fájlrendszert, ott minden újraindításkor elveszne az adat. Ha ilyen platformot választanál, szólj, és átalakítom felhő-adatbázisra (pl. Cloudflare D1, Turso, Postgres).

## Település és irányítószám adatbázis (`data/`)

A `jelentkezes.html` "Település / régió" és "Irányítószám" mezője beépített, kétirányú kereséssel működik: gépelés közben települést vagy kerületet ajánl fel (Budapestnél római számos kerület-formában, pl. *Budapest XI. kerület*), irányítószám beírásakor pedig felismeri és kitölti a hozzá tartozó települést (pl. `2040` → *Budaörs*) — mindez kliens oldalon, szerver nélkül fut.

Az adat forrása a [ferenci-tamas/IrszHnk](https://github.com/ferenci-tamas/IrszHnk) nyílt, KSH-alapú összerendelés (~3050 irányítószám, ~3180 település/kerület). A `data/` mappa tartalma:
- `telepulesek_iranyitoszamok.csv` — a forrásadat tisztított, csak a szükséges két oszlopot (`helyseg`, `iranyitoszam`) tartalmazó változata
- `build_iranyitoszam_data.py` — ebből építi a `iranyitoszam_data.json`-t (amit a `build_jelentkezes.py` beágyaz a HTML-be)

Ha frissítenéd az adatot (pl. új hivatalos KSH-lista jelenik meg), cseréld le a CSV-t, majd futtasd újra mindkét scriptet és a teljes build-et.

## Adatbázis és párosító motor (`db/`, `tools/`, `matches/`)

**`db/schema.sql`** — két, egymástól elkülönített tábla:
- `keresok` — akik segítséget/szolgáltatást keresnek (név, elérhetőség, irányítószám + település, kategória — vagy `Nincs megadva`, ha az űrlapon a "segítsenek választani" opciót adta meg —, kinek kell, heti óraigény, **havi keret Ft/hó**)
- `munkavallalok` — akik munkát (gondozói megbízást) keresnek (név, elérhetőség, irányítószám + település, kategória, tapasztalat, heti vállalt óraszám, **havi díjigény Ft/hó**)

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
