# Lab 3 H1 — AI extension review: help command

- Owner: @dknhu
- Date: 2026-10-29 (Asia/Bangkok)
- AI coding assistant: Codex (OpenAI)
- Feature: `help` and `/help` list the assistant's supported capabilities.
- Status: code and this review were prepared and checked with Codex; the student's manual review is pending.

## Request and scope

The user's request to Codex was: “xử lí H1 đi”. The agreed scope in the conversation was to add a help command to the existing `assistant_core`, test it, and document the changes to the initial AI proposal.

`AssistantService.handle(Message) -> Response` stays the public entry point. Help describes office lookup, tuition calculation, and handbook rules. It runs offline and needs no new dependencies or real AI provider.

## Initial AI proposal

The first sketch handled help directly in the CLI with substring matching:

```python
# Initial AI sketch: inside the CLI, before service.handle(...).
if "help" in args.text.lower():
    print("I can help with offices, tuition and handbook rules.")
    return
```

This sketch is retained here as review evidence; it was not shipped as application code.

## Three improvements made to the proposal

| # | Before | After | Why | Verification |
| --- | --- | --- | --- | --- |
| 1 | `"help" in args.text.lower()` matched any occurrence of the word, including ordinary questions and `helpdesk`. | `router.route()` normalizes the input using the existing rules, then matches only `help` or `/help` and returns `Intent.HELP`. | Commands no longer override tuition, office, or handbook questions. | `test_route_help_command` and `test_help_does_not_override_regular_questions`. |
| 2 | CLI-only `print()` and an early return bypassed the service contract and the normal JSON logging path. | The router selects `Intent.HELP`; the service returns a typed `Response`, with no sources and `degraded=False`. The existing CLI prints the answer and logs metadata. | CLI and future API callers receive the same behavior. The existing `Responder` interface stays unchanged, and help does not need knowledge search or provider calls. | `test_service_help_returns_a_typed_response` and `test_help_does_not_query_knowledge_or_call_a_provider`. |
| 3 | The sketch had no automated verification; a manual terminal check would miss regressions. | Added parameterized router tests, service contract checks, and real CLI subprocess tests. CLI tests check separate stdout/stderr, the JSON event fields, and a test-only secret's absence from output. | The feature is verified at its public boundaries and existing functionality remains covered by the original suite. | `tests/test_help.py` plus the full test suite. |

## Interface, dependency, and privacy review

- Public input and output remain `Message` and `Response`; the intent enum gains the additive value `help`.
- Help returns a local capability description. It does not call `Responder.explain()`, the fallback responder, or knowledge lookup methods.
- No package dependencies were added. `pyproject.toml` and pinned `requirements.txt` are unchanged.
- No logging of user messages, configuration, or credentials was added. The CLI still logs the fixed event `handled` and the existing metadata fields.
- This command still uses the existing CLI startup process, including loading its knowledge files; it is not a recovery command for missing application data.

## Run and verify

From the project root, with its environment activated and dependencies installed:

```console
python -m assistant_core help
python -m assistant_core /help
python -m pytest -q
python -m ruff check src/ tests/
python -m ruff format --check src/ tests/
```

Local verification on Python 3.13.11 with the existing pinned environment: **63 tests passed** (49 existing tests and 14 new cases); Ruff lint passed and all 18 Python files passed the format check.

The answer lists offices, tuition, and handbook rules on stdout. The CLI emits one JSON `handled` event with `intent="help"` on stderr.

## Student's manual review before submission

The three changes above were carried out with Codex assistance. They do not claim that @dknhu has already reviewed them manually. Complete the following after reading the diff and running the commands:

- [ ] Trace `Message -> route() -> Intent.HELP -> Response` in the code.
- [ ] Explain why `helpdesk` and `help me calculate tuition` must not become help commands.
- [ ] Read the three improvements and confirm they describe the actual diff.
- [ ] Run the checks and confirm that the existing features still pass.
- [ ] Record any additional corrections made during the manual review, then request review and submit the merged PR link.

AI use is recorded in [`../ai-use-log.md`](../ai-use-log.md).
