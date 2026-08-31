# -*- coding: utf-8 -*-
"""
ONA jelentkezési backend
========================

Egyetlen végpontot ad: POST /api/jelentkezes — ez veszi át a jelentkezes.html
űrlap adatait, és a kategória-kódot (senior/recovery/mama/care/nem-tudom)
átalakítva beírja a db/ona.db megfelelő táblájába (keresok vagy munkavallalok,
a "role" mező alapján).

Helyi futtatás:
    pip install -r backend/requirements.txt
    python3 backend/app.py
    # majd: http://localhost:5000/api/health -> {"status": "ok"}

Éles telepítés: bármelyik Python-t futtató, ingyenes szolgáltatóra tehető
(pl. Render.com "Web Service", Railway, Fly.io, PythonAnywhere). Telepítés
után a kapott publikus URL-t írd be a jelentkezes.html tetején lévő
API_BASE konstansba (build_jelentkezes.py-ban, majd futtasd újra a build-et
— lásd a README-t), hogy az űrlap valóban ide küldje a jelentkezéseket.

FONTOS: ez a fájl SQLite-ot használ (db/ona.db), ami egyetlen helyi fájlba
ír — ez tökéletes teszteléshez és kis forgalomhoz, de a legtöbb "serverless"
hoszting (pl. Cloudflare Workers) NEM ad tartós fájlrendszert, ott a
db/ona.db a újraindításkor elveszne. Hagyományos, tartósan futó szerveren
(VPS, Render "persistent disk", stb.) viszont pontosan úgy működik, mint
helyben.
"""
import os
import re
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "..", "db", "ona.db")

app = Flask(__name__)

# Engedélyezett eredetek (CORS) — ide vedd fel a GitHub Pages URL-edet, ha éles domainen futtatod.
ALLOWED_ORIGINS = {"*"}  # fejlesztéshez/demóhoz; élesben szűkítsd le pl. {"https://<felhasznalo>.github.io"}

KATEGORIA_KOD_TO_NEV = {
    "senior": "Senior",
    "recovery": "Recovery",
    "mama": "Mama",
    "care": "Care",
    "nem-tudom": "Nincs megadva",  # csak a "keresok" oldalon érvényes, lásd db/schema.sql CHECK
}

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin", "")
    if "*" in ALLOWED_ORIGINS or origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin or "*"
        resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.route("/api/jelentkezes", methods=["OPTIONS"])
def jelentkezes_preflight():
    return ("", 204)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "db_exists": os.path.exists(DB_PATH)})


def _clean_int(value):
    try:
        v = int(value)
        return v if v >= 0 else None
    except (TypeError, ValueError):
        return None


@app.route("/api/jelentkezes", methods=["POST"])
def jelentkezes():
    data = request.get_json(silent=True) or {}

    role = data.get("role")
    nev = (data.get("nev") or "").strip()
    email = (data.get("email") or "").strip()
    telefon = (data.get("telefon") or "").strip()
    telepules = (data.get("telepules") or "").strip()
    iranyitoszam = (data.get("iranyitoszam") or "").strip()
    uzenet = (data.get("uzenet") or "").strip()
    kategoria_kod = data.get("kategoria_kod")
    ora_per_het = _clean_int(data.get("ora_per_het"))

    if role not in ("kereso", "munkavallalo"):
        return jsonify({"error": "Érvénytelen 'role' mező (kereso / munkavallalo várt)."}), 400
    if not nev or not email or not telefon or not telepules:
        return jsonify({"error": "Hiányzó kötelező mező (nev, email, telefon, telepules)."}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Érvénytelen e-mail cím."}), 400

    kategoria = KATEGORIA_KOD_TO_NEV.get(kategoria_kod)
    if kategoria is None:
        return jsonify({"error": f"Ismeretlen kategória kód: {kategoria_kod!r}"}), 400

    if not os.path.exists(DB_PATH):
        return jsonify({"error": "Az adatbázis nem található. Futtasd először: python3 db/seed_data.py"}), 500

    conn = sqlite3.connect(DB_PATH)
    try:
        if role == "kereso":
            havi_keret_ft = _clean_int(data.get("havi_keret_ft"))
            if havi_keret_ft is None:
                return jsonify({"error": "Hiányzó vagy érvénytelen 'havi_keret_ft'."}), 400
            if kategoria == "Nincs megadva":
                pass  # engedélyezett — a schema CHECK-je csak a keresok táblánál fogadja el
            conn.execute(
                """INSERT INTO keresok
                   (nev, email, telefon, iranyitoszam, telepules, kategoria, kinek, ora_per_het, havi_keret_ft, uzenet)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (nev, email, telefon, iranyitoszam, telepules, kategoria,
                 data.get("kinek"), ora_per_het, havi_keret_ft, uzenet),
            )
        else:
            if kategoria == "Nincs megadva":
                return jsonify({"error": "Munkavállalóknál kötelező konkrét kategóriát választani."}), 400
            havi_dij_igeny_ft = _clean_int(data.get("havi_dij_igeny_ft"))
            if havi_dij_igeny_ft is None:
                return jsonify({"error": "Hiányzó vagy érvénytelen 'havi_dij_igeny_ft'."}), 400
            conn.execute(
                """INSERT INTO munkavallalok
                   (nev, email, telefon, iranyitoszam, telepules, kategoria, tapasztalat, ora_per_het, havi_dij_igeny_ft, uzenet)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (nev, email, telefon, iranyitoszam, telepules, kategoria,
                 data.get("tapasztalat"), ora_per_het, havi_dij_igeny_ft, uzenet),
            )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        return jsonify({"error": f"Adatbázis-hiba: {exc}"}), 400
    finally:
        conn.close()

    return jsonify({"status": "mentve", "role": role, "idopont": datetime.now().isoformat(timespec="seconds")}), 201


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
