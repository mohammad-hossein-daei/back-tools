# engine/actions.py

from typing import Dict, Any, Callable, Optional

# نوع تابع action: تابعی که state و مقدار را می‌گیرد و رشتهٔ لاگ (اختیاری) برمی‌گرداند
ActionFn = Callable[[Dict[str, Any], Any], Optional[str]]


def _ensure_payment_structure(state: Dict[str, Any]) -> None:
    """اطمینان از اینکه کلید payment با ساختار مورد انتظار وجود دارد."""
    if "payment" not in state or not isinstance(state["payment"], dict):
        state["payment"] = {
            "is_blocked": False,
            "blocked_reason": None,
            "blocked_methods": [],
        }
    else:
        # اطمینان از وجود فیلدهای داخلی
        state["payment"].setdefault("is_blocked", False)
        state["payment"].setdefault("blocked_reason", None)
        state["payment"].setdefault("blocked_methods", [])


def apply_discount_percent(state: Dict[str, Any], value: Any) -> str:
    """
    اعمال درصد تخفیف.
    رفتار: مقدار جدید را به int تبدیل می‌کند و اگر بزرگ‌تر از مقدار فعلی باشد جایگزین می‌کند.
    (این تصمیم برای جلوگیری از stack شدن غیرمنتظره تخفیف‌ها گرفته شده؛ اگر خواستی می‌توانیم به رفتار stack جمعی تغییر دهیم.)
    """
    try:
        percent = int(value)
    except Exception:
        raise ValueError(f"Invalid discount percent value: {value}")

    prev = int(state.get("discount_percent", 0))
    if percent > prev:
        state["discount_percent"] = percent

    state.setdefault("discount_amount", 0)
    return f"apply_discount_percent={state['discount_percent']}"


def free_shipping(state: Dict[str, Any], value: Any) -> str:
    """فعال/غیرفعال کردن ارسال رایگان (bool expected)."""
    # پذیرش رشته‌هایی مثل "true"/"false" نیز
    val = bool(value)
    state["free_shipping"] = val
    return f"free_shipping={state['free_shipping']}"


def block_payment(state: Dict[str, Any], reason: Any) -> str:
    """مسدود کردن کامل پرداخت با دلیل (reason: str)."""
    _ensure_payment_structure(state)
    reason_str = None if reason is None else str(reason)
    state["payment"]["is_blocked"] = True
    state["payment"]["blocked_reason"] = reason_str
    return f"block_payment={reason_str}"


def block_payment_method(state: Dict[str, Any], method: Any) -> str:
    """مسدود کردن یک روش پرداخت مشخص (مثل 'cod')."""
    _ensure_payment_structure(state)
    method_str = str(method)
    blocked = state["payment"].get("blocked_methods", [])
    if method_str not in blocked:
        blocked.append(method_str)
        state["payment"]["blocked_methods"] = blocked
        return f"block_payment_method={method_str}"
    return f"block_payment_method=already_blocked:{method_str}"


# مپ کردن نام action به تابع مربوطه
ACTION_MAP: Dict[str, ActionFn] = {
    "apply_discount_percent": apply_discount_percent,
    "free_shipping": free_shipping,
    "block_payment": block_payment,
    "block_payment_method": block_payment_method,
}


def execute_action(action_name: str, state: Dict[str, Any], value: Any) -> str:
    """
    فراخوانی ایمن یک اکشن از ACTION_MAP.
    - اگر اکشن وجود نداشت، ValueError پرتاب می‌شود.
    - اکشن موظف است یک عبارت لاگ (string) بازگرداند که در logs قرار می‌گیرد.
    """
    fn = ACTION_MAP.get(action_name)
    if fn is None:
        raise ValueError(f"Unknown action: {action_name}")

    log = fn(state, value)
    # اگر اکشن لاگ نداد، باز هم یک پیغام عمومی لاگ می‌سازیم
    return log if isinstance(log, str) else f"{action_name} executed"