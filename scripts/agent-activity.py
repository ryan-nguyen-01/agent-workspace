#!/usr/bin/env python3
"""Update `.maestro/runtime/agent-activity.yaml` without third-party packages.

This is an adapter-friendly helper for tools that can call a local command at
phase start, heartbeat, block, or completion. It is intentionally narrow: it
writes only the activity telemetry file and refuses likely secrets in fields
that may come from prompts or logs.
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
CONFIG = ROOT / ".maestro" / "config"
RUNTIME = ROOT / ".maestro" / "runtime"
DEFAULT_ACTIVITY_FILE = RUNTIME / "agent-activity.yaml"
MAX_TEXT_LEN = 500

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I),
    re.compile(r"\b(password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|cookie)\s*[:=]", re.I),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}", re.I),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}", re.I),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}", re.I),
]


def status_dashboard_module() -> Any:
    module_path = ROOT / "scripts" / "status-dashboard.py"
    spec = importlib.util.spec_from_file_location("status_dashboard", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return status_dashboard_module().load_yaml(path)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def elapsed_seconds(started_at: Any, now: datetime) -> int | str:
    started = parse_time(started_at)
    if started is None:
        return "unknown"
    return max(0, int((now - started).total_seconds()))


def reject_unsafe_text(label: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            reject_unsafe_text(f"{label}[{i}]", item)
        return
    text = str(value)
    if len(text) > MAX_TEXT_LEN:
        raise SystemExit(f"{label} is too long for telemetry; keep it under {MAX_TEXT_LEN} chars.")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise SystemExit(f"{label} appears to contain a secret or raw credential. Refusing to write telemetry.")


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def dump_yaml(data: Any, indent: int = 0) -> list[str]:
    pad = " " * indent
    lines: list[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{pad}{key}:")
                lines.extend(dump_yaml(value, indent + 2))
            elif isinstance(value, list):
                if not value:
                    lines.append(f"{pad}{key}: []")
                else:
                    lines.append(f"{pad}{key}:")
                    lines.extend(dump_yaml(value, indent + 2))
            else:
                lines.append(f"{pad}{key}: {yaml_scalar(value)}")
        return lines
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append(f"{pad}-")
                lines.extend(dump_yaml(item, indent + 2))
            elif isinstance(item, list):
                lines.append(f"{pad}-")
                lines.extend(dump_yaml(item, indent + 2))
            else:
                lines.append(f"{pad}- {yaml_scalar(item)}")
        return lines
    lines.append(f"{pad}{yaml_scalar(data)}")
    return lines


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(dump_yaml(data)) + "\n", encoding="utf-8")


def seed_activity() -> dict[str, Any]:
    return {
        "version": 1,
        "generated_at": now_utc(),
        "generated_by": "agent-activity-cli",
        "status": "idle",
        "active_task_id": None,
        "active_run_id": None,
        "updated_at": now_utc(),
        "updated_by": "agent-activity-cli",
        "dashboard": {
            "mode": "text-status",
            "source_of_truth": ".maestro/runtime/agent-activity.yaml",
            "response_ui": ".maestro/config/response-ui.yaml",
            "rendered_by": "/status",
            "refresh_policy": "Read this file plus workflow-state.yaml. Do not scan task folders unless a task id is active or requested.",
        },
        "automation": {
            "update_cli": "python3 scripts/agent-activity.py <start|heartbeat|block|complete|reset>",
            "status_cli": "python3 scripts/status-dashboard.py --mode dashboard",
            "health_cli": "python3 scripts/architecture-health-check.py --strict",
        },
        "totals": {
            "running_agents": 0,
            "queued_agents": 0,
            "blocked_agents": 0,
            "completed_agents_last_24h": 0,
        },
        "current_agents": [],
        "recent_events": [],
        "recording_policy": {
            "no_secrets_rule": "Never paste raw prompts, raw logs, credentials, cookies, private keys, or long outputs into this file.",
        },
    }


def ensure_activity(data: dict[str, Any]) -> dict[str, Any]:
    if not data or "_missing" in data:
        data = seed_activity()
    data.setdefault("version", 1)
    data.setdefault("generated_at", now_utc())
    data.setdefault("generated_by", "agent-activity-cli")
    data.setdefault("status", "idle")
    data.setdefault("active_run_id", None)
    data.setdefault("dashboard", seed_activity()["dashboard"])
    data.setdefault("automation", seed_activity()["automation"])
    data.setdefault("totals", seed_activity()["totals"])
    data.setdefault("current_agents", [])
    data.setdefault("recent_events", [])
    data.setdefault("token_accounting_policy", seed_activity()["token_accounting_policy"])
    if not isinstance(data["current_agents"], list):
        data["current_agents"] = []
    if not isinstance(data["recent_events"], list):
        data["recent_events"] = []
    if not isinstance(data["totals"], dict):
        data["totals"] = seed_activity()["totals"]
    return data


def model_profile_for_agent(agent_id: str, explicit_profile: str | None) -> str:
    if explicit_profile:
        return explicit_profile
    routing = load_yaml(CONFIG / "model-routing.yaml")
    agent_map = routing.get("agent_model_map", {}) if isinstance(routing, dict) else {}
    if isinstance(agent_map, dict):
        for group_name in ("workflow_agents", "built_in_coders"):
            group = agent_map.get(group_name, {})
            if isinstance(group, dict):
                cfg = group.get(agent_id)
                if isinstance(cfg, dict) and cfg.get("model_profile"):
                    return str(cfg["model_profile"])
        generated = agent_map.get("generated_service_coders", {})
        if isinstance(generated, dict) and generated.get("default_model_profile"):
            if agent_id.startswith("coder-"):
                return str(generated["default_model_profile"])
    return "unknown"


def override_model_id(routing: dict[str, Any], provider: str, provider_profile: Any) -> str | None:
    overrides = routing.get("model_overrides", {})
    if not isinstance(overrides, dict) or overrides.get("enabled") is not True:
        return None

    emergency = overrides.get("emergency_runtime_override", {})
    if isinstance(emergency, dict) and emergency.get("enabled") is True:
        emergency_provider = emergency.get("provider")
        emergency_profile = emergency.get("provider_profile")
        provider_matches = emergency_provider in (None, "", "null", provider)
        profile_matches = emergency_profile in (None, "", "null", provider_profile)
        if provider_matches and profile_matches and emergency.get("model_id"):
            return str(emergency["model_id"])

    provider_overrides = overrides.get("provider_profile_overrides", {})
    if isinstance(provider_overrides, dict):
        provider_cfg = provider_overrides.get(provider, {})
        if isinstance(provider_cfg, dict):
            cfg = provider_cfg.get(provider_profile, {})
            if isinstance(cfg, dict) and cfg.get("model_id"):
                return str(cfg["model_id"])
    return None


def model_id_for_profile(provider: str, profile: str, explicit_model_id: str | None) -> str:
    if explicit_model_id:
        return explicit_model_id
    if provider == "unknown" or profile == "unknown":
        return "unknown"
    routing = load_yaml(CONFIG / "model-routing.yaml")
    profiles = routing.get("model_profiles", {}) if isinstance(routing, dict) else {}
    defaults = routing.get("provider_defaults", {}) if isinstance(routing, dict) else {}
    if not isinstance(profiles, dict) or not isinstance(defaults, dict):
        return "unknown"
    profile_cfg = profiles.get(profile, {})
    if not isinstance(profile_cfg, dict):
        return "unknown"
    provider_profile = profile_cfg.get("default_provider_profile")
    overridden = override_model_id(routing, provider, provider_profile)
    if overridden:
        return overridden
    provider_cfg = defaults.get(provider, {})
    if not isinstance(provider_cfg, dict):
        return "unknown"
    model_cfg = provider_cfg.get(provider_profile, {})
    if isinstance(model_cfg, dict) and model_cfg.get("model_id"):
        return str(model_cfg["model_id"])
    return "unknown"


def current_agent_index(data: dict[str, Any], agent_id: str) -> int | None:
    for i, agent in enumerate(data.get("current_agents", [])):
        if isinstance(agent, dict) and agent.get("agent_id") == agent_id:
            return i
    return None


def append_event(data: dict[str, Any], agent_id: str, event: str, summary: str) -> None:
    reject_unsafe_text("event summary", summary)
    data.setdefault("recent_events", [])
    data["recent_events"].insert(
        0,
        {
            "at": now_utc(),
            "agent_id": agent_id,
            "event": event,
            "summary": summary,
        },
    )
    data["recent_events"] = data["recent_events"][:20]


def refresh_totals(data: dict[str, Any]) -> None:
    now = datetime.now(timezone.utc)
    agents = [agent for agent in data.get("current_agents", []) if isinstance(agent, dict)]
    for agent in agents:
        agent["elapsed_seconds"] = elapsed_seconds(agent.get("started_at"), now)

    running = sum(1 for agent in agents if agent.get("status") == "running")
    queued = sum(1 for agent in agents if agent.get("status") == "queued")
    blocked = sum(1 for agent in agents if agent.get("status") == "blocked")

    totals = data.setdefault("totals", {})
    totals["running_agents"] = running
    totals["queued_agents"] = queued
    totals["blocked_agents"] = blocked
    totals.setdefault("completed_agents_last_24h", 0)

    if blocked:
        data["status"] = "blocked"
    elif running or queued:
        data["status"] = "running"
    else:
        data["status"] = "idle"
    data["updated_at"] = now_utc()


def state_active_task() -> str | None:
    state = load_yaml(RUNTIME / "workflow-state.yaml")
    task_id = state.get("active_task_id") if isinstance(state, dict) else None
    if task_id in (None, "", "null", "~"):
        return None
    return str(task_id)


def state_active_run() -> str | None:
    state = load_yaml(RUNTIME / "workflow-state.yaml")
    run_id = state.get("active_run_id") if isinstance(state, dict) else None
    if run_id in (None, "", "null", "~"):
        return None
    return str(run_id)


def command_start(data: dict[str, Any], args: argparse.Namespace) -> str:
    for label in ("agent_id", "phase", "current_action", "active_file", "run_id"):
        reject_unsafe_text(label, getattr(args, label, None))
    reject_unsafe_text("evidence", args.evidence)

    profile = model_profile_for_agent(args.agent_id, args.model_profile)
    provider = args.provider or "unknown"
    model_id = model_id_for_profile(provider, profile, args.model_id)
    task_id = args.task_id or state_active_task()
    run_id = args.run_id or state_active_run()
    timestamp = now_utc()

    agent = {
        "agent_id": args.agent_id,
        "phase": args.phase,
        "status": "running",
        "model_profile": profile,
        "provider": provider,
        "model_id": model_id,
        "started_at": timestamp,
        "last_heartbeat_at": timestamp,
        "elapsed_seconds": 0,
        "eta_seconds": args.eta_seconds if args.eta_seconds is not None else "unknown",
        "current_action": args.current_action,
        "active_file": args.active_file,
        "task_id": task_id,
        "run_id": run_id,
        "evidence": args.evidence,
    }

    index = current_agent_index(data, args.agent_id)
    if index is None:
        data["current_agents"].append(agent)
    else:
        data["current_agents"][index] = agent
    data["active_task_id"] = task_id
    data["active_run_id"] = run_id
    data["updated_by"] = args.agent_id
    append_event(data, args.agent_id, "started", args.current_action)
    return f"started {args.agent_id}"


def command_heartbeat(data: dict[str, Any], args: argparse.Namespace) -> str:
    reject_unsafe_text("current_action", args.current_action)
    reject_unsafe_text("active_file", args.active_file)
    reject_unsafe_text("run_id", args.run_id)
    reject_unsafe_text("evidence", args.evidence)
    index = current_agent_index(data, args.agent_id)
    if index is None:
        raise SystemExit(f"No current agent found for {args.agent_id}; run start first.")
    agent = data["current_agents"][index]
    if args.current_action:
        agent["current_action"] = args.current_action
    if args.active_file is not None:
        agent["active_file"] = args.active_file
    if args.run_id is not None:
        agent["run_id"] = args.run_id
        data["active_run_id"] = args.run_id
    if args.eta_seconds is not None:
        agent["eta_seconds"] = args.eta_seconds
    if args.evidence:
        agent["evidence"] = args.evidence
    agent["last_heartbeat_at"] = now_utc()
    data["updated_by"] = args.agent_id
    append_event(data, args.agent_id, "heartbeat", agent.get("current_action", "heartbeat"))
    return f"heartbeat {args.agent_id}"


def command_block(data: dict[str, Any], args: argparse.Namespace) -> str:
    reject_unsafe_text("summary", args.summary)
    index = current_agent_index(data, args.agent_id)
    if index is None:
        raise SystemExit(f"No current agent found for {args.agent_id}; run start first.")
    agent = data["current_agents"][index]
    agent["status"] = "blocked"
    agent["current_action"] = args.summary
    agent["last_heartbeat_at"] = now_utc()
    data["updated_by"] = args.agent_id
    append_event(data, args.agent_id, "blocked", args.summary)
    return f"blocked {args.agent_id}"


def command_complete(data: dict[str, Any], args: argparse.Namespace) -> str:
    reject_unsafe_text("summary", args.summary)
    index = current_agent_index(data, args.agent_id)
    if index is None:
        raise SystemExit(f"No current agent found for {args.agent_id}; nothing to complete.")
    data["current_agents"].pop(index)
    remaining_runs = [
        agent.get("run_id")
        for agent in data.get("current_agents", [])
        if isinstance(agent, dict) and agent.get("run_id")
    ]
    data["active_run_id"] = remaining_runs[0] if remaining_runs else state_active_run()
    totals = data.setdefault("totals", {})
    completed = totals.get("completed_agents_last_24h", 0)
    totals["completed_agents_last_24h"] = completed + 1 if isinstance(completed, int) else 1
    data["updated_by"] = args.agent_id
    append_event(data, args.agent_id, "completed", args.summary)
    return f"completed {args.agent_id}"


def command_reset(data: dict[str, Any], args: argparse.Namespace) -> str:
    del data
    del args
    return "reset"


def add_common_agent_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--agent-id", required=True, help="Stable agent id, for example coordinator or coder-api.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update agent activity telemetry.")
    parser.add_argument(
        "--file",
        default=str(DEFAULT_ACTIVITY_FILE),
        help="Activity YAML path. Defaults to .maestro/runtime/agent-activity.yaml.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Start or replace an active agent record.")
    add_common_agent_args(start)
    start.add_argument("--phase", required=True)
    start.add_argument("--current-action", required=True)
    start.add_argument("--model-profile")
    start.add_argument("--provider", default="unknown")
    start.add_argument("--model-id")
    start.add_argument("--task-id")
    start.add_argument("--run-id")
    start.add_argument("--active-file")
    start.add_argument("--eta-seconds", type=int)
    start.add_argument("--evidence", action="append", default=[])

    heartbeat = sub.add_parser("heartbeat", help="Update current action, ETA, or evidence.")
    add_common_agent_args(heartbeat)
    heartbeat.add_argument("--current-action")
    heartbeat.add_argument("--active-file")
    heartbeat.add_argument("--run-id")
    heartbeat.add_argument("--eta-seconds", type=int)
    heartbeat.add_argument("--evidence", action="append", default=[])

    block = sub.add_parser("block", help="Mark an active agent as blocked.")
    add_common_agent_args(block)
    block.add_argument("--summary", required=True)

    complete = sub.add_parser("complete", help="Complete and remove an active agent record.")
    add_common_agent_args(complete)
    complete.add_argument("--summary", required=True)

    sub.add_parser("reset", help="Reset activity file to idle seed state.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    path = Path(args.file)
    if not path.is_absolute():
        path = ROOT / path

    if args.command == "reset":
        data = seed_activity()
        message = command_reset(data, args)
    else:
        data = ensure_activity(load_yaml(path))
        if args.command == "start":
            message = command_start(data, args)
        elif args.command == "heartbeat":
            message = command_heartbeat(data, args)
        elif args.command == "block":
            message = command_block(data, args)
        elif args.command == "complete":
            message = command_complete(data, args)
        else:
            raise SystemExit(f"Unknown command: {args.command}")
        refresh_totals(data)

    write_yaml(path, data)
    print(f"activity updated: {message} -> {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
