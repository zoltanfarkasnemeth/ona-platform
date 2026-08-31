-- ONA adatbázis séma
-- Két, egymástól elkülönített tábla: akik segítséget/szolgáltatást keresnek,
-- és akik munkát (gondozói megbízást) keresnek.
-- A díjazás mindkét oldalon Ft/hó formában szerepel, hogy összevethető legyen
-- (a jelentkezési űrlapon megadott óradíjat a rendszer havi órakerettel szorozva
-- kell majd havi összegre váltani, mielőtt ide kerül).

DROP TABLE IF EXISTS keresok;
CREATE TABLE keresok (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nev               TEXT NOT NULL,
    email             TEXT NOT NULL,
    telefon           TEXT NOT NULL,
    iranyitoszam      TEXT,
    telepules         TEXT,
    kategoria         TEXT NOT NULL CHECK (kategoria IN ('Senior','Recovery','Mama','Care','Nincs megadva')),
    kinek             TEXT,                       -- szulo / magamnak / mas
    ora_per_het       INTEGER,                     -- igényelt óraszám hetente
    havi_keret_ft     INTEGER NOT NULL,            -- tervezett havi keret (Ft/hó)
    uzenet            TEXT,
    letrehozva        TEXT NOT NULL DEFAULT (datetime('now'))
);

DROP TABLE IF EXISTS munkavallalok;
CREATE TABLE munkavallalok (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nev                 TEXT NOT NULL,
    email               TEXT NOT NULL,
    telefon             TEXT NOT NULL,
    iranyitoszam        TEXT,
    telepules           TEXT,
    kategoria           TEXT NOT NULL CHECK (kategoria IN ('Senior','Recovery','Mama','Care')),
    tapasztalat         TEXT,                      -- 0-1 / 1-3 / 3-5 / 5+ (év)
    ora_per_het         INTEGER,                    -- vállalt óraszám hetente
    havi_dij_igeny_ft   INTEGER NOT NULL,           -- elvárt havi díjazás (Ft/hó)
    uzenet              TEXT,
    letrehozva          TEXT NOT NULL DEFAULT (datetime('now'))
);
