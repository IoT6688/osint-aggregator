import re
import requests

from core.base_connector import (
    BaseConnector,
    ConnectorResult,
    TargetType,
)
from core.registry import registry


DOMAIN_REGEX = (
    r"^(?=.{1,253}$)"
    r"(?!-)"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}$"
)


@registry.register
class CrtShConnector(BaseConnector):
    name = "domain_crtsh"
    category = "domain"
    display_name = "Certificate Transparency (crt.sh)"
    accepted_target_types = [TargetType.DOMAIN]
    source = "crt.sh / Certificate Transparency"

    API_URL = "https://crt.sh/"

    def validate_target(self, target: str) -> bool:
        return bool(re.match(DOMAIN_REGEX, target.strip()))

    def fetch(self, target: str) -> ConnectorResult:
        target = target.strip()

        # Kiểm tra domain
        if not self.validate_target(target):
            return self.error_result(
                "Target không phải domain hợp lệ."
            )

        try:
            headers = {
                "User-Agent": "OSINT-Aggregator/1.0"
            }

            response = requests.get(
                self.API_URL,
                params={
                    "q": target,
                    "output": "json",
                },
                headers=headers,
                timeout=(5, 30),
            )

            response.raise_for_status()

            # Không có dữ liệu
            if not response.text.strip():
                return ConnectorResult(
                    connector_name=self.name,
                    display_name=self.display_name,
                    source=self.source,
                    status="no_data",
                    raw_data={
                        "target": target,
                        "subdomains": [],
                        "total_found": 0,
                    },
                )

            # Parse JSON
            try:
                certificates = response.json()
            except ValueError:
                return self.error_result(
                    "crt.sh trả về dữ liệu không phải JSON."
                )

            subdomains = set()

            for certificate in certificates:
                name_value = certificate.get("name_value", "")

                for name in name_value.splitlines():
                    name = name.strip().lower()

                    if not name:
                        continue

                    # Bỏ wildcard
                    if name.startswith("*."):
                        name = name[2:]

                    # Chỉ giữ tên thuộc domain đang kiểm tra
                    if (
                        name == target
                        or name.endswith("." + target)
                    ):
                        subdomains.add(name)

            subdomains = sorted(subdomains)

            return ConnectorResult(
                connector_name=self.name,
                display_name=self.display_name,
                source=self.source,
                status="ok" if subdomains else "no_data",
                raw_data={
                    "target": target,
                    "subdomains": subdomains,
                    "total_found": len(subdomains),
                },
            )

        except requests.exceptions.ConnectTimeout:
            return self.error_result(
                "Không thể kết nối tới crt.sh trong thời gian cho phép."
            )

        except requests.exceptions.ReadTimeout:
            return self.error_result(
                "crt.sh phản hồi quá chậm (read timeout)."
            )

        except requests.exceptions.Timeout:
            return self.error_result(
                "crt.sh request bị timeout."
            )

        except requests.exceptions.HTTPError as error:
            return self.error_result(
                f"crt.sh HTTP error: {error}"
            )

        except requests.exceptions.RequestException as error:
            return self.error_result(
                f"crt.sh request error: {error}"
            )

        except Exception as error:
            return self.error_result(
                f"Lỗi không xác định: {error}"
            )
