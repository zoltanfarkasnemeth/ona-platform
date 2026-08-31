/**
 * ONA jelentkezési backend — Cloudflare Worker + D1
 * ==================================================
 *
 * Ugyanazt csinálja, mint a backend/app.py (Flask+SQLite) változat, csak
 * Cloudflare-en: a jelentkezes.html POST kérését fogadja az /api/jelentkezes
 * végponton, és beírja a D1 adatbázisba (ami SQLite-kompatibilis — a
 * db/schema.sql változtatás nélkül lefuttatható rajta).
 *
 * Telepítés lépései a README.md "Backend — Cloudflare Workers + D1" részében.
 */

const ALLOWED_ORIGIN = "*"; // élesben: pl. "https://<felhasznalonev>.github.io"

const KATEGORIA_KOD_TO_NEV = {
  senior: "Senior",
  recovery: "Recovery",
  mama: "Mama",
  care: "Care",
  "nem-tudom": "Nincs megadva", // csak a "keresok" oldalon engedélyezett (lásd db/schema.sql CHECK)
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders() },
  });
}

function cleanInt(value) {
  const v = parseInt(value, 10);
  return Number.isFinite(v) && v >= 0 ? v : null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    if (url.pathname === "/api/health") {
      return json({ status: "ok" });
    }

    if (url.pathname === "/api/jelentkezes" && request.method === "POST") {
      let data;
      try {
        data = await request.json();
      } catch (e) {
        return json({ error: "Érvénytelen JSON." }, 400);
      }

      const role = data.role;
      const nev = (data.nev || "").trim();
      const email = (data.email || "").trim();
      const telefon = (data.telefon || "").trim();
      const telepules = (data.telepules || "").trim();
      const iranyitoszam = (data.iranyitoszam || "").trim();
      const uzenet = (data.uzenet || "").trim();
      const oraPerHet = cleanInt(data.ora_per_het);

      if (role !== "kereso" && role !== "munkavallalo") {
        return json({ error: "Érvénytelen 'role' mező (kereso / munkavallalo várt)." }, 400);
      }
      if (!nev || !email || !telefon || !telepules) {
        return json({ error: "Hiányzó kötelező mező (nev, email, telefon, telepules)." }, 400);
      }
      if (!EMAIL_RE.test(email)) {
        return json({ error: "Érvénytelen e-mail cím." }, 400);
      }
      const kategoria = KATEGORIA_KOD_TO_NEV[data.kategoria_kod];
      if (!kategoria) {
        return json({ error: `Ismeretlen kategória kód: ${data.kategoria_kod}` }, 400);
      }

      try {
        if (role === "kereso") {
          const haviKeretFt = cleanInt(data.havi_keret_ft);
          if (haviKeretFt === null) {
            return json({ error: "Hiányzó vagy érvénytelen 'havi_keret_ft'." }, 400);
          }
          await env.DB.prepare(
            `INSERT INTO keresok (nev, email, telefon, iranyitoszam, telepules, kategoria, kinek, ora_per_het, havi_keret_ft, uzenet)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
          )
            .bind(nev, email, telefon, iranyitoszam, telepules, kategoria, data.kinek || null, oraPerHet, haviKeretFt, uzenet)
            .run();
        } else {
          if (kategoria === "Nincs megadva") {
            return json({ error: "Munkavállalóknál kötelező konkrét kategóriát választani." }, 400);
          }
          const haviDijIgenyFt = cleanInt(data.havi_dij_igeny_ft);
          if (haviDijIgenyFt === null) {
            return json({ error: "Hiányzó vagy érvénytelen 'havi_dij_igeny_ft'." }, 400);
          }
          await env.DB.prepare(
            `INSERT INTO munkavallalok (nev, email, telefon, iranyitoszam, telepules, kategoria, tapasztalat, ora_per_het, havi_dij_igeny_ft, uzenet)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
          )
            .bind(nev, email, telefon, iranyitoszam, telepules, kategoria, data.tapasztalat || null, oraPerHet, haviDijIgenyFt, uzenet)
            .run();
        }
      } catch (e) {
        return json({ error: `Adatbázis-hiba: ${e.message}` }, 400);
      }

      return json({ status: "mentve", role, idopont: new Date().toISOString() }, 201);
    }

    return json({ error: "Not found" }, 404);
  },
};
