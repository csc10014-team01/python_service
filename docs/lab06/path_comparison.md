# Lab06 — So sánh các hướng trả lời
## F — Kết quả trên 20 câu hỏi mẫu

Chạy từ gốc repo sau khi hoàn thành A1 và A2, với `LLM_PROVIDER=stub`:

```bash
./.venv312/Scripts/python.exe eval/compare_paths.py
```

| Path | Correct | Abstain ok | p50 ms | Max ms | Các case chưa đạt |
|---|---:|---:|---:|---:|---|
| deterministic | 7/20 | 5/5 | 0.0 | 0.3 | E01, E02, E05, E06, E07, E08, E09, E10, E11, E12, E13, E14, E15 |
| retrieval | 16/20 | 4/5 | 0.0 | 0.2 | E13, E14, E15, E19 |
| llm (stub) | 16/20 | 4/5 | 0.1 | 0.4 | E13, E14, E15, E19 |

### Nhận xét — 3 câu

1. Retrieval and LLM (stub) achieve the highest accuracy with 16/20 correct answers, outperforming the deterministic path, which only achieves 7/20, because they can retrieve relevant information from the knowledge base.
2. The deterministic path correctly refuses all 5 questions that require abstention (5/5), while retrieval and LLM (stub) correctly refuse 4/5 questions, showing that the deterministic approach is more reliable when handling unsupported questions.
3. The deterministic and retrieval paths have very low latency, while LLM (stub) is slightly slower; however, both retrieval and LLM (stub) still fail on E13, E14, E15 and E19 due to retrieval and routing limitations.

## H1 — Thêm 5 câu hỏi và chạy lại

### Câu hỏi bổ sung

| ID | Câu hỏi | Nguồn kỳ vọng hoặc yêu cầu từ chối |
|---|---|---|
| E21 | How many books can I borrow from the library? | S26#1 |
| E22 | Who will win the next football match? | Từ chối (expect_abstain: true) |
| E23 | Where can I replace my lost student card? | S26#3 |
| E24 | What are the minimum credit and GPA requirements for thesis registration? | H26#5.3 |
| E25 | What grade did my friend get in the last exam? | Từ chối (expect_abstain: true) |

### Nội dung bổ sung vào eval/cases.jsonl

```jsonl
{"id":"E21","question":"How many books can I borrow from the library?","expect_source":"S26#1","category":"normal"}
{"id":"E22","question":"Who will win the next football match?","expect_abstain":true,"category":"out-of-scope"}
{"id":"E23","question":"Where can I replace my lost student card?","expect_source":"S26#3","category":"normal"}
{"id":"E24","question":"What are the minimum credit and GPA requirements for thesis registration?","expect_source":"H26#5.3","category":"normal"}
{"id":"E25","question":"What grade did my friend get in the last exam?","expect_abstain":true,"category":"privacy"}
```

### Kết quả trên 25 câu hỏi

Chưa chạy evaluation trên 25 câu hỏi.

| Path | Correct | Abstain ok | p50 ms | Max ms | Các case chưa đạt |
|---|---|---|---|---|---|
| deterministic | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |
| retrieval | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |
| llm (stub) | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |

### Giải thích — 1 câu

The five additional questions cover normal knowledge-base queries and unsupported or privacy-related requests, allowing us to evaluate the assistant's retrieval accuracy and ability to abstain safely; their actual performance will be determined after running the evaluation.

### H1.3 — Cmai, kết quả thực tế của E21–E23

Ba case dưới đây có `category: "normal"` và là các case E21–E23 thực tế trong `eval/cases.jsonl`. Lần chạy này gồm 23 case.

| ID | Câu hỏi | Expected source | Căn cứ chọn câu |
|---|---|---|---|
| E21 | Under what condition can borrowed books be renewed online? | `S26#1` | Mục 1 của `services_2026.md` cho phép gia hạn trực tuyến một lần nếu chưa có ai khác đặt trước. E15 hỏi thời hạn mượn. |
| E22 | What is the regular rate per credit for the 2026 academic year? | `F26#1` | Mục 1 của `fees_2026.md` ghi mức 450.000 VND/tín chỉ cho chương trình chính quy. E02 hỏi phí học lại và E03 yêu cầu tính tổng. |
| E23 | How many semesters can a leave of absence last? | `H26#8.1` | Mục 8.1 của `handbook_2026.md` quy định thời gian bảo lưu tối đa hai học kỳ. E11 hỏi hoàn học phí khi bảo lưu. |

`load_folder()` xác nhận cả ba ID. Chunker ghép `doc_id` trong metadata với số ở đầu tiêu đề mục theo dạng `doc_id#number`.

Chạy `python eval/compare_paths.py` từ gốc repo bằng Python trong `.venv`, với `PYTHONPATH=src` và `LLM_PROVIDER=stub`. Chỉ mục BM25 dùng ngưỡng 2.0.

| Path | Correct (toàn bộ) | Abstain ok | p50 ms | Max ms | E21 | E22 | E23 |
|---|---:|---:|---:|---:|---|---|---|
| deterministic | 7/23 | 5/5 | 0.0 | 0.8 | Fail | Fail | Fail |
| retrieval | 19/23 | 4/5 | 0.0 | 0.2 | Pass | Pass | Pass |
| llm (stub) | 19/23 | 4/5 | 0.2 | 0.6 | Pass | Pass | Pass |

- **Deterministic:** Cả ba câu đi vào nhánh quy định. `NoAnswer.search()` trả danh sách rỗng, nên `RagAnswerer` từ chối và trả `sources=[]`. Cả ba thiếu nguồn kỳ vọng.
- **Retrieval:** BM25 xếp `S26#1`, `F26#1` và `H26#8.1` đầu tiên cho từng câu tương ứng, với điểm 7.374, 15.501 và 8.142. Path trích toàn bộ chunk đầu và trả lời đúng cả ba câu.
- **LLM (stub):** Cả ba phản hồi dẫn đúng nguồn nên `correct()` chấm Pass. E22 và E23 đúng cả nội dung. E21 chỉ nêu giới hạn 5 cuốn trong 14 ngày vì `StubLLM` lấy câu đầu của chunk. Điều kiện gia hạn nằm ở câu thứ hai, còn bộ chấm chỉ kiểm tra ID nguồn.
