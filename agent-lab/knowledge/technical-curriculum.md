# Technical Curriculum Principles

## Learning objectives

Use observable verbs. A learner should build, configure, compare, debug, evaluate, or explain something that can be inspected. Avoid vague objectives such as understand, learn, or know unless a measurable performance follows.

## Scaffold

Start with a working example. Let learners inspect its inputs, outputs, and trace. Then change one variable, diagnose one failure, and build a small variation. End with a performance task that requires transfer rather than imitation.

## Hands-on labs

Every lab should specify prerequisites, environment checks, expected output, common failure modes, recovery steps, and evidence of completion. Keep setup separate from the learning objective so infrastructure problems do not obscure the target skill.

## Agent concepts

An AI agent combines a model with instructions, tools, state, and a control loop. Tool schemas constrain what the model can request. The application validates tool arguments, runs allowed functions, returns results to the model, and stops at a defined limit.

## Guardrails

Use the smallest useful tool set. Validate arguments before execution. Prefer read-only operations in beginner labs. Set step and time limits. Keep credentials outside source code and logs. Require human review for consequential outputs.

## Evaluation

Evaluate both process and output. Process evidence can include tool-selection accuracy, valid arguments, recovery from tool errors, citation to retrieved content, and compliance with step limits. Output evidence can include technical accuracy, completeness, clarity, and alignment with the objective.
