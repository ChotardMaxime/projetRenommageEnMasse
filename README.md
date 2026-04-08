# ▶ MediaRename

Personal tool to rename torrent downloads before moving them into Jellyfin.  
One Python file, runs on the homelab, accessible from any device on the network or via Tailscale.

---

## Why I built this

Torrents come with garbage filenames like:

```
[DB]Dungeon.Meshi_-_01_(Dual.Audio.10bit.BD1080p.x265).mkv
The.Dark.Knight.2008.4K.HDR.BluRay.HEVC.TrueHD-YIFY.mkv
```

Jellyfin needs clean names to pull metadata correctly:

```
Dungeon Meshi S01E01.mkv
The Dark Knight (2008).mkv
```

Instead of doing this manually or setting up FileBot, I made a small web app that I open in the browser, configure regex rules, preview the result, and apply — all in a few seconds.

---

## Stack

- Python 3 + Flask (backend + API)
- Vanilla HTML/CSS/JS (frontend, embedded directly in app.py)
- No build step, no node_modules, no separate files
- Single dependency: `flask`

---

## Server setup (Ubuntu Server 24.04)

### First time install

```bash
# Create the folder
mkdir -p ~/mediarename

# Copy the file from my PC
scp app.py max@192.168.1.154:/home/max/mediarename/app.py

# Install Flask
pip3 install flask --break-system-packages
```

### Run manually (for testing)

```bash
python3 ~/mediarename/app.py
# → http://192.168.1.154:5757
```

### Run as a service (permanent)

Create the systemd service:

```bash
sudo nano /etc/systemd/system/mediarename.service
```

```ini
[Unit]
Description=MediaRename
After=network.target

[Service]
User=max
WorkingDirectory=/home/max/mediarename
ExecStart=/home/max/.local/bin/flask --app app run --host=0.0.0.0 --port=5757
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable mediarename
sudo systemctl start mediarename
sudo systemctl status mediarename   # should show active (running)
```

Useful commands:

```bash
sudo systemctl restart mediarename
sudo journalctl -u mediarename -f    # live logs
```

### Access

| Context | URL |
|---|---|
| Local network | `http://192.168.1.154:5757` |
| Via Tailscale | `http://[tailscale-ip]:5757` |

---

## How to use it

### 1. Load a folder

Paste the full path to the folder containing the downloaded files, hit **Charger**.

```
/mnt/externe/medias/torrents/finis
```

All files appear on the left with their size. Everything is selected by default.

### 2. Pick files

Click individual files to check/uncheck them. Use **tout / rien** to toggle all.  
Only checked files will be affected.

### 3. Apply a preset or write rules

#### Presets

| Preset | What it does |
|---|---|
| 🧹 Nettoyer | Removes release tags: resolution, source, codec, audio, language, group name |
| 🎬 Film Jellyfin | Same as Nettoyer + formats year as `(Year)` |
| 📺 Série Jellyfin | Same as Nettoyer + normalizes episode format to `S01E01` |
| · → espaces | Replaces all dots with spaces |
| ✕ Vider | Clears all rules |

#### Custom rules

Each rule is a regex find → replace pair, applied in order on the filename (without extension).  
Leave the replacement field empty to delete the matched text.  
Flags `gi` (case-insensitive, all occurrences) are applied automatically.

Common patterns I use:

| Pattern | Replace | Effect |
|---|---|---|
| `\.` | ` ` | Dots → spaces |
| `_` | ` ` | Underscores → spaces |
| `\[.*?\]` | *(empty)* | Remove `[anything]` |
| `\(.*?\)` | *(empty)* | Remove `(anything)` |
| `\s*-\s*(\d{2})\s*$` | ` S01E$1` | ` - 01` at end → ` S01E01` |
| `\b(s)(\d{2})(e)(\d{2})\b` | `S$2E$4` | Normalize `s01e01` → `S01E01` |
| `-[A-Za-z0-9]{2,}$` | *(empty)* | Remove release group at end |

### 4. Check the preview

The preview section updates live. Blue entries with `→` will be renamed, grey ones with `=` won't change.  
Always check this before applying — renaming is irreversible.

### 5. Apply

- **Renommer** — renames files in place. Only active if there's at least one change.
- **Renommer + Déplacer →** — renames then moves to the destination folder. The folder is created automatically if it doesn't exist.

---

## Real examples

### Anime (fansub-style names)

Input:
```
[DB]Dungeon Meshi_-_01_(Dual Audio_10bit_BD1080p_x265).mkv
```

Rules:
| Pattern | Replace |
|---|---|
| `\[.*?\]` | *(empty)* |
| `\(.*?\)` | *(empty)* |
| `_` | ` ` |
| `\s*-\s*(\d{2})\s*$` | ` S01E$1` |

Output:
```
Dungeon Meshi S01E01.mkv
```

---

### Movie

Input:
```
The.Dark.Knight.2008.4K.HDR.BluRay.HEVC.TrueHD-YIFY.mkv
```

Preset **Film Jellyfin** → Output:
```
The Dark Knight (2008).mkv
```

---

### TV show

Input:
```
Breaking.Bad.S01E01.720p.BluRay.x264-GROUP.mkv
```

Preset **Série Jellyfin** → Output:
```
Breaking Bad S01E01.mkv
```

---

## API endpoints

The app exposes 3 REST endpoints used by the frontend.

### `POST /api/list`
Lists files in a folder.

```json
// Request
{ "path": "/path/to/folder" }

// Response
{ "files": [{ "name": "file.mkv", "size": 1073741824 }], "path": "/path/to/folder" }
```

### `POST /api/rename`
Renames files based on a list of old/new name pairs.

```json
// Request
{
  "source_dir": "/path/source",
  "renames": [{ "original": "old.mkv", "renamed": "new.mkv" }]
}
```

### `POST /api/move`
Moves files to a destination folder.

```json
// Request
{
  "source_dir": "/path/source",
  "dest_dir": "/path/destination",
  "files": ["file1.mkv", "file2.mkv"]
}
```

---

## Known limitations

- Only lists files in the **top-level** folder, not recursive
- Rename is **not undoable** — always check the preview first
- If the target filename already exists, that file is skipped
- No authentication — local/private network use only
