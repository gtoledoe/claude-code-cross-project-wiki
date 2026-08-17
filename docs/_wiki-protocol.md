# Wiki Protocol — Global Knowledge Base Rules

> Copy this file to your Obsidian vault root: `_wiki-protocol.md`
> Every Claude Code session reads this to understand vault conventions.

---

## Vault Structure

```
Obsidian Vault/
├── _wiki-protocol.md              ← this file
├── _shared/                       ← transversal knowledge
│   ├── _concepts/                 ← reusable technical concepts
│   └── _decisions/                ← decisions that apply to multiple projects
└── Projects/
    ├── {Project-A}/
    │   ├── _index.md              ← project index
    │   ├── _log.md                ← session log
    │   ├── {custom-folders}/      ← project-specific folders
    │   └── raw/                   ← unprocessed sources (read-only)
    ├── {Project-B}/
    └── ...
```

Each project defines its own folders based on its domain. See "Folder Structure" below.

---

## Scope Rule (CRITICAL)

Each Claude Code session operates within **exactly one project**:

- **Writes** only to `Projects/{its-project}/`
- **Reads** (read-only) `_shared/` and other projects' `_index.md`,
  **only when explicitly requested**
- **Never writes** to other projects' folders
- A decision made in Project A **does not apply** to Project B

This is enforced through the scope declaration in each project's `CLAUDE.md`.

---

## Required Frontmatter

Every document must have:

```yaml
---
title: "Descriptive name"
project: project-id
type: concept | decision | problem | runbook | architecture | summary | index
status: draft | active | stale | archived
tags: [relevant, tags]
related: ["[[link1]]", "[[link2]]"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### Optional: `review_after`

```yaml
review_after: YYYY-MM-DD   # optional — only for documents with a knowable expiry
```

Add it when the document has a real expiry date: a runbook pinned to a version,
a cost analysis for one month, a decision that depends on a contract term. Once
the date passes, `tools/vault.py freshness` lists the note.

**If you do not set it, the note never expires.** Most notes should not have
one. A blanket expiry on everything produces a report nobody reads.

### Status Lifecycle

```
draft → active → stale → archived
```

- `draft` — just created, not validated
- `active` — verified and current
- `stale` — may be outdated, review before using
- `archived` — no longer applies, kept for history

### Who marks a document stale?

**You do.** Detecting and marking are separate roles on purpose:

| Actor | Role | Can it change a note? |
|---|---|---|
| `tools/vault.py freshness` | **Detects** and reports candidates | **No.** It never writes to a note — the only file the toolkit writes is the ledger, and only by appending. |
| Claude Code | **Proposes** during a lint or a session close, with evidence | Only after you approve. |
| You | **Decide** and set the field | Yes. |

The reason for the boundary: no threshold knows whether a one-year-old ADR is
still valid. Age is a hint, not a verdict. A script that flipped `active` to
`stale` on a timer would be wrong often enough that you would stop trusting the
field — and then the lifecycle stops meaning anything.

`archived` follows the same rule, with one addition: **nothing is ever deleted.**
An archived document keeps the historical context of why the decision was made.

---

## Document Types

| Type | Location | Purpose |
|------|----------|---------|
| `index` | `_index.md` | Project map and state |
| `decision` | project folders | Architectural Decision Record (ADR) |
| `problem` | project folders | Problem with root cause and solution |
| `runbook` | project folders | Step-by-step reproducible procedure |
| `architecture` | project folders | Diagrams, design, structure |
| `summary` | project folders | Reference document, overview |
| `concept` | `_shared/_concepts/` | Reusable technical knowledge |

---

## Frontmatter Template for Each Type

### Decision (ADR)

```yaml
---
title: "Decision: {name}"
project: {project-id}
type: decision
status: active
tags: [relevant, tags]
related: ["[[related-doc]]"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

## Context
Why did this decision arise?

## Alternatives Evaluated
- Option A: description + trade-offs
- Option B: description + trade-offs

## Decision
What was chosen and why.

## Consequences
- ✅ What improves
- ⚠️ What complicates
```

### Problem

```yaml
---
title: "Problem: {name}"
project: {project-id}
type: problem
status: active
tags: [relevant, tags]
related: ["[[related-decision]]"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

## Symptoms
What was observed, when it occurs.

## Root Cause
Why it occurred.

## Solution Applied
Steps that resolved it.

## Status
✅ Resolved / ⚠️ Workaround / ❌ Unresolved
```

### Runbook

```yaml
---
title: "Runbook: {procedure name}"
project: {project-id}
type: runbook
status: active
tags: [relevant, tags]
related: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

## Purpose
What this accomplishes and when to use it.

## Prerequisites
What must be in place.

## Steps

### 1. Step name
```bash
# commands
```
Expected result: what you should see.

### 2. Step name
...

## Verification
How to confirm success.

## Rollback
How to undo if needed.
```

---

## Wikilink Conventions

- Use `[[exact-filename]]` for internal references
- Create the target page before linking (no orphan links). If the target doesn't exist yet, create a minimal stub first — then create the link:
  ```yaml
  ---
  title: "{Document Title}"
  project: {project-id}
  type: {type}
  status: draft
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  ---
  ```
- If a concept appears in multiple projects → create in `_shared/_concepts/`
- To reference other projects (read-only): use full path `[[Projects/ProjectName/folder/filename]]`

---

## Cross-Project Lookup Flow

When explicitly requested to use knowledge from another project:

1. Read `Projects/{source-project}/_index.md` (read-only)
2. Find the relevant document (read-only)
3. Read the document (read-only)
4. Apply knowledge to current project
5. Document result with reference: `"Based on [[Projects/X/folder/doc]]"`
6. **Never modify** source project

---

## _index.md Template

Every project has an `_index.md`:

```yaml
---
title: "Index — {Project Name}"
project: {project-id}
type: index
status: active
updated: YYYY-MM-DD
---

## Current State
{2-3 lines of project status}

## Folder Structure
- {Folder-1}: description
- {Folder-2}: description
- raw/: unprocessed sources

## Key Documents
- [[folder/document]] — description

## Active Decisions
| Date | Decision | Status |
|------|----------|--------|
| YYYY-MM-DD | [[folder/decision]] | active |

## Known Problems
| Problem | Status |
|---------|--------|
| [[folder/problem]] | resolved |

## Available Runbooks
- [[folder/runbook]] — what it does

## Session Log
→ See [[_log]]
```

---

## _log.md Template

Append-only session history:

```markdown
# Log — {Project Name}

## [YYYY-MM-DD] {type} | {title}
**Type:** ingest | decision | problem-solved | migration | lint
**Session:** what was worked on
**Documents created/updated:** [[links]]
**Pending:** what remains open
```

**Valid types:**
- `ingest` — new knowledge processed
- `decision` — decision made and documented
- `problem-solved` — problem documented
- `migration` — docs migrated to wiki format
- `lint` — vault health check performed

---

## Folder Structure Options

Different project types need different structures. Choose what fits:

### Web Application
```
Arquitectura/ | Documentación Técnica/ | Negocio/ | Infraestructura/ | Runbooks/ | Sesiones/
```

### Infrastructure (Terraform/K8s/Cloud)
```
Arquitectura/ | Decisiones/ | Estado/ | Problemas/ | Runbooks/
```

### FinOps / Cloud Governance
```
Analisis/ | Gobierno/ | Estado/ | Runbooks/ | Sesiones/
```

### Generic / Mixed
```
Decisiones/ | Problemas/ | Runbooks/ | Arquitectura/
```

**The rule:** Name folders after what you search for. Different domains = different names. Protocol stays the same.

---

## Best Practices

### Status Assignments
- New document? Start with `draft`. Promote to `active` after verification.
- Legacy document? Infer status from content age and signals.
- Outdated? Mark `stale` and note what changed.
- No longer applies? Mark `archived`. Never delete.

### Regular Maintenance
- **Monthly:** Run vault lint to surface stale documents
- **Quarterly:** Review archived documents, consolidate if needed
- **On completion:** Update status when work finishes

### Creating New Documents
1. Add complete frontmatter (don't skip created/updated dates)
2. Use appropriate type and folder
3. Create wikilinks to related documents
4. Update `_index.md` with new links
5. Append to `_log.md`

### Updating Existing Documents
1. Change `updated` date
2. Update `status` if needed
3. Update `related` field if new connections exist
4. Note in `_log.md` if major changes

---

## Executable Checks (`tools/`)

Copy `tools/` to your vault root. Pure Python 3 and bash, no dependencies. Full
documentation in `tools/README.md`.

| Command | What it answers | Writes to notes? |
|---|---|---|
| `python3 tools/vault.py freshness` | What should I look at again? | Never |
| `python3 tools/vault.py ledger sync` | Record decisions as they are made | Never (appends to `decisions.jsonl`) |
| `python3 tools/vault.py ledger verify` | Was a decision rewritten or deleted? | Never |
| `python3 tools/secret_scan.py` | Did a credential end up in a note? | Never |
| `bash tools/close.sh [project]` | Close the session: scan → ledger → commit → push | Never |

Two properties hold across all of them:

- **They report, they do not decide.** The lifecycle stays under human control.
  See "Who marks a document stale?" above.
- **`close.sh` is fail-closed on secrets.** Findings — or a scanner that cannot
  run at all — stop the close and commit nothing. A check that fails silently
  and lets you through buys false confidence.

The decision ledger deserves one line of explanation: it is a hash chain over
your `type: decision` notes, where each entry signs the previous one. The note
remains the source of truth. The ledger exists to answer the one question a
loose file cannot — whether a decision was quietly rewritten or deleted after
it was made.

Wire `close.sh` into your close-session routine. Left as a manual step it does
not get run, and the vault sits unbacked on one disk.

---

## Constraints

```
NEVER write to another project's folder
NEVER create wikilinks without creating target page
NEVER delete documents (archive instead)
NEVER let a tool change a document's status by itself — it reports, you decide
NEVER hand-edit decisions.jsonl (append-only; verify exists to catch that)
NEVER commit the vault when the secret scan fails or cannot run
NEVER assume another project's decision applies to yours
ALWAYS add complete frontmatter to new documents
ALWAYS update _log.md after documentation operations
ALWAYS review stale documents before using them
```

---

## Operational Flows

### INGEST (new knowledge)

```
New information appears
  ↓
Discuss relevance with user
  ↓
Create/update page in appropriate folder
  ↓
Identify if transversal → create in _shared/ if needed
  ↓
Update _index.md
  ↓
Append to _log.md
```

### MIGRATION (onboard existing docs)

```
List existing documents
  ↓
Classify each: type + destination folder
  ↓
Propose plan to user (before moving anything)
  ↓
Move to correct folders
  ↓
Add frontmatter
  ↓
Update _index.md
  ↓
Record in _log.md
```

### LINT (vault health check)

Two halves. The mechanical half is a script; the judgement half is a prompt.

**Mechanical — run the tools (see `tools/README.md`):**

```bash
python3 tools/vault.py freshness    # past review date · stale and forgotten
python3 tools/vault.py ledger verify # decisions rewritten or deleted
python3 tools/secret_scan.py         # credentials in changed notes
```

**Judgement — ask Claude Code to check what a script cannot:**

```
Detect broken wikilinks
Detect missing or incomplete frontmatter
Detect orphan concepts (repeated across projects, no page in _shared/)
Report findings in _log.md as type `lint`
Propose actions (don't execute without approval)
```

Neither half changes a `status` field on its own. They produce a list; you
decide what is actually outdated.

---

## Using `_shared/`

The `_shared/` folder holds knowledge that applies to **two or more projects**. Use it when:

- A concept, pattern, or decision recurs across different projects
- You want to avoid duplicating documentation (and the divergence that causes)
- Other projects should be able to find it via cross-project lookup

**When to move something to `_shared/`:**
- It appears in a second project → move it from the first project's folder to `_shared/`
- Alternatively: create it in `_shared/` directly if you know it will be reused

**When NOT to use `_shared/`:**
- The concept is specific to one project (even if it might be reused later)
- You're not sure — default to the project folder; move to `_shared/` when it's actually needed

**Example: a shared concept**

`_shared/_concepts/pgbouncer-transaction-pooling.md`

```yaml
---
title: "Concept: PgBouncer transaction pooling"
project: _shared
type: concept
status: active
tags: [postgresql, pgbouncer, connection-pooling]
related: []
created: 2024-05-22
updated: 2024-05-22
---

## What It Is

PgBouncer in transaction pooling mode sits between the application and PostgreSQL.
It multiplexes many application connections into a small pool of real database connections,
releasing each connection back to the pool at the end of every transaction.

## When to Use

When horizontal scaling causes connection count to exceed the database limit.
Effective from ~5+ application instances.

## Trade-offs

- ✅ Dramatically reduces connections to the database
- ✅ Scales with application instances
- ⚠️ Incompatible with session-level features (SET, advisory locks, prepared statements)

## References

- [[Projects/ProjectA/Problems/DB-Connection-Pool-Exhaustion]] — where this was first solved
- [[Projects/ProjectB/Runbooks/Database-Setup]] — where it was reused
```

---

## This File

This is the **single source of truth** for vault conventions. It's read-only documentation that Claude Code references. Update it only when conventions change (rare).