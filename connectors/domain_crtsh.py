import re

import requests

from core.base_connector import (
    BaseConnector,
    ConnectorResult,
    TargetType,
)
from core.registry import registry


DOMAIN_REGEX = (
    r"^(?=.{1,253}$)(?!-)"
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
        if not self.validate_target(target):
            return self.error_result(
                "Target không phải domain hợp lệ."
            )

        try:
            response = requests.get(
                self.API_URL,
                params={
                    "q": target.strip(),
                    "output": "json",
                },
                timeout=15,
            )

            response.raise_for_status()

            # crt.sh đôi khi có thể trả response rỗng
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

            try:
                certificates = response.json()
            except ValueError:
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

            subdomains = set()

            for certificate in certificates:
                name_value = certificate.get("name_value", "")

                for name in name_value.splitlines():
                    name = name.strip().lower()

                    if name:
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

        except requests.exceptions.Timeout:
            return self.error_result(
                "crt.sh request bị timeout."
            )

        except requests.exceptions.RequestException as error:
            return self.error_result(
                f"crt.sh request error: {error}"
            )

        except Exception as error:
            return self.error_result(
                f"Lỗi không xác định: {error}"
            )