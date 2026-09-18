"""
Connector DNS: tra cứu các bản ghi DNS công khai của domain
(A, AAAA, MX, NS, TXT).

Dùng thư viện `dnspython` (import tên là `dns`).
Cài đặt: pip install dnspython
"""

import re

from core.base_connector import BaseConnector, ConnectorResult, TargetType
from core.registry import registry

DOMAIN_REGEX = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))+$"
)

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT"]


@registry.register
class DomainDnsConnector(BaseConnector):
    name = "domain_dns"
    category = "domain"
    display_name = "DNS Records"
    source = "DNS resolver công khai"
    accepted_target_types = [TargetType.DOMAIN]

    def validate_target(self, target: str) -> bool:
        return bool(DOMAIN_REGEX.match(target.strip()))

    def fetch(self, target: str) -> ConnectorResult:
        try:
            import dns.resolver
        except ImportError:
            return self.error_result(
                "Thiếu thư viện 'dnspython'. Chạy: pip install dnspython"
            )

        domain = target.strip()
        raw: dict[str, list[str]] = {}
        found_anything = False

        for record_type in RECORD_TYPES:
            try:
                answers = dns.resolver.resolve(domain, record_type, lifetime=5)
                raw[record_type] = [str(rdata) for rdata in answers]
                found_anything = True
            except dns.resolver.NoAnswer:
                raw[record_type] = []
            except dns.resolver.NXDOMAIN:
                return self.error_result("Domain không tồn tại (NXDOMAIN).")
            except Exception as exc:
                raw[record_type] = []
                raw.setdefault("_errors", []).append(f"{record_type}: {exc}")

        if not found_anything:
            return ConnectorResult(
                connector_name=self.name,
                display_name=self.display_name,
                source=self.source,
                status="no_data",
                raw_data=raw,
            )

        return ConnectorResult(
            connector_name=self.name,
            display_name=self.display_name,
            source=self.source,
            status="ok",
            raw_data=raw,
        )
