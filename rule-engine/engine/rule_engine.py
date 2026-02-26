# engine/rule_engine.py

from typing import List, Dict, Any
from .models import Rule, Condition, Action, Context
from .operators import OPERATORS
# از execute_action استفاده می‌کنیم تا لاگ برگشتی اکشن رو داشته باشیم و رفتار مرکزی‌سازی شده باشد
from .actions import execute_action
from .utils import load_json_file


class RuleEngine:
    def __init__(self, context_file: str, rules_file: str):
        self.context_file = context_file
        self.rules_file = rules_file
        self.context: Context = None
        self.rules: List[Rule] = []
        self.state: Dict[str, Any] = self._init_state()
        self.logs: List[str] = []

    def _init_state(self) -> Dict[str, Any]:
        """مقداردهی اولیه state"""
        return {
            "applied_rules": [],
            "discount_percent": 0,
            "discount_amount": 0,
            "free_shipping": False,
            "payment": {
                "is_blocked": False,
                "blocked_reason": None,
                "blocked_methods": []
            },
            "final_price": 0,
            "logs": []
        }

    def _load_context(self):
        data = load_json_file(self.context_file)
        self.context = Context.from_dict(data)

    def _load_rules(self):
        data = load_json_file(self.rules_file)
        self.rules = []
        for rule_data in data:
            # ساده نگه داشتیم: فرض بر اینکه schema ورودی مناسب است
            conditions = [Condition(**cond) for cond in rule_data.get("when", [])]
            action = Action(**rule_data["then"])
            rule = Rule(
                id=rule_data["id"],
                description=rule_data.get("description", ""),
                priority=int(rule_data.get("priority", 0)),
                when=conditions,
                then=action
            )
            self.rules.append(rule)

    def _evaluate_condition(self, condition: Condition) -> bool:
        """بررسی یک شرط با context"""
        # مقدار فیلد مورد نظر از context — getattr به ما اجازه می‌دهد اگر فیلد وجود ندارد None بگیریم
        field_value = getattr(self.context, condition.field, None)
        if field_value is None:
            # اگه فیلد وجود نداشت، شرط false
            return False

        op_func = OPERATORS.get(condition.op)
        if not op_func:
            # اگه عملگر پشتیبانی نمی‌شه، false
            self.logs.append(f"Unsupported operator '{condition.op}' in condition for field '{condition.field}'")
            return False

        try:
            return op_func(field_value, condition.value)
        except Exception as e:
            # در صورت خطای داخلی در عملگر، شرط false فرض می‌شود و لاگ می‌شود
            self.logs.append(f"Error evaluating condition ({condition.field} {condition.op} {condition.value}): {e}")
            return False

    def _evaluate_rule(self, rule: Rule) -> bool:
        """بررسی همه شرایط یک قانون (AND semantics)"""
        for condition in rule.when:
            if not self._evaluate_condition(condition):
                return False
        return True

    def _apply_action(self, rule: Rule):
        """اعمال action قانون روی state و ثبت لاگ با استفاده از execute_action"""
        try:
            log_msg = execute_action(rule.then.action, self.state, rule.then.value)
            # فقط یک‌بار id قاعده اضافه می‌شود (از duplicate جلوگیری می‌کنیم)
            if rule.id not in self.state["applied_rules"]:
                self.state["applied_rules"].append(rule.id)
            # اگر execute_action لاگ بازگرداند از آن استفاده می‌کنیم، در غیر این صورت پیام پیش‌فرض می‌سازیم
            self.logs.append(f"Rule {rule.id} matched: {log_msg}")
        except Exception as e:
            # اکشن ناشناخته یا خطا — لاگ کن ولی execution را متوقف نکن
            self.logs.append(f"Rule {rule.id} matched but failed to execute action '{rule.then.action}': {e}")

    def _calculate_final(self):
        """محاسبات نهایی بعد از اجرای همه قوانین"""
        # محاسبه مبلغ تخفیف (int و گرد شده)
        try:
            percent = int(self.state.get("discount_percent", 0))
        except Exception:
            percent = 0

        if percent > 0:
            discount_amount = int(round(self.context.cart_total * percent / 100.0))
            # تضمین عدد غیرمنفی
            discount_amount = max(0, discount_amount)
            self.state["discount_amount"] = discount_amount
        else:
            self.state["discount_amount"] = 0

        # قیمت نهایی
        final = int(round(self.context.cart_total - self.state["discount_amount"]))
        final = max(0, final)
        self.state["final_price"] = final

    def run(self) -> Dict[str, Any]:
        """اجرای موتور و برگردوندن خروجی نهایی"""
        # بارگذاری و ایمن‌سازی ورودی‌ها
        self._load_context()
        self._load_rules()

        # مرتب‌سازی قوانین بر اساس priority (بزرگ‌تر = اول اجرا)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

        for rule in self.rules:
            if self._evaluate_rule(rule):
                self._apply_action(rule)

        self._calculate_final()
        # انتقال logs داخلی به state خروجی
        self.state["logs"] = self.logs
        return self.state