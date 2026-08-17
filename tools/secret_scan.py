#!/usr/bin/env python3
"""Scan modified/new vault notes for hardcoded secrets. Pure Python, no deps.

Runs before the vault is committed. It is the last gate between "I pasted a
token into a note while debugging" and a permanent entry in git history.

FAIL-CLOSED contract — the exit codes are the API:
  0 = scanned, clean
  1 = findings (printed: file, line, pattern name — NEVER the value)
  2 = could NOT scan (no git, not a repo). The caller MUST stop:
      a scanner that did not run is not a scanner that approved.

Design notes worth keeping if you fork this:

* It never prints the matched value. A secret that reaches your terminal has
  left the machine (scrollback, screen share, an agent's context). You get the
  file, the line number and which pattern fired — enough to go look yourself.
* For generic assignments (`token = ...`) it judges the VALUE, not the line.
  `token = makeTestToken(...)` is a function call, `API_KEY=${MY_KEY}` is an
  env reference, `password: <your-password>` is a placeholder. None are secrets,
  and a scanner that flags them gets muted within a week.
* Provider patterns (AWS, Stripe, GitHub, ...) are matched by SHAPE, so they
  fire regardless of context. Those formats do not occur by accident.
"""
import re
import subprocess
import sys
import pathlib

VAULT = pathlib.Path(__file__).resolve().parent.parent

# --- provider patterns: the shape alone identifies a secret -------------------
PROVIDER = [
    ("AWS access key id",      re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Stripe live key",        re.compile(r"\b(?:sk|rk)_live_[0-9a-zA-Z]{16,}")),
    ("GitHub token",           re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[0-9A-Za-z]{36,}\b")),
    ("GitHub fine-grained PAT", re.compile(r"\bgithub_pat_[0-9A-Za-z_]{50,}\b")),
    ("OpenAI API key",         re.compile(r"\bsk-(?:proj-)?[0-9A-Za-z_-]{32,}\b")),
    ("Anthropic API key",      re.compile(r"\bsk-ant-[0-9A-Za-z_-]{32,}\b")),
    ("Google API key",         re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token",            re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}")),
    ("private key block",      re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("JSON Web Token",         re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
]

# --- generic assignment: judge the VALUE, not the line -----------------------
ASSIGN = re.compile(
    r"""(?ix)
    \b(password|passwd|secret|token|api[_-]?key|access[_-]?key|auth)\b
    \s*[:=]\s*
    (?P<q>["'`]?)(?P<val>[^\s"'`,;]{6,})(?P=q)
    """
)

# A value that matches any of these is not a secret. Anchored on purpose:
# `password` is a placeholder, `password123` is somebody's actual password.
NOT_A_SECRET = [
    re.compile(r"^\w+\s*\(.*$"),                       # makeTestToken(...) — a call
    re.compile(r"^(?:process\.env|os\.environ|ENV)\b"),  # env reference
    re.compile(r"^[$%]?[{(]"),                          # ${VAR}, %(var)s, $(cmd)
    re.compile(r"^<.*>$"),                              # <your-token>
    re.compile(r"^\{\{.*\}\}$"),                        # {{TEMPLATE}}
    re.compile(r"^(?:x{3,}|\*{3,}|\.{3,}|-{3,})$"),     # xxx, ***, ...
    re.compile(r"^(?i:changeme|placeholder|redacted|example|sample|dummy|"
               r"password|secret|token|apikey|api_key|yourpassword|"
               r"your_password|none|null|true|false)$"),
]


def is_placeholder(value: str) -> bool:
    return any(p.match(value) for p in NOT_A_SECRET)


def scan_text(text: str):
    """Yield (line_number, pattern_name). Never yields the value itself."""
    for n, line in enumerate(text.splitlines(), 1):
        for name, rx in PROVIDER:
            if rx.search(line):
                yield n, name
                break
        else:
            m = ASSIGN.search(line)
            if m and not is_placeholder(m.group("val")):
                yield n, "cleartext credential assignment"


def changed_notes():
    """Modified/new .md files, per git. Committed history is not re-scanned."""
    r = subprocess.run(["git", "-C", str(VAULT), "status", "--porcelain"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("git status failed — is the vault a git repo?", file=sys.stderr)
        sys.exit(2)
    for line in r.stdout.splitlines():
        rel = line[3:].strip().strip('"')
        if rel.endswith(".md") and (VAULT / rel).exists():
            yield rel


def main():
    findings = []
    for rel in changed_notes():
        try:
            text = (VAULT / rel).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"could not read {rel}: {e}", file=sys.stderr)
            return 2
        for n, name in scan_text(text):
            findings.append((rel, n, name))

    for rel, n, name in findings:
        print(f"  {rel}:{n}\n      -> {name}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
