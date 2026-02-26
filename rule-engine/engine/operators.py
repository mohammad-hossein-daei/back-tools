from typing import Any


def _to_number(value: Any) -> float:
    """سعی می‌کنه مقدار رو به عدد تبدیل کنه (حذف جداکننده‌های هزارگانه). اگر نشد، ValueError پرتاب می‌کنه."""
    if isinstance(value, (int, float)):
        return float(value)

    if value is None:
        raise ValueError("None is not a number")

    s = str(value).strip()
    # حذف جداکننده‌های هزارگانه مرسوم
    s = s.replace(",", "").replace("_", "")
    if s == "":
        raise ValueError("empty string")

    # حالا تبدیل
    if "." in s:
        return float(s)
    return float(int(s))


def _to_bool(value: Any) -> bool:
    """تلاش برای تبدیل مقدار به بولین از رشته‌ها/اعداد رایج."""
    if isinstance(value, bool):
        return value

    if value is None:
        raise ValueError("None is not a bool")

    s = str(value).strip().lower()
    if s in {"true", "1", "yes", "y", "t"}:
        return True
    if s in {"false", "0", "no", "n", "f"}:
        return False

    raise ValueError(f"Cannot convert to bool: {value}")


def equals(a: Any, b: Any) -> bool:
    """مقایسه مقاوم در برابر نوع: ابتدا equality مستقیم، سپس تلاش برای تبدیل عددی، سپس بولی، سپس مقایسه رشته‌ای غیر حساس به حروف."""
    try:
        if a == b:
            return True
    except Exception:
        pass

    # numeric compare
    try:
        return _to_number(a) == _to_number(b)
    except Exception:
        pass

    # bool compare
    try:
        return _to_bool(a) == _to_bool(b)
    except Exception:
        pass

    # fallback: compare lowercase strings
    try:
        return str(a).strip().lower() == str(b).strip().lower()
    except Exception:
        return False


def not_equals(a: Any, b: Any) -> bool:
    return not equals(a, b)


def greater_than(a: Any, b: Any) -> bool:
    """سعی می‌کنه مقادیر رو به عدد تبدیل کنه و مقایسه کنه. در غیر این صورت False برمی‌گردونه."""
    try:
        return _to_number(a) > _to_number(b)
    except Exception:
        return False


def greater_than_or_equal(a: Any, b: Any) -> bool:
    try:
        return _to_number(a) >= _to_number(b)
    except Exception:
        return False


def less_than(a: Any, b: Any) -> bool:
    try:
        return _to_number(a) < _to_number(b)
    except Exception:
        return False


def less_than_or_equal(a: Any, b: Any) -> bool:
    try:
        return _to_number(a) <= _to_number(b)
    except Exception:
        return False


def contains(a: Any, b: Any) -> bool:
    """چک می‌کنه آیا b داخل a وجود داره.
    - اگر a لیست/تاپل/ست باشه => membership
    - اگر a رشته باشه => substring (حساس به حروف نیست)
    - در غیر این صورت False
    """
    try:
        if a is None:
            return False

        # membership برای iterableها
        if isinstance(a, (list, tuple, set)):
            return b in a

        # substring برای رشته
        if isinstance(a, str):
            return str(b).lower() in a.lower()

        return False
    except Exception:
        return False


# دیکشنری عملگرها برای دسترسی آسان
OPERATORS = {
    "==": equals,
    "!=": not_equals,
    ">": greater_than,
    ">=": greater_than_or_equal,
    "<": less_than,
    "<=": less_than_or_equal,
    "in": contains,
    "contains": contains,
}