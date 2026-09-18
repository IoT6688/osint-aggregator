"""
ConnectorRegistry: nơi "ghi danh" tất cả các connector đang có trong hệ thống.

Đây là trái tim của khả năng mở rộng: connector tự đăng ký vào registry
bằng decorator @registry.register, còn phần còn lại của hệ thống
(dispatcher, API /api/categories) chỉ cần hỏi registry, không cần biết
trước có bao nhiêu connector hay chúng tên gì.
"""

from core.base_connector import BaseConnector


class ConnectorRegistry:
    def __init__(self):
        self._by_name: dict[str, BaseConnector] = {}
        self._by_category: dict[str, list[BaseConnector]] = {}

    def register(self, connector_cls):
        """
        Dùng như decorator ngay phía trên định nghĩa class connector:

            @registry.register
            class MyConnector(BaseConnector):
                ...

        Sau dòng này, connector sẽ tự động được hệ thống nhận diện.
        """
        instance = connector_cls()
        if instance.name in self._by_name:
            raise ValueError(
                f"Connector name '{instance.name}' đã tồn tại. "
                "Mỗi connector cần một `name` duy nhất."
            )
        self._by_name[instance.name] = instance
        self._by_category.setdefault(instance.category, []).append(instance)
        return connector_cls

    def get_by_category(self, category: str) -> list[BaseConnector]:
        return self._by_category.get(category, [])

    def get_by_name(self, name: str) -> BaseConnector | None:
        return self._by_name.get(name)

    def list_categories(self) -> list[dict]:
        """Trả danh sách category kèm các connector con -> dùng cho /api/categories."""
        return [
            {
                "category": category,
                "connectors": [
                    {"name": c.name, "display_name": c.display_name}
                    for c in connectors
                ],
            }
            for category, connectors in self._by_category.items()
        ]


# Instance duy nhất (singleton) dùng chung cho toàn bộ ứng dụng.
registry = ConnectorRegistry()
