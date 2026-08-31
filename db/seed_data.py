# -*- coding: utf-8 -*-
"""
Létrehozza a db/ona.db SQLite adatbázist a schema.sql alapján, és feltölti
demonstrációs mintaadatokkal (8 segítséget kereső + 8 munkát kereső sor,
minden ONA kategóriában, néhány szándékosan egyező és néhány szándékosan
nem egyező fizetési igénnyel, hogy a match_engine.py kimenete ellenőrizhető
legyen).
"""
import sqlite3
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "ona.db")
SCHEMA_PATH = os.path.join(HERE, "schema.sql")

KERESOK = [
    # nev, email, telefon, iranyitoszam, telepules, kategoria, kinek, ora_per_het, havi_keret_ft, uzenet
    ("Kovács Anna", "kovacs.anna@example.com", "+36301112222", "1131", "Budapest XIII. kerület", "Senior", "szulo", 15, 150000, "Édesanyámnak keresek rendszeres segítséget."),
    ("Tóth Béla", "toth.bela@example.com", "+36202223333", "6720", "Szeged", "Senior", "szulo", 8, 90000, "Heti pár alkalom bevásárlással, sétával."),
    ("Nagy Eszter", "nagy.eszter@example.com", "+36703334444", "1022", "Budapest II. kerület", "Recovery", "magamnak", 20, 220000, "Csípőműtét után lábadozom, napi segítségre lenne szükségem."),
    ("Szabó Gábor", "szabo.gabor@example.com", "+36304445555", "4024", "Debrecen", "Recovery", "mas", 12, 130000, "Testvéremnek keresek segítséget lábtörés után."),
    ("Kiss Dóra", "kiss.dora@example.com", "+36205556666", "9012", "Győr", "Mama", "magamnak", 18, 180000, "Ikreket szültem 3 hete, sokat segítene a napi rutinban."),
    ("Varga Zsolt", "varga.zsolt@example.com", "+36706667777", "7622", "Pécs", "Mama", "mas", 10, 95000, "Feleségemnek keresek segítséget az első hetekre."),
    ("Molnár Katalin", "molnar.katalin@example.com", "+36307778888", "1113", "Budapest XI. kerület", "Care", "szulo", 10, 320000, "Édesapámnak rendszeres gyógytornára és rehabilitációra lenne szükség."),
    ("Horváth Imre", "horvath.imre@example.com", "+36208889999", "3508", "Miskolc", "Senior", "szulo", 6, 60000, "Csak alkalmankénti, könnyű segítséget keresek, szűk kerettel."),
]

MUNKAVALLALOK = [
    # nev, email, telefon, iranyitoszam, telepules, kategoria, tapasztalat, ora_per_het, havi_dij_igeny_ft, uzenet
    ("Farkas Mária", "farkas.maria@example.com", "+36301230001", "1011", "Budapest I. kerület", "Senior", "5+", 15, 145000, "8 éve dolgozom idősgondozóként, referenciákkal rendelkezem."),
    ("Balogh Péter", "balogh.peter@example.com", "+36202230002", "6700", "Szeged", "Senior", "1-3", 8, 88000, "Részmunkaidőben tudok segíteni, rugalmas időbeosztással."),
    ("Nemeth Judit", "nemeth.judit@example.com", "+36703230003", "1021", "Budapest II. kerület", "Recovery", "3-5", 20, 200000, "Ápolói végzettséggel rendelkezem, lábadozók gondozásában tapasztalt vagyok."),
    ("Papp László", "papp.laszlo@example.com", "+36304230004", "4000", "Debrecen", "Recovery", "1-3", 12, 140000, "Gyógytornász hallgatóként vállalok otthoni segítséget."),
    ("Simon Andrea", "simon.andrea@example.com", "+36205230005", "9000", "Győr", "Mama", "5+", 18, 170000, "Dúlaként és gyermekfelügyelőként is dolgoztam korábban."),
    ("Rácz Beáta", "racz.beata@example.com", "+36706230006", "7600", "Pécs", "Mama", "1-3", 10, 100000, "Két saját gyermekem van, szívesen segítek kismamáknak."),
    ("Fekete Gábor", "fekete.gabor@example.com", "+36307230007", "1112", "Budapest XI. kerület", "Care", "5+", 10, 300000, "Szakképzett gyógytornász, otthoni rehabilitációra specializálódva."),
    ("Oláh Zsuzsanna", "olah.zsuzsanna@example.com", "+36208230008", "3500", "Miskolc", "Senior", "5+", 15, 200000, "Nagy tapasztalattal, prémium szintű ellátást vállalok."),
]


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema_sql)

    conn.executemany(
        """INSERT INTO keresok (nev, email, telefon, iranyitoszam, telepules, kategoria, kinek, ora_per_het, havi_keret_ft, uzenet)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        KERESOK,
    )
    conn.executemany(
        """INSERT INTO munkavallalok (nev, email, telefon, iranyitoszam, telepules, kategoria, tapasztalat, ora_per_het, havi_dij_igeny_ft, uzenet)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        MUNKAVALLALOK,
    )
    conn.commit()

    n_k = conn.execute("SELECT COUNT(*) FROM keresok").fetchone()[0]
    n_m = conn.execute("SELECT COUNT(*) FROM munkavallalok").fetchone()[0]
    conn.close()
    print(f"ona.db létrehozva: {n_k} kereső, {n_m} munkavállaló sor.")


if __name__ == "__main__":
    main()
