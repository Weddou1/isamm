#!/usr/bin/env python3
"""Uniformise les photos des clubs.

Lit un dossier source (un sous-dossier par club, tous formats : jpg, png,
HEIC, MPO…) et écrit pour chaque club dans assets/photos/<slug>/ :

  1.jpg 2.jpg 3.jpg          version complète (côté long <= 1800 px), pour
                             l'agrandissement au clic
  thumb/1.jpg 2.jpg 3.jpg    vignette 800x594 au format exact des cases de la
                             fiche (310:230), pour la galerie

Les photos en paysage sont recadrées en « cover » ; les photos portrait ou
quasi carrées (affiches, logos) ne sont jamais coupées : elles sont posées sur
un fond flou issu d'elles-mêmes (blanc pour un logo).

Dépendances : pip install pillow pillow-heif
Usage : python3 tools/prep_photos.py <dossier_source>
"""
import os
import sys

from PIL import Image, ImageFilter, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    print("pillow-heif absent : les fichiers .HEIC seront ignorés")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TILE = (800, 594)             # 310:230
FULL_MAX = 1800

# dossier source -> (slug, [fichiers dans l'ordre voulu], options par fichier)
CLUBS = {
    "robotique": ("robotique", ["Copie de DSC_0165.JPG", "IMG_0336.HEIC", "23.png"], {}),
    "club radio": ("radio", None, {}),
    "j2i": ("j2i", None, {}),
    "log": ("gamers", ["717d8faa-f024-407b-8fe1-6d235af785a6.jpg",
                       "9ad3bad6-f680-4486-87d7-d052fb4973e4.jpg",
                       "1090896a-c40e-4d41-a11d-0ae0ef852176.jpg"],
            {"1090896a-c40e-4d41-a11d-0ae0ef852176.jpg": {"rotate": 90}}),
    "atia": ("atia", ["images.jpg", "images (1).jpg", "ATIA.png"],
             {"ATIA.png": {"logo": True}}),
    "orenda": ("orenda", None, {}),
    "cineclub": ("cine", None, {}),
    "isamm problem solving": ("ips", None, {}),
    "green": ("green", None, {}),
    "cultuclub": ("cultuclub", None, {}),
    "cin": ("cin", ["8e88d5ae-3024-4156-a146-6f40d5c759e3.jpg",
                    "afc32b01-0def-48fd-b74a-202716e2468a.jpg",
                    "bb0164fe-366f-4e69-a348-0ccff1c89af8.jpg"], {}),
    "music club isamm": ("music", ["635467551_17954997420073187_8523738430008430829_n.jpg",
                                   "629108879_17955204729073187_4704363587801006521_n.jpg",
                                   "641776925_17956598712073187_3099702841074116038_n.jpg"], {}),
    "roubla": ("roubla", None, {}),
    "gdg": ("gdg", None, {}),
    "aiesec": ("aiesec", ["43e2af76-8bcf-4286-9a29-0dd6ee8f5e7a.jpg",
                          "fd61beee-9371-4eb4-ab06-3b23590d5401.jpg",
                          "0e3826ce-c590-4ba9-b3b9-16bc1961bf71.jpg"], {}),
}


def load(path, opts):
    im = ImageOps.exif_transpose(Image.open(path))
    if opts.get("rotate"):
        im = im.rotate(opts["rotate"], expand=True)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def make_full(im):
    im = im.copy()
    im.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
    return im


def make_thumb(im, logo=False):
    w, h = im.size
    if w / h >= 1.15:                       # paysage : cover, centré
        return ImageOps.fit(im, TILE, Image.LANCZOS, centering=(0.5, 0.45))
    if logo:                                # logo : fond blanc uni
        bg = Image.new("RGB", TILE, "white")
    else:                                   # portrait : fond flou
        bg = ImageOps.fit(im, TILE, Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
        bg = Image.blend(bg, Image.new("RGB", TILE, "black"), 0.25)
    fg = im.copy()
    fg.thumbnail((TILE[0], TILE[1] - 2 * 18), Image.LANCZOS)
    bg.paste(fg, ((TILE[0] - fg.width) // 2, (TILE[1] - fg.height) // 2))
    return bg


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    for folder, (slug, order, opts) in CLUBS.items():
        d = os.path.join(src, folder)
        if not os.path.isdir(d):
            print("absent :", d)
            continue
        files = order or sorted(os.listdir(d))
        out = os.path.join(ROOT, "assets", "photos", slug)
        os.makedirs(os.path.join(out, "thumb"), exist_ok=True)
        for i, f in enumerate(files[:3], 1):
            o = opts.get(f, {})
            im = load(os.path.join(d, f), o)
            make_full(im).save(os.path.join(out, "%d.jpg" % i), "JPEG",
                               quality=84, optimize=True, progressive=True)
            make_thumb(im, o.get("logo", False)).save(
                os.path.join(out, "thumb", "%d.jpg" % i), "JPEG",
                quality=82, optimize=True, progressive=True)
        txt = os.path.join(out, "LISEZ-MOI.txt")
        if os.path.exists(txt):
            os.remove(txt)
        print("%-10s <- %s" % (slug, folder))


if __name__ == "__main__":
    main()
