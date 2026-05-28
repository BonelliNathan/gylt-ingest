# GYLT Ingest

Pipeline **Python gratuit** (sans IA) pour alimenter un second cerveau Obsidian depuis **YouTube**, **Instagram** et **Telegram**.

```
YouTube playlist ──► youtube_ingest.py     ──► Inbox/Youtube/*.md (RAW)
Telegram chat    ──► telegram_fetch_links  ──► instagram_links.txt
                   instagram_ingest.py    ──► Inbox/Instagram/*.md (RAW)
                                              │
                                              ▼
                                    Agent Cursor / Claude (Step 2.15)
                                              │
                                              ▼
                                    03 - Knowledge/ + archive _archived/
```

**Philosophie** : Python = extraction + transcription (Whisper local, yt-dlp). L'agent IA du vault = résumé, recherche web, notes Knowledge, wikilinks.

---

## Pour les agents — installation automatique

> **Objectif** : un agent Cursor/Claude doit pouvoir cloner ce repo, l'installer, le brancher sur un vault Obsidian existant (ou en créer un minimal), et ajouter rules + skill sans intervention humaine — sauf login Telegram (interactif, une fois).

### Variables à résoudre (demander à l'utilisateur si absentes)

| Variable | Défaut | Description |
|----------|--------|-------------|
| `VAULT_PATH` | workspace courant | Racine du vault Obsidian |
| `SCRIPTS_DIR` | `{VAULT_PATH}/10 - Scripts` | Où cloner/installer ce repo |
| `AGENT_FOLDER` | `{VAULT_PATH}/99 - Cursor` | Dossier rules/skills agent |
| `KNOWLEDGE_DIR` | `{VAULT_PATH}/03 - Knowledge` | Notes Knowledge produites |
| `PLAYLIST_URL` | voir `config.py` | Playlist YouTube à surveiller |

### Procédure agent (ordre strict)

```bash
# 1. Cloner dans le vault (ou chemin choisi)
VAULT_PATH="${VAULT_PATH:-$(pwd)}"
SCRIPTS_DIR="${SCRIPTS_DIR:-$VAULT_PATH/10 - Scripts}"
git clone https://github.com/BonelliNathan/gylt-ingest.git "$SCRIPTS_DIR"

# 2. Setup Python + dossiers inbox
cd "$SCRIPTS_DIR"
chmod +x setup.sh run_ingest.sh
./setup.sh

# 3. Config YouTube — éditer config.py : PLAYLIST_URL

# 4. Config Telegram (optionnel)
cp .env.example .env
# Remplir TELEGRAM_API_ID, TELEGRAM_API_HASH (https://my.telegram.org/apps)
# Puis login interactif (utilisateur requis) :
./venv/bin/python telegram_login.py

# 5. Test
./run_ingest.sh
```

**Prérequis système** : macOS ou Linux, `python3`, `ffmpeg` (`brew install ffmpeg`).

**Toujours** exécuter avec `./venv/bin/python` — jamais le Python système pour pip/run.

### Intégration vault — vault existant

1. **Copier les templates** depuis `docs/templates/` :
   - `cursor-rule-ingest.mdc` → `{VAULT_PATH}/.cursor/rules/gylt-ingest.mdc`
   - `skill-today-ingest-snippet.md` → fusionner dans le skill `/today` existant, ou créer `{AGENT_FOLDER}/Skills/today.md`

2. **Remplacer les placeholders** dans les fichiers copiés :
   - `{VAULT_PATH}`, `{SCRIPTS_DIR}`, `{KNOWLEDGE_DIR}`, `{AGENT_FOLDER}`

3. **Mettre à jour** `AGENTS.md` ou rules vault — ajouter une ligne dans le tableau workflows :
   ```
   Ingestion contenu | cd "{SCRIPTS_DIR}" && ./run_ingest.sh | Step 0.5 /today
   ```

4. **Créer les dossiers vault** s'ils n'existent pas :
   ```bash
   mkdir -p "$KNOWLEDGE_DIR" "$VAULT_PATH/00 - Daily notes"
   ```

5. **Projet vault optionnel** : créer `{VAULT_PATH}/04 - Projects/GYLT-Ingest/INDEX.md` (template dans `docs/templates/project-index.md`).

### Intégration vault — sans vault existant (bootstrap minimal)

L'agent crée cette arborescence :

```
{VAULT_PATH}/
├── AGENTS.md
├── 00 - Daily notes/
├── 03 - Knowledge/
│   └── INDEX.md          # section ## Cas d'usage — index rapide
├── 10 - Scripts/         # ← ce repo cloné ici
└── 99 - Cursor/
    ├── Skills/today.md   # depuis docs/templates/skill-today-minimal.md
    └── config/vault-settings.md
```

Puis copier `.cursor/rules/gylt-ingest.mdc` et lancer `./setup.sh`.

### Checklist post-install (agent)

- [ ] `./run_ingest.sh` exit 0 (ou erreurs Telegram ignorables si `.env` absent)
- [ ] Fichiers RAW dans `Inbox/Youtube/` ou `Inbox/Instagram/` avec `status: raw`
- [ ] Rule Cursor présente dans `.cursor/rules/`
- [ ] Skill `/today` référence Step 0.5 + Step 2.15
- [ ] `config.py` → `PLAYLIST_URL` personnalisée
- [ ] `.env` + `telegram_login.py` si capture Telegram souhaitée

---

## Usage humain

```bash
cd "10 - Scripts"   # ou SCRIPTS_DIR
./run_ingest.sh
```

Ordre : YouTube → Telegram → Instagram.

**Sortie** : notes Markdown Obsidian dans `Inbox/Youtube/{video_id}.md` et `Inbox/Instagram/{hash}.md`.

Frontmatter RAW :

```yaml
type: imported_content
platform: youtube | instagram
status: raw
```

L'agent traite les RAW (WebSearch, notes Knowledge, archive vers `Inbox/_archived/`).

---

## Configuration

| Fichier | Rôle |
|---------|------|
| `config.py` | `PLAYLIST_URL`, `WHISPER_MODEL` (défaut: `tiny`) |
| `instagram_links.txt` | URLs Instagram (manuel + Telegram) |
| `.env` | Credentials Telegram (copier depuis `.env.example`) |
| `telegram_session/` | Session Telethon (après `telegram_login.py`) |
| `processed_videos.json` | Historique idempotent |

### Déduplication

- **YouTube** : `youtube_{video_id}`
- **Instagram** : `instagram_{hash}` (URL normalisée)

### Telegram

| Variable | Exemple | Rôle |
|----------|---------|------|
| `TELEGRAM_CHAT` | `SecondBrain` | Titre dialog, `me`, `@user`, ou id numérique |
| `TELEGRAM_MESSAGE_LIMIT` | `20` | Messages récents à scanner |
| `TELEGRAM_INCREMENTAL` | `1` | Seulement les messages plus récents que la dernière sync |
| `TELEGRAM_MESSAGE_FILTER` | `#gylt` | Optionnel : filtrer par tag |

**Sécurité** : compte Telegram dédié recommandé. Ne jamais commiter `.env` ni `telegram_session/`.

---

## Traitement IA (Step 2.15)

Voir `docs/templates/skill-today-ingest-snippet.md` pour le workflow complet.

Résumé :

1. Scanner `Inbox/Youtube/*.md` + `Inbox/Instagram/*.md` où `status: raw`
2. WebSearch sur les sujets identifiés dans le transcript
3. Créer notes dans `03 - Knowledge/{domaine}/`
4. Mettre à jour `03 - Knowledge/INDEX.md` (cas d'usage)
5. Archiver vers `Inbox/_archived/YYYY-MM-DD/` et passer `status: processed`

---

## Dépannage

| Problème | Action |
|----------|--------|
| `venv not found` | `./setup.sh` |
| Whisper lent | `WHISPER_MODEL = "tiny"` dans config.py |
| Pas de transcript YouTube | Fallback Whisper automatique |
| Ré-ingérer une vidéo | Supprimer entrée dans `processed_videos.json` + note inbox |
| Insta privé | `yt-dlp --cookies-from-browser chrome "URL"` (manuel) |

---

## Licence

MIT — voir [LICENSE](LICENSE).

## Origine

Extrait du vault [get-your-life-together](https://github.com/Zoomma1/get-your-life-together) (projet GYLT). Repo ingestion : https://github.com/BonelliNathan/gylt-ingest
