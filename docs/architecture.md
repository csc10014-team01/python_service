# Target Architecture - `assistant_core`

## 1. Module Overview

Package `assistant_core` được phân chia thành các module có trách nhiệm riêng biệt (Single Responsibility Principle), đảm bảo tính gắn kết cao (high cohesion) và phụ thuộc thấp (low coupling):

| Module | Responsibility |
| :--- | :--- |
| `config.py` | Read settings from the environment (`.env`); validate settings using Pydantic. |
| `errors.py` | Define named domain exceptions (`AssistantError`, `ConfigError`, `DataError`, `InvalidRequest`, `ProviderError`). |
| `models.py` | Define public contract data models: `Message`, `Response`, `Intent`, `Source`. |
| `router.py` | Choose an `Intent` using deterministic rule matching. |
| `knowledge.py` | Manage office directory (`offices.csv`) and handbook (`handbook.json`) with structured search methods. |
| `tools.py` | Deterministic tuition and credit calculations. |
| `responder.py` | Response generation interface (`Responder` Protocol) with `TemplateResponder` and `StubLLMResponder`. |
| `service.py` | `AssistantService.handle(msg: Message) -> Response` as the single entry point. |
| `logging_setup.py` | Structured JSON logging without leaking sensitive keys or full raw text. |
| `__main__.py` | Command-line interface (CLI) entry point. |

## 2. Service Interface Specification

`AssistantService` đóng vai trò là điểm tương tác duy nhất (single entry point) giữa các giao diện bên ngoài (CLI, FastAPI, UI) và core service.

### Signature
```python
AssistantService.handle(msg: Message) -> Response
```

### Data Contract
* **Input (`Message`)**:
  * `text`: Chuỗi câu hỏi từ người dùng (độ dài 1–2000 ký tự).
  * `session_id`: Định danh phiên làm việc (mặc định: `"local"`).
* **Output (`Response`)**:
  * `answer`: Câu trả lời hoàn chỉnh dạng chuỗi văn bản.
  * `intent`: Ý định được phân loại (`GREETING`, `HELP`, `FEE`, `OFFICE`, `RULE`, `UNKNOWN`).
  * `sources`: Danh sách nguồn trích dẫn (`list[Source]`).
  * `degraded`: Cờ báo hiệu (`bool`) — `True` nếu hệ thống phải chuyển hướng sang cơ chế dự phòng (fallback).

### Error Handling Strategy
1. **Invalid Input**: Bị từ chối và bắn `pydantic.ValidationError` ngay tại ranh giới đầu vào.
2. **Startup / Data Errors**: Bắn ngoại lệ `ConfigError` (thiếu/sai cấu hình) hoặc `DataError` (thiếu tệp dữ liệu `offices.csv` / `handbook.json`).
3. **Provider Failures**: Nếu nhà cung cấp AI gặp sự cố (`ProviderError`), dịch vụ tự động chuyển sang `TemplateResponder`, trả về câu trả lời an toàn kèm `degraded=True`.

## 3. Key Design Decisions

1. **Fees are computed in `tools.py`, never by an LLM**:
   * *Lý do*: Tính toán tài chính/học phí yêu cầu độ chính xác tuyệt đối (exact) và khả năng kiểm thử độc lập (testable). Việc giao tính toán cho LLM dễ dẫn đến ảo giác (hallucination) và kết quả không ổn định.

2. **The LLM sits behind the `Responder` Protocol interface**:
   * *Lý do*: Áp dụng mẫu thiết kế Adapter để tách biệt `AssistantService` khỏi triển khai chi tiết của nhà cung cấp AI. Nhờ đó, `StubLLMResponder` không cần API key hay kết nối internet, cho phép Unit Tests và CI chạy hoàn toàn offline.

3. **Configuration comes from the environment, documented by `.env.example`**:
   * *Lý do*: Tuân thủ nguyên tắc Factor III trong Twelve-Factor App (Config). Mọi thông số cấu hình và secret được đọc từ môi trường / tệp `.env`. Tệp `.env.example` được lưu trên Git đóng vai trò làm tài liệu hướng dẫn cho các thành viên mà không làm lộ secret.

## Help extension (Lab 3 H1)

The router recognizes normalized `help` and `/help` commands as `Intent.HELP`. `AssistantService.handle()` returns a local capability description using the existing `Response` contract, with empty sources and `degraded=False`. The command does not call knowledge lookup or the responder, and does not introduce a new dependency. Ordinary questions containing the word `help` retain their existing routing. The CLI's existing stdout/stderr separation and metadata logging apply to help as well.
