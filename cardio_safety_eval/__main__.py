"""Command-line entry point: python -m cardio_safety_eval RESPONSES [--cases CASES] [--json]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .evaluate import evaluate, format_report, read_jsonl

DEFAULT_CASES = Path(__file__).resolve().parent.parent / "cases" / "red_flag_cases.jsonl"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m cardio_safety_eval",
        description="Score chatbot responses on cardiovascular red-flag test cases.",
    )
    parser.add_argument("responses", help="JSONL file with one {\"id\", \"response\"} object per line")
    parser.add_argument("--cases", default=str(DEFAULT_CASES), help="JSONL file of test cases")
    parser.add_argument("--json", action="store_true", help="print the full report as JSON")
    parser.add_argument(
        "--min-emergency-rate",
        type=float,
        default=None,
        help="exit with status 1 if the emergency escalation rate is below this value (0-1)",
    )
    args = parser.parse_args(argv)

    report = evaluate(read_jsonl(args.cases), read_jsonl(args.responses))
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else format_report(report))

    rate = report["summary"]["emergency_escalation_rate"]
    if args.min_emergency_rate is not None and (rate or 0) < args.min_emergency_rate:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
