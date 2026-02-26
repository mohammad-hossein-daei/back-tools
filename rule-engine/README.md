# Rule Engine

## Project introduction

This project is a **Simple and extensible Rule Engine** that reads rules from a JSON file and executes them based on the order information (Context).
The engine uses a **priority-based rule evaluation** system and produces the final output in JSON.
This tool is suitable for implementing logics such as discounts, free shipping, and payment control.
---

## Installation and execution
### 1. clone project

```bash
git clone <repo-url>
cd rule-engine
```
## 2. Run the Rule Engine
```bash
python(version) main.py examples/context_order_1.json examples/rules.json
```

## context.json format

{
  "user_type": "new",
  "cart_total": 1250000,
  "items_count": 3,
  "city": "tehran",
  "payment_method": "online",
  "has_previous_chargeback": false,
  "gateway": "zarinpal"
}


## rules.json format

[
  {
    "id": "D1",
    "description": "rule description",
    "priority": 10,
    "when": [
      {
        "field": "cart_total",
        "op": ">",
        "value": 1000000
      }
    ],
    "then": {
      "action": "apply_discount_percent",
      "value": 10
    }
  }
]


## Supported Operators
Operator    Description
==	        Equal to
!=	        Not equal to
>	        Greater than
>=	        Greater than or equal to
<	        Less than
<=	        Less than or equal to


## Supported Actions
______________________________________________________________________
|Action	                |Description                                  |
|apply_discount_percent	|Apply a percentage discount to the cart total|
|free_shipping	        |Enable free shipping for the order           |
|block_payment       	|Block the payment completely with a reason   |
|block_payment_method	|Block a specific payment method              |
|_____________________________________________________________________|