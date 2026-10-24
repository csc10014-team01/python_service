# Lab 3 — Before / After Maintainability Comparison

## Part A.2: Monolith Code Smells Analysis

| # | Code Smell | Vị trí trong Monolith | Tác hại tới hệ thống | Module chịu trách nhiệm sửa trong `assistant_core` |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Hard-coded secret** | Khai báo `API_KEY = "sk-test-..."` trực tiếp trong code | Làm rò rỉ API Key vào nhật ký (logs) và kho mã nguồn Git. | `config.py` (Đọc từ môi trường với `repr=False`). |
| **2** | **Configuration mixed with code** | Cấu hình `RATE`, `RETAKE_RATE`, `MODEL`, `DEBUG` khai báo cứng | Thay đổi mức phí hay cấu hình bắt buộc phải sửa trực tiếp code nguồn. | `config.py` & `.env`. |
| **3** | **Global mutable state** | Biến toàn cục `history`, `offices`, `handbook` | Tăng độ phụ thuộc ẩn (hidden coupling), gây ra lỗi không lường trước và không thể cô lập để test. | `knowledge.py` & `service.py` (Dependency Injection). |
| **4** | **Bare `except:`** | Câu lệnh bắt lỗi rỗng trong hàm `load()` và `main()` | Che giấu lỗi hệ thống thật sự, chặn luôn cả tín hiệu ngắt chương trình `Ctrl+C`. | `errors.py` (Bắt các ngoại lệ có tên cụ thể như `DataError`). |
| **5** | **One function does everything** | Hàm `handle()` thực hiện tất cả các tác vụ | Trộn lẫn phân tuyến, đọc chuỗi, tính học phí, tìm kiếm và gọi LLM. | Chia nhỏ vào `router.py`, `tools.py`, `knowledge.py`, `service.py`. |
| **6** | **Magic strings / return values** | Trả về các chuỗi cứng `"empty"`, `"saved"`, `"too many credits"` | Dễ gõ sai chính tả, không có kiểm soát kiểu dữ liệu ở thời gian biên dịch. | `models.py` (Pydantic models & Enums). |
| **7** | **`print` instead of logging** | Dùng `print()` khắp nơi trong file | Không phân biệt được cấp độ lỗi (level), không thể xuất cấu trúc JSON để theo dõi. | `logging_setup.py` (Structured JSON logging). |
| **8** | **Hand-made tests that print** | Hàm `test()` tự viết kiểm tra bằng `print` | Không tự động báo lỗi khi chạy CI, người phát triển phải tự nhìn mắt thường. | Thư mục `tests/` kết hợp với thư viện `pytest`. |
| **9** | **String path concatenation** | Ghép đường dẫn bằng `BASE + "/data/..."` | Dễ gãy trên các hệ điều hành khác nhau (Windows vs Linux/macOS). | `pathlib.Path` trong `config.py` và `knowledge.py`. |
| **10** | **Non-deterministic behaviour** | Gọi `random.random()` giả lập gãy LLM ngẫu nhiên | Kết quả test không ổn định (flaky tests), khó tái hiện lỗi để sửa. | `responder.py` (Tách thành `StubLLMResponder` kiểm soát lỗi cẩn thận). |

## Part E: Before / After Maintainability Comparison

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