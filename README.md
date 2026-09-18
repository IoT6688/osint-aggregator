# OSINT Aggregator — Hướng dẫn từ con số 0

Tài liệu này giả định bạn **chưa từng cài Python, chưa từng chạy Flask, chưa từng dùng dòng lệnh**. Làm theo đúng thứ tự, đừng bỏ bước.

---

## Phần 1: Cài Python

### Kiểm tra máy đã có Python chưa

Mở **Terminal** (macOS/Linux) hoặc **PowerShell** (Windows — gõ "PowerShell" vào Start Menu), gõ:

```
python3 --version
```

Trên Windows nếu lệnh trên báo lỗi, thử:
```
python --version
```

Nếu bạn thấy hiện ra ví dụ `Python 3.11.4` → bạn đã có Python, **bỏ qua bước cài đặt**, sang Phần 2.

Nếu báo lỗi "command not found" / "không nhận diện được lệnh":

- **Windows**: vào https://www.python.org/downloads/ , tải bản mới nhất, khi cài **nhớ tick vào ô "Add Python to PATH"** ở màn hình đầu tiên của trình cài đặt — đây là bước rất nhiều người bỏ sót gây lỗi sau này.
- **macOS**: vào https://www.python.org/downloads/macos/ , tải bản `.pkg`, cài như app bình thường.
- **Linux**: `sudo apt install python3 python3-venv python3-pip` (Ubuntu/Debian) hoặc lệnh tương đương của bản phân phối bạn dùng.

Cài xong, **đóng và mở lại Terminal**, gõ lại `python3 --version` để xác nhận.

---

## Phần 2: Giải nén / đặt project vào một thư mục

Tải toàn bộ project này về máy, đặt vào một thư mục dễ nhớ, ví dụ:
- Windows: `C:\Users\<ten_ban>\osint-aggregator`
- macOS/Linux: `~/osint-aggregator`

Mở Terminal, di chuyển vào thư mục đó bằng lệnh `cd`:

```
cd đường/dẫn/tới/osint-aggregator
```

Gõ `ls` (macOS/Linux) hoặc `dir` (Windows) để kiểm tra — bạn phải thấy các file như `app.py`, `requirements.txt`, thư mục `connectors/`...

---

## Phần 3: Tạo "môi trường ảo" (virtual environment)

Đây là một thư mục riêng để cài thư viện Python cho **riêng project này**, không ảnh hưởng tới máy tính của bạn. Gần như bắt buộc nên làm.

**Windows (PowerShell):**
```
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

Sau khi chạy lệnh `activate`, bạn sẽ thấy chữ `(venv)` xuất hiện ở đầu dòng lệnh — nghĩa là đã bật thành công. **Mỗi lần mở Terminal mới để làm việc với project, bạn phải chạy lại lệnh `activate` này.**

> Nếu Windows báo lỗi "không thể chạy script" (execution policy), mở PowerShell với quyền Administrator, gõ:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
> rồi thử lại lệnh `activate`.

---

## Phần 4: Cài thư viện cần thiết

Khi đã thấy `(venv)` ở đầu dòng lệnh, gõ:

```
pip install -r requirements.txt
```

Lệnh này đọc file `requirements.txt` và tự cài 4 thư viện: `flask`, `python-whois`, `dnspython`, `requests`. Quá trình này cần internet, đợi vài chục giây tới vài phút.

---

## Phần 5: Chạy thử

```
python app.py
```

Nếu thành công bạn sẽ thấy dòng:
```
* Running on http://127.0.0.1:5000
```

Mở trình duyệt, truy cập: **http://127.0.0.1:5000**

Bạn sẽ thấy giao diện có ô chọn "Loại thông tin" và ô nhập "Mục tiêu". Thử:
- Chọn `domain`, nhập `example.com` → xem WHOIS + DNS records
- Chọn `ip`, nhập `8.8.8.8` → xem vị trí địa lý ước tính

Để dừng server: quay lại Terminal, nhấn `Ctrl + C`.

---

## Phần 6: Hiểu project (đọc theo thứ tự này)

Muốn hiểu code, đừng đọc `app.py` đầu tiên — hãy đọc theo trình tự sau, vì hệ thống được thiết kế theo lớp (layer):

1. **`core/base_connector.py`** — định nghĩa "hợp đồng": mọi connector phải trông như thế nào. Đọc file này trước tiên để hiểu khung sườn chung.
2. **`connectors/ip_geolocation.py`** — connector đơn giản nhất, đọc để thấy hợp đồng ở bước 1 được áp dụng thực tế ra sao.
3. **`core/registry.py`** — nơi các connector "ghi danh" để hệ thống biết chúng tồn tại.
4. **`core/dispatcher.py`** — nơi quyết định gọi connector nào, gọi song song ra sao.
5. **`app.py`** — chỉ còn việc nối các endpoint Flask với dispatcher, khá ngắn gọn.
6. **`core/cache.py`** — lớp cache SQLite, đọc sau cùng vì nó là phần tùy chọn (tắt được).

## Cấu trúc thư mục

```
osint-aggregator/
├── app.py                  # Điểm khởi động Flask, định nghĩa API endpoints
├── config.py                # Các thiết lập (bật/tắt cache, timeout...)
├── requirements.txt         # Danh sách thư viện cần cài
├── core/
│   ├── base_connector.py    # "Hợp đồng" mọi connector phải tuân theo
│   ├── registry.py          # Nơi đăng ký + tra cứu connector
│   ├── dispatcher.py        # Điều phối gọi connector song song
│   └── cache.py             # Cache SQLite tùy chọn
├── connectors/
│   ├── domain_whois.py      # Tra WHOIS domain
│   ├── domain_dns.py        # Tra bản ghi DNS
│   └── ip_geolocation.py    # Tra vị trí địa lý IP
├── templates/index.html     # Giao diện HTML
└── static/
    ├── style.css
    └── app.js                # Gọi API, render kết quả
```

---

## Phần 7: Thêm connector mới (khi bạn đã quen)

Ví dụ bạn muốn thêm connector kiểm tra username trên các mạng xã hội:

1. Tạo file mới: `connectors/username_social.py`
2. Copy cấu trúc từ `connectors/ip_geolocation.py` làm mẫu (đơn giản nhất)
3. Đổi `name`, `category = "username"`, `accepted_target_types = [TargetType.USERNAME]`
4. Viết logic thật trong `fetch()` — nhớ bọc try/except, không để lỗi thoát ra ngoài
5. Mở `connectors/__init__.py`, thêm dòng: `from . import username_social`
6. Chạy lại `python app.py` — dropdown trên giao diện sẽ **tự động** có thêm mục "username", không cần sửa `app.js` hay `index.html`

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `command not found: python3` | Chưa cài Python hoặc chưa thêm vào PATH | Xem lại Phần 1 |
| `ModuleNotFoundError: No module named 'flask'` | Chưa activate venv hoặc chưa `pip install` | Kiểm tra có `(venv)` ở đầu dòng lệnh chưa, chạy lại `pip install -r requirements.txt` |
| `Address already in use` khi chạy `python app.py` | Đã có 1 server khác đang chạy ở cổng 5000 | Đóng terminal cũ đang chạy server, hoặc đổi cổng trong `app.run(port=5001)` |
| Trang trắng / không tải được CSS | Thường do chưa refresh cache trình duyệt | Nhấn `Ctrl + Shift + R` để hard refresh |
| Kết quả WHOIS/DNS báo lỗi kết nối | Domain không tồn tại, hoặc mạng của bạn chặn cổng WHOIS (port 43) / DNS | Thử domain khác (`google.com`) để xác nhận connector hoạt động đúng |

---

## Phần 8: Đưa lên mạng công khai (deploy)

Sau khi đã đẩy code lên GitHub, bạn có thể để **Render** (miễn phí, không cần thẻ tín dụng) tự lấy code từ GitHub và chạy thành một website thật, có link công khai.

1. Vào **render.com**, đăng ký/đăng nhập bằng tài khoản GitHub của bạn.
2. Bấm **New +** → **Web Service**.
3. Chọn repository `osint-aggregator` bạn vừa đẩy lên GitHub, bấm **Connect**.
4. Điền form cấu hình:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: chọn **Free**
5. Bấm **Create Web Service**. Đợi vài phút để Render build và chạy — xong bạn sẽ có 1 link dạng `https://osint-aggregator-xxxx.onrender.com`, ai cũng truy cập được.

**Từ giờ về sau, mỗi khi bạn `git push` code mới lên GitHub, Render tự động build và cập nhật lại website** — không cần làm lại các bước trên. Đây chính là lý do nên đẩy lên GitHub trước: code trên GitHub trở thành "nguồn sự thật" mà Render luôn đồng bộ theo.

Vài điều cần biết về gói miễn phí của Render:
- Nếu không có ai truy cập trong 15 phút, server sẽ "ngủ" để tiết kiệm tài nguyên. Lượt truy cập đầu tiên sau đó sẽ mất khoảng 30–60 giây để "thức dậy" — đây là bình thường, không phải lỗi.
- File cache `osint_cache.db` sẽ bị xóa mỗi khi server khởi động lại (restart/deploy lại) — không sao cả, vì đây chỉ là cache tạm, không phải dữ liệu quan trọng cần giữ.
- Cổng WHOIS (43) và DNS mà các connector dùng không bị Render chặn, chỉ có cổng SMTP (25/465/587) bị chặn ở gói free — không ảnh hưởng tới project này.

## Lưu ý khi sử dụng

Công cụ này chỉ nên dùng để tra cứu **dữ liệu công khai, hợp pháp** (WHOIS, DNS, geo-IP đều là dữ liệu công khai theo thiết kế của giao thức Internet). Không dùng để truy cập trái phép hệ thống của người khác, không dùng để quấy rối hay theo dõi cá nhân mà không có sự đồng ý/căn cứ hợp pháp.
