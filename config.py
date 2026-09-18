"""
Cấu hình trung tâm của ứng dụng.
Người mới bắt đầu: bạn có thể chỉnh các giá trị dưới đây mà không cần
đụng vào bất kỳ file nào khác.
"""

# Bật/tắt cache SQLite. Nếu True, kết quả các connector sẽ được lưu lại
# để lần tra cứu sau (cùng target) không phải gọi API lần nữa.
CACHE_ENABLED = True

# Thời gian (giây) một kết quả cache còn "hợp lệ" trước khi bị coi là cũ
# và cần gọi lại API. 3600 = 1 giờ.
CACHE_TTL_SECONDS = 3600

# Đường dẫn file database SQLite (sẽ tự động được tạo nếu chưa có).
CACHE_DB_PATH = "osint_cache.db"

# Thời gian tối đa (giây) chờ một connector trả kết quả trước khi coi là timeout.
CONNECTOR_TIMEOUT_SECONDS = 8

# Token cho ipinfo.io (KHÔNG bắt buộc). Để trống vẫn chạy được vì
# connector IP geolocation mặc định dùng ip-api.com (miễn phí, không cần key).
IPINFO_TOKEN = ""
