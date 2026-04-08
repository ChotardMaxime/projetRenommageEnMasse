"""
MediaRename — Application locale de renommage de fichiers médias
Usage : python app.py [port]
Défaut : http://localhost:5757
"""

from flask import Flask, request, jsonify, render_template_string
import os, re, shutil

app = Flask(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# API Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/list', methods=['POST'])
def list_files():
    path = request.json.get('path', '').strip()
    if not path or not os.path.isdir(path):
        return jsonify({'error': f'Dossier introuvable : {path}'}), 400
    try:
        entries = []
        for name in sorted(os.listdir(path)):
            full = os.path.join(path, name)
            if os.path.isfile(full):
                entries.append({'name': name, 'size': os.path.getsize(full)})
        return jsonify({'files': entries, 'path': path})
    except PermissionError:
        return jsonify({'error': 'Permission refusée sur ce dossier'}), 403

@app.route('/api/rename', methods=['POST'])
def rename_files():
    data = request.json
    source_dir = data.get('source_dir', '').strip()
    renames    = data.get('renames', [])

    if not os.path.isdir(source_dir):
        return jsonify({'error': 'Dossier source invalide'}), 400

    results = []
    for r in renames:
        original = r.get('original', '')
        renamed  = r.get('renamed', '')
        if not original or not renamed or original == renamed:
            continue
        old_path = os.path.join(source_dir, original)
        new_path = os.path.join(source_dir, renamed)
        try:
            if not os.path.exists(old_path):
                results.append({'original': original, 'success': False, 'error': 'Fichier introuvable'})
                continue
            if os.path.exists(new_path):
                results.append({'original': original, 'success': False, 'error': 'Un fichier avec ce nom existe déjà'})
                continue
            os.rename(old_path, new_path)
            results.append({'original': original, 'renamed': renamed, 'success': True})
        except Exception as e:
            results.append({'original': original, 'success': False, 'error': str(e)})

    return jsonify({'results': results})

@app.route('/api/move', methods=['POST'])
def move_files():
    data      = request.json
    source_dir = data.get('source_dir', '').strip()
    dest_dir   = data.get('dest_dir', '').strip()
    files      = data.get('files', [])

    if not os.path.isdir(source_dir):
        return jsonify({'error': 'Dossier source invalide'}), 400
    if not dest_dir:
        return jsonify({'error': 'Dossier destination manquant'}), 400

    try:
        os.makedirs(dest_dir, exist_ok=True)
    except Exception as e:
        return jsonify({'error': f'Impossible de créer le dossier : {e}'}), 400

    results = []
    for f in files:
        src = os.path.join(source_dir, f)
        dst = os.path.join(dest_dir, f)
        try:
            shutil.move(src, dst)
            results.append({'file': f, 'success': True})
        except Exception as e:
            results.append({'file': f, 'success': False, 'error': str(e)})

    return jsonify({'results': results})

# ──────────────────────────────────────────────────────────────────────────────
# HTML / CSS / JS (embedded)
# ──────────────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MediaRename</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=DM+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>
:root {
  --bg:         #0d1117;
  --surface:    #161b22;
  --surface2:   #1c2128;
  --border:     #30363d;
  --text:       #e6edf3;
  --muted:      #7d8590;
  --accent:     #f0883e;
  --accent-dim: rgba(240,136,62,0.12);
  --success:    #3fb950;
  --error:      #f85149;
  --changed:    #79c0ff;
  --mono:       'JetBrains Mono', monospace;
  --ui:         'DM Sans', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--ui);
  font-size: 14px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Header ── */
header {
  padding: 10px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--surface);
  flex-shrink: 0;
}

.logo {
  font-size: 15px;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: -0.3px;
  white-space: nowrap;
  user-select: none;
}
.logo span { color: var(--muted); font-weight: 400; }

.path-input {
  flex: 1;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 7px 11px;
  border-radius: 6px;
  font-family: var(--mono);
  font-size: 12px;
  outline: none;
  transition: border-color 0.15s;
}
.path-input:focus { border-color: var(--accent); }
.path-input::placeholder { color: var(--muted); }

/* ── Buttons ── */
.btn {
  padding: 7px 14px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-family: var(--ui);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.12s;
}
.btn:disabled { opacity: 0.35; cursor: not-allowed; pointer-events: none; }
.btn-primary  { background: var(--accent); color: #0d1117; }
.btn-primary:hover  { filter: brightness(1.1); }
.btn-ghost    { background: transparent; color: var(--muted); border: 1px solid var(--border); }
.btn-ghost:hover    { color: var(--text); border-color: var(--muted); }
.btn-success  { background: var(--success); color: #0d1117; }
.btn-success:hover  { filter: brightness(1.1); }

/* ── Layout ── */
.main {
  display: grid;
  grid-template-columns: 300px 1fr;
  flex: 1;
  min-height: 0;
}

/* ── File panel ── */
.panel-files {
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.panel-header {
  padding: 9px 14px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface2);
  flex-shrink: 0;
}
.panel-label {
  font-size: 10.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.9px;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 6px;
}
.badge {
  display: inline-flex;
  align-items: center;
  padding: 1px 6px;
  border-radius: 9px;
  font-size: 10px;
  font-weight: 600;
  background: var(--accent-dim);
  color: var(--accent);
}
.select-all-btn {
  font-size: 11px;
  color: var(--accent);
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--ui);
  padding: 0;
  opacity: 0.8;
}
.select-all-btn:hover { opacity: 1; text-decoration: underline; }

.file-list {
  flex: 1;
  overflow-y: auto;
  padding: 3px 0;
}
.file-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 6px 14px;
  cursor: pointer;
  user-select: none;
  transition: background 0.08s;
}
.file-item:hover { background: var(--surface2); }
.file-item.selected { background: var(--accent-dim); }

.check-box {
  width: 13px; height: 13px;
  border-radius: 3px;
  border: 1px solid var(--border);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.1s;
}
.file-item.selected .check-box {
  background: var(--accent);
  border-color: var(--accent);
}
.check-box svg { display: none; }
.file-item.selected .check-box svg { display: block; }

.file-name {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
.file-size {
  font-size: 10px;
  color: var(--muted);
  flex-shrink: 0;
  font-family: var(--mono);
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--muted);
  font-size: 13px;
  gap: 10px;
  padding: 24px;
  text-align: center;
  line-height: 1.6;
}

/* ── Right panel ── */
.panel-right {
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.panel-right-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 0;
}

.section-label {
  font-size: 10.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.9px;
  color: var(--muted);
  margin-bottom: 9px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Presets ── */
.preset-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}
.preset-btn {
  padding: 5px 11px;
  border-radius: 5px;
  border: 1px solid var(--border);
  background: var(--surface2);
  color: var(--text);
  font-size: 12px;
  font-family: var(--ui);
  cursor: pointer;
  transition: all 0.12s;
  display: flex;
  align-items: center;
  gap: 5px;
}
.preset-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-dim);
}
.preset-tag {
  font-size: 9.5px;
  background: rgba(255,255,255,0.06);
  padding: 1px 5px;
  border-radius: 3px;
  color: var(--muted);
}

/* ── Rules ── */
.rules-container { display: flex; flex-direction: column; gap: 5px; }
.rule-row {
  display: flex;
  align-items: center;
  gap: 7px;
}
.rule-input {
  flex: 1;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 6px 9px;
  border-radius: 5px;
  font-family: var(--mono);
  font-size: 11.5px;
  outline: none;
  transition: border-color 0.12s;
  min-width: 0;
}
.rule-input:focus { border-color: var(--accent); }
.rule-input::placeholder { color: var(--muted); }
.rule-arrow { color: var(--muted); font-size: 13px; flex-shrink: 0; }
.rule-del {
  background: none; border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 13px;
  padding: 3px 5px;
  border-radius: 4px;
  line-height: 1;
  flex-shrink: 0;
  transition: color 0.1s;
}
.rule-del:hover { color: var(--error); }
.rules-hint {
  font-size: 11.5px;
  color: var(--muted);
  font-style: italic;
  padding: 2px 0;
}

/* ── Preview ── */
.preview-container { display: flex; flex-direction: column; gap: 4px; }
.preview-item {
  display: grid;
  grid-template-columns: 1fr 16px 1fr;
  align-items: center;
  gap: 8px;
  padding: 7px 11px;
  background: var(--surface2);
  border-radius: 6px;
  border: 1px solid var(--border);
  transition: border-color 0.1s;
}
.preview-item.changed { border-color: rgba(121,192,255,0.25); background: rgba(121,192,255,0.04); }
.pv-name {
  font-family: var(--mono);
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pv-original { color: var(--muted); }
.pv-new      { color: var(--changed); }
.pv-same     { color: var(--muted); font-style: italic; }
.pv-arrow    { color: var(--muted); font-size: 11px; text-align: center; }
.preview-hint {
  font-size: 12px; color: var(--muted);
  font-style: italic; padding: 8px 0;
}

.divider { border: none; border-top: 1px solid var(--border); }

/* ── Footer ── */
footer {
  padding: 10px 20px;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--surface);
  flex-shrink: 0;
  flex-wrap: wrap;
}
.footer-info { font-size: 12px; color: var(--muted); flex-shrink: 0; }
.footer-right {
  display: flex; align-items: center; gap: 9px;
  margin-left: auto; flex-wrap: wrap;
}
.dest-input { width: 260px; }

/* ── Toasts ── */
#toasts {
  position: fixed; bottom: 72px; right: 18px;
  display: flex; flex-direction: column; gap: 7px;
  z-index: 999; pointer-events: none;
}
.toast {
  padding: 9px 14px;
  border-radius: 7px;
  font-size: 12.5px;
  font-weight: 500;
  border-left: 3px solid;
  background: var(--surface);
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  animation: tIn .18s ease, tOut .25s 2.75s ease forwards;
  max-width: 280px;
}
.toast.success { border-color: var(--success); color: var(--success); }
.toast.error   { border-color: var(--error);   color: var(--error);   }
.toast.info    { border-color: var(--accent);   color: var(--accent);  }
@keyframes tIn  { from { transform: translateX(14px); opacity:0 } to { transform:none; opacity:1 } }
@keyframes tOut { to   { transform: translateX(14px); opacity:0 } }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
</style>
</head>
<body>

<header>
  <span class="logo">▶ Media<span>Rename</span></span>
  <input id="sourceDir" class="path-input"
    placeholder="/home/max/torrents/downloads"
    onkeydown="if(event.key==='Enter') loadFiles()">
  <button class="btn btn-primary" onclick="loadFiles()">Charger</button>
</header>

<div class="main">

  <!-- ── Fichiers ── -->
  <div class="panel-files">
    <div class="panel-header">
      <span class="panel-label">
        Fichiers <span class="badge" id="fileCount">0</span>
      </span>
      <button class="select-all-btn" onclick="toggleAll()">tout / rien</button>
    </div>
    <div class="file-list" id="fileList">
      <div class="empty-state">
        <span style="font-size:30px;opacity:.4">📁</span>
        Entrez le chemin du dossier<br>contenant tes torrents
      </div>
    </div>
  </div>

  <!-- ── Droite ── -->
  <div class="panel-right">
    <div class="panel-right-scroll">

      <!-- Presets -->
      <div>
        <div class="section-label">Presets rapides</div>
        <div class="preset-grid">
          <button class="preset-btn" onclick="applyPreset('clean')">🧹 Nettoyer <span class="preset-tag">torrent</span></button>
          <button class="preset-btn" onclick="applyPreset('movie')">🎬 Film <span class="preset-tag">Jellyfin</span></button>
          <button class="preset-btn" onclick="applyPreset('series')">📺 Série <span class="preset-tag">Jellyfin</span></button>
          <button class="preset-btn" onclick="applyPreset('dots')">· → espaces</button>
          <button class="preset-btn" onclick="applyPreset('clear')" style="color:var(--muted)">✕ Vider</button>
        </div>
      </div>

      <hr class="divider">

      <!-- Règles -->
      <div>
        <div class="section-label">Règles regex <span style="font-size:10px;color:var(--muted);text-transform:none;letter-spacing:0;font-weight:400">appliquées dans l'ordre sur le nom (sans extension)</span></div>
        <div class="rules-container" id="rulesList"></div>
        <button class="btn btn-ghost" style="margin-top:8px;font-size:12px" onclick="addRule('','')">+ Ajouter une règle</button>
      </div>

      <hr class="divider">

      <!-- Aperçu -->
      <div>
        <div class="section-label">
          Aperçu
          <span class="badge" id="changedCount">0</span>
          <span style="font-size:10px;color:var(--muted);text-transform:none;letter-spacing:0;font-weight:400">changements</span>
        </div>
        <div class="preview-container" id="previewList">
          <div class="preview-hint">Charge un dossier et configure des règles pour prévisualiser</div>
        </div>
      </div>

    </div>

    <!-- Footer -->
    <footer>
      <span class="footer-info" id="footerInfo">Aucun fichier</span>
      <div class="footer-right">
        <input id="destDir" class="path-input dest-input"
          placeholder="/media/jellyfin/films  (optionnel)">
        <button class="btn btn-ghost" id="renameBtn" onclick="doRename()" disabled>Renommer</button>
        <button class="btn btn-success" id="moveBtn" onclick="doRenameAndMove()" disabled>Renommer + Déplacer →</button>
      </div>
    </footer>
  </div>
</div>

<div id="toasts"></div>

<script>
// ── État ────────────────────────────────────────────────────────────────────
const state = {
  sourceDir: '',
  files: [],   // {name, size, selected}
  rules: [],   // {find, replace}
};

// ── Utils ────────────────────────────────────────────────────────────────────
function fmt(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b/1024).toFixed(1) + ' KB';
  if (b < 1073741824) return (b/1048576).toFixed(1) + ' MB';
  return (b/1073741824).toFixed(2) + ' GB';
}
function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function toast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.getElementById('toasts').appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

// ── Charger les fichiers ─────────────────────────────────────────────────────
async function loadFiles() {
  const path = document.getElementById('sourceDir').value.trim();
  if (!path) { toast('Entrez un chemin de dossier', 'error'); return; }
  try {
    const r = await fetch('/api/list', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({path})
    });
    const d = await r.json();
    if (!r.ok) { toast(d.error || 'Erreur serveur', 'error'); return; }
    state.sourceDir = path;
    state.files = d.files.map(f => ({...f, selected: true}));
    renderFiles();
    renderPreview();
    toast(`${state.files.length} fichier${state.files.length !== 1 ? 's' : ''} chargé${state.files.length !== 1 ? 's' : ''}`, 'success');
  } catch(e) {
    toast('Impossible de joindre le serveur', 'error');
  }
}

function renderFiles() {
  document.getElementById('fileCount').textContent = state.files.length;
  const list = document.getElementById('fileList');
  if (!state.files.length) {
    list.innerHTML = '<div class="empty-state">Aucun fichier dans ce dossier</div>';
    updateFooter(); return;
  }
  list.innerHTML = state.files.map((f, i) => `
    <div class="file-item ${f.selected ? 'selected' : ''}" onclick="toggleFile(${i})">
      <div class="check-box">
        <svg width="9" height="7" viewBox="0 0 9 7"><path d="M1 3.5L3.2 5.8L8 1" stroke="#0d1117" stroke-width="1.6" stroke-linecap="round" fill="none"/></svg>
      </div>
      <span class="file-name" title="${esc(f.name)}">${esc(f.name)}</span>
      <span class="file-size">${fmt(f.size)}</span>
    </div>`).join('');
  updateFooter();
}

function toggleFile(i) {
  state.files[i].selected = !state.files[i].selected;
  renderFiles();
  renderPreview();
}
function toggleAll() {
  const any = state.files.some(f => f.selected);
  state.files.forEach(f => f.selected = !any);
  renderFiles();
  renderPreview();
}
function updateFooter() {
  const sel = state.files.filter(f => f.selected);
  document.getElementById('footerInfo').textContent =
    `${sel.length} fichier${sel.length !== 1 ? 's' : ''} sélectionné${sel.length !== 1 ? 's' : ''}`;
  const hasChange = sel.some(f => applyRules(f.name) !== f.name);
  document.getElementById('renameBtn').disabled = !hasChange;
  document.getElementById('moveBtn').disabled   = sel.length === 0;
}

// ── Règles ───────────────────────────────────────────────────────────────────
function addRule(find = '', replace = '') {
  state.rules.push({find, replace});
  renderRules();
  renderPreview();
}
function removeRule(i) {
  state.rules.splice(i, 1);
  renderRules();
  renderPreview();
}
function updateRule(i, field, val) {
  state.rules[i][field] = val;
  renderPreview();
  updateFooter();
}
function renderRules() {
  const el = document.getElementById('rulesList');
  if (!state.rules.length) {
    el.innerHTML = '<div class="rules-hint">Aucune règle — utilisez un preset ou ajoutez-en une manuellement</div>';
    return;
  }
  el.innerHTML = state.rules.map((r, i) => `
    <div class="rule-row">
      <input class="rule-input" placeholder="Pattern regex  ex: \\." value="${esc(r.find)}"
        oninput="updateRule(${i},'find',this.value)">
      <span class="rule-arrow">→</span>
      <input class="rule-input" placeholder="Remplacement  ex: (vide = supprimer)" value="${esc(r.replace)}"
        oninput="updateRule(${i},'replace',this.value)">
      <button class="rule-del" onclick="removeRule(${i})" title="Supprimer">✕</button>
    </div>`).join('');
}

// ── Logique de transformation ────────────────────────────────────────────────
function applyRules(filename) {
  const dot = filename.lastIndexOf('.');
  let base   = dot > 0 ? filename.slice(0, dot) : filename;
  const ext  = dot > 0 ? filename.slice(dot)    : '';

  for (const r of state.rules) {
    if (!r.find) continue;
    try {
      base = base.replace(new RegExp(r.find, 'gi'), r.replace);
    } catch(e) { /* regex invalide */ }
  }
  base = base.replace(/\s{2,}/g, ' ').trim();
  return base + ext;
}

// ── Presets ──────────────────────────────────────────────────────────────────
const BASE_CLEAN = [
  { find: '\\.', replace: ' ' },
  { find: '\\b(2160p|4K|UHD|HDR10\\+?|HDR|1080p|720p|576p|480p)\\b', replace: '' },
  { find: '\\b(BluRay|BDRip|BDRemux|WEB-DL|WEBRip|HDTV|DVDRip|DVDScr|AMZN|NF|DSNP|ATVP|HMAX|PCOK)\\b', replace: '' },
  { find: '\\b(x264|x265|H264|H\\.264|H265|H\\.265|HEVC|AVC|XviD|DivX|AV1)\\b', replace: '' },
  { find: '\\b(AAC2?\\.0|AAC|AC3|EAC3|MP3|DTS|TrueHD|Atmos|DD5\\.1|DD\\+)\\b', replace: '' },
  { find: '\\b(FRENCH|MULTI|VOSTFR|VFF|TRUEFRENCH|VO|VF|MULTi|DUBBED|SUBBED)\\b', replace: '' },
  { find: '-[A-Za-z0-9]{2,}$', replace: '' },
];

const PRESETS = {
  dots:   [{ find: '\\.', replace: ' ' }],
  clean:  BASE_CLEAN.map(r => ({...r})),
  movie: [
    ...BASE_CLEAN.map(r => ({...r})),
    { find: '\\s+((?:19|20)\\d{2})\\s*$', replace: ' ($1)' },
  ],
  series: [
    ...BASE_CLEAN.map(r => ({...r})),
    { find: '\\b(s)(\\d{2})(e)(\\d{2})\\b', replace: 'S$2E$4' },
  ],
  clear: [],
};

function applyPreset(name) {
  state.rules = PRESETS[name].map(r => ({...r}));
  renderRules();
  renderPreview();
  updateFooter();
  if (name !== 'clear') toast(`Preset "${name}" chargé`, 'info');
}

// ── Aperçu ───────────────────────────────────────────────────────────────────
function renderPreview() {
  const sel = state.files.filter(f => f.selected);
  const el  = document.getElementById('previewList');

  if (!sel.length) {
    el.innerHTML = '<div class="preview-hint">Aucun fichier sélectionné</div>';
    document.getElementById('changedCount').textContent = '0';
    updateFooter(); return;
  }
  if (!state.rules.length) {
    el.innerHTML = '<div class="preview-hint">Configure des règles ou choisis un preset pour voir l\'aperçu</div>';
    document.getElementById('changedCount').textContent = '0';
    updateFooter(); return;
  }

  let changed = 0;
  el.innerHTML = sel.map(f => {
    const nw = applyRules(f.name);
    const ok = nw !== f.name;
    if (ok) changed++;
    return `
      <div class="preview-item ${ok ? 'changed' : ''}">
        <span class="pv-name pv-original" title="${esc(f.name)}">${esc(f.name)}</span>
        <span class="pv-arrow">${ok ? '→' : '='}</span>
        <span class="pv-name ${ok ? 'pv-new' : 'pv-same'}" title="${esc(nw)}">${esc(nw)}</span>
      </div>`;
  }).join('');
  document.getElementById('changedCount').textContent = changed;
  updateFooter();
}

// ── Actions serveur ──────────────────────────────────────────────────────────
function getRenames() {
  return state.files
    .filter(f => f.selected)
    .map(f => ({original: f.name, renamed: applyRules(f.name)}))
    .filter(r => r.original !== r.renamed);
}

async function doRename() {
  const renames = getRenames();
  if (!renames.length) { toast('Aucun changement à appliquer', 'info'); return; }

  const r = await fetch('/api/rename', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({source_dir: state.sourceDir, renames})
  });
  const d = await r.json();
  let ok = 0, fail = 0;
  for (const res of d.results) {
    if (res.success) {
      const f = state.files.find(f => f.name === res.original);
      if (f) f.name = res.renamed;
      ok++;
    } else { fail++; }
  }
  renderFiles();
  renderPreview();
  if (ok)   toast(`${ok} fichier${ok > 1 ? 's' : ''} renommé${ok > 1 ? 's' : ''}`, 'success');
  if (fail) toast(`${fail} erreur${fail > 1 ? 's' : ''} — voir la console`, 'error');
}

async function doRenameAndMove() {
  const destDir = document.getElementById('destDir').value.trim();
  if (!destDir) { toast('Précise un dossier destination', 'error'); return; }

  // 1. Renommer d'abord
  const renames = getRenames();
  if (renames.length) {
    const r = await fetch('/api/rename', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({source_dir: state.sourceDir, renames})
    });
    const d = await r.json();
    for (const res of d.results.filter(r => r.success)) {
      const f = state.files.find(f => f.name === res.original);
      if (f) f.name = res.renamed;
    }
  }

  // 2. Déplacer
  const toMove = state.files.filter(f => f.selected).map(f => f.name);
  const r2 = await fetch('/api/move', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({source_dir: state.sourceDir, dest_dir: destDir, files: toMove})
  });
  const d2 = await r2.json();
  if (!r2.ok) { toast(d2.error || 'Erreur lors du déplacement', 'error'); return; }

  const movedNames = d2.results.filter(r => r.success).map(r => r.file);
  const ok   = movedNames.length;
  const fail = d2.results.filter(r => !r.success).length;

  state.files = state.files.filter(f => !movedNames.includes(f.name));
  renderFiles();
  renderPreview();
  if (ok)   toast(`${ok} fichier${ok > 1 ? 's' : ''} déplacé${ok > 1 ? 's' : ''} → ${destDir}`, 'success');
  if (fail) toast(`${fail} erreur${fail > 1 ? 's' : ''} lors du déplacement`, 'error');
}

// ── Init ─────────────────────────────────────────────────────────────────────
renderRules();
</script>
</body>
</html>"""

# ──────────────────────────────────────────────────────────────────────────────
# Lancement
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5757
    print(f"\n  ▶ MediaRename  →  http://localhost:{port}\n")
    app.run(host='0.0.0.0', port=port, debug=False)
