# engine/models.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Condition:
    """شرط یک قانون"""
    field: str
    op: str        # عملگر مثل ==, >, >=
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
    cart_total: float
    items_count: int
    city: str
    payment_method: str
    has_previous_chargeback: bool
    gateway: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            user_type=data["user_type"],
            cart_total=data["cart_total"],
            items_count=data["items_count"],
            city=data["city"],
            payment_method=data["payment_method"],
            has_previous_chargeback=data["has_previous_chargeback"],
            gateway=data["gateway"]
        )