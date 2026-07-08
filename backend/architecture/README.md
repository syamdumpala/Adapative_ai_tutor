# Architecture Folder — Source of Truth

This folder is the **single source of truth** for how the Adaptive AI Tutor
backend is structured and how it must be changed. Any developer or AI agent
**must read this folder before writing or modifying code**, and **must update
it after every change**.

## Files

| File            | Purpose                                                                 |
| --------------- | ----------------------------------------------------------------------- |
| `WORKFLOW.md`   | The mandatory step-by-step process for adding/changing a feature.       |
| `STRUCTURE.md`  | The full file/folder tree, naming conventions, and file responsibilities. |
| `DIAGRAM.md`    | Architecture diagrams (components, request lifecycle, AI pipeline).      |
| `HISTORY.md`    | Chronological log of every change made to the project.                   |

## How to use it (AI agents and developers)

1. **Before any work** → read `STRUCTURE.md`, `DIAGRAM.md`, and `HISTORY.md`.
2. Implement the change following the conventions in `STRUCTURE.md`.
3. Write unit tests, run them, and get a green suite.
4. **After the change** → update `STRUCTURE.md` / `DIAGRAM.md` (if structure or flow changed)
   and always append an entry to `HISTORY.md`.
5. Follow the full checklist in `WORKFLOW.md`.
