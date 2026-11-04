#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère un QR code par club, pointant vers sa fiche en ligne.

L'adresse de base est lue dans data/clubs.json (champ site.base_url) ; on peut
la remplacer en argument :

    python3 tools/make_qr.py
    python3 tools/make_qr.py https://weddou1.github.io/isamm/

L'option --missing-only ne génère que les QR absents et laisse les autres
intacts ; c'est ce que fait le déploiement automatique, pour ne jamais écraser
un code déjà imprimé.

Produit, pour chaque club :
    assets/img/qr/<slug>.png          utilisé automatiquement par l'accueil
    assets/img/qr/print/<slug>.svg    version vectorielle pour l'impression

Les QR sont en bleu nuit #162E6A sur blanc : c'est la seule couleur de la
palette qui garde un contraste suffisant pour être lue de façon fiable par
l'appareil photo d'un téléphone, y compris imprimée et sous un éclairage
moyen.

Nécessite segno (pip install segno). Relancer ensuite python3 build.py.
"""

import json
import os
import sys

try:
    import segno
except ImportError:  # pragma: no cover
    sys.exit("segno est requis : pip install segno")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "clubs.json")
QR_DIR = os.path.join(ROOT, "assets", "img", "qr")
PRINT_DIR = os.path.join(QR_DIR, "print")

DARK = "#162e6a"
ERROR_LEVEL = "q"   # ~25 % de redondance : tolère l'usure et les reflets
BORDER = 4          # zone de silence standard, indispensable au décodage


def main():
    with open(DATA, encoding="utf-8") as fh:
        data = json.load(fh)

    args = sys.argv[1:]
    missing_only = "--missing-only" in args
    positional = [a for a in args if not a.startswith("--")]

    base = positional[0] if positional else data["site"].get("base_url", "")
    if not base:
        sys.exit("Aucune adresse de base : renseignez site.base_url dans "
                 "data/clubs.json ou passez-la en argument.")
    if not base.endswith("/"):
        base += "/"

    os.makedirs(QR_DIR, exist_ok=True)
    os.makedirs(PRINT_DIR, exist_ok=True)

    print("Base :", base, "\n")
    written = skipped = 0
    for club in data["clubs"]:
        png = os.path.join(QR_DIR, club["slug"] + ".png")
        if missing_only and os.path.exists(png):
            skipped += 1
            print("  %-11s déjà présent, conservé" % club["slug"])
            continue

        url = "%sc/%s/" % (base, club["slug"])
        qr = segno.make(url, error=ERROR_LEVEL)
        written += 1

        qr.save(
            os.path.join(QR_DIR, club["slug"] + ".png"),
            scale=16,
            border=BORDER,
            dark=DARK,
            light="#ffffff",
        )
        qr.save(
            os.path.join(PRINT_DIR, club["slug"] + ".svg"),
            scale=16,
            border=BORDER,
            dark=DARK,
            light="#ffffff",
        )
        print("  %-11s v%-3s %s" % (club["slug"], qr.version, url))

    print("\n%d QR codes générés, %d conservés — relancez python3 build.py"
          % (written, skipped))


if __name__ == "__main__":
    main()
