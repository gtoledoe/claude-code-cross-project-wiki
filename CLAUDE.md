# CLAUDE.md — llm-claude-code-wiki

This repository contains documentation for a multi-project wiki system for Claude Code.

## What This Repo Is

A methodology and set of templates for maintaining persistent technical documentation
across multiple Claude Code projects. It solves three problems:

- **Scope bleed** — Claude Code carries context from one project into another
- **Knowledge rot** — documentation goes stale with no signal
- **Knowledge silos** — no controlled way to reuse solutions across projects

## Your Role When Someone Opens This Repo

This is NOT a project to develop. It is a documentation system to ADOPT.

When the user asks you to implement these practices in their project:

1. Read `docs/_wiki-protocol.md` — understand vault conventions
2. Read `docs/implementation-guide.md` — follow the 8 setup steps
3. Read `docs/CLAUDE.md` — use as the CLAUDE.md template for their project
4. Ask the user for: project name, vault path, project type, preferred folder structure
5. Execute setup in the USER'S project — not in this repo
6. Never modify files in this repo

## Files in This Repo

| File | Purpose |
|------|---------|
| `README.md` | System overview — concepts, problems, solutions |
| `index.md` | Document map and reading order |
| `docs/_wiki-protocol.md` | Global protocol — copy to Obsidian vault root |
| `docs/CLAUDE.md` | CLAUDE.md template — copy to project repo |
| `docs/implementation-guide.md` | Step-by-step setup (8 steps, ~20 min) |
| `docs/example-prompts.md` | 7 ready-to-use prompts for Claude Code |
| `docs/example-documents.md` | Reference examples: ADR, Problem, Runbook |

## Do Not

- Modify any file in this repo unless the user explicitly asks to update the documentation system itself
- Create documents in this repo's folders (vault setup goes in the user's Obsidian vault)
- Assume the user wants to document THIS repo — they want to adopt the system for THEIR project
