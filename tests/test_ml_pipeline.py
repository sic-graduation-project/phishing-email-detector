import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "ml"))

from calibrated_svc import choose_threshold
from feature_builder import PRODUCTION_URL_FEATURES, SENDER_FEATURES
from model_artifact import load_bundle
from prepare_features import split_development_data


def test_production_model_excludes_unavailable_sender_features():
    assert not (set(PRODUCTION_URL_FEATURES) & set(SENDER_FEATURES))
    assert not (set(load_bundle()["numeric_features"]) & set(SENDER_FEATURES))


def test_partitions_are_sender_disjoint_and_stratified():
    rows = []
    for index in range(100):
        rows.append({
            "email_id": index,
            "sender": f"sender-{index // 2}@example.com",
            "label": (index // 2) % 2,
        })
    frame = pd.DataFrame(rows)
    partitions = split_development_data(frame)
    seen = set()
    for partition in partitions.values():
        senders = set(partition["sender"])
        assert not seen.intersection(senders)
        assert set(partition["label"]) == {0, 1}
        seen.update(senders)


def test_threshold_is_selected_from_validation_predictions():
    labels = np.array([0, 0, 1, 1])
    probabilities = np.array([0.05, 0.10, 0.60, 0.90])
    threshold = choose_threshold(labels, probabilities, minimum_precision=1.0)
    assert 0.10 < threshold <= 0.60


def test_bundle_is_complete_and_version_compatible():
    bundle = load_bundle()
    assert 0 < bundle["threshold"] < 1
    assert bundle["model"].n_features_in_ == (
        len(bundle["tfidf"].vocabulary_) + len(bundle["numeric_features"])
    )
