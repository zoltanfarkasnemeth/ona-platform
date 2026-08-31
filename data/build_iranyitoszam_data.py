# -*- coding: utf-8 -*-
"""
Beolvassa a telepulesek_iranyitoszamok.csv-t (forrás: ferenci-tamas/IrszHnk,
https://github.com/ferenci-tamas/IrszHnk — nyílt, KSH-alapú összerendelés),
és tömör JSON-t épít belőle a jelentkezes.html autocomplete mezőihez:
  - codeToName: irányítószám -> megjelenítendő név (Budapestnél kerület, római számmal)
  - nameToCodes: megjelenítendő név -> hozzá tartozó irányítószám(ok) listája
"""
import csv
import json
import os
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "telepulesek_iranyitoszamok.csv")
OUT = os.path.join(HERE, "iranyitoszam_data.json")

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII",
         "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII"]


def build():
    code_to_name = {}
    name_to_codes = collections.defaultdict(list)

    with open(SRC, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            name = row["helyseg"].strip()
            code = row["iranyitoszam"].strip()
            if not name or not code:
                continue
            if name.lower().startswith("budapest"):
                num = int("".join(ch for ch in name.split()[1] if ch.isdigit()))
                display = f"Budapest {ROMAN[num - 1]}. kerület"
            else:
                display = name
            code_to_name[code] = display
            name_to_codes[display].append(code)

    data = {"codeToName": code_to_name, "nameToCodes": dict(name_to_codes)}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(code_to_name)} irányítószám, {len(name_to_codes)} egyedi település/kerület -> {OUT}")


if __name__ == "__main__":
    build()
