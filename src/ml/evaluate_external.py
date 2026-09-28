"""Evaluate the locked production bundle on an independent labeled CSV.

Required columns: sender, subject, body, label. This command never retrains or
changes the production model.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "url_analysis"))

from calibrated_svc import evaluate
from analyzer import analyze_single_email
from predict import DECISION_THRESHOLD, predict_from_analysis


def evaluate_csv(path: Path) -> dict:
    frame = pd.read_csv(path, keep_default_na=False)
    required = {"sender", "subject", "body", "label"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"External dataset is missing columns: {sorted(missing)}")
    if not set(frame["label"].unique()).issubset({0, 1}):
        raise ValueError("External labels must contain only 0 (legitimate) and 1 (phishing).")

    probabilities = []
    for row in frame.itertuples(index=False):
        analysis = analyze_single_email(str(row.sender), str(row.body))
        result = predict_from_analysis(
            str(row.sender), str(row.subject), str(row.body), analysis
        )
        probabilities.append(result["phishing_probability"])
    report = evaluate(
        frame["label"].to_numpy(), np.asarray(probabilities), DECISION_THRESHOLD
    )
    report["dataset"] = str(path.resolve())
    report["independent_external_data"] = True
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "models" / "external_evaluation_report.json")
    arguments = parser.parse_args()
    report = evaluate_csv(arguments.csv)
    arguments.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
