# Local AI Technical Curriculum Agent Lab

This working reference project connects a Python agent loop to a self-hosted OpenWebUI endpoint. It demonstrates the skills a technical curriculum developer needs to teach: tool definitions, model-driven tool selection, retrieval from a controlled knowledge base, error handling, guardrails, trace logging, and evaluation.

## What the agent does

Given a request for a technical lesson, the agent can:

1. Search a small, local curriculum knowledge base.
2. Check a proposed learning objective for measurable language.
3. Produce a concise lesson outline grounded in retrieved material.
4. Record a JSONL trace so the builder can inspect every model and tool step.

The tools are read-only. The agent cannot run shell commands, browse the network, or modify the knowledge base.

## Requirements

- Python 3.10 or newer
- A running OpenWebUI instance with an OpenAI-compatible API enabled
- An OpenWebUI API key
- A model that supports OpenAI-style tool calling

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your OpenWebUI URL, API key, and model name. A typical local base URL is `http://localhost:3000/api`.

## Run

Interactive mode:

```bash
python agent_lab.py
```

One request from the command line:

```bash
python agent_lab.py --prompt "Create a 45-minute introduction to tool calling for technical instructors."
```

The run trace is written to `runs/agent-trace.jsonl`.

## Verify

```bash
python smoke_test.py
```

The smoke test exercises the local tools without contacting a model. Then complete the acceptance test in [`docs/lab-guide.md`](docs/lab-guide.md) against your OpenWebUI server.

## Portfolio evidence

Capture these items after a successful run:

- A screenshot of the completed terminal interaction
- The sanitized JSONL trace with the API key excluded
- The model name and deployment environment
- A short note describing one failure you encountered and how you corrected it

That evidence turns this repository from source code into a demonstrable deployed agent project.

## Responsible-use boundary

This is a curriculum prototyping tool. A human instructor reviews every output before it is used with learners. Do not place student records, protected information, credentials, or proprietary curriculum in the knowledge folder or prompts.
