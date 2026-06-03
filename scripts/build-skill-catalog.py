#!/usr/bin/env python3
"""Build a discoverability layer over the flat .claude/skills/ collection.

Skills MUST stay physically flat (`.claude/skills/<name>/SKILL.md`) for harness
discovery, so instead of moving folders this script taxonomises them:

  1. Reads name + description from each SKILL.md frontmatter.
  2. Classifies into ~12 domains (heuristic on name + description).
  3. Injects `category: <domain>` into the frontmatter (idempotent — skips if present).
  4. Writes machine index   -> .runtime/context/skill-taxonomy.yaml
  5. Writes human catalog    -> .agent/docs/skill-catalog.md  (quick-selection tables)

Usage:
  python3 scripts/build-skill-catalog.py            # write taxonomy + catalog + inject category
  python3 scripts/build-skill-catalog.py --check     # report only, no writes (CI drift check)
  python3 scripts/build-skill-catalog.py --no-inject # build outputs but don't touch SKILL.md files
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
TAXONOMY_YAML = ROOT / ".runtime" / "context" / "skill-taxonomy.yaml"
CATALOG_MD = ROOT / ".agent" / "docs" / "skill-catalog.md"

# (category, label) in match priority order. First matching rule wins.
CATEGORY_LABELS = {
    "workflow": "Workflow (control-plane skills)",
    "knowledge-patch": "Framework knowledge patches (post-cutoff updates)",
    "payments": "Payments & billing",
    "mobile": "Mobile",
    "data-ai": "Data & AI",
    "testing": "Testing & QA",
    "security": "Security & auth",
    "database": "Database & data stores",
    "devops-cloud": "DevOps, cloud & infra",
    "frontend": "Frontend & UI",
    "backend": "Backend & APIs",
    "meta-process": "Engineering process & meta",
    "misc": "Misc / cross-cutting",
}

# Ordered (category, keywords) — keyword matched against "<name> <description>".
RULES = [
    ("workflow", [r"^skill-"]),  # name-prefix rule
    ("knowledge-patch", [r"knowledge-patch$"]),  # name-suffix rule
    ("payments", ["stripe", "paypal", "payment", "billing-ops", "finance-billing", "customer-billing"]),
    ("mobile", ["android", "kotlin", "flutter", "swift", "capacitor", "react-native", "expo", "native-ui", "building-native"]),
    ("data-ai", ["genkit", "claude-api", "foundry", "firebase-ai", "machine learning", " ml ", "ml-", "llm", "data-engineer", "data pipeline", "analytics"]),
    ("testing", ["test", "playwright", "rspec", "tdd", "webapp-testing", "verification-before", "python-testing"]),
    ("security", ["security", "owasp", "auth", " iam", "iam ", "cognito", "vulnerab"]),
    ("database", ["postgres", "mysql", "redis", "mongo", "prisma", "drizzle", "typeorm", "sql", "dynamodb", "neon", "supabase", "oracle-database", "query-expert", "convex", "database", "kql", "upstash"]),
    ("devops-cloud", ["docker", "kubernetes", "k8s", "aws", "azure", "gcp", "cloud", "terraform", "cloudformation", "lambda", " s3", "eventbridge", "sqs", "cloudwatch", "serverless", "nginx", "traefik", "github-actions", "deploy", "firebase", "cost", "infra", "container"]),
    ("frontend", ["react", "vue", "angular", "svelte", "next", "astro", "tailwind", "shadcn", "css", " ui ", "ui ", "frontend", "framer", "gsap", " mui", "redux", "zustand", "accessibility", "web-design", "styled", "postcss", "scss", "vite", "vercel", "storefront", "admin-dashboard"]),
    ("backend", ["fastapi", "nestjs", "node", "spring", "django", "laravel", " php", "ruby", "rails", "golang", "go-", " go ", "rust", "koa", "fastify", "celery", "graphql", "rest", "websocket", "java", "aspnet", "blazor", "csharp", "axum", "tokio", "serde", "microservices", "kafka", "event-driven", "loom", "medusa", "notification", "python", "typescript", "email", "resend", "messages-ops", "performance-optim", "uv"]),
    ("meta-process", ["dispatching-parallel", "executing-plans", "writing-plans", "subagent-driven", "git-worktree", "systematic-debugging", "finishing-a-development", "code-review", "find-skills", "deep-research", "discover-"]),
]


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"')
    return fm


def classify(name: str, description: str) -> str:
    hay = f" {name.lower()} {description.lower()} "
    for category, keywords in RULES:
        for kw in keywords:
            if kw.startswith("^") or kw.endswith("$"):
                if re.search(kw, name.lower()):
                    return category
            elif kw in hay:
                return category
    return "misc"


def inject_category(path: Path, text: str, category: str) -> bool:
    """Insert `category: <cat>` after the description line. Idempotent."""
    fm = parse_frontmatter(text)
    if "category" in fm:
        return False
    lines = text.splitlines(keepends=True)
    # find description line within first frontmatter block
    for i, line in enumerate(lines[:40]):
        if re.match(r"^description:\s*", line):
            indent_line = f"category: {category}\n"
            lines.insert(i + 1, indent_line)
            path.write_text("".join(lines), encoding="utf-8")
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, no writes")
    ap.add_argument("--no-inject", action="store_true", help="build outputs but do not edit SKILL.md")
    args = ap.parse_args()

    entries = []  # (name, category, description)
    injected = 0
    for skill_md in sorted(SKILLS.rglob("SKILL.md")):
        text = skill_md.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        name = fm.get("name") or skill_md.parent.name
        desc = fm.get("description", "")
        category = fm.get("category") or classify(name, desc)
        entries.append((name, category, desc))
        if not args.check and not args.no_inject and "category" not in fm:
            if inject_category(skill_md, text, category):
                injected += 1

    by_cat: dict[str, list] = {c: [] for c in CATEGORY_LABELS}
    for name, category, desc in entries:
        by_cat.setdefault(category, []).append((name, desc))

    # ---- machine index ----
    yaml_lines = [
        "# Generated by scripts/build-skill-catalog.py — do not edit by hand.",
        "version: 1",
        f"total_skills: {len(entries)}",
        "categories:",
    ]
    for cat, label in CATEGORY_LABELS.items():
        items = sorted(by_cat.get(cat, []))
        yaml_lines.append(f"  {cat}:")
        yaml_lines.append(f'    label: "{label}"')
        yaml_lines.append(f"    count: {len(items)}")
        yaml_lines.append("    skills:")
        for name, _ in items:
            yaml_lines.append(f'      - "{name}"')
    yaml_text = "\n".join(yaml_lines) + "\n"

    # ---- human catalog ----
    md = [
        "# Skill Catalog",
        "",
        f"> Generated by `scripts/build-skill-catalog.py`. **{len(entries)} skills** across "
        f"{len([c for c in by_cat if by_cat[c]])} domains. Machine index: "
        "`.runtime/context/skill-taxonomy.yaml`. Skills stay physically flat at "
        "`.claude/skills/<name>/SKILL.md`; this catalog is the discovery layer.",
        "",
        "Each skill folder has a `category:` frontmatter field matching the tables below.",
        "",
        "## Quick selection",
        "",
        "| Domain | # | Skills |",
        "|--------|---|--------|",
    ]
    for cat, label in CATEGORY_LABELS.items():
        items = sorted(by_cat.get(cat, []))
        if not items:
            continue
        names = ", ".join(f"`{n}`" for n, _ in items)
        md.append(f"| **{label}** | {len(items)} | {names} |")
    md.append("")
    for cat, label in CATEGORY_LABELS.items():
        items = sorted(by_cat.get(cat, []))
        if not items:
            continue
        md.append(f"### {label} ({len(items)})")
        md.append("")
        for name, desc in items:
            md.append(f"- **`{name}`** — {desc}")
        md.append("")
    md_text = "\n".join(md)

    if args.check:
        print(f"[check] {len(entries)} skills; would write taxonomy + catalog.")
        for cat in CATEGORY_LABELS:
            print(f"  {cat:16s} {len(by_cat.get(cat, []))}")
        return 0

    TAXONOMY_YAML.write_text(yaml_text, encoding="utf-8")
    CATALOG_MD.write_text(md_text, encoding="utf-8")
    print(f"Wrote {TAXONOMY_YAML.relative_to(ROOT)} and {CATALOG_MD.relative_to(ROOT)}")
    print(f"Injected category frontmatter into {injected} SKILL.md files.")
    for cat in CATEGORY_LABELS:
        print(f"  {cat:16s} {len(by_cat.get(cat, []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
