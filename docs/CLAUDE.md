# CLAUDE.md Template — Annotated

This file configures Claude Code for a specific project. Copy, customize (replace `{placeholders}`), and add to your project repo root as `CLAUDE.md`.

> **How to copy:** Copy only the content inside the code block below — not the ` ```markdown ` delimiters themselves. Paste it as your project's `CLAUDE.md`.

> **What's required for the wiki:** The sections marked `[REQUIRED FOR WIKI]` are the ones that implement scope isolation and documentation behavior. All other sections are optional general-purpose configuration — include them if they're useful for your project.

---

```markdown
# CLAUDE.md — {Project Name}

> Configuration guide for Claude Code working on {Project Name}.

## Purpose

{1-2 sentences describing what this project is and your role.}

State/reference: `docs/STATE.md` (or wherever current state lives)

---

## Quick Reference
<!-- OPTIONAL: Add whatever's useful for your project -->

{Add whatever's useful for this project:}
- Tech stack
- Key ports/services
- Common commands
- Important docs

Example:
```
| Component | Port | Command |
|-----------|------|---------|
| Backend   | 3000 | npm run dev |
| Database  | 5432 | docker-compose up db |
```

---

## Language
<!-- OPTIONAL -->

Respond always in {language}.
Comments and commits in {language}.
Variables and functions in English.

---

## Work Mode
<!-- OPTIONAL -->

```
intake → context → plan → implement → verify → document
```

- Do not implement without clear acceptance criteria
- If it affects multiple files: propose plan first
- Done = explicit verification executed

---

## Model Selection
<!-- OPTIONAL -->

Thinking always OFF.

| Task | Model | Effort |
|------|-------|--------|
| Analysis / reading repo | Sonnet | medium |
| Simple implementation | Haiku | medium |
| Complex implementation | Sonnet | medium |
| Architectural decisions* | Opus | high |

*Opus only if Sonnet was insufficient. Max 1-2 calls.

---

## Guardrails
<!-- OPTIONAL -->

```
NEVER commit / push without explicit approval
NEVER make changes without understanding the existing code first
ALWAYS deliver: what was done + verification + next step
```

---

## Repo Documentation
<!-- OPTIONAL -->

Load only what's relevant for the current task:

| Need | Document |
|------|----------|
| Current state | `docs/STATE.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Setup | `docs/SETUP.md` |

---

## External Documentation (Obsidian Wiki)
<!-- REQUIRED FOR WIKI: The sections below implement scope isolation and documentation behavior -->

### This Project's Scope
<!-- REQUIRED FOR WIKI -->

This Claude Code session operates **exclusively** on **{Project Name}**.

- **Writes** to: `{VAULT_PATH}/Projects/{Project-Name}/`
- **Reads** (read-only): `{VAULT_PATH}/_shared/` and other projects' `_index.md`,
  **only when explicitly requested**
- **Never writes** to other projects' folders
- A decision made here applies only to **{Project Name}**, not to other projects

### Global Protocol
<!-- REQUIRED FOR WIKI -->

All vault conventions are defined in:

```
{VAULT_PATH}/_wiki-protocol.md
```

Read this before any documentation operation.

### Project Structure in Vault

```
{VAULT_PATH}/Projects/{Project-Name}/
├── _index.md          ← project index (maintained by Claude Code)
├── _log.md            ← append-only session log
├── {Folder-1}/        ← {description}
├── {Folder-2}/        ← {description}
└── raw/               ← unprocessed sources (read-only)
```

Example folder structures by project type:

**Web application:**
```
Arquitectura/ | Documentación Técnica/ | Negocio/ | Infraestructura/ | Runbooks/ | Sesiones/
```

**Infrastructure:**
```
Arquitectura/ | Decisiones/ | Estado/ | Problemas/ | Runbooks/
```

**FinOps / Governance:**
```
Analisis/ | Gobierno/ | Estado/ | Runbooks/ | Sesiones/
```

### Content-to-Folder Mapping

| Content type | Destination | When |
|---|---|---|
| Technical decisions (ADRs) | {Folder}/ | When completing milestone |
| Resolved problems / incidents | {Folder}/ | When resolving relevant issue |
| Reproducible procedures | {Folder}/ | When defining operational procedure |
| Session summary | {Folder}/YYYY-MM-DD - {Topic}.md | When closing significant session |

### Cross-Project Lookup

When user asks to use knowledge from another project:

```
1. Read {VAULT_PATH}/_wiki-protocol.md (exact flow)
2. Read Projects/{other-project}/_index.md (locate document)
3. Read the document (read-only)
4. Apply to current project, reference origin:
   "Based on [[Projects/X/Folder/document]]"
5. Never modify source project
```

### Session Close
<!-- REQUIRED FOR WIKI -->

1. Update `docs/STATE.md` if something changed
2. Create vault document for any:
   - Technical decision → appropriate folder
   - Resolved problem → appropriate folder
   - New procedure → appropriate folder
   - Session summary → appropriate folder
3. Append entry to `_log.md` with links
4. Update `_index.md` if structural changes
5. State pending items and suggested next step
```

---

## How to Customize

1. **Replace `{Project Name}`** throughout
2. **Add Quick Reference** section for your specific tech
3. **Adjust folder structure** to match your domain
4. **Update content-to-folder mapping** with your folders
5. **Set the path** to your actual vault location

---

## Notes

- The **scope declaration** (the section starting "This project's scope") is the critical part. Claude Code reads this at session start.
- Everything else is documentation for **you**, to help Claude Code understand your project.
- The vault path `{VAULT_PATH}` should be something like `~/Documents/Obsidian Vault` or `/Users/username/vaults/my-vault`
- Don't overthink this. It can be simple. The key is the scope declaration + reference to protocol.