# Maestro SDLC

Classic software delivery: web, mobile, API products built greenfield through the full BA -> design -> UI/UX -> code -> QC pipeline.

A self-contained Maestro workspace. Copy this folder anywhere, put your source code inside
(`services/`, `apps/` — or register existing paths in `.maestro/registry/components.yaml`),
then run `claude` (or `codex`) in this folder and JUST DESCRIBE what you want in plain language
("phân tích dự án này", "sửa bug X", "tình hình?") — no commands needed; the coordinator maps
intent to the right flow. Power-user shortcuts exist in COMMAND.md if you want them.

Entry points: `CLAUDE.md` (Claude) - `AGENTS.md` (Codex) - `COMMAND.md` (commands)
- `.maestro/INSTRUCTIONS.md` (workflow brain).

Generated from the maestro platform - do not edit framework files by hand (see VARIANT.yaml).
