# AI use log

## 2026-10-29 — @dknhu — Lab 3 H1 help extension

- Tool: Codex (OpenAI), used as a coding assistant; no runtime AI API was added.
- User request: “xử lí H1 đi”, following the discussion of H1 on page 18 of the Lab 3 tutorial.
- Scope: add a help command to the existing service, improve the initial proposal, add automated tests, and prepare the H1 review document.
- AI-generated material retained: `Intent.HELP`, command routing, the service's help response, `tests/test_help.py`, usage documentation, and the initial draft of the H1 review.
- Changes to the initial proposal: replace substring detection with exact normalized commands; move the response from the CLI into the typed service flow; add router, service, CLI, and privacy regression checks.
- Verification: full pytest suite, Ruff lint, Ruff format check, and GitHub Actions for the PR. Refer to the PR checks for the CI result.
- Dependencies: none added; the pinned requirements remain unchanged.
- Human-review status: pending. Code and documentation were prepared with Codex; @dknhu must read, verify, and update the manual-review checklist before presenting this work as manually reviewed.

Details and before/after evidence: [`lab3/ai_extension_review.md`](lab3/ai_extension_review.md).
