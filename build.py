#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère le site statique « Les clubs de l'ISAMM » à partir de data/clubs.json.

    python3 build.py

Sortie :
    index.html              page d'accueil (la planche de la maquette)
    c/<slug>/index.html     une fiche par club

Rien d'autre à faire : tout est statique, prêt pour GitHub Pages.
"""

import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "clubs.json")

# rotation de couleurs de la maquette : teal, orange, vert, bleu, navy, indigo
THEMES = [
    ("var(--teal)", "var(--teal-soft)"),
    ("var(--orange)", "var(--orange-soft)"),
    ("var(--green)", "var(--green-soft)"),
    ("var(--blue)", "var(--blue-soft)"),
    ("var(--navy)", "var(--navy-soft)"),
    ("var(--indigo)", "var(--indigo-soft)"),
]

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet">'
)

SCAN_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M3 8V5a2 2 0 0 1 2-2h3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/>'
    '<path d="M21 16v3a2 2 0 0 1-2 2h-3"/><path d="M8 21H5a2 2 0 0 1-2-2v-3"/>'
    '<rect x="8" y="8" width="8" height="8" rx="1.5"/></svg>'
)

PLACEHOLDER = '<p class="muted">À compléter</p>'


def esc(value):
    return html.escape(value or "", quote=True)


def paragraphs(text):
    """Transforme un texte multi-lignes en paragraphes HTML."""
    blocks = [b.strip() for b in (text or "").split("\n") if b.strip()]
    if not blocks:
        return PLACEHOLDER
    return "\n          ".join("<p>%s</p>" % esc(b) for b in blocks)


def line(text):
    return "<p>%s</p>" % esc(text) if (text or "").strip() else PLACEHOLDER


def initials(name):
    words = [w for w in name.replace("-", " ").split() if w[:1].isalpha()]
    return "".join(w[0].upper() for w in words[:3]) or "?"


def find_photos(slug):
    """Retourne jusqu'à 3 photos déposées dans assets/photos/<slug>/."""
    folder = os.path.join(ROOT, "assets", "photos", slug)
    if not os.path.isdir(folder):
        return []
    exts = (".jpg", ".jpeg", ".png", ".webp", ".avif")
    names = sorted(f for f in os.listdir(folder) if f.lower().endswith(exts))
    return names[:3]


def head(title, description, css_prefix, extra_body_class=""):
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta name="theme-color" content="#162e6a">
<link rel="icon" href="{css_prefix}assets/img/isamm-logo.png">
{FONTS}
<link rel="stylesheet" href="{css_prefix}assets/css/style.css">
</head>
<body class="{extra_body_class}">"""


# ---------------------------------------------------------------------------
# fiche club
# ---------------------------------------------------------------------------

def render_club(club, theme, prefix="../../"):
    color, soft = theme
    name = club["name"]
    abbr = club.get("abbr") or ""
    extra = ""
    if abbr and abbr.lower() != name.lower():
        extra = ' <span class="muted">(%s)</span>' % esc(abbr)

    # responsables
    rows = []
    if club.get("responsable"):
        rows.append(("Responsable", esc(club["responsable"])))
    if club.get("referent"):
        rows.append(("Enseignant référent", esc(club["referent"])))
    if club.get("email"):
        rows.append(
            ("Contact", '<a href="mailto:%s">%s</a>' % (esc(club["email"]), esc(club["email"])))
        )
    if rows:
        resp = '<dl>\n          ' + "\n          ".join(
            "<dt>%s</dt><dd>%s</dd>" % (k, v) for k, v in rows
        ) + "\n          </dl>"
    else:
        resp = PLACEHOLDER

    # galerie
    photos = find_photos(club["slug"])
    tiles = []
    for i in range(3):
        if i < len(photos):
            src = "%sassets/photos/%s/%s" % (prefix, club["slug"], photos[i])
            tiles.append(
                '<div class="shot"><span>Photo %d</span>'
                '<img src="%s" alt="%s — photo %d" loading="lazy"></div>'
                % (i + 1, esc(src), esc(name), i + 1)
            )
        else:
            tiles.append('<div class="shot"><span>Photo %d</span></div>' % (i + 1))

    if club.get("email"):
        subject = "Je souhaite venir visiter le club " + name
        cta_href = "mailto:%s?subject=%s" % (
            club["email"],
            esc(subject).replace(" ", "%20"),
        )
    else:
        cta_href = "%sindex.html#%s" % (prefix, club["slug"])

    desc = club.get("description") or ""
    meta_desc = (desc.split("\n")[0][:155] if desc else
                 "Fiche du club %s de l'ISAMM." % name)

    return f"""{head(name + " — Clubs de l'ISAMM", meta_desc, prefix)}
<main class="page">
  <article class="sheet" style="--c: {color}; --c-soft: {soft};">

    <header class="hero">
      <h1>{esc(name)}</h1>
      <p class="hero-sub">ISAMM · Fiche club</p>
    </header>

    <div class="fields">

      <section class="field">
        <h2>Nom du club</h2>
        <div class="box"><p>{esc(name)}{extra}</p></div>
      </section>

      <section class="field">
        <h2>Cible</h2>
        <div class="box alt">{line(club.get('cible'))}</div>
      </section>

      <section class="field">
        <h2>Domaine d'activité</h2>
        <div class="box">{line(club.get('domaine'))}</div>
      </section>

      <section class="field">
        <h2>Description</h2>
        <div class="box alt tall">
          {paragraphs(club.get('description'))}
        </div>
      </section>

      <section class="field">
        <h2>Responsables</h2>
        <div class="box">{resp}</div>
      </section>

      <section class="field">
        <h2>Activités</h2>
        <div class="box tall">
          {paragraphs(club.get('activites'))}
        </div>
      </section>

      <section class="field">
        <h2>En images</h2>
        <div class="gallery">
          {"".join(tiles)}
        </div>
      </section>

      <a class="cta" href="{cta_href}">Venir visiter le club</a>
    </div>

    <div class="deco">
      <i class="bl"></i><i class="sq"></i><i class="ci"></i>
      <a class="back" href="{prefix}index.html">← Tous les clubs</a>
    </div>

  </article>
</main>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# accueil
# ---------------------------------------------------------------------------

def render_home(site, clubs):
    cards = []
    for i, club in enumerate(clubs):
        color, _ = THEMES[i % len(THEMES)]
        shape = "round" if i % 2 == 0 else ""
        logo = club.get("logo")
        if logo:
            inner = '<img src="assets/img/logos/%s" alt="Logo %s" loading="lazy">' % (
                esc(logo),
                esc(club["name"]),
            )
        else:
            inner = '<span class="initials">%s</span>' % esc(
                club.get("abbr") or initials(club["name"])
            )

        # logo « tuile pleine » : il remplit la pastille, séparé du contour
        # coloré par un liseré blanc (cf. tools/detect_logo_bg.py)
        bleed = bool(club.get("logo_bleed")) and bool(club.get("logo_bg"))
        frame_cls = "frame " + shape + (" bleed" if bleed else "")
        frame_style = ' style="--lb: %s;"' % esc(club["logo_bg"]) if bleed else ""

        qr_path = os.path.join(ROOT, "assets", "img", "qr", club["slug"] + ".png")
        if os.path.exists(qr_path):
            qr = ('<span class="qr has-img"><img src="assets/img/qr/%s.png" '
                  'alt="QR code %s"></span>' % (esc(club["slug"]), esc(club["name"])))
        else:
            qr = '<span class="qr">QR</span>'

        abbr = club.get("abbr") or ""
        abbr_html = ""
        if abbr and abbr.lower() != club["name"].lower():
            abbr_html = '<span class="cabbr">%s</span>' % esc(abbr)

        cards.append(
            f"""      <a class="card" id="{esc(club['slug'])}" style="--c: {color};" href="c/{esc(club['slug'])}/">
        <span class="card-in">
          <span class="{frame_cls.strip()}"{frame_style}><span class="frame-fill">{inner}</span></span>
          <span class="card-body">
            <span class="cname">{esc(club.get('short') or club['name'])}</span>
            {abbr_html}
            <span class="scan">{SCAN_ICON} Scannez</span>
          </span>
          {qr}
        </span>
      </a>"""
        )

    dots = ["var(--teal)", "var(--orange)", "var(--green)"]
    steps = "\n        ".join(
        '<li><i style="--d: %s;"></i>%s</li>' % (dots[i % 3], esc(s))
        for i, s in enumerate(site["steps"])
    )

    return f"""{head(site['title'], site['lede'], "", "home")}
<div class="poster">

  <div class="poster-deco"><i class="ring"></i><i class="dot"></i><i class="blob"></i></div>

  <header class="masthead">
    <img class="isamm" src="assets/img/isamm-logo.png" alt="ISAMM">
    <div>
      <h1>Les clubs</h1>
      <p class="sub">DE L'ISAMM</p>
      <ul class="steps">
        {steps}
      </ul>
    </div>
  </header>

  <p class="lede">{esc(site['lede'])}</p>

  <div class="grid">
{chr(10).join(cards)}
  </div>

  <p class="poster-foot">Institut Supérieur des Arts Multimédias de la Manouba</p>
</div>
</body>
</html>
"""


def main():
    with open(DATA, encoding="utf-8") as fh:
        data = json.load(fh)

    clubs = data["clubs"]

    out = os.path.join(ROOT, "c")
    if os.path.isdir(out):
        shutil.rmtree(out)

    for i, club in enumerate(clubs):
        folder = os.path.join(out, club["slug"])
        os.makedirs(folder, exist_ok=True)
        page = render_club(club, THEMES[i % len(THEMES)])
        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page)
        print("  c/%s/index.html" % club["slug"])

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(render_home(data["site"], clubs))
    print("  index.html")
    print("%d fiches générées." % len(clubs))


if __name__ == "__main__":
    main()
