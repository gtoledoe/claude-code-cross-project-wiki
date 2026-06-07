# Example Prompts — Ready-to-Use

Copy and paste these into Claude Code sessions. Customize the placeholders in `{braces}`.

---

## Tips for Using Prompts

**Customize the placeholders before pasting:**
```
{Project Name}           → MyWebApp, MyInfra, etc.
{VAULT_PATH}             → ~/Documents/Obsidian\ Vault
{Folder}                 → Arquitectura, Decisiones, etc.
{other-project}          → name of the project you're referencing
```

**Paste the entire prompt at once** — Claude Code processes better with full context, not line by line.

**For decisions, problems, and sessions — provide the key information.** The more detail you include, the better the documentation Claude Code generates.

**Always wait for Claude Code to show you the result before confirming.** Verify the document was created in the right folder with correct frontmatter.

---

## Prompt 1: Initialize a New Project

**Use when:** Setting up a new project in the wiki for the first time.

```
You are Claude Code working on {Project Name}.

Read {VAULT_PATH}/_wiki-protocol.md to understand vault conventions.

Then create two files in {VAULT_PATH}/Projects/{Project-Name}/:

1. _index.md — the project index with:
   - Current state (2-3 lines)
   - Folder structure listing these folders: {list your folders}
   - Empty tables for decisions, problems, runbooks (to fill later)
   - Reference to _log

2. _log.md — the session log with just the header and first entry recording the creation

Do not move, delete, or modify any existing documents.
Do not create a ZIP file.
```

---

## Prompt 2: Document a Technical Decision

**Use when:** You've made an architectural or technical decision that should be documented.

```
We just made a decision about {brief description of what}.

Document it as an ADR (Architecture Decision Record) in the vault.

Steps:
1. Create a new file: {VAULT_PATH}/Projects/{Project-Name}/{Folder}/ADR-{decision-name}.md
2. Use the ADR template from _wiki-protocol.md:
   - title: "Decision: {decision name}"
   - project: {project-id}
   - type: decision
   - status: active (if implemented) or draft (if pending)
   - Include: Context, Alternatives, Decision, Consequences
3. Update {VAULT_PATH}/Projects/{Project-Name}/_index.md to add this decision to the table
4. Append entry to _log.md

Key information about the decision:
{paste the actual decision details, context, alternatives, consequences}
```

---

## Prompt 3: Document a Resolved Problem

**Use when:** You've solved an incident, bug, or problem that took debugging.

```
We just resolved a problem. Document it in the vault.

Steps:
1. Create file: {VAULT_PATH}/Projects/{Project-Name}/{Folder}/Problem-{name}.md
2. Structure (from _wiki-protocol.md):
   - title: "Problem: {name}"
   - type: problem
   - status: active (fully resolved) or stale (workaround only, underlying cause remains)
   - Include: Symptoms, Root Cause, Solution Applied, Status, References
3. Update _index.md to add this to the problems table
4. Append to _log.md with type: problem-solved

Problem details:
{describe symptoms, root cause, solution applied, how to verify it's fixed}
```

---

## Prompt 4: Cross-Project Lookup

**Use when:** You want to reuse a solution or decision from another project.

```
I need to implement {description} in {current project}.

We solved something similar in {other project}. Look up how we did it and use it as input.

Steps:
1. Read {VAULT_PATH}/Projects/{other-project}/_index.md to find the relevant document
2. Read that document (read-only, do not modify it)
3. Implement the equivalent in {current project}
4. Create a new document in {current project}'s appropriate folder
5. Reference the source: "Based on [[Projects/{other-project}/Folder/document-name]]"

Never modify the source project. Adapt the approach for our current context.
```

---

## Prompt 5: Vault Health Check (Lint)

**Use when:** Monthly or quarterly — to detect stale docs, broken links, documentation debt.

```
Run a health check on {VAULT_PATH}/Projects/{Project-Name}/:

1. List all .md files and check:
   - Do they have frontmatter (title, project, type, status, etc.)?
   - Are wikilinks valid? (Do target files exist?)
   - Any files with status "stale"? List them with last update date.
   - Any files with status "draft" older than 14 days? These should be resolved.

2. Generate a report:
   - Total files: X
   - By status: active Y | stale Z | archived W | draft V
   - Broken wikilinks: {count}
   - Missing frontmatter: {count}
   - Stale documents (60+ days): {list}

3. Append findings to _log.md with type: lint

Propose actions but do not execute without approval:
- Fix broken wikilinks
- Update stale documents
- Promote drafts to active or archive
```

---

## Prompt 6: Migrate Existing Documentation

**Use when:** You have legacy docs that need to be moved into the wiki.

```
I have existing documentation I want to migrate to the wiki system.

Phase 1 - Inventory (do not move anything yet):

List all .md files in {source folder}:
- Filename
- Current folder
- Suggested type: decision | problem | runbook | architecture | summary | raw
- One sentence description

Show me the list. Do not move anything yet.
```

After you review and approve, use this continuation:

```
Phase 2 - Move and add frontmatter:

For each file in {the approved inventory}:
1. Move to {VAULT_PATH}/Projects/{Project-Name}/{destination-folder}/
2. Add complete frontmatter with:
   - title (from filename or content)
   - project: {project-id}
   - type: {as per inventory}
   - status: {infer from content — draft/active/stale/archived}
   - tags: relevant technical topics
   - created: {from filename if available, else today}
   - updated: today
3. Do not modify content, only add frontmatter

Phase 3 - Update project metadata:

1. Update _index.md to add links to all migrated documents
2. Append entry to _log.md with type: migration

When done, show a summary: X files migrated, Y to each folder, Z with status issues to review.
```

---

## Prompt 7: Document a Session Summary

**Use when:** Closing a significant work session — decisions made, context established, progress worth preserving for future sessions.

```
We're closing this work session on {Project Name}. Document a session summary.

Steps:
1. Create file: {VAULT_PATH}/Projects/{Project-Name}/{Folder}/YYYY-MM-DD - {Topic}.md
2. Structure:
   - title: "Session: {date} — {topic}"
   - type: summary
   - status: active
   - Include: What was worked on, decisions made, problems encountered, current state, next steps
3. Update _index.md if any new decisions or problems were documented during this session
4. Append entry to _log.md with type: ingest (or decision/problem-solved if applicable)

Session context:
{describe what was done, what was decided, what remains open, what the next step is}
```

---

## Real-World Examples

### Example 1: Initialize a web app project

```
You are Claude Code working on UserAPI.

Read ~/Documents/Obsidian\ Vault/_wiki-protocol.md to understand vault conventions.

Then create two files in ~/Documents/Obsidian\ Vault/Projects/UserAPI/:

1. _index.md with folders: Arquitectura, Documentación Técnica, Infraestructura, Runbooks
2. _log.md with the header and first entry

Do not create a ZIP file.
```

### Example 2: Document an auth decision

```
We just decided to use JWT tokens with httpOnly cookies for authentication.

Document it as an ADR in the vault.

Steps:
1. Create: ~/Documents/Obsidian\ Vault/Projects/UserAPI/Arquitectura/ADR-Auth-Strategy.md
2. Content:
   - Context: Security vulnerabilities in localStorage auth
   - Alternatives: localStorage, session cookies, OAuth
   - Decision: httpOnly cookies + JWT
   - Consequences: improved security, slightly more complex, compatible with SSR
3. Update _index.md Active Decisions table
4. Append to _log.md

Key info: Chose httpOnly because localStorage vulnerable to XSS, JWT in cookie avoids server session storage, works with SPA and SSR.
```

### Example 3: Cross-project lookup

```
I need to set up monitoring dashboards for this project.

We built comprehensive Prometheus dashboards in ProjectX. Use that as reference.

Steps:
1. Read ~/Documents/Obsidian\ Vault/Projects/ProjectX/_index.md
2. Find the dashboard decision/runbook
3. Read it
4. Create equivalent monitoring setup for current project
5. Create document referencing the source

Adapt for our stack: we use DataDog instead of Prometheus.
```

---

## Shorthand (when you're in a hurry)

Don't have time for a full prompt? Try shorthand:

```
Doc this: We decided to use Postgres instead of MongoDB.
(Claude Code will handle the format)

Solved: Database connection pooling issue with PgBouncer.
(Claude Code will create the problem doc)

Runbook: Steps to recover from etcd corruption.
(Claude Code will create the procedure)
```

Claude Code will infer the rest based on `_wiki-protocol.md`.

---

## When to Use Each Prompt

| Situation | Prompt |
|-----------|--------|
| First setup | Prompt 1 (Initialize) |
| Architectural decision made | Prompt 2 (Decision) |
| Bug fixed / incident resolved | Prompt 3 (Problem) |
| Want to reuse from other project | Prompt 4 (Cross-project) |
| Monthly maintenance | Prompt 5 (Vault lint) |
| Have legacy docs to onboard | Prompt 6 (Migration) |
| Closing a significant session | Prompt 7 (Session summary) |
