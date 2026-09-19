"""
Import tất cả các module connector tại đây để decorator @registry.register
được thực thi (Python chỉ chạy code của 1 module khi module đó được import).

Khi bạn thêm connector mới, chỉ cần thêm 1 dòng import ở đây.
Không cần sửa gì khác trong app.py, dispatcher.py, registry.py.
"""

from . import domain_whois     # noqa: F401
from . import domain_dns       # noqa: F401
from . import ip_geolocation   # noqa: F401
from . import domain_crtsh
from . import phone_metadata
