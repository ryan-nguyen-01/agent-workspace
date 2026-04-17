#!/usr/bin/env bash
# validate-install.sh — Kiểm tra tính toàn vẹn agent-platform framework
# Usage: bash scripts/validate-install.sh [path-to-project]
#
# Exit codes: 0 = OK, 1 = errors found

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="${1:-.}"
CLAUDE_DIR="$PROJECT_ROOT/.claude"

ERRORS=0
WARNINGS=0

pass()  { echo -e "  ${GREEN}✓${NC} $1"; }
fail()  { echo -e "  ${RED}✗${NC} $1"; ((ERRORS++)); }
warn()  { echo -e "  ${YELLOW}⚠${NC} $1"; ((WARNINGS++)); }

echo "═══════════════════════════════════════════"
echo " agent-platform — Installation Validator"
echo "═══════════════════════════════════════════"
echo ""

# ─── 1. Core files ───────────────────────────────────────────
echo "▸ Core files"

for f in CLAUDE.md CLAUDE.local.md CHANGELOG.md SETUP.md GUIDELINES.md README.md; do
  if [[ -f "$PROJECT_ROOT/$f" ]]; then
    pass "$f"
  else
    fail "$f — missing"
  fi
done

# ─── 2. .claude directory structure ──────────────────────────
echo ""
echo "▸ Directory structure"

for d in agents skills rules templates commands context docs docs/diagrams tasks bugs; do
  if [[ -d "$CLAUDE_DIR/$d" ]]; then
    pass ".claude/$d/"
  else
    fail ".claude/$d/ — missing"
  fi
done

# ─── 3. Agent count ─────────────────────────────────────────
echo ""
echo "▸ Agents"

AGENT_COUNT=$(find "$CLAUDE_DIR/agents" -name "*.agent.md" 2>/dev/null | wc -l | tr -d ' ')
EXPECTED_AGENTS=11

if [[ "$AGENT_COUNT" -ge "$EXPECTED_AGENTS" ]]; then
  pass "Agents: $AGENT_COUNT found (expected ≥$EXPECTED_AGENTS)"
else
  fail "Agents: $AGENT_COUNT found (expected ≥$EXPECTED_AGENTS)"
fi

# ─── 4. Skill count ─────────────────────────────────────────
echo ""
echo "▸ Skills"

SKILL_COUNT=$(find "$CLAUDE_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
EXPECTED_SKILLS=12  # At minimum: 12 workflow skills

if [[ "$SKILL_COUNT" -ge "$EXPECTED_SKILLS" ]]; then
  pass "Skills: $SKILL_COUNT found (expected ≥$EXPECTED_SKILLS)"
else
  fail "Skills: $SKILL_COUNT found (expected ≥$EXPECTED_SKILLS)"
fi

# ─── 5. Rules ───────────────────────────────────────────────
echo ""
echo "▸ Rules"

RULE_COUNT=$(find "$CLAUDE_DIR/rules" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
EXPECTED_RULES=15

if [[ "$RULE_COUNT" -ge "$EXPECTED_RULES" ]]; then
  pass "Rules: $RULE_COUNT found (expected ≥$EXPECTED_RULES)"
else
  fail "Rules: $RULE_COUNT found (expected ≥$EXPECTED_RULES)"
fi

# ─── 6. Templates ───────────────────────────────────────────
echo ""
echo "▸ Templates"

TEMPLATE_COUNT=$(find "$CLAUDE_DIR/templates" -type f 2>/dev/null | wc -l | tr -d ' ')
EXPECTED_TEMPLATES=13

if [[ "$TEMPLATE_COUNT" -ge "$EXPECTED_TEMPLATES" ]]; then
  pass "Templates: $TEMPLATE_COUNT found (expected ≥$EXPECTED_TEMPLATES)"
else
  warn "Templates: $TEMPLATE_COUNT found (expected ≥$EXPECTED_TEMPLATES)"
fi

# ─── 7. Commands ────────────────────────────────────────────
echo ""
echo "▸ Commands"

COMMAND_COUNT=$(find "$CLAUDE_DIR/commands" -type f 2>/dev/null | wc -l | tr -d ' ')
EXPECTED_COMMANDS=15

if [[ "$COMMAND_COUNT" -ge "$EXPECTED_COMMANDS" ]]; then
  pass "Commands: $COMMAND_COUNT found (expected ≥$EXPECTED_COMMANDS)"
else
  warn "Commands: $COMMAND_COUNT found (expected ≥$EXPECTED_COMMANDS)"
fi

# ─── 8. Context placeholders ────────────────────────────────
echo ""
echo "▸ Context files"

for f in project-brain.yaml service-catalog.yaml agent-registry.yaml test-policy.yaml; do
  if [[ -f "$CLAUDE_DIR/context/$f" ]]; then
    pass ".claude/context/$f"
  else
    warn ".claude/context/$f — missing (created after /onboard)"
  fi
done

# ─── 9. Settings ────────────────────────────────────────────
echo ""
echo "▸ Settings"

if [[ -f "$CLAUDE_DIR/settings.json" ]]; then
  if [[ "$(cat "$CLAUDE_DIR/settings.json" | tr -d '[:space:]')" == "{}" ]]; then
    warn ".claude/settings.json — empty (no defaults configured)"
  else
    pass ".claude/settings.json"
  fi
else
  warn ".claude/settings.json — missing"
fi

# ─── 10. Documentation ──────────────────────────────────────
echo ""
echo "▸ Documentation"

DOC_COUNT=$(find "$CLAUDE_DIR/docs" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
SVG_COUNT=$(find "$CLAUDE_DIR/docs/diagrams" -name "*.svg" 2>/dev/null | wc -l | tr -d ' ')

if [[ "$DOC_COUNT" -ge 1 ]]; then
  pass "Docs: $DOC_COUNT markdown files"
else
  warn "Docs: none found in .claude/docs/"
fi

if [[ "$SVG_COUNT" -ge 1 ]]; then
  pass "Diagrams: $SVG_COUNT SVG files"
else
  warn "Diagrams: none found in .claude/docs/diagrams/"
fi

# ─── Summary ────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════"
if [[ "$ERRORS" -eq 0 && "$WARNINGS" -eq 0 ]]; then
  echo -e " ${GREEN}ALL CHECKS PASSED${NC}"
elif [[ "$ERRORS" -eq 0 ]]; then
  echo -e " ${GREEN}PASSED${NC} with ${YELLOW}$WARNINGS warning(s)${NC}"
else
  echo -e " ${RED}FAILED${NC}: $ERRORS error(s), $WARNINGS warning(s)"
fi
echo "═══════════════════════════════════════════"

exit "$ERRORS"
