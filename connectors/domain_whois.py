"""
Connector WHOIS: tra cứu thông tin đăng ký của một domain
(registrar, ngày tạo, ngày hết hạn, name servers...).

Dùng thư viện `python-whois` (import tên là `whois`).
Cài đặt: pip install python-whois
"""

import re

from core.base_connector import BaseConnector, ConnectorResult, TargetType
from core.registry import registry

DOMAIN_REGEX = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))+$"
)


@registry.register
class DomainWhoisConnector(BaseConnector):
    name = "domain_whois"
    category = "domain"
    display_name = "WHOIS"
    source = "WHOIS (qua thư viện python-whois)"
    accepted_target_types = [TargetType.DOMAIN]

    def validate_target(self, target: str) -> bool:
        return bool(DOMAIN_REGEX.match(target.strip()))

    def fetch(self, target: str) -> ConnectorResult:
        try:
            import whois  # import trong hàm để lỗi thiếu thư viện không làm sập cả app
        except ImportError:
            return self.error_result(
                "Thiếu thư viện 'python-whois'. Chạy: pip install python-whois"
            )

        try:
            data = whois.whois(target.strip())
        except Exception as exc:
            return self.error_result(f"Không truy vấn được WHOIS: {exc}")

        if not data or not getattr(data, "domain_name", None):
            return ConnectorResult(
                connector_name=self.name,
                display_name=self.display_name,
                source=self.source,
                status="no_data",
                raw_data=None,
            )

        raw = {
            "domain_name": _stringify(data.get("domain_name")),
            "registrar": data.get("registrar"),
            "creation_date": _stringify(data.get("creation_date")),
            "expiration_date": _stringify(data.get("expiration_date")),
            "updated_date": _stringify(data.get("updated_date")),
            "name_servers": _stringify(data.get("name_servers")),
            "status": _stringify(data.get("status")),
            "emails": _stringify(data.get("emails")),
            "org": data.get("org"),
            "country": data.get("country"),
        }

        return ConnectorResult(
            connector_name=self.name,
            display_name=self.display_name,
            source=self.source,
            status="ok",
            raw_data=raw,
        )


def _stringify(value):
    """WHOIS trả về đủ kiểu dữ liệu (datetime, list, str...) -> ép hết về str/list[str]
    để có thể JSON-serialize được an toàn."""
    if value is None:
        return None
    if isinstance(value, list):
        return [str(v) for v in value]
    return str(value)
