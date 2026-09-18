"""
Connector IP Geolocation: tra cứu vị trí địa lý ước tính, ISP, tổ chức
sở hữu của một địa chỉ IP.

Dùng API miễn phí ip-api.com -- KHÔNG cần API key, nhưng có giới hạn
~45 request/phút cho bản miễn phí. Đây là lý do lớp cache ở core/cache.py
rất hữu ích cho connector này.
"""

import re

import requests

from core.base_connector import BaseConnector, ConnectorResult, TargetType
from core.registry import registry
import config

IPV4_REGEX = re.compile(
    r"^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$"
)

API_URL = "http://ip-api.com/json/{ip}"
FIELDS = "status,message,country,regionName,city,zip,lat,lon,isp,org,as,query"


@registry.register
class IPGeolocationConnector(BaseConnector):
    name = "ip_geolocation"
    category = "ip"
    display_name = "IP Geolocation"
    source = "ip-api.com (miễn phí)"
    accepted_target_types = [TargetType.IP]

    def validate_target(self, target: str) -> bool:
        # Bản demo chỉ hỗ trợ IPv4 cho đơn giản.
        return bool(IPV4_REGEX.match(target.strip()))

    def fetch(self, target: str) -> ConnectorResult:
        ip = target.strip()
        try:
            response = requests.get(
                API_URL.format(ip=ip),
                params={"fields": FIELDS},
                timeout=config.CONNECTOR_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            return self.error_result("Timeout khi gọi ip-api.com.")
        except requests.exceptions.RequestException as exc:
            return self.error_result(f"Lỗi kết nối tới ip-api.com: {exc}")
        except ValueError:
            return self.error_result("ip-api.com trả về dữ liệu không phải JSON hợp lệ.")

        if data.get("status") != "success":
            return ConnectorResult(
                connector_name=self.name,
                display_name=self.display_name,
                source=self.source,
                status="no_data",
                raw_data=None,
                error_message=data.get("message", "Không tìm thấy dữ liệu."),
            )

        raw = {
            "ip": data.get("query"),
            "country": data.get("country"),
            "region": data.get("regionName"),
            "city": data.get("city"),
            "zip": data.get("zip"),
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
            "isp": data.get("isp"),
            "org": data.get("org"),
            "as": data.get("as"),
        }

        return ConnectorResult(
            connector_name=self.name,
            display_name=self.display_name,
            source=self.source,
            status="ok",
            raw_data=raw,
        )
