# Cryptoccino

1. Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:

State your assumptions explicitly. If uncertain, ask.
If multiple interpretations exist, present them - don't pick silently.
If a simpler approach exists, say so. Push back when warranted.
If something is unclear, stop. Name what's confusing. Ask.
2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

No features beyond what was asked.
No abstractions for single-use code.
No "flexibility" or "configurability" that wasn't requested.
No error handling for impossible scenarios.
If you write 200 lines and it could be 50, rewrite it.
Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:

Don't "improve" adjacent code, comments, or formatting.
Don't refactor things that aren't broken.
Match existing style, even if you'd do it differently.
If you notice unrelated dead code, mention it - don't delete it.
When your changes create orphans:

Remove imports/variables/functions that YOUR changes made unused.
Don't remove pre-existing dead code unless asked.
The test: Every changed line should trace directly to the user's request.

4. Goal-Driven Execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

"Add validation" → "Write tests for invalid inputs, then make them pass"
"Fix the bug" → "Write a test that reproduces it, then make it pass"
"Refactor X" → "Ensure tests pass before and after"
For multi-step tasks, state a brief plan:

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

A daily Web3 news brief in the style of Morning Brew. Static site on GitHub Pages, regenerated each morning by a Python pipeline.

## Audience

Crypto-native operators, builders, security people, fund and PM types. They know the jargon. The brief is meant to be read in five minutes over an espresso.

## Beats (fixed order)

1. **The Tape** — market state and the majors.
2. **Projects & Money** — launches, upgrades, funding, DeFi.
3. **Security Desk** — exploits and threat intel. Skim only, no deep technical breakdowns.
4. **On the Hill** — regulators and policy.

A beat may be skipped entirely on a slow day. Each beat is capped (see `config/feeds.yaml` → `meta.max_per_beat`).

## Daily flow

GitHub Actions cron triggers `pipeline/run.py`:

1. **Ingest** (`pipeline/ingest.py`) pulls every feed in `config/feeds.yaml`. Each fetch must fail independently — one dead feed never kills the run.
2. **Store** (`pipeline/store.py`) dedupes against the SQLite `seen` table in `data/cryptoccino.db`. Keyed by URL hash with first-seen date.
3. **Curate** (`pipeline/curate.py`) makes a single Claude call. Same-day cross-source clustering of duplicate stories happens here, inside the model, not in code. Loads `prompts/brief_system.md` as the system prompt.
4. **Render** (`pipeline/render.py`) writes a dated Jekyll post to `_posts/YYYY-MM-DD-cryptoccino.md`.
5. The workflow commits the new post **and** the updated `data/cryptoccino.db` back to `main`. Pages rebuilds and the new issue is live.

## Models

- Primary: `claude-sonnet-4-6` for curation and writing.
- Fallback (cheaper): `claude-haiku-4-5-20251001`.

The curation/writing call is a single shot — selection, clustering, beat assignment, and prose all happen in one pass.

## Deduplication

- The `seen` table in `data/cryptoccino.db` stores URL hashes with their first-seen date.
- `store.filter_unseen` drops anything already in the table before curation runs.
- Cross-source clustering (multiple feeds reporting the same event today) is **not** done in code. The model handles it during curation because it is a judgement call about which version is best.

## Resilience

- `ingest.fetch_feeds` must wrap every per-feed fetch in its own try/except. Log and skip on failure; never raise out of the loop.
- A run with zero usable items should fail loudly (no point publishing an empty issue), but a partial feed failure must not abort the run.

## Repo layout

| Path | Purpose |
|------|---------|
| `config/feeds.yaml` | Feed list, beat metadata, caps. |
| `prompts/brief_system.md` | System prompt for the curation call. Edit here, not in code. |
| `pipeline/` | The Python pipeline (`ingest`, `store`, `curate`, `render`, `run`). |
| `data/cryptoccino.db` | SQLite seen-state. Committed back to `main` each run. |
| `_posts/` | Jekyll posts. One per published day. |
| `_layouts/` | Jekyll templates. |
| `assets/` | Static assets for the site. |
| `.github/workflows/` | The daily cron workflow. |

## Naming

The brand and repo are **Cryptoccino**. There is no other name. Earlier drafts used "Doppio Block" — do not reintroduce it in new code, copy, or commit messages.
