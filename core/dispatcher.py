"""
Dispatcher: nhận (category, target) từ client, tìm các connector phù hợp
trong registry, và gọi chúng SONG SONG (vì đa số là network call, chờ
tuần tự sẽ rất chậm).
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

from core.base_connector import BaseConnector, ConnectorResult
from core.registry import ConnectorRegistry


class Dispatcher:
    def __init__(self, registry: ConnectorRegistry, cache=None):
        self.registry = registry
        self.cache = cache  # có thể là None nếu cache bị tắt

    def run(self, category: str, target: str) -> list[ConnectorResult]:
        candidates = self.registry.get_by_category(category)
        connectors = [c for c in candidates if c.validate_target(target)]

        if not connectors:
            return []

        results: list[ConnectorResult] = []
        with ThreadPoolExecutor(max_workers=max(len(connectors), 1)) as pool:
            future_map = {
                pool.submit(self._run_one, connector, target): connector
                for connector in connectors
            }
            for future in as_completed(future_map):
                results.append(future.result())

        # Sắp xếp lại theo thứ tự connector trong registry cho ổn định giao diện
        order = {c.name: i for i, c in enumerate(connectors)}
        results.sort(key=lambda r: order.get(r.connector_name, 999))
        return results

    def _run_one(self, connector: BaseConnector, target: str) -> ConnectorResult:
        if self.cache:
            cached = self.cache.get(connector.name, target)
            if cached is not None:
                return cached

        try:
            result = connector.fetch(target)
        except Exception as exc:  # an toàn tuyệt đối: không để 1 connector sập cả hệ thống
            result = connector.error_result(f"Lỗi không mong muốn: {exc}")

        if self.cache and result.status == "ok":
            self.cache.set(connector.name, target, result)

        return result
