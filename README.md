# ▶ MediaRename

Application web locale de renommage de fichiers médias, pensée pour les utilisateurs de **Jellyfin** et les amateurs de homelab.

---

## 💡 Idée de base

Quand on télécharge des fichiers via torrent, les noms sont souvent du genre :

```
[DB]Dungeon.Meshi_-_01_(Dual.Audio.10bit.BD1080p.x265).mkv
The.Dark.Knight.2008.4K.HDR.BluRay.HEVC.TrueHD-YIFY.mkv
Breaking.Bad.S01E01.720p.BluRay.x264-GROUP.mkv
```

Jellyfin (et Plex, Emby) ont besoin de noms propres et standardisés pour récupérer automatiquement les métadonnées (pochettes, synopsis, acteurs...) depuis les bases de données en ligne. Les formats attendus sont :

```
Dungeon Meshi S01E01.mkv
The Dark Knight (2008).mkv
Breaking Bad S01E01.mkv
```

**MediaRename** est une petite application web que tu héberges toi-même sur ton serveur ou ton homelab. Elle te permet de :
- charger un dossier de fichiers téléchargés
- appliquer des règles de renommage par regex
- prévisualiser le résultat avant d'appliquer
- renommer et/ou déplacer les fichiers directement dans leur dossier de destination

Pas besoin de FileBot, pas besoin d'une interface graphique sur le serveur. Tout se passe dans le navigateur, depuis n'importe quel appareil sur ton réseau (PC, téléphone, tablette).

---

## ✨ Fonctionnalités

- **Chargement de dossier** — liste tous les fichiers d'un chemin donné avec leur taille
- **Sélection individuelle ou globale** — coche/décoche les fichiers à traiter
- **Presets rapides** — règles prédéfinies pour les cas les plus courants
- **Règles regex personnalisées** — ajoute, modifie, supprime des règles dans l'ordre de ton choix
- **Aperçu en temps réel** — vois exactement ce que donnera chaque renommage avant d'appliquer
- **Renommage sur place** — renomme les fichiers dans le dossier source
- **Renommer + Déplacer** — renomme et déplace en une seule action vers un dossier destination
- **Interface sombre, responsive** — fonctionne sur mobile et desktop
- **Zéro dépendance externe** — un seul fichier Python, une seule dépendance (Flask)

---

## 🗂️ Structure du projet

```
mediarename/
├── app.py            # Application complète (serveur Flask + interface HTML/CSS/JS)
└── requirements.txt  # Dépendances Python (flask)
```

Tout le code frontend (HTML, CSS, JavaScript) est embarqué dans `app.py`. Pas de build, pas de node_modules, pas de fichiers séparés.

---

## ⚙️ Installation

### Prérequis

- Python 3.10 ou supérieur
- pip3

### 1. Copier les fichiers sur le serveur

Depuis ton PC (Windows) :
```bash
scp app.py utilisateur@IP_SERVEUR:/home/utilisateur/mediarename/app.py
```

Ou directement sur le serveur :
```bash
mkdir -p ~/mediarename
nano ~/mediarename/app.py   # colle le contenu
```

### 2. Installer Flask

```bash
pip3 install flask --break-system-packages
```

### 3. Lancer l'application

```bash
python3 ~/mediarename/app.py
```

Par défaut, l'app est accessible sur le port **5757** :
```
http://localhost:5757          # sur le serveur lui-même
http://192.168.X.X:5757        # depuis n'importe quel appareil sur le réseau local
http://IP_TAILSCALE:5757       # depuis partout via Tailscale
```

Pour utiliser un port différent :
```bash
python3 ~/mediarename/app.py 8080
```

---

## 🔁 Démarrage automatique avec systemd

Pour que l'app se lance automatiquement au démarrage du serveur et tourne en arrière-plan (sans avoir besoin d'un terminal SSH ouvert) :

### 1. Créer le fichier de service

```bash
sudo nano /etc/systemd/system/mediarename.service
```

Contenu (adapte `User` et les chemins à ton utilisateur) :

```ini
[Unit]
Description=MediaRename
After=network.target

[Service]
User=ton_utilisateur
WorkingDirectory=/home/ton_utilisateur/mediarename
ExecStart=/home/ton_utilisateur/.local/bin/flask --app app run --host=0.0.0.0 --port=5757
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 2. Activer et démarrer le service

```bash
sudo systemctl daemon-reload
sudo systemctl enable mediarename   # démarre au boot
sudo systemctl start mediarename    # démarre maintenant
sudo systemctl status mediarename   # vérifie que c'est actif
```

Tu devrais voir `active (running)` en vert.

### Commandes utiles

```bash
sudo systemctl stop mediarename      # arrêter
sudo systemctl restart mediarename   # redémarrer
sudo journalctl -u mediarename -f    # voir les logs en temps réel
```

---

## 📖 Tutoriel d'utilisation

### Étape 1 — Charger un dossier

Entre le chemin absolu du dossier contenant tes fichiers dans la barre en haut, puis clique **Charger**.

```
Exemple : /mnt/externe/medias/torrents/finis
```

Tous les fichiers du dossier apparaissent dans la colonne de gauche avec leur taille. Ils sont tous cochés par défaut.

### Étape 2 — Sélectionner les fichiers

- Clique sur un fichier pour le cocher/décocher individuellement
- Clique sur **tout / rien** pour tout sélectionner ou tout désélectionner
- Seuls les fichiers cochés seront affectés par les règles et les actions

### Étape 3 — Choisir un preset ou configurer des règles

#### Presets disponibles

| Preset | Ce qu'il fait |
|---|---|
| 🧹 **Nettoyer** | Supprime les tags typiques des releases torrent : résolutions (`1080p`, `4K`), sources (`BluRay`, `WEB-DL`), codecs (`x264`, `HEVC`), audio (`AAC`, `TrueHD`), langues (`FRENCH`, `VOSTFR`, `MULTI`), groupe de release (`-GROUP`) |
| 🎬 **Film Jellyfin** | Même chose que Nettoyer, puis formate l'année en `(Année)` → compatible 100% Jellyfin |
| 📺 **Série Jellyfin** | Même chose que Nettoyer, puis normalise le format épisode en `S01E01` → compatible 100% Jellyfin |
| **· → espaces** | Remplace tous les points par des espaces |
| ✕ **Vider** | Supprime toutes les règles |

#### Règles personnalisées

Chaque règle est composée de deux champs :
- **Gauche** : pattern regex (ce qu'on cherche)
- **Droite** : remplacement (ce par quoi on remplace — laisser vide pour supprimer)

Les règles sont appliquées **dans l'ordre**, uniquement sur le **nom** du fichier (sans l'extension).

Clique **+ Ajouter une règle** pour en ajouter une manuellement.

#### Exemples de règles utiles

| Pattern | Remplacement | Effet |
|---|---|---|
| `\.` | ` ` | Remplace les points par des espaces |
| `_` | ` ` | Remplace les underscores par des espaces |
| `\[.*?\]` | *(vide)* | Supprime tout ce qui est entre crochets `[...]` |
| `\(.*?\)` | *(vide)* | Supprime tout ce qui est entre parenthèses `(...)` |
| `\s*-\s*(\d{2})\s*$` | ` S01E$1` | Transforme ` - 01` en fin de nom en ` S01E01` |
| `\b(s)(\d{2})(e)(\d{2})\b` | `S$2E$4` | Normalise `s01e01` → `S01E01` |
| `-[A-Za-z0-9]{2,}$` | *(vide)* | Supprime le groupe de release en fin de nom |

> Les patterns utilisent la syntaxe **regex JavaScript** (équivalente à Python pour les cas courants). Le flag `gi` (insensible à la casse, toutes occurrences) est appliqué automatiquement.

### Étape 4 — Vérifier l'aperçu

La section **Aperçu** affiche en temps réel, pour chaque fichier sélectionné :
- **Gris** (avec `=`) : le fichier ne changera pas
- **Bleu** (avec `→`) : le fichier sera renommé, avec le nouveau nom affiché

Un compteur indique le nombre de fichiers qui seront effectivement modifiés.

### Étape 5 — Appliquer

Deux boutons en bas à droite :

**Renommer** — renomme les fichiers sur place dans le dossier source. Le bouton n'est actif que s'il y a au moins un changement à appliquer.

**Renommer + Déplacer →** — renomme les fichiers puis les déplace vers le dossier indiqué dans le champ destination. Le dossier est créé automatiquement s'il n'existe pas. Actif dès qu'au moins un fichier est sélectionné.

```
Exemple de destination : /mnt/externe/medias/series/Dungeon Meshi/Season 01
```

---

## 🎯 Cas d'usage concrets

### Anime téléchargé (fansub)

Fichiers originaux :
```
[DB]Dungeon Meshi_-_01_(Dual Audio_10bit_BD1080p_x265).mkv
[DB]Dungeon Meshi_-_02_(Dual Audio_10bit_BD1080p_x265).mkv
```

Règles à appliquer (dans l'ordre) :
| Pattern | Remplacement |
|---|---|
| `\[.*?\]` | *(vide)* |
| `\(.*?\)` | *(vide)* |
| `_` | ` ` |
| `\s*-\s*(\d{2})\s*$` | ` S01E$1` |

Résultat :
```
Dungeon Meshi S01E01.mkv
Dungeon Meshi S01E02.mkv
```

---

### Film torrent

Fichier original :
```
The.Dark.Knight.2008.4K.HDR.BluRay.HEVC.TrueHD-YIFY.mkv
```

Preset **Film Jellyfin** → résultat :
```
The Dark Knight (2008).mkv
```

---

### Série torrent classique

Fichier original :
```
Breaking.Bad.S01E01.720p.BluRay.x264-GROUP.mkv
```

Preset **Série Jellyfin** → résultat :
```
Breaking Bad S01E01.mkv
```

---

## 🔌 API interne

L'application expose trois endpoints REST utilisés par l'interface :

### `POST /api/list`
Liste les fichiers d'un dossier.

```json
// Requête
{ "path": "/chemin/vers/dossier" }

// Réponse
{
  "files": [
    { "name": "fichier.mkv", "size": 1073741824 }
  ],
  "path": "/chemin/vers/dossier"
}
```

### `POST /api/rename`
Renomme les fichiers selon une liste de correspondances.

```json
// Requête
{
  "source_dir": "/chemin/source",
  "renames": [
    { "original": "ancien.mkv", "renamed": "nouveau.mkv" }
  ]
}

// Réponse
{
  "results": [
    { "original": "ancien.mkv", "renamed": "nouveau.mkv", "success": true }
  ]
}
```

### `POST /api/move`
Déplace des fichiers vers un dossier destination.

```json
// Requête
{
  "source_dir": "/chemin/source",
  "dest_dir": "/chemin/destination",
  "files": ["fichier1.mkv", "fichier2.mkv"]
}
```

---

## ⚠️ Limitations connues

- L'application liste uniquement les **fichiers directs** du dossier (pas récursif dans les sous-dossiers)
- Le renommage est **irréversible** — vérifie toujours l'aperçu avant d'appliquer
- Pas de gestion des **conflits de noms** avancée (si le nom cible existe déjà, l'opération est annulée pour ce fichier)
- Conçu pour un usage **local / réseau privé** — pas de système d'authentification

---

## 🛠️ Stack technique

| Composant | Technologie |
|---|---|
| Serveur | Python 3 + Flask |
| Interface | HTML / CSS / JavaScript vanilla |
| Polices | JetBrains Mono, DM Sans (Google Fonts) |
| Dépendances Python | `flask` uniquement |
| Dépendances JS | Aucune (vanilla JS pur) |

---

## 📄 Licence

Usage personnel. Projet privé.
