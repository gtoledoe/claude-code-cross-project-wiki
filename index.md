# Documentation Index

All documents are in `/docs/`. Here is what each one does and the recommended reading order.

---

## Documents

### 1. README.md — START HERE

**What it is:** Full system explanation. Concepts, problems it solves, benefits.

**Contains:**
- The 3 problems: scope bleed, knowledge rot, knowledge silos
- The 4 solutions: scope isolation, document lifecycle, cross-project lookup, adaptive folders
- How they work together
- Benefits for individuals, teams, and the knowledge base

Read this first. It explains why everything else exists.

---

### 2. docs/CLAUDE.md

**What it is:** Annotated CLAUDE.md template. How to configure Claude Code for your project.

**Contains:**
- What goes in CLAUDE.md and why
- The scope declaration (the critical section)
- Reference to `_wiki-protocol.md`
- Folder structure options
- Content-to-folder mapping

**Use this:** Copy the content inside the code block to your project's `CLAUDE.md` and customize.

---

### 3. docs/_wiki-protocol.md

**What it is:** Global protocol for the Obsidian vault. Conventions, formats, lifecycle.

**Contains:**
- Vault structure
- Required frontmatter
- Document types and lifecycle
- Wikilink conventions
- Cross-project lookup flow
- Templates per document type
- Best practices and constraints

**Use this:** Copy to the root of your Obsidian vault as `_wiki-protocol.md`.

---

### 4. docs/implementation-guide.md

**What it is:** Concrete setup steps. 8 steps, ~20 minutes total.

**Contains:**
- Steps 1–8: complete setup for the first project
- For multiple projects: what to do next
- Migrating existing documentation: how to onboard legacy docs
- Troubleshooting common issues

**Use this:** Follow the 8 steps in order.

---

### 5. docs/example-prompts.md

**What it is:** 7 ready-to-use prompts for Claude Code. With real examples.

**Contains:**
- Prompt 1: Initialize a new project
- Prompt 2: Document a technical decision
- Prompt 3: Document a resolved problem
- Prompt 4: Cross-project lookup
- Prompt 5: Vault health check
- Prompt 6: Migrate existing docs
- Prompt 7: Document a session summary
- Tips and shorthand

**Use this:** Copy and customize the prompt you need. Paste it into Claude Code.

---

### 6. docs/example-documents.md

**What it is:** 3 real document examples — ADR, Problem, Runbook — with full content.

**Contains:**
- Example 1: Full ADR (caching strategy) with context, alternatives, decision, consequences
- Example 2: Problem document (DB connection pool exhaustion) with symptoms, root cause, solution, validation
- Example 3: Runbook (incident response) with steps, verification, rollback, escalation
- What makes documentation good

**Use this:** As a quality reference. Show these to Claude Code if you want it to generate documents at this level.

---

### 7. tools/

**What it is:** The executable half of the protocol — freshness report, decision ledger,
secret scan and session close. Pure Python 3 and bash, no dependencies, no installs.

**Contains:**
- `vault.py freshness` — notes past their review date or marked stale and forgotten
- `vault.py ledger verify|sync` — hash-chained index of decisions; detects rewrites/deletions
- `secret_scan.py` — credentials in changed notes; never prints the value
- `close.sh` — scan → ledger → commit → push, fail-closed on secrets
- `test_secret_scan.py` — 17-case regression battery

**Use this:** Copy the whole `tools/` folder to your Obsidian vault root
(the vault must be a git repo). Read `tools/README.md` first.

---

## Recommended Reading Order

**To understand the concept:**
1. README.md (9 min)
2. First 2 sections of docs/implementation-guide.md (5 min)

**To implement:**
3. docs/implementation-guide.md Steps 1–8 (20 min)
4. docs/CLAUDE.md (customize and copy to your repo)
5. docs/_wiki-protocol.md (copy to your Obsidian vault)

**For ongoing use:**
6. docs/example-prompts.md (when you need to document something)
7. docs/example-documents.md (as quality reference)

**Total: ~45–60 minutes of setup. Then, automatic operation.**

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

## Repository Structure

```
llm-claude-code-wiki/
├── README.md                    — system overview
├── index.md                     — this file
├── CLAUDE.md                    — tells Claude Code how to use this repo
├── docs/
│   ├── CLAUDE.md                — CLAUDE.md template (copy to your project)
│   ├── _wiki-protocol.md        — global protocol (copy to your vault)
│   ├── implementation-guide.md  — 8-step setup guide
│   ├── example-prompts.md       — 7 ready-to-use prompts
│   └── example-documents.md     — ADR, Problem, Runbook examples
└── tools/                       — executable checks (copy to your vault root)
    ├── README.md                — what each tool does and why
    ├── vault.py                 — freshness report + decision ledger
    ├── secret_scan.py           — fail-closed secret scan of changed notes
    ├── close.sh                 — session close: scan → ledger → commit → push
    └── test_secret_scan.py      — regression battery for the patterns
```

---

## Checklist: Do You Have Everything?

Before using or sharing, verify you have these files:

- [ ] README.md — concepts and benefits
- [ ] docs/CLAUDE.md — CLAUDE.md template
- [ ] docs/_wiki-protocol.md — global protocol
- [ ] docs/implementation-guide.md — 8-step setup
- [ ] docs/example-prompts.md — 7 ready-to-use prompts
- [ ] docs/example-documents.md — 3 real document examples
- [ ] CLAUDE.md (repo root) — tells Claude Code its role
- [ ] tools/ — executable checks (5 files, no dependencies)

**If you have these 8 items, you have everything.**

---

## Notes

**No references to specific projects.** All documents are generic — instructions for anyone to implement the system.

**Ready to share.** Upload to GitHub, share with your team, publish as reference. No private information.

**Obsidian-based.** The system was built and tested with Obsidian. The protocol is compatible with any folder of `.md` files, but examples and conventions follow Obsidian patterns.

**Flexible.** All examples and templates can be customized. The system adapts to your workflow, not the other way around.

**After implementing:** The system runs automatically. Claude Code documents during work sessions. Maintenance: monthly vault lint (Prompt 5), quarterly archived doc review, 5 minutes per new project added.
