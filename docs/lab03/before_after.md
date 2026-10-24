# Lab 3 — Before / After Maintainability Comparison

Fill in for the monolith (before) and your refactored package (after).

| Question | Before (Monolith) | After (`assistant_core`) |
| :--- | :--- | :--- |
| **Where would you change the credit rate? How many places?** | 1 constant in code (`RATE = 450000` in `assistant_monolith.py`) | 1 environment variable in `.env` (`CREDIT_RATE_VND=450000`) |
| **Can you run the tests without internet or an API key?** | No (uses random failures and hardcoded API key) | Yes (uses `StubLLMResponder` offline without external calls) |
| **What happens if `handbook.json` is missing?** | Prints `"could not load handbook"` and continues silently | Raises `DataError` at startup and halts execution safely |
| **Is any secret printed or logged?** | Yes (`API_KEY` is printed in debug output) | No (`llm_api_key` uses `repr=False` in Pydantic settings) |
| **How long does it take a new teammate to find the fee logic?** | Hard (must scan through a 160-line single-script file) | Instant (located directly in `src/assistant_core/tools.py`) |
| **Number of global variables** | 9 (`API_KEY`, `MODEL`, `RATE`, `RETAKE_RATE`, `DEBUG`, `history`, `offices`, `handbook`, `BASE`) | 0 (all state encapsulated in classes or environment settings) |
| **Number of bare `except:` blocks** | 3 (in `load()` for offices/handbook, and `main()` input) | 0 (replaced with explicit exceptions like `DataError`, `FileNotFoundError`) |
| **Lines in the longest function** | ~65 lines (`handle()` function) | ~15 lines (`AssistantService.handle()`) |
| **`ruff check` issues** | >15 issues (bare except, unused imports, global statements, line formatting) | 0 issues (All checks passed) |
| **Can you swap the LLM without touching the service?** | No (LLM call is tightly coupled inside `handle()`) | Yes (via the `Responder` Protocol interface / adapter pattern) |


### Reflection Summary

* **What improved most**: System maintainability, testability, and security improved drastically by eliminating global mutable state, enforcing typed input/output boundaries with Pydantic, and moving configuration out of code.
* **What got more complex**: The project layout became more complex with multiple single-responsibility files, abstraction layers (Protocols/Adapters), and explicit exception handling.
* **What you would still change**: I would replace the basic keyword-matching algorithm in `knowledge.py` with semantic vector retrieval (RAG) to improve handbook query accuracy.