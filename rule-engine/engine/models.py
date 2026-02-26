from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Condition:
    """شرط یک قانون"""
    field: str
    op: str        # عملگر مثل '==', '>', '>='
    value: Any


@dataclass
class Action:
    """اقدامی که در صورت تطبیق قانون انجام میشه"""
    action: str
    value: Any


@dataclass
class Rule:
    """یک قانون کامل"""
    id: str
    description: str
    priority: int
    when: List[Condition]
    then: Action


@dataclass
class Context:
    """اطلاعات سفارش و کاربر (ورودی)"""
    user_type: str
    cart_total: int  # مقدار پول به صورت integer (مثلاً به تومان)
    items_count: int
    city: str
    payment_method: str
    has_previous_chargeback: bool
    gateway: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Context":
        # تبدیل و تایپ‌کست امن ورودی‌ها
        return cls(
            user_type=data["user_type"],
            cart_total=int(data.get("cart_total", 0)),
            items_count=int(data.get("items_count", 0)),
            city=data.get("city", ""),
            payment_method=data.get("payment_method", ""),
            has_previous_chargeback=bool(data.get("has_previous_chargeback", False)),
            gateway=data.get("gateway", "")
        )


@dataclass
class EngineResult:
    """خروجی استاندارد موتور قوانین"""
    applied_rules: List[str] = field(default_factory=list)
    discount_percent: int = 0
    discount_amount: int = 0
    free_shipping: bool = False
    payment: Dict[str, Any] = field(default_factory=lambda: {
        "is_blocked": False,
        "blocked_reason": None,
        "blocked_methods": []
    })
    final_price: int = 0
    logs: List[str] = field(default_factory=list)
