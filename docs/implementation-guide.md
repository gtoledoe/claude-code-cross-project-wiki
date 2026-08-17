# Implementation Guide — Multi-Project Wiki

Step-by-step guide to set up the multi-project wiki system for Claude Code.

---

## Prerequisites

- **Obsidian** installed (the system was built and tested with Obsidian; it also works with any folder of `.md` files, but examples and conventions follow Obsidian patterns)
- **Claude Code** installed
- Your project already has a `CLAUDE.md` file (or you're ready to create one)
- **For Step 9 (executable checks):** `python3` available, and your vault initialized as a
  git repo (`cd "your vault" && git init`). Both are optional — the protocol works without
  them, you just lose the automated half.

---

## Setup (~20 minutes total)

**Before you start:** Replace `~/Documents/Obsidian Vault` with the actual path to your vault in all commands below.

---

### Step 1 — Copy the global protocol

Copy `docs/_wiki-protocol.md` to the root of your Obsidian vault:

```bash
cp docs/_wiki-protocol.md ~/Documents/Obsidian\ Vault/_wiki-protocol.md
```

This is the single source of truth for conventions. Done once, then rarely touched again.

---

### Step 2 — Create the shared folder

```bash
mkdir -p ~/Documents/Obsidian\ Vault/_shared/{_concepts,_decisions}
```

This is where knowledge shared across multiple projects lives. Leave it empty for now — you'll move things here when a concept appears in a second project.

---

### Step 3 — Choose your project's folder structure

Different project types need different structures:

**Web app?**
```
Arquitectura/ | Documentación Técnica/ | Negocio/ | Infraestructura/ | Runbooks/ | Sesiones/
```

**Infrastructure?**
```
Arquitectura/ | Decisiones/ | Estado/ | Problemas/ | Runbooks/
```

**FinOps / Cloud Governance?**
```
Analisis/ | Gobierno/ | Estado/ | Runbooks/ | Sesiones/
```

**Something else?** Keep it simple:
```
Decisiones/ | Problemas/ | Runbooks/ | Arquitectura/
```

Name folders after what you search for. The protocol stays the same regardless of folder names.

---

### Step 4 — Create your project folder structure

```bash
# Replace {Your-Project} and {Folder1,Folder2,...} with your actual values
mkdir -p ~/Documents/Obsidian\ Vault/Projects/{Your-Project}/{Folder1,Folder2,Folder3,raw}
touch ~/Documents/Obsidian\ Vault/Projects/{Your-Project}/_log.md
```

Example for a web app:
```bash
mkdir -p ~/Documents/Obsidian\ Vault/Projects/MyWebApp/{Arquitectura,Documentación\ Técnica,Negocio,Infraestructura,Runbooks,Sesiones,raw}
touch ~/Documents/Obsidian\ Vault/Projects/MyWebApp/_log.md
```

---

### Step 5 — Create the project index

Create `_index.md` in your project folder. Use this template:

```yaml
---
title: "Index — {Your Project Name}"
project: your-project-id
type: index
status: active
updated: YYYY-MM-DD
---

## Current State
Brief description of the project (2-3 lines).

## Folder Structure
- {Folder-1}: description
- {Folder-2}: description
- raw/: unprocessed sources

## Key Documents
(You'll add links here as you create documents)

## Active Decisions
| Date | Decision | Status |
|------|----------|--------|
(You'll populate this as decisions are made)

## Known Problems
| Problem | Status |
|---------|--------|
(You'll populate this as problems are solved)

## Available Runbooks
(You'll populate this as procedures are documented)

## Session Log
→ See [[_log]]
```

---

### Step 6 — Initialize the session log

Create `_log.md` in your project folder:

```markdown
# Log — {Your Project Name}

## [YYYY-MM-DD] ingest | Initial wiki setup
**Type:** ingest
**Session:** Created vault structure and initialized project index
**Documents created:** [[_index]]
**Pending:** Start documenting decisions and problems
```

---

### Step 7 — Add the scope declaration to CLAUDE.md

Open your project's `CLAUDE.md` (the repo file, not the vault file) and add this section:

```markdown
## External Documentation (Obsidian Wiki)

### This Project's Scope

This Claude Code session operates **exclusively** on **{Your Project Name}**.

- **Writes** to: `~/Documents/Obsidian Vault/Projects/{Your-Project}/`
- **Reads** (read-only): `~/Documents/Obsidian Vault/_shared/` and other projects' `_index.md`,
  **only when explicitly requested**
- **Never writes** to other projects' folders
- A decision made here applies only to **{Your Project Name}**

### Global Protocol

All vault conventions are defined in:

` ` `
~/Documents/Obsidian Vault/_wiki-protocol.md
` ` `

Read this before any documentation operation.

### Project Structure in Vault

` ` `
~/Documents/Obsidian Vault/Projects/{Your-Project}/
├── _index.md          ← project index
├── _log.md            ← session log
├── {Folder-1}/        ← {description}
├── {Folder-2}/        ← {description}
└── raw/               ← unprocessed sources
` ` `

### Content-to-Folder Mapping

| Content type | Destination | When |
|---|---|---|
| Technical decisions (ADRs) | {Folder}/ | When completing milestone |
| Resolved problems | {Folder}/ | When resolving relevant issue |
| Reproducible procedures | {Folder}/ | When defining operational procedure |
| Session summary | {Folder}/YYYY-MM-DD - {Topic}.md | When closing session |

### Cross-Project Lookup

When user asks to use knowledge from another project:

` ` `
1. Read ~/Documents/Obsidian Vault/_wiki-protocol.md (exact flow)
2. Read Projects/{other-project}/_index.md (locate document)
3. Read the document (read-only)
4. Apply to current project, reference origin:
   "Based on [[Projects/X/Folder/document]]"
5. Never modify source project
` ` `

### Session Close

1. Update repo docs if something changed
2. Create vault documents for:
   - Technical decision → appropriate folder
   - Resolved problem → appropriate folder
   - New procedure → appropriate folder
   - Session summary → appropriate folder
3. Append entry to `_log.md` with links
4. Update `_index.md` if structural changes
5. State pending items and suggested next step
```

> **Note:** The backtick code blocks above use spaces between backticks for display purposes. In your actual CLAUDE.md, use real triple-backtick fences.

---

### Step 8 — Test it works

Open Claude Code in your project repo. At the start of a session, run this prompt:

```
Read ~/Documents/Obsidian Vault/_wiki-protocol.md

Then tell me:
1. What is the vault structure?
2. What is the project scope for {Your Project Name}?
3. Which folders in my project should I use for [decision/problem/runbook]?
```

Claude Code should:
- Read the protocol
- Understand your project's scope
- Know where to document things

If it does, you're set up correctly. ✅

---

### Step 9 — Install the executable checks (optional, ~3 minutes)

Conventions decay. These four scripts are the half a machine can verify. No dependencies.

```bash
# from the repo you cloned
cp -R tools "$HOME/Documents/Obsidian Vault/tools"

cd "$HOME/Documents/Obsidian Vault"
git init                                  # if it is not a repo yet
python3 tools/test_secret_scan.py         # expect: 17/17 cases passed
python3 tools/vault.py freshness          # expect: a report, and no note modified
python3 tools/vault.py ledger sync        # index the decisions you already wrote
```

Add a remote if you want the notes actually backed up:

```bash
git remote add origin <your-private-repo-url>
```

Then close a session with:

```bash
bash tools/close.sh my-project
```

**Wire that last command into your close-session routine** (a skill, a slash command, or
your own checklist). Left as "run it by hand", it does not get run — and you find out the
day the disk does.

A note on the first run: if your vault lives in iCloud Drive, OneDrive or Dropbox with
sync-on-demand, the first pass can take minutes of I/O wait while files are materialized.
Later runs are fast.

See `tools/README.md` for what each script guarantees.

---

## Using It

### During a work session

When you make a decision, solve a problem, or define a procedure:

```
You: "Document this decision we just made about authentication"

Claude Code:
1. Creates document in correct folder with proper frontmatter
2. Adds to _index.md
3. Updates _log.md
4. You verify and approve
```

### Cross-project reuse

```
You: "We solved a similar database pooling problem in Project A.
      Use that as a starting point for this implementation."

Claude Code:
1. Reads Projects/Project-A/_index.md
2. Finds the relevant document
3. Reads it (read-only)
4. Implements in current project
5. Creates new document with reference to source
```

### Vault health check (monthly)

```
You: "Run a vault lint on this project"

Claude Code:
1. Detects broken wikilinks
2. Detects missing frontmatter
3. Lists stale documents (60+ days)
4. Reports findings
5. Proposes actions (you approve)
```

---

## For Multiple Projects

Once the first project is working, adding new projects is fast:

1. Create `Projects/{New-Project}/` folder with your chosen structure
2. Create `_index.md` and `_log.md`
3. Add scope declaration to that project's `CLAUDE.md`
4. Done — each project operates independently with the same protocol

---

## Migrating Existing Documentation (Optional)

If you have legacy docs in notes, READMEs, Notion, or other places, you can onboard them incrementally.

### Phase 1 — Inventory (do not move anything yet)

Use this prompt in Claude Code:

```
I have existing documentation I want to migrate to the wiki system.

List all .md files in {source folder}:
- Filename
- Current folder
- Suggested type: decision | problem | runbook | architecture | summary | raw
- One sentence description

Show me the list. Do not move anything yet.
```

Review the list and approve before proceeding.

### Phase 2 — Classify

For each document, decide:

| Document type | Destination folder |
|---|---|
| Architectural decision | `{Decisions folder}/` |
| Bug or incident with solution | `{Problems folder}/` |
| Step-by-step procedure | `Runbooks/` |
| System design or diagram | `Arquitectura/` |
| Reference or overview | `{most relevant folder}/` |
| Raw / unprocessed | `raw/` |

### Phase 3 — Move and add frontmatter

Use this continuation prompt:

```
For each file in the approved inventory:
1. Move to ~/Documents/Obsidian Vault/Projects/{Project-Name}/{destination-folder}/
2. Add complete frontmatter:
   - title (from filename or content)
   - project: {project-id}
   - type: {as per inventory}
   - status: {infer from content — draft/active/stale/archived}
   - tags: relevant technical topics
   - created: {from filename if available, else today}
   - updated: today
3. Do not modify content, only add frontmatter
```

### Phase 4 — Update project metadata

```
Update _index.md to add links to all migrated documents.
Append entry to _log.md with type: migration.
Show a summary: X files migrated, Y to each folder.
```

### Tips

- Migrate incrementally — you don't have to convert everything at once
- Old docs of uncertain age: mark as `stale`, not `archived`
- Very short content: consider merging into an existing document rather than creating a new file
- Docs with no clear type: put in `raw/` and classify later

---

## Common Issues

### Claude Code doesn't know about the scope
**Solution:** Check that the scope declaration section is in your project's `CLAUDE.md`. Verify the path to `_wiki-protocol.md` is correct.

### Documents aren't being created in the right folder
**Solution:** Add a content-to-folder mapping table in your `CLAUDE.md` so Claude Code knows where each type goes.

### Wikilinks are broken
**Solution:** Make sure the folder names in your links match the actual folder names. Check spelling and case. If the target file doesn't exist, create a stub first (see `_wiki-protocol.md` → Wikilink Conventions).

### I can't find old documents
**Solution:** Check if they're archived. Add search-friendly frontmatter tags so you can filter by status or topic.

---

## Next Steps

Once setup is complete:

1. **Start documenting** — next decision, problem, or session — create a document
2. **Monthly lint** — run the vault health check (Prompt 5 in `docs/example-prompts.md`)
3. **Add projects** — each new project takes ~5 minutes to set up
4. **Refine folders** — add new folders as you need them; don't pre-create empty ones

The system runs automatically. Claude Code handles documentation during sessions. You maintain it with monthly lint checks.
