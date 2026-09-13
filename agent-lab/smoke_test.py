"""Offline checks for the agent lab's controlled tools."""

from agent_lab import check_learning_objective, search_knowledge


def main() -> None:
    search = search_knowledge("agent guardrails tool schemas evaluation")
    assert search["results"], "Knowledge search returned no results"
    good = check_learning_objective("Build and test an agent that calls two read-only tools.")
    assert good["measurable"] is True, good
    weak = check_learning_objective("Understand AI agents.")
    assert weak["measurable"] is False, weak
    print("PASS: knowledge retrieval and objective checks")


if __name__ == "__main__":
    main()
