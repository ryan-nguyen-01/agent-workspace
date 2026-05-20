#!/usr/bin/env python3
"""Render the agent-workspace status dashboard from runtime YAML files.

This script is a tool-agnostic mirror of the /status command. It does not
require third-party packages. It mutates files only when --write is passed.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / ".runtime" / "context"
SUPPORTED_MODES = {"compact", "concise", "dashboard", "models", "json"}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"_missing": str(path)}

    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        return data if isinstance(data, dict) else {"_raw": data}
    except Exception:
        return parse_simple_yaml(text)


def parse_simple_yaml(text: str) -> dict[str, Any]:
    """Small fallback parser for the YAML subset used by runtime status files."""
    lines = yaml_lines(text)
    if not lines:
        return {}
    parsed, _ = parse_node(lines, 0, lines[0][0])
    return parsed if isinstance(parsed, dict) else {"_raw": parsed}


def yaml_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        value = strip_inline_comment(raw.rstrip())
        if not value.strip():
            continue
        indent = len(value) - len(value.lstrip(" "))
        lines.append((indent, value.strip()))
    return lines


def strip_inline_comment(raw: str) -> str:
    quote: str | None = None
    escaped = False
    for i, char in enumerate(raw):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char in {'"', "'"}:
            quote = None if quote == char else char if quote is None else quote
            continue
        if char == "#" and quote is None and (i == 0 or raw[i - 1].isspace()):
            return raw[:i].rstrip()
    return raw


def parse_node(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    if is_list_item(lines[index][1]):
        return parse_list(lines, index, indent)
    return parse_map(lines, index, indent)


def parse_map(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        line_indent, text = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            index += 1
            continue
        if is_list_item(text):
            break

        key, raw_value = split_key_value(text)
        if raw_value == "":
            if index + 1 < len(lines) and lines[index + 1][0] > line_indent:
                result[key], index = parse_node(lines, index + 1, lines[index + 1][0])
            else:
                result[key] = {}
                index += 1
        else:
            result[key] = clean_scalar(raw_value)
            index += 1
    return result, index


def parse_list(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        line_indent, text = lines[index]
        if line_indent < indent:
            break
        if line_indent != indent or not is_list_item(text):
            break

        item_text = "" if text == "-" else text[2:].strip()
        if item_text == "":
            if index + 1 < len(lines) and lines[index + 1][0] > line_indent:
                item, index = parse_node(lines, index + 1, lines[index + 1][0])
            else:
                item = None
                index += 1
            result.append(item)
            continue

        if looks_like_key_value(item_text):
            item: dict[str, Any] = {}
            key, raw_value = split_key_value(item_text)
            if raw_value == "":
                if index + 1 < len(lines) and lines[index + 1][0] > line_indent:
                    item[key], index = parse_node(lines, index + 1, lines[index + 1][0])
                else:
                    item[key] = {}
                    index += 1
            else:
                item[key] = clean_scalar(raw_value)
                index += 1

            if index < len(lines) and lines[index][0] > line_indent:
                extra, index = parse_map(lines, index, lines[index][0])
                item.update(extra)
            result.append(item)
        else:
            result.append(clean_scalar(item_text))
            index += 1
    return result, index


def looks_like_key_value(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z0-9_.-]+\s*:", value))


def is_list_item(value: str) -> bool:
    return value == "-" or value.startswith("- ")


def split_key_value(value: str) -> tuple[str, str]:
    key, raw_value = value.split(":", 1)
    return key.strip(), raw_value.strip()


def clean_scalar(value: str) -> Any:
    if value in {"null", "~"}:
        return None
    if value in {"[]", "{}"}:
        return [] if value == "[]" else {}
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [clean_scalar(part.strip()) for part in split_inline_list(inner)]
    if value in {"true", "false"}:
        return value == "true"
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def split_inline_list(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    for char in value:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            current.append(char)
            escaped = True
            continue
        if char in {'"', "'"}:
            quote = None if quote == char else char if quote is None else quote
            current.append(char)
            continue
        if char == "," and quote is None:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current).strip())
    return parts


def profile_rows(model_routing: dict[str, Any]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    agent_map = model_routing.get("agent_model_map", {})
    if isinstance(agent_map, dict):
        for group_name in ("workflow_agents", "built_in_coders"):
            group = agent_map.get(group_name, {})
            if isinstance(group, dict):
                for agent_id, cfg in group.items():
                    if isinstance(cfg, dict):
                        profile = cfg.get("model_profile")
                        if profile:
                            rows.append((str(agent_id), str(profile)))
        generated = agent_map.get("generated_service_coders", {})
        if isinstance(generated, dict) and generated.get("default_model_profile"):
            rows.append(("generated-service-coders", str(generated["default_model_profile"])))
    return rows


def provider_defaults(model_routing: dict[str, Any]) -> list[str]:
    defaults = model_routing.get("provider_defaults", {})
    lines: list[str] = []
    if not isinstance(defaults, dict):
        return lines
    for provider in ("claude", "codex"):
        cfg = defaults.get(provider, {})
        if not isinstance(cfg, dict):
            continue
        deep = nested(cfg, "deep_reasoning", "model_id")
        coding = nested(cfg, "coding", "model_id")
        fast = nested(cfg, "fast", "model_id")
        parts = []
        if deep:
            parts.append(f"deep={deep}")
        if coding:
            parts.append(f"coding={coding}")
        if fast:
            parts.append(f"fast={fast}")
        if parts:
            lines.append(f"{provider}: " + ", ".join(parts))
    return lines


def model_override_rows(model_routing: dict[str, Any]) -> list[str]:
    overrides = model_routing.get("model_overrides", {})
    if not isinstance(overrides, dict) or overrides.get("enabled") is not True:
        return ["overrides: disabled"]

    rows: list[str] = []
    emergency = overrides.get("emergency_runtime_override", {})
    if isinstance(emergency, dict) and emergency.get("enabled") is True:
        rows.append(
            "override emergency: "
            + f"provider={fmt(emergency.get('provider'), 'any')} "
            + f"profile={fmt(emergency.get('provider_profile'), 'any')} "
            + f"model={fmt(emergency.get('model_id'), 'unknown')} "
            + f"expires={fmt(emergency.get('expires_at'), 'unknown')}"
        )

    provider_overrides = overrides.get("provider_profile_overrides", {})
    if isinstance(provider_overrides, dict):
        for provider, profiles in provider_overrides.items():
            if not isinstance(profiles, dict):
                continue
            for provider_profile, cfg in profiles.items():
                if isinstance(cfg, dict) and cfg:
                    rows.append(
                        "override provider: "
                        + f"{provider}.{provider_profile} -> {fmt(cfg.get('model_id'), 'unknown')}"
                    )

    agent_overrides = overrides.get("agent_overrides", {})
    if isinstance(agent_overrides, dict):
        for agent_id, cfg in agent_overrides.items():
            if isinstance(cfg, dict) and cfg:
                target = cfg.get("model_profile") or cfg.get("model_id") or cfg.get("provider_profile")
                rows.append(f"override agent: {agent_id} -> {fmt(target, 'unknown')}")

    phase_overrides = overrides.get("phase_overrides", {})
    if isinstance(phase_overrides, dict):
        for phase, cfg in phase_overrides.items():
            if isinstance(cfg, dict) and cfg:
                target = cfg.get("model_profile") or cfg.get("model_id") or cfg.get("provider_profile")
                rows.append(f"override phase: {phase} -> {fmt(target, 'unknown')}")

    return rows or ["overrides: enabled, none active"]


def response_default_mode(response_ui: dict[str, Any]) -> str:
    defaults = response_ui.get("defaults", {})
    if isinstance(defaults, dict):
        mode = defaults.get("status_mode")
        if mode in SUPPORTED_MODES:
            return str(mode)
    return "dashboard"


def response_mode_config(response_ui: dict[str, Any], mode: str) -> dict[str, Any]:
    modes = response_ui.get("modes", {})
    if not isinstance(modes, dict):
        return {}
    config = modes.get(mode, {})
    if not config and mode == "models":
        config = modes.get("dashboard", {})
    return config if isinstance(config, dict) else {}


def response_sections(response_ui: dict[str, Any], mode: str, fallback: list[str]) -> list[str]:
    sections = response_mode_config(response_ui, mode).get("sections")
    if isinstance(sections, list) and all(isinstance(item, str) for item in sections):
        return sections
    return fallback


def response_line_budget(response_ui: dict[str, Any], mode: str) -> int | None:
    budget = response_mode_config(response_ui, mode).get("line_budget")
    return budget if isinstance(budget, int) and budget > 0 else None


def response_ui_summary(response_ui: dict[str, Any], selected_mode: str) -> dict[str, Any]:
    defaults = response_ui.get("defaults", {})
    modes = response_ui.get("modes", {})
    return {
        "status": response_ui.get("status", "unknown"),
        "selected_mode": selected_mode,
        "status_mode": nested(defaults, "status_mode") if isinstance(defaults, dict) else "unknown",
        "final_mode": nested(defaults, "final_mode") if isinstance(defaults, dict) else "unknown",
        "review_mode": nested(defaults, "review_mode") if isinstance(defaults, dict) else "unknown",
        "available_modes": sorted(modes.keys()) if isinstance(modes, dict) else [],
        "status_artifacts": {
            key: display_path(path) for key, path in status_artifact_paths(response_ui).items()
        },
    }


def project_brain_freshness(state: dict[str, Any], project_brain: dict[str, Any]) -> str:
    if project_brain.get("_missing"):
        return "missing"

    state_mode = state.get("distribution_mode")
    state_instance = state.get("instance_status")
    brain_mode = nested(project_brain, "distribution", "mode")
    brain_instance = nested(project_brain, "distribution", "instance_status")
    if (state_mode, state_instance) == ("framework-template", "not_applied") or (
        brain_mode,
        brain_instance,
    ) == ("framework-template", "not_applied"):
        return "template-seed"

    freshness = project_brain.get("freshness", {})
    if isinstance(freshness, dict):
        if freshness.get("stale") is True:
            return "stale"
        if freshness.get("stale") is False:
            return "fresh"
        if freshness.get("memory_epoch") or freshness.get("last_indexed_at"):
            return "unknown"
    return "unknown"


def project_brain_summary(project_brain: dict[str, Any]) -> dict[str, Any]:
    freshness = project_brain.get("freshness", {})
    freshness = freshness if isinstance(freshness, dict) else {}
    return {
        "freshness": freshness,
        "memory_epoch": freshness.get("memory_epoch"),
        "last_indexed_at": freshness.get("last_indexed_at"),
        "last_drift_check_result": freshness.get("last_drift_check_result"),
        "stale_reasons": freshness.get("stale_reasons", []),
    }


def service_count(service_catalog: dict[str, Any]) -> int:
    services = service_catalog.get("services", [])
    return len(services) if isinstance(services, list) else 0


def active_coder_count(agent_registry: dict[str, Any]) -> int:
    agents = agent_registry.get("agents", [])
    if not isinstance(agents, list):
        return 0
    total = 0
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        agent_id = str(agent.get("id", ""))
        agent_type = str(agent.get("type", ""))
        if agent.get("status") == "active" and (agent_id.startswith("coder-") or "coder" in agent_type):
            total += 1
    return total


def status_artifact_paths(response_ui: dict[str, Any]) -> dict[str, Path]:
    artifacts = response_ui.get("status_artifacts", {})
    if not isinstance(artifacts, dict):
        artifacts = {}

    defaults = {
        "markdown": ".runtime/status.md",
        "html": ".runtime/status.html",
    }
    paths: dict[str, Path] = {}
    for key, fallback in defaults.items():
        raw = artifacts.get(key, fallback)
        if not isinstance(raw, str) or not raw.strip():
            raw = fallback
        path = Path(raw)
        paths[key] = path if path.is_absolute() else ROOT / path
    return paths


def nested(data: dict[str, Any], *keys: str) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def fmt(value: Any, default: str = "-") -> str:
    if value is None or value == "":
        return default
    return str(value)


def age(updated_at: Any) -> str:
    if not updated_at:
        return "unknown"
    raw = str(updated_at)
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        seconds = max(0, int((datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds()))
        if seconds < 60:
            return f"{seconds}s"
        if seconds < 3600:
            return f"{seconds // 60}m"
        return f"{seconds // 3600}h"
    except ValueError:
        return "unknown"


def status_snapshot() -> dict[str, Any]:
    state = load_yaml(CONTEXT / "workflow-state.yaml")
    model_routing = load_yaml(CONTEXT / "model-routing.yaml")
    activity = load_yaml(CONTEXT / "agent-activity.yaml")
    response_ui = load_yaml(CONTEXT / "response-ui.yaml")
    project_brain = load_yaml(CONTEXT / "project-brain.yaml")
    service_catalog = load_yaml(CONTEXT / "service-catalog.yaml")
    agent_registry = load_yaml(CONTEXT / "agent-registry.yaml")

    totals = activity.get("totals", {}) if isinstance(activity.get("totals"), dict) else {}
    current_agents = activity.get("current_agents", [])
    if not isinstance(current_agents, list):
        current_agents = []

    return {
        "state": state,
        "model_routing": model_routing,
        "activity": activity,
        "response_ui": response_ui,
        "project_brain": project_brain,
        "service_catalog": service_catalog,
        "agent_registry": agent_registry,
        "project_brain_status": project_brain_freshness(state, project_brain),
        "project_brain_summary": project_brain_summary(project_brain),
        "services_detected": service_count(service_catalog),
        "active_coder_agents": active_coder_count(agent_registry),
        "totals": totals,
        "current_agents": current_agents,
        "provider_defaults": provider_defaults(model_routing),
        "model_overrides": model_override_rows(model_routing),
        "profile_rows": profile_rows(model_routing),
    }


def render_compact(snapshot: dict[str, Any]) -> str:
    state = snapshot["state"]
    activity = snapshot["activity"]
    totals = snapshot["totals"]
    sections = response_sections(
        snapshot["response_ui"],
        "compact",
        ["state", "current_action", "blocker", "next"],
    )
    values = {
        "state": "state="
        + fmt(state.get("current_state"))
        + " mode="
        + fmt(state.get("distribution_mode"))
        + "/"
        + fmt(state.get("instance_status"))
        + " brain="
        + fmt(snapshot.get("project_brain_status"))
        + " ui="
        + fmt(snapshot.get("selected_mode"), response_default_mode(snapshot["response_ui"]))
        + " task="
        + fmt(state.get("active_task_id"), "none"),
        "current_action": "activity="
        + fmt(activity.get("status"), "unknown")
        + " running="
        + fmt(totals.get("running_agents"), "0"),
        "blocker": "blocked=" + fmt(totals.get("blocked_agents"), "0"),
        "next": "next=" + next_command(snapshot),
        "token_cost": "tokens="
        + fmt(totals.get("actual_tokens_used"), "unknown")
        + " cost="
        + fmt(totals.get("actual_cost_usd"), "unknown"),
    }
    return " | ".join(values[section] for section in sections if section in values)


def render_dashboard(snapshot: dict[str, Any], mode: str, show_models: bool) -> str:
    sections = response_sections(
        snapshot["response_ui"],
        mode,
        ["workflow_state", "agent_activity", "model_profile", "elapsed_eta", "token_cost", "next_command"],
    )
    lines = ["Agent Workspace Status", "=" * 24]
    for section in sections:
        rendered = render_section(section, snapshot, show_models)
        if not rendered:
            continue
        if lines and lines[-1] != "":
            lines.append("")
        lines.extend(rendered)

    if show_models and "model_profile" not in sections:
        if lines and lines[-1] != "":
            lines.append("")
        lines.extend(render_section("model_profile", snapshot, show_models=True))

    budget = response_line_budget(snapshot["response_ui"], mode)
    return "\n".join(apply_line_budget(lines, budget))


def render_section(section: str, snapshot: dict[str, Any], show_models: bool) -> list[str]:
    state = snapshot["state"]
    activity = snapshot["activity"]
    totals = snapshot["totals"]
    current_agents = snapshot["current_agents"]
    project_brain = snapshot.get("project_brain_summary", {})

    if section == "workflow_state":
        return [
            "Workflow",
            f"- mode: {fmt(state.get('distribution_mode'))} / {fmt(state.get('instance_status'))}",
            f"- state: {fmt(state.get('current_state'))}",
            f"- active task: {fmt(state.get('active_task_id'), 'none')}",
            f"- services detected: {fmt(snapshot.get('services_detected'), '0')}",
            f"- active coder agents: {fmt(snapshot.get('active_coder_agents'), '0')}",
        ]
    if section == "project_brain":
        stale_reasons = project_brain.get("stale_reasons", []) if isinstance(project_brain, dict) else []
        lines = [
            "Project Brain",
            f"- freshness: {fmt(snapshot.get('project_brain_status'), 'unknown')}",
            f"- memory epoch: {fmt(project_brain.get('memory_epoch') if isinstance(project_brain, dict) else None, 'unknown')}",
            f"- last indexed: {fmt(project_brain.get('last_indexed_at') if isinstance(project_brain, dict) else None, 'unknown')}",
            f"- drift check: {fmt(project_brain.get('last_drift_check_result') if isinstance(project_brain, dict) else None, 'unknown')}",
        ]
        if isinstance(stale_reasons, list) and stale_reasons:
            lines.append(f"- stale reasons: {len(stale_reasons)} recorded")
        return lines
    if section == "response_ui":
        summary = response_ui_summary(
            snapshot["response_ui"],
            str(snapshot.get("selected_mode") or response_default_mode(snapshot["response_ui"])),
        )
        artifacts = summary.get("status_artifacts", {})
        return [
            "Response UI",
            f"- selected mode: {fmt(summary.get('selected_mode'), 'unknown')}",
            f"- defaults: status={fmt(summary.get('status_mode'), 'unknown')} final={fmt(summary.get('final_mode'), 'unknown')} review={fmt(summary.get('review_mode'), 'unknown')}",
            f"- available modes: {', '.join(summary.get('available_modes', [])) if summary.get('available_modes') else 'unknown'}",
            f"- artifacts: markdown={fmt(artifacts.get('markdown') if isinstance(artifacts, dict) else None)} html={fmt(artifacts.get('html') if isinstance(artifacts, dict) else None)}",
        ]
    if section == "agent_activity":
        lines = [
            "Agent Activity",
            f"- status: {fmt(activity.get('status'), 'unknown')} (updated {age(activity.get('updated_at'))} ago)",
            "- totals: "
            + f"running={fmt(totals.get('running_agents'), '0')} "
            + f"queued={fmt(totals.get('queued_agents'), '0')} "
            + f"blocked={fmt(totals.get('blocked_agents'), '0')}",
        ]
        if current_agents:
            for agent in current_agents:
                if isinstance(agent, dict):
                    lines.append(
                        "- "
                        + f"{fmt(agent.get('agent_id'))} | "
                        + f"{fmt(agent.get('status'))} | "
                        + f"{fmt(agent.get('current_action'))}"
                    )
        else:
            lines.append("- active agents: none")
        return lines
    if section == "model_profile":
        lines = ["Model Routing"]
        defaults = snapshot["provider_defaults"]
        lines.extend(f"- {line}" for line in defaults) if defaults else lines.append("- provider defaults: unknown")
        override_rows = snapshot.get("model_overrides", [])
        if isinstance(override_rows, list):
            lines.extend(f"- {line}" for line in override_rows)
        if show_models:
            rows = snapshot["profile_rows"]
            if rows:
                width = max(len(agent_id) for agent_id, _ in rows)
                lines.extend(f"- {agent_id.ljust(width)} -> {profile}" for agent_id, profile in rows)
            else:
                lines.append("- agent model profiles: unknown")
        return lines
    if section == "elapsed_eta":
        lines = ["Elapsed / ETA"]
        if current_agents:
            for agent in current_agents:
                if isinstance(agent, dict):
                    lines.append(
                        "- "
                        + f"{fmt(agent.get('agent_id'))}: "
                        + f"elapsed={fmt(agent.get('elapsed_seconds', agent.get('elapsed')), 'unknown')} "
                        + f"eta={fmt(agent.get('eta_seconds', agent.get('eta')), 'unknown')}"
                    )
        else:
            lines.append("- active agents: none")
        return lines
    if section == "token_cost":
        return [
            "Token / Cost",
            f"- actual tokens: {fmt(totals.get('actual_tokens_used'), 'unknown')}",
            f"- estimated tokens: {fmt(totals.get('estimated_tokens_used'), 'unknown')}",
            f"- actual cost USD: {fmt(totals.get('actual_cost_usd'), 'unknown')}",
            f"- estimated cost USD: {fmt(totals.get('estimated_cost_usd'), 'unknown')}",
        ]
    if section == "next_command":
        return ["Next", f"- {next_command(snapshot)}"]
    if section == "summary":
        return [
            "Summary",
            f"- state={fmt(state.get('current_state'))}",
            f"- activity={fmt(activity.get('status'), 'unknown')}",
            f"- task={fmt(state.get('active_task_id'), 'none')}",
        ]
    if section == "verification":
        return ["Verification", "- status dashboard data loaded from .runtime/context/"]
    return []


def next_command(snapshot: dict[str, Any]) -> str:
    state = snapshot["state"].get("current_state")
    mode = snapshot["state"].get("distribution_mode")
    instance = snapshot["state"].get("instance_status")
    if mode == "framework-template" and instance == "not_applied":
        return "/coord <framework request> or /onboard after cloning services"
    if state == "NEED_ONBOARDING":
        return "/onboard"
    if state == "ONBOARDED":
        return "/create-coders"
    if state in {"AGENTS_READY", "READY_FOR_ANALYSIS"}:
        return "/analyze-task"
    if state == "ANALYZED":
        return "/plan-dev"
    if state == "PLANNED":
        return "/dev"
    if state == "DEV_DONE":
        return "/handoff-qc"
    if state == "QC_READY":
        return "/qc"
    return "/coord"


def apply_line_budget(lines: list[str], budget: int | None) -> list[str]:
    if budget is None or len(lines) <= budget:
        return lines
    if budget <= 1:
        return [f"... truncated by response-ui line_budget={budget}"]
    return lines[: budget - 1] + [f"... truncated by response-ui line_budget={budget}"]


def render(mode: str | None, show_models: bool) -> str:
    snapshot = status_snapshot()
    selected_mode = mode or response_default_mode(snapshot["response_ui"])
    snapshot["selected_mode"] = selected_mode
    if selected_mode == "compact":
        return render_compact(snapshot)
    if selected_mode == "json":
        response_ui = response_ui_summary(snapshot["response_ui"], selected_mode)
        return json.dumps(
            {
                "workflow_state": snapshot["state"].get("current_state"),
                "distribution_mode": snapshot["state"].get("distribution_mode"),
                "instance_status": snapshot["state"].get("instance_status"),
                "active_task_id": snapshot["state"].get("active_task_id"),
                "project_brain": snapshot["project_brain_status"],
                "services_detected": snapshot["services_detected"],
                "active_coder_agents": snapshot["active_coder_agents"],
                "activity_status": snapshot["activity"].get("status"),
                "totals": snapshot["totals"],
                "current_agents": snapshot["current_agents"],
                "provider_defaults": snapshot["provider_defaults"],
                "model_overrides": snapshot["model_overrides"],
                "agent_model_profiles": snapshot["profile_rows"],
                "response_ui": response_ui,
            },
            indent=2,
            sort_keys=True,
        )
    return render_dashboard(snapshot, mode=selected_mode, show_models=show_models or selected_mode == "models")


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def render_markdown_status(content: str, selected_mode: str, generated_at: str) -> str:
    return (
        "# Agent Workspace Status\n\n"
        f"Generated by `scripts/status-dashboard.py --mode {selected_mode}`.\n\n"
        f"Generated at: `{generated_at}`.\n\n"
        "```text\n"
        f"{content.rstrip()}\n"
        "```\n"
    )


def html_status_card(label: str, value: Any, tone: str = "neutral") -> str:
    return (
        f'<article class="metric metric-{escape(tone)}">'
        f'<span class="metric-label">{escape(label)}</span>'
        f'<strong>{escape(fmt(value, "unknown"))}</strong>'
        "</article>"
    )


def render_html_metric_grid(snapshot: dict[str, Any]) -> str:
    totals = snapshot.get("totals", {})
    return "\n        ".join(
        [
            html_status_card("Workflow", snapshot["state"].get("current_state"), "accent"),
            html_status_card("Brain", snapshot.get("project_brain_status"), "ok"),
            html_status_card("Services", snapshot.get("services_detected"), "neutral"),
            html_status_card("Active coders", snapshot.get("active_coder_agents"), "neutral"),
            html_status_card("Running agents", totals.get("running_agents", 0), "neutral"),
            html_status_card("Estimated tokens", totals.get("estimated_tokens_used", "unknown"), "neutral"),
        ]
    )


def render_html_tabs() -> str:
    tabs = [
        ("README", "#readme", True),
        ("Workflow", "#workflow", False),
        ("Models", "#models", False),
        ("Feedback", "#feedback", False),
        ("Raw status", "#raw-status", False),
    ]
    return "\n        ".join(
        f'<a class="tab{" tab-active" if active else ""}" href="{href}">{escape(label)}</a>'
        for label, href, active in tabs
    )


def render_html_status(content: str, selected_mode: str, generated_at: str) -> str:
    snapshot = status_snapshot()
    snapshot["selected_mode"] = selected_mode
    state = snapshot["state"]
    response_summary = response_ui_summary(snapshot["response_ui"], selected_mode)
    safe_content = escape(content.rstrip())
    safe_mode = escape(selected_mode)
    safe_generated_at = escape(generated_at)
    safe_next = escape(next_command(snapshot))
    safe_defaults = ", ".join(escape(line) for line in snapshot.get("provider_defaults", []))
    safe_overrides = ", ".join(escape(line) for line in snapshot.get("model_overrides", []))
    safe_modes = ", ".join(escape(mode) for mode in response_summary.get("available_modes", []))
    metric_grid = render_html_metric_grid(snapshot)
    tabs = render_html_tabs()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Workspace Status</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0d1117;
      --panel: #0d1117;
      --panel-soft: #161b22;
      --border: #30363d;
      --fg: #e6edf3;
      --muted: #8b949e;
      --accent: #ff7b72;
      --accent-2: #f1c40f;
      --ok: #3fb950;
      --shadow: rgba(1, 4, 9, 0.45);
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--fg);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(1160px, calc(100% - 32px));
      margin: 36px auto;
    }}
    .repo-shell {{
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      background: var(--panel);
      box-shadow: 0 24px 80px var(--shadow);
    }}
    .tabs {{
      display: flex;
      align-items: center;
      gap: 22px;
      min-height: 64px;
      padding: 0 20px;
      border-bottom: 1px solid var(--border);
      overflow-x: auto;
      white-space: nowrap;
    }}
    .tab {{
      position: relative;
      display: inline-flex;
      align-items: center;
      height: 64px;
      color: var(--muted);
      font-weight: 650;
      text-decoration: none;
      letter-spacing: 0;
    }}
    .tab-active {{
      color: var(--fg);
    }}
    .tab-active::after {{
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 3px;
      border-radius: 999px 999px 0 0;
      background: var(--accent);
    }}
    .readme {{
      padding: clamp(24px, 5vw, 48px);
    }}
    .hero {{
      min-height: 176px;
      display: grid;
      place-items: center;
      margin-bottom: 34px;
      background:
        linear-gradient(180deg, rgba(255, 212, 59, 0.08), rgba(255, 123, 114, 0.04)),
        #111;
      border: 1px solid #171717;
      overflow: hidden;
    }}
    .hero-title {{
      margin: 0;
      color: var(--accent-2);
      font-family: Impact, Haettenschweiler, "Arial Black", sans-serif;
      font-size: clamp(42px, 10vw, 112px);
      line-height: 0.92;
      letter-spacing: 0;
      text-align: center;
      text-transform: uppercase;
      text-shadow:
        4px 4px 0 #b66a25,
        8px 8px 0 #151515,
        11px 11px 0 #d28a31;
    }}
    h1 {{
      margin: 0;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
      font-size: clamp(34px, 5vw, 56px);
      line-height: 1.08;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 14px 0 0;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.6;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin: 28px 0;
    }}
    .metric {{
      min-height: 92px;
      padding: 16px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--panel-soft);
    }}
    .metric-label {{
      display: block;
      margin-bottom: 10px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .metric strong {{
      display: block;
      overflow-wrap: anywhere;
      font-size: 22px;
      line-height: 1.2;
    }}
    .metric-accent strong {{
      color: var(--accent);
    }}
    .metric-ok strong {{
      color: var(--ok);
    }}
    .section {{
      margin-top: 28px;
      padding-top: 24px;
      border-top: 1px solid var(--border);
    }}
    .section h2 {{
      margin: 0 0 12px;
      font-size: 22px;
      letter-spacing: 0;
    }}
    .facts {{
      display: grid;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.55;
    }}
    .facts strong {{
      color: var(--fg);
    }}
    pre {{
      margin: 0;
      padding: 18px;
      overflow: auto;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #010409;
      color: var(--fg);
      font: 13px/1.55 ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
      white-space: pre-wrap;
    }}
    @media (max-width: 760px) {{
      main {{
        width: min(100% - 16px, 1160px);
        margin: 8px auto;
      }}
      .readme {{
        padding: 20px;
      }}
      .grid {{
        grid-template-columns: 1fr;
      }}
      .tabs {{
        gap: 16px;
        padding: 0 14px;
      }}
    }}
  </style>
</head>
<body>
  <!-- Generated at: {safe_generated_at} -->
  <main data-view="github-readme-card">
    <section class="repo-shell">
      <nav class="tabs" aria-label="Status sections">
        {tabs}
      </nav>
      <article class="readme" id="readme">
        <div class="hero" aria-label="Agent Workspace banner">
          <p class="hero-title">Agent Workspace</p>
        </div>
        <h1>Agent Workspace</h1>
        <p class="subtitle">Generated by <strong>scripts/status-dashboard.py --mode {safe_mode}</strong> at {safe_generated_at}. This HTML is a styled mirror; runtime YAML remains the source of truth.</p>

        <section class="grid" aria-label="Status metrics">
        {metric_grid}
        </section>

        <section class="section" id="workflow">
          <h2>Workflow</h2>
          <ul class="facts">
            <li><strong>Mode:</strong> {escape(fmt(state.get("distribution_mode")))} / {escape(fmt(state.get("instance_status")))}</li>
            <li><strong>Active task:</strong> {escape(fmt(state.get("active_task_id"), "none"))}</li>
            <li><strong>Next:</strong> {safe_next}</li>
          </ul>
        </section>

        <section class="section" id="models">
          <h2>Models</h2>
          <ul class="facts">
            <li><strong>Provider defaults:</strong> {safe_defaults or "unknown"}</li>
            <li><strong>Overrides:</strong> {safe_overrides or "unknown"}</li>
          </ul>
        </section>

        <section class="section" id="feedback">
          <h2>Response UI</h2>
          <ul class="facts">
            <li><strong>Selected mode:</strong> {safe_mode}</li>
            <li><strong>Available modes:</strong> {safe_modes or "unknown"}</li>
            <li><strong>Token/cost policy:</strong> exact values are shown only when adapter metrics are available.</li>
          </ul>
        </section>

        <section class="section" id="raw-status">
          <h2>Raw Status</h2>
          <pre>{safe_content}</pre>
        </section>
      </article>
    </section>
  </main>
</body>
</html>
"""


def write_status_artifacts(content: str, selected_mode: str) -> list[Path]:
    response_ui = load_yaml(CONTEXT / "response-ui.yaml")
    paths = status_artifact_paths(response_ui)
    markdown_path = paths["markdown"]
    html_path = paths["html"]
    generated_at = current_utc_timestamp()

    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown_status(content, selected_mode, generated_at), encoding="utf-8")
    html_path.write_text(render_html_status(content, selected_mode, generated_at), encoding="utf-8")
    return [markdown_path, html_path]


def main() -> int:
    parser = argparse.ArgumentParser(description="Render agent-workspace status dashboard.")
    parser.add_argument(
        "--mode",
        choices=["compact", "concise", "dashboard", "models", "json"],
        help="Response UI mode. Defaults to .runtime/context/response-ui.yaml defaults.status_mode.",
    )
    parser.add_argument("--models", action="store_true", help="Show full agent-to-model-profile mapping.")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write configured status artifacts (.runtime/status.md and .runtime/status.html by default).",
    )
    args = parser.parse_args()
    selected_mode = args.mode or ("models" if args.models else response_default_mode(load_yaml(CONTEXT / "response-ui.yaml")))
    content = render(mode=selected_mode, show_models=args.models)
    print(content)
    if args.write:
        written = write_status_artifacts(content, selected_mode)
        rel_paths = [display_path(path) for path in written]
        print("\nWrote status artifacts: " + ", ".join(rel_paths))
    return 0


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
