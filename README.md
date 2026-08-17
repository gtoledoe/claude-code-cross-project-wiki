# LLM Wiki — Multi-Project Knowledge Base for Claude Code

A practical system for maintaining persistent technical documentation across multiple Claude Code projects, with scope isolation, document lifecycle management, and controlled cross-project knowledge reuse.

---

## The Problem

When using Claude Code across multiple projects, three things go wrong:

### 1. Scope Bleed
You're working on Project A with Terraform + GCP. Claude Code learns the patterns, decisions, and constraints.

Later, you're on Project B (also Terraform + GCP, but different requirements). Claude Code silently applies patterns from Project A without you asking. Same technology doesn't mean same decisions.

**Result:** Incorrect assumptions baked into Project B because Claude Code carried context from Project A.

### 2. Silent Knowledge Rot
You document a decision. It's useful. Months pass. The decision is superseded, the technology changes, the workaround is replaced.

But the document still looks valid. There's no signal that it's outdated. Claude Code (or you) acts on stale information.

**Result:** Knowledge base full of documents that look current but aren't.

### 3. Knowledge Silos
You solve a problem in Project A. Later, Project B has the same problem.

You remember vaguely that you solved it before, but you have to search all your docs, or ask Claude Code to re-solve it from scratch.

Even worse: you can't share knowledge across projects without the recipient assuming it applies exactly as-is.

**Result:** Duplicated effort, lost context, unnecessary re-invention.

---

## The Solution

This system implements five interconnected practices:

### 1. Scope Isolation

**The Problem:** Claude Code carries context between projects.

**The Solution:** Every Claude Code session reads an explicit **scope declaration** in your project's `CLAUDE.md`:

```markdown
### Project Scope

This Claude Code session operates exclusively on **{Project Name}**.

- **Writes** to: `{VAULT_PATH}/Projects/{Project-Name}/`
- **Reads** (read-only) `{VAULT_PATH}/_shared/` and other projects' `_index.md`,
  **only when explicitly requested**
- **Never writes** to other projects' folders
- A decision made here applies only to **{Project Name}**
```

Claude Code reads this at session start. It knows its boundaries. It doesn't assume decisions transfer between projects.

**What this prevents:**
- ✅ Pattern from Project A affecting Project B
- ✅ Accidental modifications to other projects
- ✅ Silent assumption that "we did this before, so do it again"

---

### 2. Document Lifecycle

**The Problem:** Documents age silently. No way to signal "this is outdated."

**The Solution:** Every document has a **status field** that progresses through a lifecycle:

```
draft → active → stale → archived
```

- **`draft`** — just created, not validated
- **`active`** — verified and current, safe to use
- **`stale`** — may be outdated, review before using
- **`archived`** — no longer applies, kept for historical context

**Who marks a document stale?** You do. Detecting and marking are separate roles:
`tools/vault.py freshness` **detects** and reports candidates but never writes to a note;
Claude Code **proposes** during a lint or a session close; **you decide** and set the field.

No threshold knows whether a one-year-old ADR is still valid. Age is a hint, not a verdict —
a script that flipped `active` to `stale` on a timer would be wrong often enough that you
would stop trusting the field.

Optionally add `review_after: YYYY-MM-DD` to documents that have a *knowable* expiry (a
runbook pinned to a version, a cost analysis for one month). No field, no expiry.

**What this prevents:**
- ✅ Acting on outdated information
- ✅ Knowledge base rot
- ✅ Lost context (archived docs are kept, not deleted)

**Example:**
```yaml
---
title: "ADR: PostgreSQL 13 for production"
status: archived  ← Signal: this is outdated
created: 2024-01-15
updated: 2024-01-15
---

Superseded by [[ADR-PostgreSQL-15-upgrade]]
```

---

### 3. Cross-Project Lookup

**The Problem:** You can't safely reuse knowledge from other projects.

**The Solution:** Explicit, controlled, read-only knowledge reuse.

When you ask "how did we solve this in Project X?", the flow is:

1. Claude Code reads Project X's `_index.md` (read-only)
2. Finds and reads the relevant document (read-only)
3. Uses it as **input** for the current project
4. Documents the result in the current project **with a reference to the source**
5. **Never modifies** Project X

**What this enables:**
- ✅ Reuse solutions without duplicating effort
- ✅ Adapt approaches for different contexts
- ✅ Keep source projects clean (read-only)
- ✅ Know where knowledge came from (traceability)

**Example:**
```markdown
# Problem: Database connection timeout

## Solution
Based on approach documented in [[Projects/Project-A/Problemas/DB-Pooling-Solution]],
adapted for our PostgreSQL configuration.

Implemented PgBouncer in transaction pooling mode.
```

---

### 4. Executable Checks

**The Problem:** A protocol made only of conventions decays. Nothing tells you the lint was
skipped for three months, that a decision was quietly rewritten, or that a token you pasted
into a note while debugging is now in git history forever.

**The Solution:** `tools/` — pure Python 3 and bash, **no dependencies**. Copy it to your
vault root.

```bash
python3 tools/vault.py freshness      # what should I look at again?
python3 tools/vault.py ledger verify  # was a decision rewritten or deleted?
python3 tools/secret_scan.py          # did a credential end up in a note?
bash    tools/close.sh my-project     # close: scan → ledger → commit → push
```

**The decision ledger** is the piece that does not exist elsewhere. It hash-chains your
`type: decision` notes into `decisions.jsonl`, each entry signing the previous one. The note
stays the source of truth; the ledger answers what a loose file cannot — *was this decision
rewritten or deleted after it was made?* It detects an altered entry, a deleted line,
reordering, a note edited behind your back and a decision quietly removed.

**Two properties hold throughout:**

- **They report, they do not decide.** No tool ever changes a document's `status`.
- **The session close is fail-closed on secrets.** Findings — or a scanner that cannot run at
  all — stop the close and commit nothing. A check that fails silently and lets you through
  buys false confidence.

Full documentation: [`tools/README.md`](tools/README.md).

---

### 5. Adaptive Folder Structure

**The Problem:** Different project types need different knowledge structures.

Forcing a web app and a cloud governance project into identical `decisions/`, `problems/`, `runbooks/` folders loses clarity.

**The Solution:** Each project defines its own folder structure based on its domain.

**Web app example:**
```
Arquitectura/ | Documentación Técnica/ | Negocio/ | Infraestructura/ | Runbooks/ | Sesiones/
```

**Infrastructure example:**
```
Arquitectura/ | Decisiones/ | Estado/ | Problemas/ | Runbooks/
```

**FinOps example:**
```
Analisis/ | Gobierno/ | Estado/ | Runbooks/ | Sesiones/
```

The **protocol** (frontmatter, wikilinks, scope guard, lifecycle) stays the same. The **folders** adapt to what you actually search for.

**What this enables:**
- ✅ Semantic clarity (folder names match your domain language)
- ✅ Faster lookup (search for "Negocio/" not "decisions/")
- ✅ Flexibility (add folders as you need them)

---

## How It Works Together

### Session startup
```
Claude Code starts
  ↓
reads CLAUDE.md (project scope declaration)
  ↓
reads _wiki-protocol.md (global conventions)
  ↓
reads _index.md (project map)
  ↓
Has full context, knows its boundaries
```

### During work
```
Decision made / Problem solved / Procedure defined
  ↓
Claude Code creates document in correct folder
  ↓
Adds frontmatter (status, tags, related docs)
  ↓
Updates _index.md (add link)
  ↓
Appends to _log.md (record activity)
  ↓
Knowledge persists across sessions
```

### Cross-project reuse
```
You: "Use the approach from Project A for this"
  ↓
Claude Code reads Project A's _index.md
  ↓
Finds relevant document
  ↓
Implements in current project
  ↓
Documents result with reference: "Based on [[Projects/A/folder/doc]]"
  ↓
Only current project modified
```

---

## Benefits

### For individuals / small teams
- **Low cognitive load** — Claude Code handles documentation automatically
- **No rot** — Status tracking keeps knowledge fresh
- **Reusable patterns** — Controlled access to previous solutions
- **Flexible structure** — Folders match your domain, not a template

### For organizations / multiple teams
- **Scope boundaries** — Multiple teams can use Claude Code safely without cross-contamination
- **Knowledge sharing** — Explicit, traceable reuse across teams
- **Audit trail** — `_log.md` records who documented what when
- **Consistency** — Same protocol across all projects, different structures per domain

### For the knowledge base
- **No deletion** — Archived docs keep context
- **Status signals** — Clear visibility into document freshness
- **Relationships** — Wikilinks show how decisions connect
- **Search-friendly** — Semantic folder names, frontmatter for filtering

---

## Core Files You Need

### 1. `_wiki-protocol.md` (copy to vault root)
Global rules and conventions. Defines:
- Frontmatter format
- Document types and lifecycle
- Wikilink conventions
- Cross-project lookup flow

### 2. `CLAUDE.md` (per project)
Project configuration. Includes:
- Scope declaration (what this session can read/write)
- Folder structure and mapping
- Reference to `_wiki-protocol.md`

### 3. `_index.md` (per project)
Project map. Shows:
- Current state (2-3 lines)
- Folder structure
- Links to key documents
- Active decisions, problems, runbooks

### 4. `_log.md` (per project)
Append-only session history:
```
## [YYYY-MM-DD] {type} | {title}
**Type:** decision | problem-solved | migration | lint
**Session:** {what was worked on}
**Documents created:** [[links]]
**Pending:** {what remains}
```

### 5. `tools/` (copy to vault root, optional but recommended)
The executable half of the protocol. No dependencies:
- `vault.py freshness` — what needs a second look
- `vault.py ledger` — detects decisions rewritten or deleted
- `secret_scan.py` — credentials in changed notes (never prints the value)
- `close.sh` — session close: scan → ledger → commit → push, fail-closed

### 6. Project folders (your choice)
Name them based on your domain:
- Web apps: `Arquitectura/`, `Negocio/`, `Sesiones/`
- Infrastructure: `Decisiones/`, `Estado/`, `Problemas/`
- FinOps: `Analisis/`, `Gobierno/`, `Estado/`

---

## How to Adopt This System

Clone this repo, open it in Claude Code, and paste this prompt:

```
I want to implement the multi-project wiki system documented in this repo.

Read the following files in order:
1. docs/_wiki-protocol.md — global conventions
2. docs/implementation-guide.md — setup steps
3. docs/CLAUDE.md — the CLAUDE.md template

Then set up the system for my project:
- Project name: {My Project Name}
- Vault path: {~/path/to/my/obsidian/vault}
- Project type: {web app | infrastructure | finops | other}

Follow the 8 setup steps. Show me what you'll create before creating anything.
```

Claude Code will read the docs in this repo and configure the system in your project.

---

## Getting Started

### The fast version (10 minutes)

1. Copy `docs/_wiki-protocol.md` to your Obsidian vault root as `_wiki-protocol.md`
2. Create a `Projects/{Your-Project}/` folder with `_index.md` and `_log.md`
3. Add the **Project Scope** section to your project's `CLAUDE.md`
4. Use the provided prompts with Claude Code

### The thorough version (~30 minutes)

Read:
1. This README (you are here)
2. `docs/implementation-guide.md`
3. `docs/CLAUDE.md` (template)
4. Choose prompts from `docs/example-prompts.md`

---

## What's Included

- **README.md** — This file (concepts + benefits)
- **docs/CLAUDE.md** — CLAUDE.md template with annotations
- **docs/_wiki-protocol.md** — Global protocol to copy to your Obsidian vault
- **docs/implementation-guide.md** — Step-by-step setup (8 steps, ~20 min)
- **docs/example-prompts.md** — 7 ready-to-use prompts
- **docs/example-documents.md** — Sample ADR, Problem, Runbook
- **tools/** — Executable checks: freshness report, decision ledger, secret scan,
  session close. Pure Python 3 + bash, no dependencies. See `tools/README.md`.

---

## Why This Works

**Scope isolation** prevents Claude Code from carrying assumptions between projects.

**Document lifecycle** ensures knowledge doesn't rot silently.

**Cross-project lookup** lets you reuse solutions without duplicating effort.

**Adaptive folders** make documentation semantic and searchable.

Together, they solve the three core problems: scope bleed, knowledge rot, and knowledge silos.

---

## Questions?

See the included guides for implementation details, prompts, and examples.

---

**Built on the foundation of [LLM Wiki](https://github.com/context-labs/llm-wiki), extended with multi-project isolation, lifecycle management, and controlled knowledge reuse.**