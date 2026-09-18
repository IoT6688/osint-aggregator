"""
Đây là "hợp đồng" (interface) mà MỌI connector trong hệ thống phải tuân theo.
Nếu bạn muốn viết connector mới, bạn kế thừa BaseConnector và implement
2 phương thức: validate_target() và fetch().
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class TargetType(str, Enum):
    """Các loại 'mục tiêu' mà một connector có thể chấp nhận."""
    DOMAIN = "domain"
    IP = "ip"
    USERNAME = "username"
    EMAIL = "email"


@dataclass
class ConnectorResult:
    """
    Kết quả trả về CHUẨN HÓA của một connector, dù connector đó
    gọi WHOIS, DNS, hay bất kỳ API nào khác.

    Lưu ý quan trọng: object này KHÔNG có trường "kết luận" hay
    "mức độ rủi ro" — chỉ có dữ liệu thô (raw_data). Việc phân tích
    thuộc về người dùng, không phải hệ thống.
    """
    connector_name: str                 # id duy nhất, vd "domain_whois"
    display_name: str                   # tên hiển thị, vd "WHOIS"
    source: str                         # nguồn dữ liệu, vd "RDAP / IANA"
    status: str                         # "ok" | "error" | "no_data"
    raw_data: Optional[dict] = None
    error_message: Optional[str] = None
    fetched_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    from_cache: bool = False

    def to_dict(self) -> dict:
        return {
            "connector_name": self.connector_name,
            "display_name": self.display_name,
            "source": self.source,
            "status": self.status,
            "raw_data": self.raw_data,
            "error_message": self.error_message,
            "fetched_at": self.fetched_at,
            "from_cache": self.from_cache,
        }


class BaseConnector(ABC):
    """Lớp cha bắt buộc cho mọi connector."""

    name: str                                   # id duy nhất (dùng làm key cache)
    category: str                                # nhóm hiển thị trên UI, vd "domain"
    display_name: str                            # tên hiển thị cho người dùng
    accepted_target_types: list[TargetType]      # loại target connector này xử lý
    source: str = "unknown"                      # mô tả nguồn dữ liệu

    @abstractmethod
    def validate_target(self, target: str) -> bool:
        """Trả True nếu `target` đúng định dạng connector này xử lý được."""
        raise NotImplementedError

    @abstractmethod
    def fetch(self, target: str) -> ConnectorResult:
        """
        Gọi nguồn dữ liệu thật và trả về ConnectorResult.

        QUAN TRỌNG: không được để exception thoát ra ngoài hàm này.
        Nếu có lỗi (timeout, API die, v.v...), hãy bắt lại bằng try/except
        và trả về ConnectorResult với status="error".
        """
        raise NotImplementedError

    def error_result(self, message: str) -> ConnectorResult:
        """Hàm tiện ích: tạo nhanh một ConnectorResult báo lỗi."""
        return ConnectorResult(
            connector_name=self.name,
            display_name=self.display_name,
            source=self.source,
            status="error",
            error_message=message,
        )
