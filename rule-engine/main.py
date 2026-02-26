import sys
import json
import argparse
import traceback
from pathlib import Path
from engine.rule_engine import RuleEngine

def parse_args():
    p = argparse.ArgumentParser(
        prog="rule-engine",
        description="Run Rule Engine: evaluate discount & payment rules against a context JSON."
    )
    p.add_argument("context_file", help="Path to context JSON file (e.g. context/context_order_1.json)")
    p.add_argument("rules_file", help="Path to rules JSON file (e.g. rules/rules.json)")
    p.add_argument("-o", "--output", help="Optional path to write resulting JSON. If omitted prints to stdout.")
    p.add_argument("--pretty", action="store_true", help="Pretty-print the JSON output (indented).")
    return p.parse_args()


def main():
    args = parse_args()

    context_path = Path(args.context_file)
    rules_path = Path(args.rules_file)

    if not context_path.exists():
        print(f"Error: context file not found: {context_path}", file=sys.stderr)
        sys.exit(2)

    if not rules_path.exists():
        print(f"Error: rules file not found: {rules_path}", file=sys.stderr)
        sys.exit(3)

    try:
        engine = RuleEngine(str(context_path), str(rules_path))
        result = engine.run()

        # Create JSON output
        if args.pretty:
            out_str = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            out_str = json.dumps(result, separators=(",", ":"), ensure_ascii=False)

        if args.output:
            out_file = Path(args.output)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(out_str, encoding="utf-8")
            print(f"Result written to {out_file}")
        else:
            print(out_str)

    except Exception as e:
        # Full traceback log for debugging in dev mode
        print("Rule engine execution failed:", str(e), file=sys.stderr)
        
        # traceback.print_exc()
        sys.exit(4)


if __name__ == "__main__":
    main()