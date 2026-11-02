# Study Assistant - Python Service

Backend trợ lý học tập của nhóm CSC10014. Lab03 cung cấp phần xử lý nghiệp vụ
`assistant_core`; Lab04 bổ sung REST API bằng FastAPI trong `assistant_api`.

Nhóm phát triển Lab04 trực tiếp trong `src/` và `tests/` ở gốc repo.
Bộ bài warm-up và code mẫu trong `lab04/` chỉ giữ trên máy để tham khảo,
được bỏ qua bởi Git và không nằm trong bản dự án chung trên GitHub.

## 1. Cài đặt trên Windows với Git Bash

Dùng **Python 3.12**, cùng phiên bản minor với CI. Bộ dependencies cố định hiện tại
không cài được đầy đủ bằng Python 3.14.

Mở Git Bash tại thư mục repo `python_service`. Nếu chưa có môi trường `.venv`:

```bash
py -3.12 -m venv .venv
```

Nếu đã có `.venv` dùng Python 3.12 thì dùng lại. Kích hoạt môi trường mỗi khi mở
terminal mới, rồi cài dependencies:

```bash
source .venv/Scripts/activate
python --version
python -c "import sys; print(sys.executable)"
python -m pip install -r requirements.txt && python -m pip install -e .
python -m pip check
```

Đường dẫn Python phải nằm trong `.venv/Scripts/` của repo.

## 2. Cấu hình môi trường

Chỉ chạy lệnh sau nếu chưa có `.env`:

```bash
cp .env.example .env
```

Mở `.env`, đặt key thử nghiệm để dùng endpoint xem feedback của admin:

```dotenv
API_ADMIN_KEY=change-me
```

Giữ `LLM_PROVIDER=stub` để chạy với responder mô phỏng, không cần API key LLM.
`ASSISTANT_DATA_DIR=data` dùng dữ liệu tại thư mục `data/` ở gốc repo.
Các thiết lập weather và giới hạn request đã có trong `.env.example`.
Biến môi trường của terminal được ưu tiên hơn giá trị trong `.env`.

Chỉ commit `.env.example`; `.env`, key thật và môi trường `.venv` phải được bỏ qua
bởi Git. Nếu đã có `.env`, bổ sung các biến mới thay vì chép đè file.

## 3. Chạy API

Chạy từ gốc repo sau khi kích hoạt `.venv`:

```bash
python -m uvicorn assistant_api.main:create_app --factory --reload
```

- Kiểm tra server: <http://127.0.0.1:8000/health>
- Swagger UI để thử endpoint: <http://127.0.0.1:8000/docs>

Giữ terminal mở để server nhận request. Nhấn `Ctrl+C` để dừng.
Muốn chạy lệnh khác trong lúc server hoạt động, mở Git Bash thứ hai và kích hoạt
`.venv` tại gốc repo.

### Trạng thái Lab04 ở giai đoạn setup

`/health` và trang `/docs` đã có sẵn. Các task sau được nhóm hoàn thiện tiếp:

| Phần | Chức năng |
|---|---|
| D - T1 | `POST /v1/chat`: gọi service và trả `request_id` |
| D - T2, T3 | `POST /v1/feedback`, `GET /v1/feedback`: lưu và xem feedback |
| D - T4 | `GET /v1/weather`: trả thời tiết hoặc lỗi `503` |
| F | Rate limiting cho chat, trả `429` khi vượt giới hạn |
| H1 | `GET /v1/offices`, danh sách sắp xếp theo tên và hai test |

Endpoint còn `NotImplementedError` có thể trả `500` khi gọi; đó là phần task chưa
hoàn thành. Sau khi hoàn thiện feedback, `GET /v1/feedback` yêu cầu header
`X-API-Key` khớp với `API_ADMIN_KEY` trong `.env`.

## 4. Chạy test

Mọi lệnh bên dưới chạy từ gốc repo, trong `.venv` đã cài dependencies.

### Kiểm tra setup hiện tại

Liệt kê test để kiểm tra việc thu thập và import; lệnh này chưa chạy test:

```bash
python -m pytest --collect-only -q
```

Chạy test core Lab03:

```bash
python -m pytest -q --ignore=tests/test_api.py
```

Chạy các test API không cần hoàn thành T1-T4:

```bash
python -m pytest -q tests/test_api.py -k "health or validation_error or rating_out_of_range or stale_cache"
```

CI ở giai đoạn setup chạy hai nhóm kiểm tra trên. `deselected` nghĩa là test
không được chọn bởi bộ lọc, không phải test thất bại.

### Khi hoàn thành Lab04

```bash
python -m pytest -q
```

Các test API dùng `TestClient` và mock weather, không cần mở server hoặc gọi
dịch vụ thời tiết thật. Test rate limiting đang được skip trong starter;
người làm phần F bỏ dấu skip sau khi triển khai chức năng.
Người làm H1 bổ sung hai test: endpoint trả `200` và danh sách có `Library`.

Khi D, F và H1 hoàn thành, cập nhật `.github/workflows/ci.yml` để thay hai bước
kiểm tra setup bằng bước chạy toàn bộ `python -m pytest -q`.
`testpaths = ["tests"]` trong `pyproject.toml` giữ nguyên để không quét test mẫu
còn lại trong `lab04/`.

### Kiểm tra code style

```bash
python -m ruff check src/ tests/
python -m ruff format --check src/ tests/
```

## 5. Kiểm thử thủ công với curl hoặc Postman

Sau khi các endpoint tương ứng được triển khai, mở server theo mục 3.
Trong Git Bash thứ hai, tại gốc repo, chạy:

```bash
bash api-tests/curl_tests.sh
```

Script mặc định dùng `http://127.0.0.1:8000` và admin key `change-me`.
Nếu dùng key khác, đặt biến `API_ADMIN_KEY` trong terminal thứ hai trước khi chạy
script để khớp với key trong `.env`. Script không tự đọc `.env`.
Script in mã HTTP để đối chiếu thủ công, không thay thế bộ test pytest.
Weather thật có thể trả `503` khi dịch vụ ngoài không truy cập được.

Có thể nhập `api-tests/study-assistant.postman_collection.json` vào Postman,
rồi chỉnh các biến `base` và `admin_key` cho phù hợp.
Đính kèm ảnh `/docs` gọi `POST /v1/chat` thành công vào PR hoàn thiện Lab04.

## 6. Chạy CLI Lab03

```bash
python -m assistant_core "where is the library"
```

## Cấu trúc chính

```text
python_service/
|-- .github/workflows/ci.yml
|-- api-tests/                  # curl script và Postman collection
|-- data/                       # dữ liệu offices và handbook
|-- docs/                       # tài liệu dự án
|-- src/
|   |-- assistant_core/         # nghiệp vụ Lab03 và phần core bổ sung của H1
|   `-- assistant_api/          # lớp HTTP của Lab04
|-- tests/                     # test core và API của dự án chung
|-- .env.example
|-- pyproject.toml
`-- requirements.txt
```
