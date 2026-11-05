# Lab04 – Part C (dknhu / Nhukei)

Bài cá nhân P1–P5 theo trang 9–11 của đề Lab04. Reviewer theo bảng phân công: **Nghi**.
Dùng chung môi trường `.venv` và dependencies của repo `python_service`.
Code và bộ test dựa trên [practice gốc của môn](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/main/lab04/practice).
Bài nộp trên nhánh riêng `feat/lab04-practice-dknhu` trong repo `python_service`.

Từ gốc repo, trong PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q lab04/practice/test_hello_api.py
cd lab04/practice
python -m uvicorn hello_api:app --reload
```

Với Git Bash, kích hoạt bằng `source .venv/Scripts/activate`, rồi chạy các lệnh Python tương tự.
Mở <http://127.0.0.1:8000/docs> để thử API. Dừng server bằng `Ctrl+C`.

| Bài | Request | Kết quả |
|---|---|---|
| P1 | `GET /` | `{"message":"Hello, CSC10014!"}` |
| P2 | `GET /hello/Lan` | `{"message":"Hello, Lan!"}` |
| P3 | `GET /square?n=7` | `{"n":7,"square":49}`; `n=abc` trả `422` |
| P4 | `POST /add`, JSON `{"a":2,"b":3}` | `{"sum":5.0}` |
| P5 | `GET /courses/CSC10014` | Mã và tên môn học; `/courses/XYZ` trả `404` |

File nộp: `hello_api.py` và `test_hello_api.py`. Kết quả mong đợi: **5 passed**.
