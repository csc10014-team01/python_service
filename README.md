# Study Assistant - Python Service

Trợ lý học tập của nhóm CSC10014 gồm phần xử lý nghiệp vụ `assistant_core`,
REST API bằng FastAPI trong `assistant_api` và giao diện Streamlit Lab07 trong `ui/`.
UI giao tiếp với backend qua HTTP API.

Nhóm phát triển trực tiếp trong `src/`, `ui/` và `tests/` ở gốc repo.
Mọi lệnh bên dưới chạy từ thư mục gốc `python_service`.

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
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pip check
```

Đường dẫn Python phải nằm trong `.venv/Scripts/` của repo.

## 2. Cấu hình môi trường

Chỉ chạy lệnh sau nếu chưa có `.env`:

```bash
if [ ! -e .env ]; then
  cp .env.example .env
fi
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

## 3. Chạy API và UI bằng hai terminal Git Bash

Mở hai terminal Git Bash tại gốc repo `python_service`.
Kích hoạt cùng môi trường `.venv` trong mỗi terminal và chạy API trước UI.

### Terminal 1 — API

```bash
source .venv/Scripts/activate
python -m uvicorn assistant_api.main:create_app --factory --reload
```

- Kiểm tra server: <http://127.0.0.1:8000/health>
- Swagger UI để thử endpoint: <http://127.0.0.1:8000/docs>

### Terminal 2 — UI Streamlit

```bash
source .venv/Scripts/activate
python -m streamlit run ui/app.py
```

Mở <http://localhost:8501> để dùng giao diện chat.
UI mặc định gọi API tại `http://127.0.0.1:8000`.
Giữ cả hai terminal chạy khi sử dụng ứng dụng. Nhấn `Ctrl+C` trong từng terminal
để dừng server tương ứng.

### Đổi địa chỉ API cho UI

Nếu API chạy ở cổng khác, đặt `ASSISTANT_API_URL` trong terminal Git Bash chạy UI
trước khi khởi động Streamlit. Ví dụ dùng cổng 8001:

Terminal 1, thay lệnh chạy API ở trên bằng:

```bash
python -m uvicorn assistant_api.main:create_app --factory --reload --port 8001
```

Terminal 2:

```bash
export ASSISTANT_API_URL="http://127.0.0.1:8001"
python -m streamlit run ui/app.py
```

UI hiện đọc biến này từ môi trường của terminal, chưa tự nạp từ file `.env`.
Để quay về cổng 8000, dừng hai server, chạy lệnh API mặc định và đặt
`export ASSISTANT_API_URL="http://127.0.0.1:8000"` trước khi khởi động lại UI.

### Trạng thái Lab04

T1–T4, H1 và phần F đã được triển khai. `/health` dùng để kiểm tra server;
`/docs` cung cấp giao diện Swagger để thử các endpoint.

| Phần | Chức năng |
|---|---|
| D - T1 | `POST /v1/chat`: gọi service và trả `request_id` |
| D - T2, T3 | `POST /v1/feedback`, `GET /v1/feedback`: lưu và xem feedback |
| D - T4 | `GET /v1/weather`: trả thời tiết hoặc lỗi `503` |
| F | Rate limiting cho chat, trả `429` khi vượt giới hạn |
| H1 | `GET /v1/offices`, danh sách sắp xếp theo tên và hai test |

`GET /v1/feedback` yêu cầu header
`X-API-Key` khớp với `API_ADMIN_KEY` trong `.env`.
Feedback lưu trong database theo `DATABASE_URL`. Với cấu hình mặc định
`sqlite:///assistant.db`, dữ liệu nằm trong file `assistant.db` ở gốc repo và
được giữ lại khi server khởi động lại. Gửi feedback với `request_id` không tồn tại
trả về `404`.

`GET /v1/offices` trả danh sách văn phòng được sắp xếp theo tên, mỗi mục gồm
`name`, `room` và `hours`.

`POST /v1/chat` giới hạn mặc định 30 request hợp lệ mỗi phút cho mỗi IP;
cấu hình bằng `RATE_LIMIT_PER_MIN`. Khi vượt giới hạn, server trả `429`.
Bộ đếm lưu trong bộ nhớ của từng instance ứng dụng và được xóa khi khởi động lại.

## 4. Chạy test

Mọi lệnh bên dưới chạy từ gốc repo, trong `.venv` đã cài dependencies.

### Chạy toàn bộ test

Chạy toàn bộ test trong `tests/`, gồm core, API, database, RAG và UI:

```bash
python -m pytest -q
```

### Chạy riêng từng nhóm

Chạy các test ngoài nhóm API:

```bash
python -m pytest -q --ignore=tests/test_api.py
```

Chạy toàn bộ test API Lab04:

```bash
python -m pytest -q tests/test_api.py
```

Các test API dùng `TestClient` và mock weather, không cần mở server hoặc gọi
dịch vụ thời tiết thật. Bộ test bao gồm Chat, kiểm tra dữ liệu đầu vào, Feedback,
xác thực admin, Weather, Offices và Rate limiting. Test Rate limiting đã được bật,
kiểm tra giới hạn theo IP, địa chỉ client bị thiếu và thời gian hết hạn bộ đếm.

Workflow `.github/workflows/ci.yml` chạy riêng hai nhóm core Lab03 và API Lab04
khi push lên `main` hoặc tạo/cập nhật PR hướng vào `main`. Workflow cũng kiểm tra
Ruff, định dạng code và dấu conflict còn sót.
`testpaths = ["tests"]` trong `pyproject.toml` giữ nguyên để không quét test mẫu
còn lại trong `lab04/`.

### Kiểm tra code style

```bash
python -m ruff check src/ tests/
python -m ruff format --check src/ tests/
```

## 5. Kiểm thử thủ công với curl hoặc Postman

Mở server theo mục 3.
Trong Git Bash thứ hai, tại gốc repo, chạy:

```bash
bash api-tests/curl_tests.sh
```

Script mặc định dùng `http://127.0.0.1:8000` và admin key `change-me`.
Nếu dùng key khác, đặt biến `API_ADMIN_KEY` trong terminal thứ hai trước khi chạy
script để khớp với key trong `.env`. Script không tự đọc `.env`.
Script in mã HTTP để đối chiếu thủ công, không thay thế bộ test pytest.
Weather thật có thể trả `503` khi dịch vụ ngoài không truy cập được.

Script kiểm tra Health, Chat, Feedback, xác thực admin, Weather, đường dẫn không
tồn tại và Offices. Với Offices, kiểm tra mã `200`, danh sách có `Library` và
các văn phòng được sắp xếp theo tên. Khi chạy lại nhiều lần trong một phút,
Chat có thể trả `429` do giới hạn request; chờ hơn một phút hoặc khởi động lại
server để kiểm tra lại từ đầu.

### Kiểm tra Rate limiting bằng curl

Dùng một server mới ở cổng 8001 để có bộ đếm ban đầu trống. Trong Git Bash thứ
nhất, tại gốc repo và sau khi kích hoạt `.venv`, chạy nguyên dòng sau:

```bash
RATE_LIMIT_PER_MIN=5 LLM_PROVIDER=stub python -m uvicorn assistant_api.main:create_app --factory --port 8001
```

Đặt `RATE_LIMIT_PER_MIN` ở terminal khởi động server; đặt biến ở terminal chạy
curl không thay đổi cấu hình server. Nếu cổng 8001 đã được sử dụng, dừng server
cũ bằng `Ctrl+C` trong terminal của nó trước khi chạy lệnh trên.

Giữ server chạy. Trong Git Bash thứ hai, gửi sáu request liên tiếp:

```bash
for i in {1..6}; do
  printf "Request %s: " "$i"
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST http://127.0.0.1:8001/v1/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"hi"}'
done
```

Kết quả mong đợi là năm request đầu trả `200`, request thứ sáu trả `429`.
Chạy trên server vừa khởi động và không gửi thêm request Chat trước phép thử.
Muốn lặp lại từ đầu, dừng rồi khởi động lại server. Lệnh cấu hình giới hạn 5
chỉ áp dụng cho lần chạy đó, không sửa giá trị trong `.env`.

### Postman và minh chứng PR

Có thể nhập `api-tests/study-assistant.postman_collection.json` vào Postman,
rồi chỉnh các biến `base` và `admin_key` cho phù hợp.

Trên server cổng 8000, mở `/docs`, chọn `POST /v1/chat` → `Try it out`, gửi:

```json
{"message": "tuition for 18 credits and 2 retake", "session_id": "demo"}
```

Chụp ảnh thấy mã `200`, câu trả lời và `request_id`. Đính kèm ảnh này, kết quả
pytest, script curl và phép thử Rate limiting vào PR hoàn thiện Lab04.

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
|-- eval/                       # đánh giá các hướng xử lý câu hỏi
|-- scripts/                    # migration và seed database
|-- sql/                        # schema, migrations và truy vấn
|-- src/
|   |-- assistant_core/         # nghiệp vụ, truy xuất tài liệu và AI
|   `-- assistant_api/          # REST API và lưu trữ database
|-- ui/                        # giao diện Streamlit và HTTP client
|-- tests/                     # test core, API, database, RAG và UI
|   `-- test_ui.py              # test HTTP client và logic UI
|-- worksheets/                # phiếu đánh giá Lab07
|   |-- usability_checklist.md
|   `-- user_test_observations.md
|-- .env.example
|-- pyproject.toml
`-- requirements.txt
```
