# Lab Guide: Build and Inspect a Tool-Calling Curriculum Agent

## Audience

Technical instructors, implementation consultants, and power users who understand basic Python and APIs.

## Objective

Build, run, and evaluate a local AI agent that selects from two read-only tools, recovers from invalid tool requests, and produces a grounded technical lesson outline with an inspectable trace.

## Estimated time

60-90 minutes.

## Prerequisites

- Complete the environment setup in the project README.
- Confirm that OpenWebUI can answer a normal chat-completions request with the selected model.
- Run `python smoke_test.py` and obtain a passing result.

## Part 1: Inspect the working example

Read `agent_lab.py`. Identify the five agent components: instructions, tool schemas, callable functions, message history, and control loop. Predict which tool the model should call for this request:

> Create a 45-minute introduction to tool calling for technical instructors.

Run the request. Save the final response and trace as evidence.

## Part 2: Trace the decision path

Open `runs/agent-trace.jsonl`. Locate:

1. The model step that selected a tool.
2. The validated arguments.
3. The tool result returned to the model.
4. The step that produced the final answer.

Explain whether the final answer is grounded in retrieved material.

## Part 3: Diagnose a failure

Temporarily change the `search_knowledge` function name in its schema so it no longer matches the allowlist. Run the same request and inspect the recoverable error in the trace. Restore the correct name and verify that the agent completes.

## Part 4: Extend the agent

Add one read-only tool that supports a real learning need. Define a narrow JSON schema, validate all arguments, return a serializable result, and add one smoke-test assertion.

## Evidence of completion

- Passing offline smoke test
- Successful model-backed run
- Trace showing at least one tool call
- Short failure-and-recovery note
- One added read-only tool with an argument-validation test

## Evaluation rubric

| Criterion | Meets the standard |
| --- | --- |
| Tool design | Schema is narrow, arguments are validated, and the function is read-only. |
| Agent loop | Tool results return to the model and execution stops within the configured limit. |
| Grounding | Final lesson cites or clearly uses retrieved curriculum guidance. |
| Recovery | Learner identifies a failed tool call and documents a successful correction. |
| Technical communication | Explanation connects implementation decisions to learner safety and reliability. |

## Human review checkpoint

Before using the generated lesson, verify technical accuracy, required prerequisites, expected outputs, accessibility, and whether any learner data appears in the prompt or trace.
