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

## Szerkesztés

Minden oldal önálló, teljes HTML fájl (a stílus és a szkriptek inline-ban vannak benne, hogy a fájlok egyenként is hordozhatók legyenek). Ha egy közös elemet (pl. navigáció, lábléc, színek) mindenhol módosítanál, ugyanazt a részt mind az 5 fájlban át kell vezetni — vagy szólj, és összeállítok egy build-scriptet, ami egy közös sablonból generálja újra az oldalakat.

## Jogi megjegyzés

Az ONA nem minősül egészségügyi szolgáltatónak, és nem végez orvosi vagy ápolói beavatkozást (gyógyszerbeadás, sebkezelés). A szolgáltatás otthoni jelenlétet, mindennapi és háztartási segítséget, valamint logisztikai támogatást nyújt.
