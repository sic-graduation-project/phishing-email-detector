"""Build leakage-safe feature matrices without publishing artifacts."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import MaxAbsScaler

from feature_builder import PRODUCTION_URL_FEATURES, build_feature_dataset
from nlp_feature_builder import NLP_NUMERIC_FEATURES, build_nlp_features

RANDOM_STATE = 42
N_SPLITS = 10
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_tfidf_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.9,
        sublinear_tf=True,
    )


def build_combined_dataset():
    base_df = build_feature_dataset()
    nlp_df = build_nlp_features(base_df)
    nlp_columns = ["email_id", "clean_body", *NLP_NUMERIC_FEATURES]
    combined_df = base_df.merge(
        nlp_df[nlp_columns], on="email_id", how="inner", validate="one_to_one"
    )
    if len(combined_df) != len(base_df) or combined_df["email_id"].duplicated().any():
        raise ValueError("NLP merge changed or duplicated dataset rows.")
    return combined_df


def normalized_sender_groups(df):
    groups = df["sender"].fillna("").astype(str).str.strip().str.lower()
    empty = groups.eq("")
    groups.loc[empty] = "missing_sender_" + df.loc[empty, "email_id"].astype(str)
    return groups


def split_development_data(df):
    """Create sender-disjoint 60/10/10/20 train/calibration/validation/test sets."""
    groups = normalized_sender_groups(df)
    splitter = StratifiedGroupKFold(
        n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE
    )
    fold_for_row = np.full(len(df), -1, dtype=int)
    for fold, (_, fold_idx) in enumerate(splitter.split(df, df["label"], groups)):
        fold_for_row[fold_idx] = fold
    if (fold_for_row < 0).any():
        raise ValueError("Some rows were not assigned to a data partition.")

    masks = {
        "test": np.isin(fold_for_row, [0, 1]),
        "calibration": fold_for_row == 2,
        "validation": fold_for_row == 3,
        "train": fold_for_row >= 4,
    }
    partitions = {name: df.loc[mask].copy() for name, mask in masks.items()}
    group_sets = {name: set(groups.loc[frame.index]) for name, frame in partitions.items()}
    names = list(group_sets)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            if group_sets[left] & group_sets[right]:
                raise ValueError(f"Sender leakage between {left} and {right} partitions.")
    for name, frame in partitions.items():
        if set(frame["label"].unique()) != {0, 1}:
            raise ValueError(f"Partition {name} does not contain both labels.")
    return partitions


def _combine(text_matrix, numeric_matrix):
    return hstack([text_matrix, csr_matrix(numeric_matrix)]).tocsr()


def prepare_features():
    df = build_combined_dataset()
    frames = split_development_data(df)
    numeric_features = PRODUCTION_URL_FEATURES + NLP_NUMERIC_FEATURES

    tfidf = create_tfidf_vectorizer()
    scaler = MaxAbsScaler()
    tfidf.fit(frames["train"]["clean_body"])
    scaler.fit(frames["train"][numeric_features].astype(float))

    result = {
        "tfidf": tfidf,
        "scaler": scaler,
        "numeric_features": numeric_features,
        "frames": frames,
    }
    expected_features = len(tfidf.vocabulary_) + len(numeric_features)
    for name, frame in frames.items():
        text = tfidf.transform(frame["clean_body"])
        numeric = scaler.transform(frame[numeric_features].astype(float))
        matrix = _combine(text, numeric)
        if matrix.shape[1] != expected_features:
            raise ValueError(f"Unexpected feature count in {name} partition.")
        result[f"X_{name}"] = matrix
        result[f"y_{name}"] = frame["label"].to_numpy()

    print("Sender-disjoint data partitions:")
    for name, frame in frames.items():
        print(f"  {name:11} rows={len(frame):6,} phishing_rate={frame['label'].mean():.3f}")
    print(f"Final feature count: {expected_features:,}")
    return result


if __name__ == "__main__":
    prepare_features()
