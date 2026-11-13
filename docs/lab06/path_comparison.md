# Lab06 — So sánh các hướng trả lời

## F — Kết quả trên 20 câu hỏi mẫu

Chạy từ gốc repo sau khi hoàn thành A1 và A2, với `LLM_PROVIDER=stub`:

```bash
./.venv312/Scripts/python.exe eval/compare_paths.py
```

Điền bảng bằng kết quả thực tế của script. `correct` là số câu đạt kỳ vọng,
`abstain ok` là số câu từ chối đúng trong các câu cần từ chối.

| Path | Correct | Abstain ok | p50 ms | Max ms | Các case chưa đạt |
|---|---|---|---|---|---|
| deterministic | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |
| retrieval | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |
| llm (stub) | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |

### Nhận xét — 3 câu

1. [Điền nhận xét về khả năng trả lời đúng của ba hướng.]
2. [Điền nhận xét về việc từ chối khi thiếu thông tin hoặc gặp câu hỏi riêng tư.]
3. [Điền nhận xét về độ trễ và một hạn chế quan sát được.]

## H1 — Thêm 5 câu hỏi và chạy lại

Thêm 5 dòng vào `eval/cases.jsonl`, giữ nguyên 20 câu mẫu:

- 3 câu bình thường có `expect_source` đối chiếu với tài liệu trong `data/kb/`.
- 2 câu cần từ chối có `"expect_abstain": true`.
- Mỗi câu có ID riêng, tiếp nối các ID đã có.

### Câu hỏi bổ sung

| ID | Câu hỏi | Nguồn kỳ vọng hoặc yêu cầu từ chối |
|---|---|---|
| E21 | Chưa bổ sung | Chưa bổ sung |
| E22 | Chưa bổ sung | Chưa bổ sung |
| E23 | Chưa bổ sung | Chưa bổ sung |
| E24 | Chưa bổ sung | Chưa bổ sung |
| E25 | Chưa bổ sung | Chưa bổ sung |

### Kết quả trên 25 câu hỏi

Chạy lại cùng lệnh ở phần F và điền bảng bằng kết quả thực tế.

| Path | Correct | Abstain ok | p50 ms | Max ms | Các case chưa đạt |
|---|---|---|---|---|---|
| deterministic | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |
| retrieval | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |
| llm (stub) | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |

### Giải thích — 1 câu

[Nêu câu hỏi bổ sung nào chưa đạt và lý do, hoặc ghi nhận cả 5 câu đã đạt kỳ vọng.]
