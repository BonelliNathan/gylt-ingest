# Snippet — fusionner dans le skill `/today` existant

> Copier les sections ci-dessous dans `{AGENT_FOLDER}/Skills/today.md` (ou skill équivalent « plan du jour »).

---

## Step 0.5 — Content ingestion (YouTube + Instagram, non-blocking)

Run the Python pipeline **before** reading context (no AI in Python — extraction/transcription only).

**Command** (from vault root):

```bash
cd "{SCRIPTS_DIR}" && ./run_ingest.sh
```

**If `venv/` or `run_ingest.sh` missing** → set `INGEST_SUMMARY = "⚠️ Ingestion non configurée — lancer setup.sh dans {SCRIPTS_DIR}"` and continue.

**If command fails** → capture stderr, set `INGEST_SUMMARY` with error summary, continue.

**On success** → parse stdout for counts (`[OK]`, `[SKIP]`, `[ERROR]`) and set:

```
INGEST_SUMMARY = "YouTube: … | Telegram: … links | Instagram: …"
```

Order: YouTube → `telegram_fetch_links.py` → `instagram_ingest.py`.

Do not block `/today` if ingestion fails entirely.

---

## Step 2.15 — Process RAW content inbox (agent IA)

**After Step 0.5**. Scan:

- `{SCRIPTS_DIR}/Inbox/Youtube/*.md`
- `{SCRIPTS_DIR}/Inbox/Instagram/*.md`

Keep only notes with `status: raw` in frontmatter.

**Process ALL RAW notes** — no limit, no deferral.

**Philosophy**: transcript = index of topics; reliable content from `WebSearch`.

**For each RAW note**:

1. Scan transcript → 2–5 topics/tools
2. `WebSearch` each topic
3. Fill RAW sections: `## AI Processing`, `## Related Concepts`, `## Actionable Ideas`
4. Create knowledge notes in `{KNOWLEDGE_DIR}/{subfolder}/` (self-contained, 80–200 lines if warranted)
5. Update `{KNOWLEDGE_DIR}/INDEX.md` → `## Cas d'usage — index rapide`
6. Move to `{SCRIPTS_DIR}/Inbox/_archived/YYYY-MM-DD/` ; set `status: processed`

**Knowledge note template** (minimal):

```markdown
---
date: YYYY-MM-DD
source: "[[path/to/archived/raw]]"
tags: [domain, keyword]
status: new
type: knowledge
---

# [Titre explicite]

## En une phrase
…

## Contexte
…

## Comment ça marche
…

## Points clés
- …

## Possibilités et cas d'usage (général)
- **Situation** / **Usage** / **Bénéfice**

## Voir aussi
- [[wikilink]]
```
