"""
Entrypoint của ứng dụng. Chạy bằng lệnh:  python app.py
Sau đó mở trình duyệt vào:  http://127.0.0.1:5000
"""

from flask import Flask, jsonify, render_template, request

import config
from core.registry import registry
from core.dispatcher import Dispatcher
from core.cache import SQLiteCache

# Import package connectors để trigger việc đăng ký (@registry.register).
# Dòng import này BẮT BUỘC phải có, nếu không registry sẽ rỗng.
import connectors  # noqa: F401

app = Flask(__name__)

cache = SQLiteCache() if config.CACHE_ENABLED else None
dispatcher = Dispatcher(registry=registry, cache=cache)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/categories")
def api_categories():
    """Trả danh sách category + connector con, để frontend build dropdown động."""
    return jsonify(registry.list_categories())


@app.route("/api/search", methods=["POST"])
def api_search():
    """
    Body JSON kỳ vọng: {"category": "domain", "target": "example.com"}
    Trả về danh sách kết quả thô từ mỗi connector phù hợp.
    """
    payload = request.get_json(silent=True) or {}
    category = (payload.get("category") or "").strip()
    target = (payload.get("target") or "").strip()

    if not category or not target:
        return jsonify({"error": "Thiếu 'category' hoặc 'target'."}), 400

    if category not in {c["category"] for c in registry.list_categories()}:
        return jsonify({"error": f"Category '{category}' không tồn tại."}), 400

    results = dispatcher.run(category=category, target=target)

    if not results:
        return jsonify(
            {
                "target": target,
                "category": category,
                "results": [],
                "message": "Không có connector nào chấp nhận định dạng target này.",
            }
        )

    return jsonify(
        {
            "target": target,
            "category": category,
            "results": [r.to_dict() for r in results],
        }
    )


if __name__ == "__main__":
    # debug=True chỉ dùng khi phát triển. Khi triển khai thật, tắt debug đi.
    app.run(host="127.0.0.1", port=5000, debug=True)
