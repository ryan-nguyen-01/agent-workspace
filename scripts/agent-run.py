#!/usr/bin/env python3
"""Create and update maestro run records without third-party packages."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".maestro" / "work"
RUNS = WORK / "runs"
RUNTIME = ROOT / ".maestro" / "runtime"
MAX_TEXT_LEN = 500
UNSET = object()

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
            if isinstance(item, (dict, list)):
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


def reject_unsafe_text(label: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            reject_unsafe_text(f"{label}[{i}]", item)
        return
    text = str(value)
    if len(text) > MAX_TEXT_LEN:
        raise SystemExit(f"{label} is too long for a run record; keep it under {MAX_TEXT_LEN} chars.")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise SystemExit(f"{label} appears to contain a secret or raw credential. Refusing to write run record.")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or "run"


def next_run_id(slug: str) -> str:
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    existing = sorted(RUNS.glob(f"RUN-{day}-*-*"))
    nums: list[int] = []
    for path in existing:
        match = re.match(rf"RUN-{day}-(\d{{3}})-", path.name)
        if match:
            nums.append(int(match.group(1)))
    number = max(nums, default=0) + 1
    return f"RUN-{day}-{number:03d}-{slugify(slug)}"


def checkpoint_id() -> str:
    return "CHK-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def ensure_run_index() -> dict[str, Any]:
    data = load_yaml(RUNS / "index.yaml")
    if not data:
        data = {
            "schema_version": "1.0",
            "role": "run-index",
            "run_id_format": "RUN-YYYYMMDD-NNN-slug",
            "states": ["new", "running", "waiting-for-human", "blocked", "verifying", "completed", "failed", "cancelled"],
            "relationships": {
                "task_to_runs": "A task may have zero or more runs.",
                "run_to_checkpoints": "A run may have many checkpoints.",
                "run_to_traces": "A run may link to trace summaries.",
                "run_to_evals": "A run may link to eval evidence.",
            },
            "active": {"run_ids": []},
            "completed": {"run_ids": []},
        }
    data.setdefault("active", {}).setdefault("run_ids", [])
    data.setdefault("completed", {}).setdefault("run_ids", [])
    return data


def state_file() -> Path:
    return RUNTIME / "workflow-state.yaml"


def update_state(run_id: Any = UNSET, task_id: Any = UNSET, checkpoint: Any = UNSET) -> None:
    path = state_file()
    data = load_yaml(path)
    if not data:
        return
    if run_id is not UNSET:
        data["active_run_id"] = run_id
    if task_id is not UNSET:
        data["active_task_id"] = task_id
    if checkpoint is not UNSET:
        data["active_checkpoint_id"] = checkpoint
    data["updated_at"] = now_utc()
    data["updated_by"] = "agent-run-cli"
    write_yaml(path, data)


def run_path(run_id: str) -> Path:
    return RUNS / run_id / "run.yaml"


def load_run(run_id: str) -> dict[str, Any]:
    path = run_path(run_id)
    if not path.exists():
        raise SystemExit(f"Run not found: {run_id}")
    return load_yaml(path)


def append_history(run: dict[str, Any], actor: str, event: str, summary: str) -> None:
    reject_unsafe_text("summary", summary)
    run.setdefault("history", [])
    run["history"].append({"at": now_utc(), "actor": actor, "event": event, "summary": summary})
    run["history"] = run["history"][-50:]


def command_create(args: argparse.Namespace) -> str:
    for label in ("summary", "objective", "agent_id", "task_id"):
        reject_unsafe_text(label, getattr(args, label, None))
    run_id = args.run_id or next_run_id(args.slug or args.summary or args.task_id or "run")
    folder = RUNS / run_id
    if folder.exists() and not args.force:
        raise SystemExit(f"Run folder already exists: {run_id}. Use --force to overwrite run.yaml.")

    for child in ("checkpoints", "traces", "evals", "approvals"):
        (folder / child).mkdir(parents=True, exist_ok=True)

    timestamp = now_utc()
    task_path = f".maestro/work/tasks/{args.task_id}/task.yaml" if args.task_id else None
    run = {
        "schema_version": "1.0",
        "run_id": run_id,
        "task_id": args.task_id,
        "status": "running",
        "execution_mode": args.execution_mode,
        "verification_owner": args.verification_owner,
        "created_at": timestamp,
        "updated_at": timestamp,
        "created_by": args.agent_id,
        "updated_by": args.agent_id,
        "summary": args.summary,
        "objective": args.objective or args.summary,
        "artifacts": {
            "checkpoints": f".maestro/work/runs/{run_id}/checkpoints",
            "traces": f".maestro/work/runs/{run_id}/traces",
            "evals": f".maestro/work/runs/{run_id}/evals",
            "approvals": f".maestro/work/runs/{run_id}/approvals",
            "report": f".maestro/work/runs/{run_id}/report.md",
        },
        "links": {
            "task": task_path,
            "trace_refs": [],
            "eval_refs": [],
            "approval_refs": [],
            "report_refs": [],
        },
        "current": {
            "checkpoint_id": None,
            "phase": args.phase,
            "action": args.summary,
            "blocker": None,
            "next_action": None,
        },
        "history": [{"at": timestamp, "actor": args.agent_id, "event": "run.created", "summary": args.summary}],
    }
    write_yaml(folder / "run.yaml", run)
    (folder / "report.md").write_text(f"# Run Report\n\nRun: `{run_id}`\n\nStatus: `running`\n", encoding="utf-8")

    index = ensure_run_index()
    active = index.setdefault("active", {}).setdefault("run_ids", [])
    if run_id not in active:
        active.append(run_id)
    write_yaml(RUNS / "index.yaml", index)
    update_state(run_id, args.task_id, None)
    return f"created {run_id}"


def command_heartbeat(args: argparse.Namespace) -> str:
    reject_unsafe_text("summary", args.summary)
    run = load_run(args.run_id)
    run["status"] = args.status
    run["updated_at"] = now_utc()
    run["updated_by"] = args.agent_id
    current = run.setdefault("current", {})
    if args.phase:
        current["phase"] = args.phase
    current["action"] = args.summary
    current["blocker"] = args.blocker
    if args.next_action is not None:
        current["next_action"] = args.next_action
    append_history(run, args.agent_id, f"run.{args.status}", args.summary)
    write_yaml(run_path(args.run_id), run)
    update_state(args.run_id, str(run.get("task_id")) if run.get("task_id") else None, current.get("checkpoint_id"))
    return f"updated {args.run_id}"


def command_checkpoint(args: argparse.Namespace) -> str:
    for label in ("summary", "next_action", "agent_id"):
        reject_unsafe_text(label, getattr(args, label, None))
    run = load_run(args.run_id)
    chk_id = args.checkpoint_id or checkpoint_id()
    data = {
        "schema_version": "1.0",
        "checkpoint_id": chk_id,
        "run_id": args.run_id,
        "task_id": run.get("task_id"),
        "created_at": now_utc(),
        "created_by": args.agent_id,
        "summary": args.summary,
        "completed": args.completed,
        "decisions": args.decision,
        "open_questions": args.open_question,
        "known_constraints": args.constraint,
        "next_action": args.next_action,
        "references": args.reference,
    }
    checkpoint_path = RUNS / args.run_id / "checkpoints" / f"{chk_id}.yaml"
    write_yaml(checkpoint_path, data)
    run.setdefault("current", {})["checkpoint_id"] = chk_id
    run.setdefault("current", {})["next_action"] = args.next_action
    run["updated_at"] = now_utc()
    run["updated_by"] = args.agent_id
    append_history(run, args.agent_id, "run.checkpointed", args.summary)
    write_yaml(run_path(args.run_id), run)
    update_state(args.run_id, str(run.get("task_id")) if run.get("task_id") else None, chk_id)
    return f"checkpointed {args.run_id} -> {chk_id}"


def command_complete(args: argparse.Namespace) -> str:
    reject_unsafe_text("summary", args.summary)
    run = load_run(args.run_id)
    run["status"] = args.outcome
    run["updated_at"] = now_utc()
    run["updated_by"] = args.agent_id
    run.setdefault("current", {})["action"] = args.summary
    append_history(run, args.agent_id, f"run.{args.outcome}", args.summary)
    write_yaml(run_path(args.run_id), run)

    index = ensure_run_index()
    active = index.setdefault("active", {}).setdefault("run_ids", [])
    completed = index.setdefault("completed", {}).setdefault("run_ids", [])
    if args.run_id in active:
        active.remove(args.run_id)
    if args.run_id not in completed:
        completed.append(args.run_id)
    write_yaml(RUNS / "index.yaml", index)

    state = load_yaml(state_file())
    if state.get("active_run_id") == args.run_id:
        update_state(None, None, None)
    return f"{args.outcome} {args.run_id}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create and update maestro run records.")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a run and mark it active.")
    create.add_argument("--task-id")
    create.add_argument("--run-id")
    create.add_argument("--slug")
    create.add_argument("--summary", required=True)
    create.add_argument("--objective")
    create.add_argument("--agent-id", default="coordinator")
    create.add_argument("--phase")
    create.add_argument("--execution-mode", choices=["direct", "assisted", "governed"], default="assisted")
    create.add_argument("--verification-owner", choices=["agent", "user", "shared"], default="shared")
    create.add_argument("--force", action="store_true")

    heartbeat = sub.add_parser("heartbeat", help="Update active run status/action.")
    heartbeat.add_argument("--run-id", required=True)
    heartbeat.add_argument("--agent-id", default="coordinator")
    heartbeat.add_argument("--status", choices=["running", "waiting-for-human", "blocked", "verifying"], default="running")
    heartbeat.add_argument("--summary", required=True)
    heartbeat.add_argument("--phase")
    heartbeat.add_argument("--blocker")
    heartbeat.add_argument("--next-action")

    checkpoint = sub.add_parser("checkpoint", help="Create a checkpoint for a run.")
    checkpoint.add_argument("--run-id", required=True)
    checkpoint.add_argument("--checkpoint-id")
    checkpoint.add_argument("--agent-id", default="coordinator")
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--next-action", required=True)
    checkpoint.add_argument("--completed", action="append", default=[])
    checkpoint.add_argument("--decision", action="append", default=[])
    checkpoint.add_argument("--open-question", action="append", default=[])
    checkpoint.add_argument("--constraint", action="append", default=[])
    checkpoint.add_argument("--reference", action="append", default=[])

    complete = sub.add_parser("complete", help="Complete, fail, or cancel a run.")
    complete.add_argument("--run-id", required=True)
    complete.add_argument("--agent-id", default="coordinator")
    complete.add_argument("--outcome", choices=["completed", "failed", "cancelled"], default="completed")
    complete.add_argument("--summary", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "create":
        message = command_create(args)
    elif args.command == "heartbeat":
        message = command_heartbeat(args)
    elif args.command == "checkpoint":
        message = command_checkpoint(args)
    elif args.command == "complete":
        message = command_complete(args)
    else:
        raise SystemExit(f"Unknown command: {args.command}")
    print(f"run updated: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
