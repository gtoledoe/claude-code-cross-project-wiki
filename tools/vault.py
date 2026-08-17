#!/usr/bin/env python3
"""Vault health tools. Pure Python, no dependencies, no third-party installs.

Two commands:
  freshness  — report notes that are past review or marked stale and forgotten
  ledger     — index `type: decision` notes into a hash-chained JSONL

Both are READ-ONLY over your notes: neither ever edits a note. The only file
this script writes is `decisions.jsonl`, and only by appending.

That is a deliberate boundary, not an implementation detail. See "Who marks a
document stale?" in `_wiki-protocol.md`: a tool can detect, only a human can
decide. A script that silently flips `status: active` to `stale` on a timer
would be wrong about your one-year-old ADR that is still perfectly valid.
"""
import sys
import re
import json
import hashlib
import subprocess
import datetime
import pathlib

VAULT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = VAULT / "decisions.jsonl"
SKIP = ("/.obsidian/", "/.git/", "/tools/", "/venv/", "/node_modules/")

# Historical record types never expire — a session summary from last year is
# not "outdated", it is what happened. Reporting them is noise that teaches
# people to ignore the report.
HISTORICAL = {"summary"}


# --- minimal frontmatter parser (no PyYAML dependency) -----------------------
def frontmatter(text):
    """Extract YAML frontmatter. Handles `key: value` pairs only — enough for
    the fields this protocol defines, and it never fails on a weird note."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        if line[0] in " \t":          # list continuation: out of scope
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def notes():
    for f in sorted(VAULT.rglob("*.md")):
        if any(x in str(f) for x in SKIP):
            continue
        try:
            yield f, f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue


def as_date(s):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s or "")
    if not m:
        return None
    try:
        return datetime.date(*map(int, m.groups()))
    except ValueError:
        return None


def git(*args):
    try:
        r = subprocess.run(["git", "-C", str(VAULT), *args],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


# --- freshness ---------------------------------------------------------------
# Reports. Never archives, never edits. Two signals, both opt-in or bounded:
#   1. `review_after: YYYY-MM-DD` — an expiry date YOU set on notes that have
#      one (a runbook pinned to a version, a cost analysis for one month).
#      No field, no expiry. Most notes never get one, and that is correct.
#   2. `status: stale` untouched for >N days — the ugly case: you flagged it
#      for review months ago and never came back.
def cmd_freshness(argv):
    today = datetime.date.today()
    days = 60
    if "--days" in argv:
        try:
            days = int(argv[argv.index("--days") + 1])
        except (IndexError, ValueError):
            pass

    expired, forgotten, undated = [], [], []
    total = 0
    for f, text in notes():
        fm = frontmatter(text)
        if not fm:
            continue
        total += 1
        rel = str(f.relative_to(VAULT))

        review = as_date(fm.get("review_after", ""))
        if review and review < today:
            expired.append((rel, (today - review).days, fm.get("title", "")))
            continue

        if fm.get("status") == "stale" and fm.get("type") not in HISTORICAL:
            updated = as_date(fm.get("updated", ""))
            if updated and (today - updated).days > days:
                forgotten.append((rel, (today - updated).days, fm.get("title", "")))
            elif not updated:
                undated.append(rel)

    print(f"FRESHNESS · {total} notes with frontmatter · {today}\n")
    if expired:
        print(f"# PAST REVIEW DATE — `review_after` has passed ({len(expired)})")
        for rel, d, title in sorted(expired, key=lambda x: -x[1]):
            print(f"    +{d:>4}d  {title or rel}")
            print(f"           {rel}")
        print()
    if forgotten:
        print(f"# STALE, UNATTENDED — flagged stale >{days}d ago ({len(forgotten)})")
        for rel, d, title in sorted(forgotten, key=lambda x: -x[1])[:20]:
            print(f"    {d:>4}d  {title or rel}")
        if len(forgotten) > 20:
            print(f"    ... and {len(forgotten)-20} more")
        print()
    if undated:
        print(f"# STALE WITHOUT `updated` ({len(undated)}) — age cannot be measured")
        for rel in undated[:10]:
            print(f"    {rel}")
        print()
    if not (expired or forgotten or undated):
        print("Nothing to review.")
    print("This command does NOT modify notes. What to do with each item is your call.")
    return 0


# --- decision ledger ---------------------------------------------------------
# Indexes the `type: decision` notes you already have. It does not invent a new
# format: the note stays the source of truth. The ledger answers what a loose
# file cannot — WAS THIS DECISION REWRITTEN OR DELETED AFTER IT WAS MADE?
# Append-only: correcting an entry means adding a new one, never editing.
def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def entry_hash(e):
    """Hash of the entry's content, excluding entry_hash itself. It MUST be the
    same function at sign time and at verify time — otherwise verification
    validates something other than what was signed, and the chain proves
    nothing."""
    return sha(json.dumps({k: e[k] for k in sorted(e) if k != "entry_hash"},
                          ensure_ascii=False, sort_keys=True))


def read_ledger():
    if not LEDGER.exists():
        return []
    out = []
    for i, line in enumerate(LEDGER.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"ledger corrupt at line {i}", file=sys.stderr)
            sys.exit(2)
    return out


def decisions():
    for f, text in notes():
        fm = frontmatter(text)
        if fm.get("type") != "decision":
            continue
        body = text[text.find("\n---", 3) + 4:] if text.startswith("---") else text
        yield {
            "file": str(f.relative_to(VAULT)),
            "title": fm.get("title", ""),
            "project": fm.get("project", ""),
            "status": fm.get("status", ""),
            "created": fm.get("created", ""),
            "hash": sha(body.strip()),
        }


def cmd_ledger(argv):
    mode = argv[0] if argv else "verify"
    prev = read_ledger()
    last = {e["file"]: e for e in prev}
    current = {d["file"]: d for d in decisions()}

    new     = [d for f, d in current.items() if f not in last]
    changed = [d for f, d in current.items()
               if f in last and last[f]["hash"] != d["hash"]]
    missing = [f for f in last if f not in current]

    if mode == "verify":
        print(f"LEDGER · {len(current)} decisions in vault · "
              f"{len(prev)} entries recorded\n")
        broken = reason = None
        for i, e in enumerate(prev):
            expected = prev[i - 1]["entry_hash"] if i else None
            if e.get("prev") != expected:
                broken, reason = i + 1, "`prev` pointer does not match"
                break
            if e.get("entry_hash") != entry_hash(e):
                broken, reason = i + 1, "entry was altered after signing"
                break
        if prev:
            print("  OK  chain intact" if broken is None
                  else f"  !!  chain BROKEN at line {broken} — {reason}")
        if new:
            print(f"  ·  {len(new)} unrecorded (run: ledger sync)")
        if changed:
            print(f"  ·  {len(changed)} modified since they were recorded")
        if missing:
            print(f"  !!  {len(missing)} recorded but NO LONGER EXIST:")
            for f in missing[:10]:
                print(f"      {f}")
        if not (new or changed or missing) and prev:
            print("  OK  up to date")
        return 1 if (broken is not None or missing) else 0

    if mode == "sync":
        if not (new or changed):
            print("Nothing to record.")
            return 0
        commit = git("rev-parse", "--short", "HEAD") or "no-commit"
        today = datetime.date.today().isoformat()
        prev_hash = prev[-1]["entry_hash"] if prev else None
        lines = []
        for d in new + changed:
            e = dict(d)
            e["ts"] = today
            e["commit"] = commit
            e["kind"] = "recorded" if d in new else "modified"
            e["prev"] = prev_hash
            e["entry_hash"] = entry_hash(e)
            prev_hash = e["entry_hash"]
            lines.append(json.dumps(e, ensure_ascii=False, sort_keys=True))
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"Recorded: {len(new)} new · {len(changed)} modified -> decisions.jsonl")
        return 0

    print(f"unknown mode: {mode}", file=sys.stderr)
    return 2


USAGE = """usage: python3 tools/vault.py <command>

  freshness [--days N]   Report past-review and forgotten-stale notes. Read-only.
  ledger verify          Verify the hash chain and report drift.
  ledger sync            Record new or modified decisions (append-only).
"""


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        return 2
    cmd, argv = sys.argv[1], sys.argv[2:]
    if cmd == "freshness":
        return cmd_freshness(argv)
    if cmd == "ledger":
        return cmd_ledger(argv)
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main())
