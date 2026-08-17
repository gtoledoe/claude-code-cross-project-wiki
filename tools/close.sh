#!/bin/bash
# Mechanical session close for the vault: scan -> ledger -> commit -> push.
# Call it from your /close-session skill (or by hand). Idempotent.
# It NEVER edits a note.
#
#   bash tools/close.sh [project-name]
#
# The commit is automatic on purpose. These are your own notes, not code under
# review, and a save that needs approval is a save that gets skipped — and then
# the vault is out of date exactly when it matters. The "never commit without
# explicit approval" guardrail still applies to your CODE repos.
#
# The secret scan is FAIL-CLOSED. If it finds something, or if it cannot run at
# all, nothing is committed. A check that fails silently and lets you through is
# worse than no check: it buys false confidence.
#
# Swap in your own scanner with:
#   SECRET_SCAN_CMD="python3 /path/to/your/scanner.py" bash tools/close.sh
# It must honour the exit contract: 0 clean · 1 findings · 2 could not scan.
set -uo pipefail

VAULT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$VAULT" || { echo "vault not found: $VAULT" >&2; exit 1; }
[ -d .git ] || { echo "vault is not a git repo — run: git init" >&2; exit 1; }

PROJECT="${1:-}"
SCAN="${SECRET_SCAN_CMD:-python3 $VAULT/tools/secret_scan.py}"

# 0) Nothing to do
if [ -z "$(git status --porcelain)" ]; then
  echo "vault unchanged"
  exit 0
fi

# 1) Secrets, fail-closed.
if ! command -v python3 >/dev/null 2>&1; then
  echo "no python3: cannot scan for secrets. Nothing was committed." >&2
  exit 1
fi
out=$($SCAN 2>&1); rc=$?
case $rc in
  0) ;;
  1) echo "possible secrets in modified notes:"
     echo "$out"
     echo "  Review them before closing. Nothing was committed."
     exit 1 ;;
  *) echo "the secret scanner could NOT run:" >&2
     echo "$out" >&2
     echo "  Fail-closed: nothing was committed." >&2
     exit 1 ;;
esac

# 2) Keep the decision ledger current
python3 "$VAULT/tools/vault.py" ledger sync 2>/dev/null | grep -v '^Nothing' || true

# 3) Commit
n=$(git status --porcelain | wc -l | tr -d ' ')
git add -A
msg="docs: session close"
[ -n "$PROJECT" ] && msg="docs($PROJECT): session close"
git commit -q -m "$msg

$n file(s). Automatic commit from session close.
Decision ledger synced; secret scan clean." || true
echo "vault: committed $n file(s)"

# 4) Push — the actual backup. If it fails, say so; do not break the close.
if git remote get-url origin >/dev/null 2>&1; then
  if git push -q origin HEAD 2>/dev/null; then
    echo "vault: backed up to remote"
  else
    echo "vault: local commit OK, push FAILED — no remote backup"
  fi
fi
