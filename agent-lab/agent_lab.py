"""A small, inspectable agent loop for a technical curriculum lab."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent
KNOWLEDGE_DIR = ROOT / "knowledge"
RUN_DIR = ROOT / "runs"

SYSTEM_PROMPT = """You are a technical curriculum design assistant.
Use the available tools before drafting. Ground recommendations in retrieved material.
Create concise, technically accurate learning experiences for adult technical learners.
Include a measurable objective, prerequisites, a working-example sequence, one failure-and-recovery task, evidence of completion, and a human-review checkpoint.
Never request credentials, student records, or protected information.
"""


def search_knowledge(query: str, max_results: int = 5) -> dict[str, Any]:
    """Return relevant paragraphs from the controlled local knowledge folder."""
    terms = {term.lower() for term in re.findall(r"[A-Za-z0-9]+", query) if len(term) > 2}
    scored: list[tuple[int, str, str]] = []
    for path in KNOWLEDGE_DIR.glob("*.md"):
        for paragraph in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
            score = sum(paragraph.lower().count(term) for term in terms)
            if score:
                scored.append((score, path.name, paragraph.strip()))
    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    return {
        "query": query,
        "results": [
            {"source": source, "text": text}
            for _, source, text in scored[: max(1, min(max_results, 8))]
        ],
    }


def check_learning_objective(objective: str) -> dict[str, Any]:
    """Check whether an objective begins with observable performance language."""
    observable = {
        "build", "configure", "compare", "create", "debug", "demonstrate",
        "design", "evaluate", "explain", "identify", "implement", "test", "trace",
    }
    vague = {"understand", "learn", "know", "appreciate", "become familiar"}
    lowered = objective.lower()
    matches = sorted(verb for verb in observable if re.search(rf"\b{re.escape(verb)}\b", lowered))
    vague_matches = sorted(verb for verb in vague if re.search(rf"\b{re.escape(verb)}\b", lowered))
    return {
        "objective": objective,
        "measurable": bool(matches) and not vague_matches,
        "observable_verbs": matches,
        "vague_language": vague_matches,
        "recommendation": (
            "Keep the objective and name the evidence learners will produce."
            if matches and not vague_matches
            else "Rewrite with an observable verb and a product or performance that can be inspected."
        ),
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Search the controlled local curriculum knowledge base for relevant guidance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "minimum": 1, "maximum": 8},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_learning_objective",
            "description": "Check a proposed learning objective for observable, measurable language.",
            "parameters": {
                "type": "object",
                "properties": {"objective": {"type": "string"}},
                "required": ["objective"],
                "additionalProperties": False,
            },
        },
    },
]

FUNCTIONS: dict[str, Callable[..., dict[str, Any]]] = {
    "search_knowledge": search_knowledge,
    "check_learning_objective": check_learning_objective,
}


def load_local_env(path: Path) -> None:
    """Load simple KEY=VALUE settings without adding a runtime dependency."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def trace(event: str, payload: dict[str, Any]) -> None:
    RUN_DIR.mkdir(exist_ok=True)
    record = {"time": datetime.now(timezone.utc).isoformat(), "event": event, **payload}
    with (RUN_DIR / "agent-trace.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def run_agent(prompt: str) -> str:
    from openai import OpenAI

    load_local_env(ROOT / ".env")
    base_url = os.getenv("OPENWEBUI_BASE_URL", "").strip()
    api_key = os.getenv("OPENWEBUI_API_KEY", "").strip()
    model = os.getenv("OPENWEBUI_MODEL", "").strip()
    max_steps = int(os.getenv("AGENT_MAX_STEPS", "6"))
    if not base_url or not api_key or not model:
        raise SystemExit("Set OPENWEBUI_BASE_URL, OPENWEBUI_API_KEY, and OPENWEBUI_MODEL in .env")

    client = OpenAI(base_url=base_url, api_key=api_key)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    trace("run_started", {"model": model, "prompt": prompt, "max_steps": max_steps})

    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2,
        )
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))
        tool_calls = message.tool_calls or []
        trace("model_step", {"step": step, "tool_calls": [call.function.name for call in tool_calls]})

        if not tool_calls:
            answer = message.content or ""
            trace("run_completed", {"step": step, "answer": answer})
            return answer

        for call in tool_calls:
            name = call.function.name
            try:
                arguments = json.loads(call.function.arguments)
                if name not in FUNCTIONS:
                    raise ValueError(f"Tool is not allowed: {name}")
                result = FUNCTIONS[name](**arguments)
                trace("tool_result", {"step": step, "tool": name, "ok": True, "result": result})
            except (json.JSONDecodeError, TypeError, ValueError) as error:
                result = {"error": str(error), "recoverable": True}
                trace("tool_result", {"step": step, "tool": name, "ok": False, "result": result})
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result, ensure_ascii=True),
            })

    trace("run_stopped", {"reason": "step_limit", "max_steps": max_steps})
    return "The agent stopped at its configured step limit. Review the trace before retrying."


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", help="Run one request and exit")
    args = parser.parse_args()
    if args.prompt:
        print(run_agent(args.prompt))
        return
    print("Local AI Technical Curriculum Agent Lab. Type 'quit' to exit.")
    while True:
        prompt = input("\nRequest: ").strip()
        if prompt.lower() in {"quit", "exit"}:
            break
        if prompt:
            print("\n" + run_agent(prompt))


if __name__ == "__main__":
    main()
