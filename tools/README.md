# tools/ — making the protocol executable

The protocol in `docs/_wiki-protocol.md` is conventions. These four files are
the part a machine can check. Pure Python 3 and bash, **no dependencies, no
installs** — copy the folder into your vault root and it works.

```
your-vault/
├── _wiki-protocol.md
├── decisions.jsonl        ← created by `ledger sync`
├── tools/
│   ├── vault.py           ← freshness report + decision ledger
│   ├── secret_scan.py     ← fail-closed secret scan of changed notes
│   ├── close.sh           ← session close: scan → ledger → commit → push
│   ├── test_secret_scan.py
│   └── .gitignore         ← keeps Python bytecode out of your notes repo
└── Projects/
```

Your vault must be a git repo (`git init`) for `close.sh` and the scanner.

---

## `vault.py freshness`

Reports notes that need a human look. **It never edits a note.**

```bash
python3 tools/vault.py freshness
python3 tools/vault.py freshness --days 90   # widen the stale window
```

Two signals, and neither one guesses:

| Signal | Fires when | Why it is opt-in |
|---|---|---|
| `review_after: YYYY-MM-DD` | the date has passed | Only some notes have a knowable expiry — a runbook pinned to a version, a cost analysis for one month. No field, no expiry. |
| `status: stale` + `updated` older than N days | N defaults to 60 | The ugly case: you flagged it for review and never came back. |

`type: summary` notes are **never** reported for age. A session record from last
year is not outdated — it is what happened.

## `vault.py ledger`

Indexes your `type: decision` notes into `decisions.jsonl`, a hash chain where
each entry signs the previous one. The note stays the source of truth; the
ledger answers what a loose file cannot: **was this decision rewritten or
deleted after it was made?**

```bash
python3 tools/vault.py ledger sync     # record new/changed decisions (append-only)
python3 tools/vault.py ledger verify   # check the chain
```

`verify` exit codes: `0` fine · `1` chain broken or a recorded decision is gone.

| Situation | Reported | Exit |
|---|---|---|
| Entry altered after signing | chain BROKEN at line N | 1 |
| Ledger line deleted / reordered | chain BROKEN at line N | 1 |
| Decision note deleted | recorded but NO LONGER EXIST | 1 |
| Decision note edited | modified since recorded | 0 |

That last row is deliberate. Editing a decision is legitimate — decisions get
superseded. What the ledger guarantees is that the edit is *visible*, not that
it is forbidden.

Append-only means append-only: to correct an entry you add a new one. Never
hand-edit `decisions.jsonl` — that is precisely what `verify` is built to catch.

## `secret_scan.py`

Scans **modified and new** `.md` files (per `git status`) for hardcoded
credentials. Committed history is not re-scanned.

```bash
python3 tools/secret_scan.py     # 0 clean · 1 findings · 2 could not scan
```

Three properties worth preserving if you fork it:

- **It never prints the matched value.** A secret that reaches your terminal has
  left the machine — scrollback, a screen share, an agent's context window. You
  get file, line and pattern name; go look yourself.
- **For generic assignments it judges the value, not the line.**
  `token = makeTestToken(...)` is a call, `API_KEY=${MY_KEY}` is a reference,
  `password: <your-password>` is a placeholder. Flag those and the scanner gets
  muted within a week.
- **Exit `2` means "did not run", not "clean".** Callers must stop on it.

Run the battery after touching any pattern:

```bash
python3 tools/test_secret_scan.py     # 17/17 cases passed
```

## `close.sh`

One command at the end of a session: **scan → ledger sync → commit → push.**

```bash
bash tools/close.sh                # generic commit message
bash tools/close.sh my-project     # docs(my-project): session close
```

Idempotent: with no changes it prints `vault unchanged` and exits 0.

**It commits without asking, on purpose.** These are your own notes, not code
under review, and a save that needs approval is a save that gets skipped —
then the vault is out of date exactly when you need it. Keep the "never commit
without approval" rule for your *code* repos.

**It is fail-closed on secrets.** Findings, or a scanner that cannot run at all,
stop the close and commit nothing. A check that fails silently and lets you
through is worse than no check: it buys false confidence.

To plug in your own scanner (keep the 0/1/2 exit contract):

```bash
SECRET_SCAN_CMD="python3 /path/to/your/scanner.py" bash tools/close.sh
```

Wire it into your `/close-session` skill as the last step, after the docs are
written. If you leave it as "run it by hand", it will not get run — the notes
stay on disk, unbacked, and you find out when the disk does.

---

## A note on speed

Everything here walks the vault and reads every `.md`. On a local disk that is
under a second for a few thousand notes. If your vault lives in a
sync-on-demand folder (iCloud Drive, OneDrive Files On-Demand, Dropbox smart
sync), the **first** run can take minutes of pure I/O wait while files are
materialized — the CPU time stays near zero. That is the sync client, not the
script. Later runs are fast.
