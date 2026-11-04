#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse les logos de assets/img/logos/ et met à jour data/clubs.json.

Pour chaque logo, on regarde l'anneau de pixels du bord :
  - majoritairement blanc ou transparent  -> logo détouré, posé sur fond blanc
  - majoritairement coloré                -> « tuile pleine » : le logo occupe
    tout son cadre, on le laisse donc remplir la pastille (cercle ou carré)
    et on retient sa couleur moyenne comme fond.

Écrit deux champs par club :
    "logo_bleed": true/false   le logo remplit la pastille
    "logo_bg":    "#rrggbb"    couleur de fond (null si détouré)

Nécessite Pillow (pip install pillow). À relancer uniquement quand on change
un logo ; build.py, lui, n'a besoin d'aucune dépendance.

    python3 tools/detect_logo_bg.py
"""

import json
import os
import sys

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("Pillow est requis : pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGOS = os.path.join(ROOT, "assets", "img", "logos")
DATA = os.path.join(ROOT, "data", "clubs.json")

# part de pixels de bord blancs/transparents en dessous de laquelle on
# considère que le logo est une tuile pleine
BLEED_THRESHOLD = 0.35


def analyse(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    margin = max(2, int(min(w, h) * 0.04))

    total = 0
    empty = 0
    r_sum = g_sum = b_sum = 0
    solid = 0

    for y in range(h):
        for x in range(w):
            if not (x < margin or y < margin or x >= w - margin or y >= h - margin):
                continue
            r, g, b, a = px[x, y]
            total += 1
            if a < 200 or (r > 240 and g > 240 and b > 240):
                empty += 1
                continue
            solid += 1
            r_sum += r
            g_sum += g
            b_sum += b

    if not total:
        return False, None

    if empty / total > BLEED_THRESHOLD or not solid:
        return False, None

    bg = "#%02x%02x%02x" % (r_sum // solid, g_sum // solid, b_sum // solid)
    return True, bg


def main():
    with open(DATA, encoding="utf-8") as fh:
        data = json.load(fh)

    for club in data["clubs"]:
        logo = club.get("logo")
        if not logo:
            club["logo_bleed"] = False
            club["logo_bg"] = None
            print("%-11s pas de logo" % club["slug"])
            continue

        path = os.path.join(LOGOS, logo)
        if not os.path.exists(path):
            club["logo_bleed"] = False
            club["logo_bg"] = None
            print("%-11s INTROUVABLE : %s" % (club["slug"], logo))
            continue

        bleed, bg = analyse(path)
        club["logo_bleed"] = bleed
        club["logo_bg"] = bg
        print(
            "%-11s %s %s"
            % (club["slug"], "tuile pleine" if bleed else "détouré", bg or "")
        )

    with open(DATA, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print("\ndata/clubs.json mis à jour — relancez python3 build.py")


if __name__ == "__main__":
    main()
