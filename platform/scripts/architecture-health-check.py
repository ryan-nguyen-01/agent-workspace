#!/usr/bin/env python3
"""Deterministic architecture drift check for the framework distribution.

This script is an optional CI/local safety net. It does not replace the
agent-native `/policy-check`, whose contract intentionally has no runtime
dependency. The checks here focus on things deterministic code is good at:
required files, counts, cross-tool entrypoint drift, model/profile consistency,
response UI consistency, generated status artifacts, and script smoke tests.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / ".maestro" / "engine"
KNOWLEDGE = ROOT / ".maestro" / "knowledge"
REGISTRY = ROOT / ".maestro" / "registry"
CONFIG = ROOT / ".maestro" / "config"
RUNTIME = ROOT / ".maestro" / "runtime"
WORK = ROOT / ".maestro" / "work"
REPORT_JSON = RUNTIME / "reports" / "architecture-health-report.json"
REPORT_MD = RUNTIME / "reports" / "architecture-health-report.md"

EXPECTED_COUNTS = {
    "agents": 34,
    "skills": 231,
    "rules": 23,
    "templates": 59,
    "commands": 19,
}

# Framework-owned agents: 12 workflow + 19 specialist advisors + 3 built-in coders.
# Generated service coders (coders/coder-<svc>.agent.md) are intentionally excluded so
# this count stays stable in applied workspaces.
BUILT_IN_CODERS = {"coder-infra", "coder-database", "coder-data"}
EXPECTED_SPECIALIST_COUNT = 19
SPECIALIST_CATEGORIES = {
    "architecture",
    "quality-security",
    "product",
    "data-ai",
    "ops-devex",
    "research-qa",
}

EXPECTED_WORKFLOW_AGENTS = {
    "coordinator",
    "onboarding",
    "agent-factory",
    "task-analysis",
    "solution-architect",
    "coder-leader",
    "dev-verification",
    "qc-handoff",
    "qc-runner",
    "bug-router",
    "memory-update",
    "workflow-policy",
}

EXPECTED_PROFILES = {
    "fast_router",
    "deep_reasoning",
    "coding",
    "coding_planner",
    "verification",
    "memory_light",
}

EXPECTED_PROVIDER_PROFILES = {"deep_reasoning", "coding", "fast"}

EXPECTED_RESPONSE_MODES = {
    "compact",
    "concise",
    "dashboard",
    "models",
    "dev",
    "review",
    "policy",
}

EXPECTED_STATUS_JSON_KEYS = {
    "workflow_state",
    "execution_mode",
    "verification_owner",
    "active_run_id",
    "active_runs",
    "project_knowledge",
    "project_brain",
    "components_detected",
    "active_coder_agents",
    "response_ui",
    "agent_model_profiles",
    "activity_status",
}

REQUIRED_PATHS = [
    "AGENTS.md",
    "CLAUDE.md",
    "COMMAND.md",
    ".maestro/engine/workflow.md",
    ".maestro/engine/rules/15-model-routing-observability-rules.md",
    ".maestro/project.yaml",
    ".maestro/methodology.yaml",
    ".maestro/manifest.yaml",
    ".maestro/observability/index.yaml",
    ".maestro/governance/index.yaml",
    ".maestro/registry/components.yaml",
    ".maestro/registry/skills.yaml",
    ".maestro/registry/artifacts.yaml",
    ".maestro/knowledge/project.yaml",
    ".maestro/work/index.yaml",
    ".maestro/design/index.yaml",
    ".maestro/decision/index.yaml",
    ".maestro/engine/templates/workflow-state.template.yaml",
    ".maestro/engine/templates/run.template.yaml",
    ".maestro/engine/templates/trace-summary.template.yaml",
    ".maestro/engine/templates/eval-run.template.yaml",
    ".maestro/engine/templates/approval-record.template.yaml",
    ".maestro/engine/templates/audit-view.template.md",
    ".maestro/config/model-routing.yaml",
    ".maestro/engine/templates/agent-activity.template.yaml",
    ".maestro/engine/templates/active-context.template.yaml",
    ".maestro/config/response-ui.yaml",
    ".maestro/INSTRUCTIONS.md",
    ".maestro/runtime/README.md",
    ".maestro/work/runs/index.yaml",
    "scripts/status-dashboard.py",
    "scripts/agent-activity.py",
    "scripts/agent-run.py",
    "scripts/architecture-health-check.py",
    "docs/README.md",
    "apps/README.md",
    "services/README.md",
    "packages/README.md",
    "infra/README.md",
    "tests/README.md",
]

ENTRYPOINT_REQUIREMENTS = {
    "AGENTS.md": [
        ".maestro/config/model-routing.yaml",
        ".maestro/runtime/agent-activity.yaml",
        ".maestro/config/response-ui.yaml",
        "scripts/status-dashboard.py",
        "R-015-01..22",
    ],
    "CLAUDE.md": [
        ".maestro/config/model-routing.yaml",
        ".maestro/runtime/agent-activity.yaml",
        ".maestro/config/response-ui.yaml",
        "scripts/status-dashboard.py",
    ],
    ".codex/AGENTS.md": [
        ".maestro/config/model-routing.yaml",
        ".maestro/runtime/agent-activity.yaml",
        ".maestro/config/response-ui.yaml",
        "scripts/status-dashboard.py",
    ],
}

STALE_TEXT_PATTERNS = [
    re.compile(r"\b227\s+skills?\b", re.I),
    re.compile(r"\b215\s+technical\s+skills?\b", re.I),
    re.compile(r"\b15\s+workflow\s+rules?\b", re.I),
    re.compile(r"R-015-01\.\.18"),
    re.compile(r"workflow-policy-check\.py"),
]

SERVICE_POLICY_DOCS = [
    "AGENTS.md",
    "README.md",
    "SETUP.md",
    "QUICKSTART.md",
    "GUIDELINES.md",
    ".maestro/README.md",
    "services/README.md",
]

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I),
    re.compile(r"\b(password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|cookie)\s*[:=]", re.I),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}", re.I),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}", re.I),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}", re.I),
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def status_dashboard_module() -> Any:
    module_path = ROOT / "scripts" / "status-dashboard.py"
    spec = importlib.util.spec_from_file_location("status_dashboard", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_yaml(path: Path) -> dict[str, Any]:
    return status_dashboard_module().load_yaml(path)


def add(findings: list[dict[str, str]], severity: str, code: str, message: str, evidence: str) -> None:
    findings.append(
        {
            "severity": severity,
            "code": code,
            "message": message,
            "evidence": evidence,
        }
    )


def count_framework_agents() -> int:
    agents_dir = ROOT / ".claude" / "agents"
    workflow = len(list((agents_dir / "workflow").glob("*.agent.md")))
    specialists = len(list((agents_dir / "specialists").rglob("*.agent.md")))
    builtins = sum(1 for c in BUILT_IN_CODERS if (agents_dir / "coders" / f"{c}.agent.md").exists())
    return workflow + specialists + builtins


def count_files() -> dict[str, int]:
    return {
        "agents": count_framework_agents(),
        "skills": len(list((ROOT / ".claude" / "skills").rglob("SKILL.md"))),
        "rules": len([p for p in (ENGINE / "rules").glob("*.md") if p.name != "README.md"]),
        "templates": len([p for p in (ENGINE / "templates").iterdir() if p.is_file()]),
        "commands": len([p for p in (ROOT / ".claude" / "commands").glob("*.md") if p.name != "README.md"]),
    }


def check_required_paths(findings: list[dict[str, str]]) -> None:
    for raw in REQUIRED_PATHS:
        path = ROOT / raw
        if not path.exists():
            add(findings, "error", "missing-required-file", f"Missing required file: {raw}", raw)


def check_counts(findings: list[dict[str, str]]) -> dict[str, int]:
    counts = count_files()
    for key, expected in EXPECTED_COUNTS.items():
        actual = counts.get(key)
        if actual != expected:
            add(findings, "error", "count-drift", f"{key} count drift: expected {expected}, got {actual}", key)
    return counts


def check_entrypoints(findings: list[dict[str, str]]) -> None:
    for raw, fragments in ENTRYPOINT_REQUIREMENTS.items():
        path = ROOT / raw
        if not path.exists():
            add(findings, "error", "entrypoint-missing", f"Missing entrypoint {raw}", raw)
            continue
        text = path.read_text(encoding="utf-8")
        for fragment in fragments:
            if fragment not in text:
                add(findings, "error", "entrypoint-drift", f"{raw} missing required fragment: {fragment}", raw)


def iter_scan_files() -> list[Path]:
    suffixes = {".md", ".mdc", ".yaml", ".yml", ".json", ".toml", ".py", ".sh"}
    ignored_dirs = {".git", "services", "__pycache__", "node_modules"}
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in ignored_dirs or part.startswith("maestro-") for part in path.parts):
            continue
        if path.is_file() and path.suffix in suffixes:
            files.append(path)
    return files


def check_stale_text(findings: list[dict[str, str]]) -> None:
    for path in iter_scan_files():
        rel = path.relative_to(ROOT)
        if rel.as_posix() == "skills-lock.json":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in STALE_TEXT_PATTERNS:
            match = pattern.search(text)
            if match:
                add(findings, "error", "stale-text", f"Stale reference `{match.group(0)}` in {rel}", str(rel))


def check_model_routing(findings: list[dict[str, str]]) -> None:
    routing = load_yaml(CONFIG / "model-routing.yaml")
    profiles = routing.get("model_profiles", {})
    if not isinstance(profiles, dict):
        add(findings, "error", "model-routing-invalid", "model_profiles is missing or not a map", "model-routing.yaml")
        return
    profile_names = set(profiles.keys())
    missing_profiles = EXPECTED_PROFILES - profile_names
    if missing_profiles:
        add(findings, "error", "model-profile-missing", f"Missing model profiles: {sorted(missing_profiles)}", "model-routing.yaml")

    agent_map = routing.get("agent_model_map", {})
    workflow_agents = agent_map.get("workflow_agents", {}) if isinstance(agent_map, dict) else {}
    if not isinstance(workflow_agents, dict):
        add(findings, "error", "agent-model-map-invalid", "workflow_agents is missing or not a map", "model-routing.yaml")
        return
    actual_agents = set(workflow_agents.keys())
    if actual_agents != EXPECTED_WORKFLOW_AGENTS:
        add(
            findings,
            "error",
            "workflow-agent-map-drift",
            f"Workflow agent model map mismatch: missing={sorted(EXPECTED_WORKFLOW_AGENTS - actual_agents)} extra={sorted(actual_agents - EXPECTED_WORKFLOW_AGENTS)}",
            "model-routing.yaml",
        )

    for agent_id, cfg in workflow_agents.items():
        profile = cfg.get("model_profile") if isinstance(cfg, dict) else None
        if profile not in profile_names:
            add(findings, "error", "agent-profile-invalid", f"{agent_id} uses unknown model_profile {profile}", "model-routing.yaml")

    built_in = agent_map.get("built_in_coders", {}) if isinstance(agent_map, dict) else {}
    for coder in ("coder-infra", "coder-database", "coder-data"):
        cfg = built_in.get(coder) if isinstance(built_in, dict) else None
        profile = cfg.get("model_profile") if isinstance(cfg, dict) else None
        if profile not in profile_names:
            add(findings, "error", "builtin-profile-invalid", f"{coder} uses unknown model_profile {profile}", "model-routing.yaml")

    defaults = routing.get("provider_defaults", {})
    for provider in ("claude", "codex", "generic"):
        provider_cfg = defaults.get(provider) if isinstance(defaults, dict) else None
        if not isinstance(provider_cfg, dict):
            add(findings, "error", "provider-default-missing", f"Missing provider defaults for {provider}", "model-routing.yaml")
            continue
        for profile in ("deep_reasoning", "coding", "fast"):
            if profile not in provider_cfg:
                add(findings, "error", "provider-profile-missing", f"{provider} missing {profile} default", "model-routing.yaml")
    check_model_overrides(findings, routing, profile_names, defaults if isinstance(defaults, dict) else {})


def model_profile_map(agent_map: dict[str, Any], group_name: str) -> dict[str, str]:
    group = agent_map.get(group_name, {})
    if not isinstance(group, dict):
        return {}
    result: dict[str, str] = {}
    for agent_id, cfg in group.items():
        if isinstance(cfg, dict) and cfg.get("model_profile"):
            result[str(agent_id)] = str(cfg["model_profile"])
    return result


def check_model_routing_template(findings: list[dict[str, str]]) -> None:
    runtime = load_yaml(CONFIG / "model-routing.yaml")
    template = load_yaml(ENGINE / "templates" / "model-routing.template.yaml")
    runtime_map = runtime.get("agent_model_map", {})
    template_map = template.get("agent_model_map", {})
    if not isinstance(runtime_map, dict) or not isinstance(template_map, dict):
        add(findings, "error", "model-routing-template-invalid", "runtime/template agent_model_map must both be maps", "model-routing.template.yaml")
        return

    for group_name in ("workflow_agents", "built_in_coders"):
        runtime_profiles = model_profile_map(runtime_map, group_name)
        template_profiles = model_profile_map(template_map, group_name)
        if runtime_profiles != template_profiles:
            missing = sorted(set(runtime_profiles) - set(template_profiles))
            extra = sorted(set(template_profiles) - set(runtime_profiles))
            changed = sorted(
                agent_id
                for agent_id in set(runtime_profiles) & set(template_profiles)
                if runtime_profiles[agent_id] != template_profiles[agent_id]
            )
            add(
                findings,
                "error",
                "model-routing-template-drift",
                f"{group_name} profile map differs from runtime seed: missing={missing} extra={extra} changed={changed}",
                "model-routing.template.yaml",
            )

    runtime_generated = runtime_map.get("generated_service_coders", {})
    template_generated = template_map.get("generated_service_coders", {})
    runtime_default = runtime_generated.get("default_model_profile") if isinstance(runtime_generated, dict) else None
    template_default = template_generated.get("default_model_profile") if isinstance(template_generated, dict) else None
    if runtime_default != template_default:
        add(
            findings,
            "error",
            "model-routing-generated-default-drift",
            f"generated_service_coders.default_model_profile differs: runtime={runtime_default} template={template_default}",
            "model-routing.template.yaml",
        )


def override_reason_required(overrides: dict[str, Any]) -> bool:
    policy = overrides.get("policy", {})
    return isinstance(policy, dict) and policy.get("require_reason") is True


def check_override_reason(
    findings: list[dict[str, str]],
    code: str,
    cfg: Any,
    evidence: str,
    required: bool,
) -> None:
    if required and isinstance(cfg, dict) and cfg and not cfg.get("reason"):
        add(findings, "error", code, f"Model override missing required reason: {evidence}", "model-routing.yaml")


def check_model_overrides(
    findings: list[dict[str, str]],
    routing: dict[str, Any],
    profile_names: set[str],
    defaults: dict[str, Any],
) -> None:
    overrides = routing.get("model_overrides")
    if not isinstance(overrides, dict):
        add(findings, "error", "model-overrides-missing", "model_overrides map is required for safe model switching", "model-routing.yaml")
        return

    policy = overrides.get("policy", {})
    if not isinstance(policy, dict):
        add(findings, "error", "model-overrides-policy-invalid", "model_overrides.policy must be a map", "model-routing.yaml")
        policy = {}
    valid_provider_profiles = policy.get("valid_provider_profiles", [])
    if set(valid_provider_profiles) != EXPECTED_PROVIDER_PROFILES:
        add(
            findings,
            "error",
            "model-overrides-provider-profiles-invalid",
            "model_overrides.policy.valid_provider_profiles must be deep_reasoning/coding/fast",
            "model-routing.yaml",
        )

    reason_required = override_reason_required(overrides)
    provider_overrides = overrides.get("provider_profile_overrides", {})
    if not isinstance(provider_overrides, dict):
        add(findings, "error", "provider-profile-overrides-invalid", "provider_profile_overrides must be a map", "model-routing.yaml")
    else:
        for provider, provider_cfg in provider_overrides.items():
            if provider not in defaults:
                add(findings, "error", "provider-override-unknown-provider", f"Override uses unknown provider {provider}", "model-routing.yaml")
            if not isinstance(provider_cfg, dict):
                add(findings, "error", "provider-override-invalid", f"Override for provider {provider} must be a map", "model-routing.yaml")
                continue
            for provider_profile, cfg in provider_cfg.items():
                if provider_profile not in EXPECTED_PROVIDER_PROFILES:
                    add(
                        findings,
                        "error",
                        "provider-override-unknown-profile",
                        f"Override uses unknown provider profile {provider}.{provider_profile}",
                        "model-routing.yaml",
                    )
                if not isinstance(cfg, dict):
                    add(findings, "error", "provider-override-entry-invalid", f"Override {provider}.{provider_profile} must be a map", "model-routing.yaml")
                    continue
                if not cfg.get("model_id"):
                    add(findings, "error", "provider-override-model-missing", f"Override {provider}.{provider_profile} missing model_id", "model-routing.yaml")
                check_override_reason(findings, "provider-override-reason-missing", cfg, f"{provider}.{provider_profile}", reason_required)

    agent_overrides = overrides.get("agent_overrides", {})
    known_agent_ids = EXPECTED_WORKFLOW_AGENTS | {"coder-infra", "coder-database", "coder-data", "generated-service-coders"}
    if not isinstance(agent_overrides, dict):
        add(findings, "error", "agent-overrides-invalid", "agent_overrides must be a map", "model-routing.yaml")
    else:
        for agent_id, cfg in agent_overrides.items():
            if agent_id not in known_agent_ids and not str(agent_id).startswith("coder-"):
                add(findings, "error", "agent-override-unknown-agent", f"Agent override targets unknown agent {agent_id}", "model-routing.yaml")
            if not isinstance(cfg, dict):
                add(findings, "error", "agent-override-entry-invalid", f"Agent override {agent_id} must be a map", "model-routing.yaml")
                continue
            profile = cfg.get("model_profile")
            if profile is not None and profile not in profile_names:
                add(findings, "error", "agent-override-profile-invalid", f"Agent override {agent_id} uses unknown model_profile {profile}", "model-routing.yaml")
            check_override_reason(findings, "agent-override-reason-missing", cfg, str(agent_id), reason_required)

    phase_overrides = overrides.get("phase_overrides", {})
    if not isinstance(phase_overrides, dict):
        add(findings, "error", "phase-overrides-invalid", "phase_overrides must be a map", "model-routing.yaml")
    else:
        for phase, cfg in phase_overrides.items():
            if not isinstance(cfg, dict):
                add(findings, "error", "phase-override-entry-invalid", f"Phase override {phase} must be a map", "model-routing.yaml")
                continue
            profile = cfg.get("model_profile")
            provider_profile = cfg.get("provider_profile")
            if profile is not None and profile not in profile_names:
                add(findings, "error", "phase-override-profile-invalid", f"Phase override {phase} uses unknown model_profile {profile}", "model-routing.yaml")
            if provider_profile is not None and provider_profile not in EXPECTED_PROVIDER_PROFILES:
                add(findings, "error", "phase-override-provider-profile-invalid", f"Phase override {phase} uses unknown provider_profile {provider_profile}", "model-routing.yaml")
            check_override_reason(findings, "phase-override-reason-missing", cfg, str(phase), reason_required)

    emergency = overrides.get("emergency_runtime_override", {})
    if not isinstance(emergency, dict):
        add(findings, "error", "emergency-override-invalid", "emergency_runtime_override must be a map", "model-routing.yaml")
    elif emergency.get("enabled") is True:
        if not emergency.get("model_id"):
            add(findings, "error", "emergency-override-model-missing", "Enabled emergency override requires model_id", "model-routing.yaml")
        if not emergency.get("reason"):
            add(findings, "error", "emergency-override-reason-missing", "Enabled emergency override requires reason", "model-routing.yaml")
        if policy.get("require_expires_at_for_emergency") is True and not emergency.get("expires_at"):
            add(findings, "error", "emergency-override-expiry-missing", "Enabled emergency override requires expires_at", "model-routing.yaml")
        provider_profile = emergency.get("provider_profile")
        if provider_profile is not None and provider_profile not in EXPECTED_PROVIDER_PROFILES:
            add(findings, "error", "emergency-override-provider-profile-invalid", f"Emergency override uses unknown provider_profile {provider_profile}", "model-routing.yaml")


def check_response_ui(findings: list[dict[str, str]]) -> None:
    response_ui = load_yaml(CONFIG / "response-ui.yaml")
    modes = response_ui.get("modes", {})
    if not isinstance(modes, dict):
        add(findings, "error", "response-ui-invalid", "modes is missing or not a map", "response-ui.yaml")
        return
    missing = EXPECTED_RESPONSE_MODES - set(modes.keys())
    if missing:
        add(findings, "error", "response-mode-missing", f"Missing response modes: {sorted(missing)}", "response-ui.yaml")

    intent_routing = response_ui.get("intent_routing", {})
    if isinstance(intent_routing, dict):
        for intent, cfg in intent_routing.items():
            mode = cfg.get("mode") if isinstance(cfg, dict) else None
            if mode not in modes:
                add(findings, "error", "intent-mode-invalid", f"intent_routing.{intent} points to unknown mode {mode}", "response-ui.yaml")

    artifacts = response_ui.get("status_artifacts", {})
    if not isinstance(artifacts, dict) or not artifacts.get("markdown") or not artifacts.get("html"):
        add(findings, "error", "status-artifacts-missing", "response-ui status_artifacts markdown/html paths are required", "response-ui.yaml")


def check_status_dashboard(findings: list[dict[str, str]]) -> None:
    module = status_dashboard_module()
    for mode in ("compact", "concise", "dashboard", "models"):
        try:
            rendered = module.render(mode=mode, show_models=False)
        except Exception as exc:  # noqa: BLE001 - surface exact smoke-test failure.
            add(findings, "error", "status-render-failed", f"status-dashboard render failed for {mode}: {exc}", "status-dashboard.py")
            continue
        if "Maestro Status" not in rendered and mode != "compact":
            add(findings, "error", "status-render-invalid", f"status-dashboard output for {mode} is missing title", "status-dashboard.py")
        if mode == "dashboard":
            required_fragments = ["Project Knowledge", "freshness:", "Response UI", "selected mode:"]
            missing = [fragment for fragment in required_fragments if fragment not in rendered]
            if missing:
                add(
                    findings,
                    "error",
                    "status-contract-missing-section",
                    f"dashboard mode missing required /status fragments: {missing}",
                    "status-dashboard.py",
                )
    try:
        data = json.loads(module.render(mode="json", show_models=False))
        missing_keys = sorted(EXPECTED_STATUS_JSON_KEYS - set(data.keys()))
        if missing_keys:
            add(findings, "error", "status-json-contract-drift", f"status json missing keys: {missing_keys}", "status-dashboard.py")
        response_ui = data.get("response_ui")
        if not isinstance(response_ui, dict) or not response_ui.get("selected_mode"):
            add(findings, "error", "status-json-response-ui-drift", "status json missing response_ui.selected_mode", "status-dashboard.py")
        if data.get("project_brain") not in {"fresh", "stale", "missing", "unknown"}:
            add(findings, "error", "status-json-brain-drift", f"status json has invalid project_brain value: {data.get('project_brain')}", "status-dashboard.py")
    except Exception as exc:  # noqa: BLE001
        add(findings, "error", "status-json-invalid", f"status-dashboard json mode failed: {exc}", "status-dashboard.py")

    response_ui = load_yaml(CONFIG / "response-ui.yaml")
    artifacts = response_ui.get("status_artifacts", {}) if isinstance(response_ui, dict) else {}
    html_style = artifacts.get("html_style") if isinstance(artifacts, dict) else None
    for key in ("markdown", "html"):
        raw = artifacts.get(key) if isinstance(artifacts, dict) else None
        if not raw:
            continue
        path = ROOT / str(raw)
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "Generated at:" not in text:
                add(findings, "error", "generated-status-stale-format", f"Generated status artifact lacks Generated at marker: {raw}", str(raw))
            if key == "html" and html_style == "github-readme-card" and 'data-view="github-readme-card"' not in text:
                add(findings, "error", "generated-status-html-style-drift", "Generated HTML status does not use github-readme-card style", str(raw))


def check_services_workspace_policy(findings: list[dict[str, str]]) -> None:
    registry = load_yaml(REGISTRY / "components.yaml")
    discovery = registry.get("discovery", {}) if isinstance(registry, dict) else {}
    scan_roots = discovery.get("scan_roots", []) if isinstance(discovery, dict) else []
    registered_roots = {
        str(item.get("path"))
        for item in scan_roots
        if isinstance(item, dict) and item.get("path")
    }
    required_roots = {"apps", "services", "packages", "infra", "tests"}
    if registered_roots != required_roots:
        add(
            findings,
            "error",
            "component-roots-drift",
            f"components.yaml scan roots must be {sorted(required_roots)}, got {sorted(registered_roots)}",
            ".maestro/registry/components.yaml",
        )
    for root_name in required_roots:
        if not (ROOT / root_name / "README.md").is_file():
            add(
                findings,
                "error",
                "component-root-missing",
                f"Missing component root documentation: {root_name}/README.md",
                root_name,
            )


def collect_task_bug_refs(value: Any) -> list[Any]:
    refs: list[Any] = []

    def visit(item: Any) -> None:
        if isinstance(item, list):
            for child in item:
                visit(child)
            return
        if isinstance(item, dict):
            if item.get("bug_id") or item.get("id") or item.get("canonical_path"):
                refs.append(item)
                return
            for key in ("bugs", "blockers", "non_blockers", "non-blockers", "open", "assigned", "fixed", "retest"):
                if key in item:
                    visit(item[key])
            return
        if isinstance(item, str) and item.strip().startswith("BUG-"):
            refs.append(item.strip())

    raw = value.get("_raw") if isinstance(value, dict) and "_raw" in value else value
    visit(raw)
    return refs


def bug_ref_field(ref: Any, *keys: str) -> str | None:
    if isinstance(ref, str):
        return ref if "bug_id" in keys or "id" in keys else None
    if not isinstance(ref, dict):
        return None
    for key in keys:
        value = ref.get(key)
        if value:
            return str(value)
    return None


def canonical_bug_path(ref: Any) -> Path | None:
    raw_path = bug_ref_field(ref, "canonical_path", "path", "artifact")
    if raw_path:
        path = Path(raw_path)
        return path if path.is_absolute() else ROOT / path

    bug_id = bug_ref_field(ref, "bug_id", "id")
    if not bug_id:
        return None

    severity = (bug_ref_field(ref, "severity") or "").lower()
    candidate_dirs: list[Path]
    if severity == "blocker":
        candidate_dirs = [WORK / "bugs" / "blockers"]
    elif severity in {"non-blocker", "non_blocker", "nonblocker"}:
        candidate_dirs = [WORK / "bugs" / "non-blockers"]
    else:
        candidate_dirs = [WORK / "bugs" / "blockers", WORK / "bugs" / "non-blockers"]

    for directory in candidate_dirs:
        candidate = directory / f"{bug_id}.yaml"
        if candidate.exists():
            return candidate
    matches = list((WORK / "bugs").glob(f"**/{bug_id}.yaml"))
    return matches[0] if matches else candidate_dirs[0] / f"{bug_id}.yaml"


def check_bug_artifact_integrity(findings: list[dict[str, str]]) -> None:
    tasks_root = WORK / "tasks"
    if not tasks_root.exists():
        return
    for bugs_index in tasks_root.glob("*/bugs.yaml"):
        rel_index = bugs_index.relative_to(ROOT).as_posix()
        data = load_yaml(bugs_index)
        refs = collect_task_bug_refs(data)
        for ref in refs:
            bug_id = bug_ref_field(ref, "bug_id", "id") or str(ref)
            path = canonical_bug_path(ref)
            if path is None or not path.exists():
                add(
                    findings,
                    "error",
                    "bug-canonical-missing",
                    f"{rel_index} references {bug_id} but matching canonical .maestro/work/bugs artifact is missing",
                    rel_index,
                )


def check_feedback_loop_contract(findings: list[dict[str, str]]) -> None:
    required_fragments = {
        ".maestro/engine/templates/bug.template.yaml": [
            "prevention:",
            "root_cause:",
            "prevention_rule:",
            "regression_check:",
            "recurrence_key:",
        ],
        ".maestro/engine/templates/dev-verification.template.yaml": [
            "feedback_loop:",
            "repeated_error_detected:",
            "new_coding_error_feedback:",
            "memory_update_required:",
        ],
        ".maestro/engine/templates/memory-update.template.yaml": [
            "coding-error-feedback",
            "coding_errors_captured:",
            "prevention_rules_added:",
            "regression_checks_added:",
        ],
        ".maestro/engine/templates/agent-coder.template.md": [
            "feedback_preflight:",
            "coding_error_feedback:",
            "known_error_patterns:",
            "regression_checks:",
        ],
        ".maestro/memory/project/feedback/inbox.md": [
            "coding-error",
            "root_cause:",
            "prevention_rule:",
            "regression_check:",
            "recurrence_key:",
        ],
        ".maestro/memory/project/feedback/anti-patterns.md": [
            "recurrence_key:",
            "prevention_rule:",
            "regression_check:",
        ],
    }
    for raw, fragments in required_fragments.items():
        path = ROOT / raw
        if not path.exists():
            add(findings, "error", "feedback-contract-file-missing", f"Missing feedback-loop contract file: {raw}", raw)
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        missing = [fragment for fragment in fragments if fragment not in text]
        if missing:
            add(
                findings,
                "error",
                "feedback-loop-contract-drift",
                f"{raw} missing feedback-loop fragments: {missing}",
                raw,
            )


def check_agent_activity(findings: list[dict[str, str]]) -> None:
    activity_path = RUNTIME / "agent-activity.yaml"
    if not activity_path.is_file():
        activity_path = ENGINE / "templates" / "agent-activity.template.yaml"
    activity = load_yaml(activity_path)
    if not isinstance(activity, dict):
        add(findings, "error", "agent-activity-invalid", "agent-activity.yaml is not a map", "agent-activity.yaml")
        return
    automation = activity.get("automation", {})
    if not isinstance(automation, dict) or "agent-activity.py" not in str(automation.get("update_cli", "")):
        add(findings, "error", "activity-automation-missing", "agent-activity.yaml must advertise scripts/agent-activity.py automation", "agent-activity.yaml")
    text = json.dumps(activity, ensure_ascii=False)
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            add(findings, "error", "activity-secret-risk", "agent-activity.yaml appears to contain secret-like text", "agent-activity.yaml")



def check_specialists(findings: list[dict[str, str]]) -> None:
    spec_dir = ROOT / ".claude" / "agents" / "specialists"
    if not spec_dir.is_dir():
        add(findings, "error", "specialists-dir-missing", "Missing .claude/agents/specialists/ directory", "specialists")
        return
    files = sorted(spec_dir.rglob("*.agent.md"))
    if len(files) != EXPECTED_SPECIALIST_COUNT:
        add(findings, "error", "specialist-count-drift", f"specialist count drift: expected {EXPECTED_SPECIALIST_COUNT}, got {len(files)}", "specialists")

    routing = load_yaml(CONFIG / "model-routing.yaml")
    agent_map = routing.get("agent_model_map", {}) if isinstance(routing, dict) else {}
    advisors = agent_map.get("specialist_advisors", {}) if isinstance(agent_map, dict) else {}
    advisor_ids = set(advisors.keys()) if isinstance(advisors, dict) else set()

    file_ids = set()
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        name_m = re.search(r"^name:\s*(.+)$", text, re.M)
        cat_m = re.search(r"^category:\s*(.+)$", text, re.M)
        name = name_m.group(1).strip().strip('"') if name_m else f.stem.replace(".agent", "")
        file_ids.add(name)
        if not cat_m:
            add(findings, "error", "specialist-frontmatter-invalid", f"{f.name} missing category frontmatter", f.name)
        elif cat_m.group(1).strip().strip('"') not in SPECIALIST_CATEGORIES:
            add(findings, "error", "specialist-category-invalid", f"{f.name} has unknown category {cat_m.group(1).strip()}", f.name)
        # advisor-only contract guard
        if "Advisor-only" not in text and "advisor-only" not in text.lower():
            add(findings, "error", "specialist-advisory-contract-missing", f"{f.name} lacks advisor-only contract text", f.name)

    if isinstance(advisors, dict):
        missing = sorted(file_ids - advisor_ids)
        extra = sorted(advisor_ids - file_ids)
        if missing or extra:
            add(findings, "error", "specialist-routing-drift", f"specialist_advisors map vs files mismatch: missing={missing} extra={extra}", "model-routing.yaml")
        profile_names = set(routing.get("model_profiles", {}).keys()) if isinstance(routing, dict) else set()
        for sid, cfg in advisors.items():
            prof = cfg.get("model_profile") if isinstance(cfg, dict) else None
            if prof not in profile_names:
                add(findings, "error", "specialist-profile-invalid", f"specialist {sid} uses unknown model_profile {prof}", "model-routing.yaml")
    else:
        add(findings, "error", "specialist-routing-missing", "model-routing.yaml missing agent_model_map.specialist_advisors", "model-routing.yaml")

    # Guard the integration: specialists must be operationally wired into the agents that invoke them,
    # not just defined. Each of these workflow agents must reference the advisory contract.
    wiring = {
        "task-analysis": "advisory_required",
        "solution-architect": "advisor",
        "coder-leader": "advisor",
        "dev-verification": "advisor",
        "qc-handoff": "advisor",
    }
    wf_dir = ROOT / ".claude" / "agents" / "workflow"
    for agent_id, needle in wiring.items():
        path = wf_dir / f"{agent_id}.agent.md"
        text = path.read_text(encoding="utf-8", errors="ignore").lower() if path.is_file() else ""
        if needle.lower() not in text or "advisor" not in text:
            add(findings, "error", "specialist-wiring-missing", f"{agent_id}.agent.md does not wire specialist advisories (R-016 integration)", f"{agent_id}.agent.md")


def check_claude_hooks(findings: list[dict[str, str]]) -> None:
    settings_path = ROOT / ".claude" / "settings.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        add(findings, "error", "claude-settings-invalid", f"Cannot parse .claude/settings.json: {exc}", ".claude/settings.json")
        return
    hooks = settings.get("hooks", {})
    pre = hooks.get("PreToolUse", []) if isinstance(hooks, dict) else []
    commands = " ".join(
        h.get("command", "")
        for group in pre if isinstance(group, dict)
        for h in group.get("hooks", []) if isinstance(h, dict)
    )
    for script in ("scope-guard.py", "secret-guard.py", "destructive-guard.py"):
        if script not in commands:
            add(findings, "error", "claude-hook-missing", f"settings.json PreToolUse missing {script}", ".claude/settings.json")
        if not (ROOT / "scripts" / "hooks" / script).is_file():
            add(findings, "error", "claude-hook-script-missing", f"Missing hook script scripts/hooks/{script}", f"scripts/hooks/{script}")


def check_plugin_wrapper(findings: list[dict[str, str]]) -> None:
    """The Claude plugin wrapper must exist, be valid JSON, and stay generated from source."""
    plugin_dir = ROOT / ".claude-plugin"
    for name in ("plugin.json", "hooks.json", "marketplace.json"):
        path = plugin_dir / name
        if not path.is_file():
            add(findings, "error", "plugin-wrapper-missing", f"Missing .claude-plugin/{name} (run scripts/build-plugin.py)", f".claude-plugin/{name}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            add(findings, "error", "plugin-wrapper-invalid", f".claude-plugin/{name} is not valid JSON: {exc}", f".claude-plugin/{name}")
    # Drift: wrapper must match scripts/build-plugin.py output (single source of truth).
    try:
        module_path = ROOT / "scripts" / "build-plugin.py"
        spec = importlib.util.spec_from_file_location("build_plugin", module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            version = module.framework_version()
            c = module.counts()
            expected = {
                module.PLUGIN_DIR / "plugin.json": module.dump(module.PLUGIN_DIR / "plugin.json", module.build_manifest(version, c)),
                module.PLUGIN_DIR / "hooks.json": module.dump(module.PLUGIN_DIR / "hooks.json", module.translate_hooks()),
                module.PLUGIN_DIR / "marketplace.json": module.dump(module.PLUGIN_DIR / "marketplace.json", module.build_marketplace(version)),
            }
            for path, exp in expected.items():
                actual = path.read_text(encoding="utf-8") if path.is_file() else None
                if actual != exp:
                    add(findings, "error", "plugin-wrapper-drift", f"{path.relative_to(ROOT).as_posix()} out of sync; run scripts/build-plugin.py", path.name)
    except Exception as exc:  # noqa: BLE001
        add(findings, "error", "plugin-wrapper-check-failed", f"plugin wrapper drift check failed: {exc}", "scripts/build-plugin.py")


def check_skill_taxonomy(findings: list[dict[str, str]]) -> None:
    tax_path = REGISTRY / "skill-taxonomy.yaml"
    if not tax_path.is_file():
        add(findings, "error", "skill-taxonomy-missing", "Missing .maestro/registry/skill-taxonomy.yaml (run scripts/build-skill-catalog.py)", "skill-taxonomy.yaml")
        return
    tax = load_yaml(tax_path)
    total = tax.get("total_skills") if isinstance(tax, dict) else None
    actual = len(list((ROOT / ".claude" / "skills").rglob("SKILL.md")))
    if total != actual:
        add(findings, "error", "skill-taxonomy-stale", f"skill-taxonomy total_skills={total} but {actual} SKILL.md found; rerun scripts/build-skill-catalog.py", "skill-taxonomy.yaml")
    if not (ENGINE / "docs" / "skill-catalog.md").is_file():
        add(findings, "error", "skill-catalog-missing", "Missing .maestro/engine/docs/skill-catalog.md", "skill-catalog.md")

    registry = load_yaml(REGISTRY / "skills.yaml")
    catalog = registry.get("catalog", {}) if isinstance(registry, dict) else {}
    if not isinstance(catalog, dict) or len(catalog) != actual:
        add(
            findings,
            "error",
            "skill-registry-incomplete",
            f"skills.yaml catalog must address all {actual} skills; found {len(catalog) if isinstance(catalog, dict) else 0}",
            ".maestro/registry/skills.yaml",
        )
        return
    for skill_id, entry in catalog.items():
        path = entry.get("path") if isinstance(entry, dict) else None
        capability = entry.get("capability") if isinstance(entry, dict) else None
        if not path or not (ROOT / str(path)).is_file() or not capability:
            add(
                findings,
                "error",
                "skill-registry-entry-invalid",
                f"Skill {skill_id} must have an existing path and non-empty capability",
                ".maestro/registry/skills.yaml",
            )


# Commands excluded from the Codex prompt surface (Claude-plugin-specific). Keep in sync with
# scripts/build-codex-prompts.py EXCLUDE.
CODEX_PROMPT_EXCLUDE = {"access"}


def check_codex_plugin(findings: list[dict[str, str]]) -> None:
    """Codex plugin manifests must exist + be valid. The skills copy is build-time/gitignored, so
    it is NOT required here — only the manifests are checked for drift parity with the Claude side."""
    manifest = ROOT / ".codex" / "marketplace" / "plugins" / "maestro" / ".codex-plugin" / "plugin.json"
    market = ROOT / ".codex" / "marketplace" / ".agents" / "plugins" / "marketplace.json"
    for raw, label in ((manifest, "codex-plugin"), (market, "codex-marketplace")):
        if not raw.is_file():
            add(findings, "error", f"{label}-missing", f"Missing {raw.relative_to(ROOT)} (run scripts/build-codex-plugin.py)", raw.relative_to(ROOT).as_posix())
            continue
        try:
            data = json.loads(raw.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            add(findings, "error", f"{label}-invalid", f"Cannot parse {raw.relative_to(ROOT)}: {exc}", raw.relative_to(ROOT).as_posix())
            continue
        if data.get("name") != "maestro":
            add(findings, "error", f"{label}-name-drift", f"{raw.relative_to(ROOT)} name != maestro", raw.relative_to(ROOT).as_posix())


def check_codex_prompts(findings: list[dict[str, str]]) -> None:
    """Each command (minus the Codex-excluded set) must have a generated Codex prompt, and there
    must be no stale prompts left over."""
    cmd_dir = ROOT / ".claude" / "commands"
    out_dir = ROOT / ".codex" / "prompts"
    if not out_dir.is_dir():
        add(findings, "error", "codex-prompts-missing", "Missing .codex/prompts/ (run scripts/build-codex-prompts.py)", ".codex/prompts")
        return
    expected = {p.stem for p in cmd_dir.glob("*.md") if p.name != "README.md" and p.stem not in CODEX_PROMPT_EXCLUDE}
    actual = {p.stem for p in out_dir.glob("*.md") if p.name != "README.md"}
    missing = sorted(expected - actual)
    stale = sorted(actual - expected)
    if missing or stale:
        add(findings, "error", "codex-prompts-drift", f"Codex prompts out of sync: missing={missing} stale={stale}; rerun scripts/build-codex-prompts.py", ".codex/prompts")


def score(findings: list[dict[str, str]]) -> float:
    errors = sum(1 for item in findings if item["severity"] == "error")
    warnings = sum(1 for item in findings if item["severity"] == "warning")
    return max(0.0, round(10.0 - errors * 0.7 - warnings * 0.2, 1))


def build_report(findings: list[dict[str, str]], counts: dict[str, int]) -> dict[str, Any]:
    errors = [item for item in findings if item["severity"] == "error"]
    warnings = [item for item in findings if item["severity"] == "warning"]
    return {
        "generated_at": now_utc(),
        "tool": "scripts/architecture-health-check.py",
        "purpose": "Optional deterministic drift check; does not replace agent-native /policy-check.",
        "result": "pass" if not errors else "fail",
        "score": score(findings),
        "counts": counts,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": findings,
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "Architecture Health Check",
        "=========================",
        f"result: {report['result']}",
        f"score: {report['score']}",
        f"errors: {report['error_count']}",
        f"warnings: {report['warning_count']}",
        "counts: "
        + ", ".join(f"{key}={value}" for key, value in report["counts"].items()),
    ]
    if report["findings"]:
        lines.append("")
        lines.append("Findings")
        for item in report["findings"]:
            lines.append(f"- [{item['severity']}] {item['code']}: {item['message']} ({item['evidence']})")
    return "\n".join(lines)


def write_report(report: dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Architecture Health Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        f"- result: `{report['result']}`",
        f"- score: `{report['score']}`",
        f"- errors: `{report['error_count']}`",
        f"- warnings: `{report['warning_count']}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in report["counts"].items():
        lines.append(f"- {key}: {value}")
    if report["findings"]:
        lines.extend(["", "## Findings", ""])
        for item in report["findings"]:
            lines.append(f"- **{item['severity']}** `{item['code']}`: {item['message']} ({item['evidence']})")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_checks() -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    check_required_paths(findings)
    counts = check_counts(findings)
    check_entrypoints(findings)
    check_stale_text(findings)
    check_model_routing(findings)
    check_model_routing_template(findings)
    check_response_ui(findings)
    check_status_dashboard(findings)
    check_services_workspace_policy(findings)
    check_bug_artifact_integrity(findings)
    check_feedback_loop_contract(findings)
    check_agent_activity(findings)
    check_specialists(findings)
    check_claude_hooks(findings)
    check_skill_taxonomy(findings)
    check_codex_plugin(findings)
    check_codex_prompts(findings)
    check_plugin_wrapper(findings)
    return build_report(findings, counts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic architecture health checks.")
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    parser.add_argument("--write-report", action="store_true", help="Write .maestro/runtime/reports/architecture-health-report.json and .md.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero on warnings as well as errors.")
    args = parser.parse_args()

    report = run_checks()
    if args.write_report:
        write_report(report)
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) if args.json else render_text(report))
    if report["error_count"] > 0 or (args.strict and report["warning_count"] > 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
