# Les clubs de l'ISAMM

Site statique reproduisant la maquette Figma : une planche d'accueil avec les
clubs (logo + QR code) et une fiche par club.

Tout est en HTML/CSS statique — **aucun serveur, aucune base, aucun build à
déployer**. GitHub Pages suffit.

En ligne : <https://weddou1.github.io/isamm/>

---

## Mise en ligne (GitHub Pages)

```bash
git init
git add .
git commit -m "Site des clubs de l'ISAMM"
git branch -M main
git remote add origin https://github.com/Weddou1/isamm.git
git push -u origin main
```

Puis sur GitHub : **Settings → Pages → Source : `GitHub Actions`**.

> C'est bien `GitHub Actions` et **pas** `Deploy from a branch` : le dépôt
> contient un workflow qui régénère les pages avant de les publier. Avec
> l'autre réglage, le workflow tournerait dans le vide et le site ne bougerait
> pas.

Au bout d'une minute le site est en ligne, et il se remet à jour tout seul à
chaque `git push` (voir « Déploiement automatique » plus bas).

| Page | URL |
| --- | --- |
| Accueil | `https://weddou1.github.io/isamm/` |
| Fiche d'un club | `https://weddou1.github.io/isamm/c/ips/` |

Les douze fiches sont à `/c/<slug>/`, avec les slugs : `gdg`, `ips`, `radio`,
`cultuclub`, `orenda`, `cine`, `music`, `robotique`, `j2i`, `cin`, `green`,
`gamers`.

> **Important :** les QR codes encodent ces adresses. Si le dépôt change de nom
> ou de compte, il faut régénérer les QR (voir plus bas).

---

## Déploiement automatique

`.github/workflows/deploy.yml` se déclenche à chaque push sur `main` (et à la
demande depuis l'onglet **Actions**). Il :

1. génère les QR codes des clubs qui n'en ont pas encore ;
2. relance `build.py`, donc régénère `index.html` et les douze fiches depuis
   `data/clubs.json` ;
3. publie le résultat sur GitHub Pages.

Concrètement : **il suffit de modifier `data/clubs.json`, même directement
depuis l'éditeur web de GitHub, pour que le site se mette à jour tout seul.**
Pas besoin d'avoir Python installé pour corriger une description.

Deux garde-fous volontaires :

- les QR codes sont générés avec `--missing-only`, donc un code déjà présent —
  et peut-être déjà imprimé — n'est jamais réécrit. Pour tout régénérer après
  un changement d'adresse, lancer `python3 tools/make_qr.py` en local et
  committer le résultat ;
- `tools/detect_logo_bg.py` ne tourne **pas** dans le workflow : il réécrit les
  champs `logo_bleed` et `logo_bg`, ce qui effacerait un réglage fait à la
  main. À lancer en local quand on ajoute ou remplace un logo.

Le suivi des déploiements est dans l'onglet **Actions** du dépôt ; en cas
d'échec, le log indique l'étape fautive.

---

## Modifier le contenu

Tout le texte vit dans **`data/clubs.json`**. On édite le JSON, puis :

```bash
python3 build.py
```

Le script régénère `index.html` et les `c/<slug>/index.html`.
Aucune dépendance : Python 3 standard suffit. En poussant sur GitHub, cette
étape est de toute façon rejouée automatiquement.

### Champs d'un club

| Champ | Rôle |
| --- | --- |
| `slug` | identifiant dans l'URL (`c/<slug>/`) — ne pas changer après impression des QR |
| `name` | nom complet, affiché dans le bandeau de la fiche |
| `short` | nom court, affiché sur la carte de l'accueil |
| `abbr` | sigle (IPS, CRI, OJE…) |
| `email` | adresse de contact ; alimente le bouton « Venir visiter le club » |
| `domaine`, `cible`, `description`, `activites`, `adherents` | contenu des champs de la fiche |
| `responsable`, `referent` | bloc « Responsables » |
| `logo` | nom du fichier dans `assets/img/logos/`, ou `null` |
| `logo_bleed`, `logo_bg` | traitement de la pastille (voir plus bas), calculés automatiquement |

Un champ laissé vide affiche « À compléter », exactement comme la maquette.
Dans `description` et `activites`, une ligne vide crée un nouveau paragraphe.

Pour **ajouter un club** : copier un bloc dans `data/clubs.json`, déposer son
logo dans `assets/img/logos/`, puis relancer les trois scripts
(`detect_logo_bg.py`, `make_qr.py`, `build.py`).

---

## Les QR codes

```bash
pip install segno
python3 tools/make_qr.py          # lit site.base_url dans clubs.json
python3 build.py
```

Un QR par club est écrit dans :

- `assets/img/qr/<slug>.png` — repris automatiquement par l'accueil, à la
  place du carré pointillé ;
- `assets/img/qr/print/<slug>.svg` — version vectorielle, pour l'impression
  grand format sans perte.

Chaque code pointe vers `https://weddou1.github.io/isamm/c/<slug>/`, avec une
correction d'erreur de niveau Q (~25 % de redondance : il reste lisible même
abîmé, plié ou sous un reflet) et la zone de silence standard de 4 modules.

Ils sont en bleu nuit `#162E6A` plutôt qu'aux couleurs des clubs : c'est la
seule teinte de la palette dont le contraste sur blanc reste suffisant pour un
décodage fiable à l'appareil photo. Le turquoise, l'orange et surtout le vert
descendent sous le seuil et deviennent capricieux à l'impression.

Pour changer l'adresse de base, modifier `site.base_url` dans
`data/clubs.json`, ou la passer en argument :

```bash
python3 tools/make_qr.py https://exemple.github.io/mon-depot/
```

---

## Pastilles de logo

Sur l'accueil, chaque logo est posé dans une pastille (cercle ou carré arrondi
en alternance) bordée de la couleur du club. Deux traitements :

- **logo détouré** (fond blanc ou transparent) : il flotte sur le blanc ;
- **logo « tuile pleine »** (fond de couleur — IPS, Club Radio, Music Club,
  CIN, Life of Gamers) : sa couleur remplit toute la pastille, séparée du
  contour coloré par un liseré blanc.

La détection est automatique :

```bash
pip install pillow
python3 tools/detect_logo_bg.py
python3 build.py
```

Le script lit l'anneau de pixels du bord de chaque logo et écrit `logo_bleed`
(true/false) et `logo_bg` (la couleur) dans `data/clubs.json`. On peut forcer
le comportement d'un club en modifiant ces deux champs à la main — à condition
de ne pas relancer le script ensuite, il les réécrirait.

---

## Ajouter les photos d'un club

Déposer 1 à 3 images dans `assets/photos/<slug>/` (jpg, png ou webp), puis
relancer `python3 build.py`. Elles remplacent les cases « Photo 1/2/3 » dans
l'ordre alphabétique des noms de fichiers — le plus simple est de les nommer
`1.jpg`, `2.jpg`, `3.jpg`.

---

## Structure

```
.github/workflows/deploy.yml  build + publication automatiques
index.html                 accueil (planche des clubs)
c/<slug>/index.html        fiche club
assets/css/style.css       feuille de style unique
assets/img/isamm-logo.png
assets/img/logos/          logos des clubs
assets/img/qr/             QR codes (png pour le web, print/ en svg)
assets/photos/<slug>/      photos des clubs
data/clubs.json            contenu éditable
build.py                   générateur (sans dépendance)
tools/detect_logo_bg.py    détection du fond des logos (Pillow)
tools/make_qr.py           génération des QR codes (segno)
```

## Notes

- La maquette est reproduite à l'identique : palette relevée au pixel près sur
  le PDF (bandeaux `#00A8C0` `#FB5A1A` `#7DD3A0` `#3373C4` `#162E6A` `#4568B0`
  en rotation), géométrie des champs, galerie, bouton et décors d'angle.
- Les dimensions sont proportionnelles à la maquette (artboards 1080×1920 et
  1920×1080) grâce aux unités de conteneur CSS ; les tailles de texte sont
  bornées par `clamp()` pour rester lisibles sur téléphone, puisque les fiches
  sont destinées à être ouvertes après un scan.
- La grille de l'accueil est sur quatre colonnes et trois lignes, comme la
  maquette. En ajoutant un treizième club, la quatrième ligne n'en contiendrait
  qu'un : passer la règle `.grid { grid-template-columns: repeat(4, 1fr) }` à
  `repeat(5, 1fr)` dans `assets/css/style.css` range alors tout en trois lignes.
- Les numéros de téléphone et les adresses personnelles des responsables
  présents dans le fichier source **ne sont pas publiés** : seules les adresses
  de contact des clubs apparaissent.
- Polices : Poppins (Google Fonts) avec repli système, pour coller au
  lettrage de la maquette.
