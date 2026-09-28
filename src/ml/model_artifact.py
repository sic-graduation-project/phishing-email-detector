"""Versioned and atomic persistence for the complete inference pipeline."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import joblib
import sklearn

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
BUNDLE_PATH = MODELS_DIR / "phishing_model_bundle.joblib"
REPORT_PATH = MODELS_DIR / "evaluation_report.json"
SCHEMA_VERSION = 1


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def working_tree_dirty() -> bool:
    try:
        return bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=PROJECT_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return True


def build_metadata(numeric_features: list[str], threshold: float) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": git_commit(),
        "working_tree_dirty": working_tree_dirty(),
        "sklearn_version": sklearn.__version__,
        "decision_threshold": threshold,
        "numeric_features": numeric_features,
        "datasets": {
            "cleaned_dataset.csv": sha256_file(
                PROJECT_ROOT / "data" / "processed" / "cleaned_dataset.csv"
            ),
            "url_sender_features_output.csv": sha256_file(
                PROJECT_ROOT / "data" / "FEATURES" / "url_sender_features_output.csv"
            ),
        },
        "pipeline_sources": {
            name: sha256_file(PROJECT_ROOT / "src" / "ml" / name)
            for name in (
                "calibrated_svc.py",
                "feature_builder.py",
                "model_artifact.py",
                "nlp_feature_builder.py",
                "predict.py",
                "prepare_features.py",
            )
        },
        "url_analysis_source": sha256_file(
            PROJECT_ROOT / "src" / "url_analysis" / "analyzer.py"
        ),
        "requirements": sha256_file(PROJECT_ROOT / "requirements.txt"),
    }


def _atomic_joblib_dump(value, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=destination.name + ".", suffix=".tmp", dir=destination.parent
    )
    os.close(descriptor)
    temporary_path = Path(temporary)
    try:
        joblib.dump(value, temporary_path)
        temporary_path.replace(destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def publish_bundle(bundle: dict, report: dict) -> None:
    _atomic_joblib_dump(bundle, BUNDLE_PATH)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = REPORT_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(REPORT_PATH)


def load_bundle(path: Path = BUNDLE_PATH) -> dict:
    bundle = joblib.load(path)
    required = {"model", "tfidf", "scaler", "numeric_features", "threshold", "metadata"}
    missing = required - set(bundle)
    if missing:
        raise ValueError(f"Incomplete model bundle; missing: {sorted(missing)}")
    metadata = bundle["metadata"]
    if metadata.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported model bundle schema version.")
    if metadata.get("sklearn_version") != sklearn.__version__:
        raise RuntimeError(
            "Model was trained with scikit-learn "
            f"{metadata.get('sklearn_version')}, running {sklearn.__version__}."
        )
    expected = len(bundle["tfidf"].vocabulary_) + len(bundle["numeric_features"])
    if bundle["model"].n_features_in_ != expected:
        raise ValueError("Model and preprocessing feature counts do not match.")
    return bundle
