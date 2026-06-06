---
name: add-feed
description: Add a new RSS/Atom source to config/feeds.yaml. Validates the feed is live and parseable (same fetch path as the daily pipeline) before appending it. Use when the user wants to add, register, or wire up a new feed/source.
disable-model-invocation: true
---

# Add a feed

Adds one source to `config/feeds.yaml` — but only after confirming it actually fetches and parses, so a dead URL never lands in config and silently produces "skipped" every morning.

## Inputs to gather

Ask the user for anything not provided:

- **url** (required) — the RSS/Atom feed URL.
- **id** (required) — short snake_case identifier, unique within `feeds.yaml` (e.g. `bankless`, `cointelegraph_nft`). Used in logs and as `source_id`.
- **category** (required) — one of `crypto`, `security`, `regulatory`. This is only a hint to the curation model; final beat assignment still happens in `curate.py`.

Do not invent these. If the user gave a URL only, propose an `id` and `category` and confirm before writing.

## Steps

1. **Validate** the feed using the bundled script (run from the repo root):

   ```bash
   .venv/bin/python .claude/skills/add-feed/validate_feed.py "<url>" --id "<id>"
   ```

   It mirrors `pipeline/ingest._fetch_one` exactly (browser User-Agent, 15s timeout, `feedparser.parse`) and also checks the id is not already taken.
   - On `VALID:` continue.
   - On `INVALID:` stop and report the reason to the user. Do **not** edit `feeds.yaml`. Offer to retry with a corrected URL/id.

2. **Append** the entry to the `feeds:` list in `config/feeds.yaml`, matching the existing one-line, column-aligned style:

   ```yaml
   - { id: <id>,    category: <category>, url: "<url>" }
   ```

   Insert it grouped with feeds of the same category where the file already clusters them. Preserve the file's existing alignment and the leading comment block — make a surgical edit, nothing else.

3. **Confirm** to the user: show the added line and the validation summary (feed title + entry count). Mention that the new source takes effect on the next daily run and is subject to `meta.max_per_beat`.

## Notes

- This skill is intentionally user-invoked only (it edits committed config).
- It does **not** run the full pipeline or commit. Adding the line is the whole job; the user reviews and commits.
- If `.venv/bin/python` is missing, fall back to `python3` (the script only needs `feedparser`, `requests`, `pyyaml`, all in `requirements.txt`).
