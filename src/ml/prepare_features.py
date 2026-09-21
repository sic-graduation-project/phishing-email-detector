from pathlib import Path

import joblib
import numpy as np

from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import MaxAbsScaler

from feature_builder import (
    URL_SENDER_FEATURES,
    build_feature_dataset,
)

from nlp_feature_builder import (
    NLP_NUMERIC_FEATURES,
    build_nlp_features,
)


# ============================================================
# Configuration
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.30

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"


# ============================================================
# TF-IDF configuration
# Same final configuration used by the NLP component
# ============================================================

def create_tfidf_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.9,
        sublinear_tf=True,
    )


# ============================================================
# Build combined dataset
# ============================================================

def build_combined_dataset():
    print("=" * 60)
    print("BUILDING COMBINED ML DATASET")
    print("=" * 60)

    # Cleaned dataset + Ryan's 15 ML features
    base_df = build_feature_dataset()

    print(f"Base + URL/Sender rows: {len(base_df):,}")

    # Buthaina's NLP feature logic, preserving email_id
    nlp_df = build_nlp_features(base_df)

    nlp_columns = [
        "email_id",
        "clean_body",
        *NLP_NUMERIC_FEATURES,
    ]

    combined_df = base_df.merge(
        nlp_df[nlp_columns],
        on="email_id",
        how="inner",
        validate="one_to_one",
    )

    if len(combined_df) != len(base_df):
        raise ValueError(
            "NLP merge changed the number of dataset rows."
        )

    if combined_df["email_id"].duplicated().any():
        raise ValueError(
            "Duplicate email_id detected after NLP merge."
        )

    return combined_df


# ============================================================
# Prepare train/test features
# ============================================================

def prepare_features():
    df = build_combined_dataset()

    print("\n" + "=" * 60)
    print("TRAIN / TEST SPLIT")
    print("=" * 60)

    # --------------------------------------------------------
    # 70% training / 30% testing
    # Stratified to preserve label distribution
    # --------------------------------------------------------

    # ==========================================================
    # Sender-based Group Split
    # Same sender cannot appear in both Train and Test
    # ==========================================================
    groups = (
        df["sender"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # If sender is empty, treat that email as its own group
    empty_sender = groups.eq("")

    groups.loc[empty_sender] = (
        "missing_sender_" + df.loc[empty_sender, "email_id"].astype(str)
    )

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.30,
        random_state=42,
    )

    train_idx, test_idx = next(
        splitter.split(
            df,
            y=df["label"],
            groups=groups,
        )
    )

    train_df = df.iloc[train_idx].copy()
    test_df = df.iloc[test_idx].copy()

    print("\nSender-based split completed.")
    print("Train rows:", len(train_df))
    print("Test rows:", len(test_df))

    print("\nTrain label distribution:")
    print(train_df["label"].value_counts(normalize=True))

    print("\nTest label distribution:")
    print(test_df["label"].value_counts(normalize=True))

    train_senders = set(groups.iloc[train_idx])
    test_senders = set(groups.iloc[test_idx])

    sender_overlap = train_senders.intersection(test_senders)

    print("\nSender overlap between Train/Test:", len(sender_overlap))

    assert len(sender_overlap) == 0, (
        "ERROR: Sender leakage detected between Train and Test."
    )

    print(f"Training rows: {len(train_df):,}")
    print(f"Testing rows:  {len(test_df):,}")

    print("\nTraining label distribution:")
    print(train_df["label"].value_counts().sort_index())

    print("\nTesting label distribution:")
    print(test_df["label"].value_counts().sort_index())

    # --------------------------------------------------------
    # TF-IDF
    #
    # IMPORTANT:
    # fit ONLY on training data.
    # This prevents information leakage from the test set.
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("TF-IDF")
    print("=" * 60)

    tfidf = create_tfidf_vectorizer()

    print("Fitting TF-IDF on training data...")

    X_train_tfidf = tfidf.fit_transform(
        train_df["clean_body"]
    )

    print("Transforming testing data...")

    X_test_tfidf = tfidf.transform(
        test_df["clean_body"]
    )

    print(
        f"TF-IDF vocabulary size: "
        f"{len(tfidf.vocabulary_):,}"
    )

    print(
        f"Training TF-IDF shape: "
        f"{X_train_tfidf.shape}"
    )

    print(
        f"Testing TF-IDF shape: "
        f"{X_test_tfidf.shape}"
    )

    # --------------------------------------------------------
    # Numeric features
    # 15 URL/Sender + 8 NLP = 23 features
    # --------------------------------------------------------

    numeric_features = (
        URL_SENDER_FEATURES
        + NLP_NUMERIC_FEATURES
    )

    print("\n" + "=" * 60)
    print("NUMERIC FEATURES")
    print("=" * 60)

    print(
        f"URL/Sender features: "
        f"{len(URL_SENDER_FEATURES)}"
    )

    print(
        f"NLP numeric features: "
        f"{len(NLP_NUMERIC_FEATURES)}"
    )

    print(
        f"Total numeric features: "
        f"{len(numeric_features)}"
    )

    X_train_numeric_raw = train_df[
        numeric_features
    ].astype(float)

    X_test_numeric_raw = test_df[
        numeric_features
    ].astype(float)

    # --------------------------------------------------------
    # Scale numeric features.
    #
    # Fit scaler on TRAINING data only.
    # MaxAbsScaler keeps zero values and works well with
    # sparse/high-dimensional ML pipelines.
    # --------------------------------------------------------

    scaler = MaxAbsScaler()

    X_train_numeric = scaler.fit_transform(
        X_train_numeric_raw
    )

    X_test_numeric = scaler.transform(
        X_test_numeric_raw
    )

    X_train_numeric = csr_matrix(
        X_train_numeric
    )

    X_test_numeric = csr_matrix(
        X_test_numeric
    )

    # --------------------------------------------------------
    # Combine TF-IDF + numeric features
    # --------------------------------------------------------

    X_train = hstack(
        [
            X_train_tfidf,
            X_train_numeric,
        ]
    ).tocsr()

    X_test = hstack(
        [
            X_test_tfidf,
            X_test_numeric,
        ]
    ).tocsr()

    y_train = train_df["label"].to_numpy()
    y_test = test_df["label"].to_numpy()

    print("\n" + "=" * 60)
    print("FINAL ML MATRICES")
    print("=" * 60)

    print(f"X_train: {X_train.shape}")
    print(f"X_test:  {X_test.shape}")

    print(f"y_train: {y_train.shape}")
    print(f"y_test:  {y_test.shape}")

    expected_features = (
        X_train_tfidf.shape[1]
        + len(numeric_features)
    )

    if X_train.shape[1] != expected_features:
        raise ValueError(
            "Unexpected final training feature count."
        )

    if X_test.shape[1] != expected_features:
        raise ValueError(
            "Unexpected final testing feature count."
        )

    # --------------------------------------------------------
    # Save preprocessing objects required later by backend
    # --------------------------------------------------------

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        tfidf,
        MODELS_DIR / "tfidf_vectorizer.pkl",
    )

    joblib.dump(
        scaler,
        MODELS_DIR / "numeric_scaler.pkl",
    )

    joblib.dump(
        numeric_features,
        MODELS_DIR / "numeric_feature_names.pkl",
    )

    print("\nPreprocessing objects saved to:")
    print(MODELS_DIR)

    print(
        "\nFeature preparation completed successfully."
    )

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "train_df": train_df,
        "test_df": test_df,
        "tfidf": tfidf,
        "scaler": scaler,
        "numeric_features": numeric_features,
    }


# ============================================================
# Run validation
# ============================================================

if __name__ == "__main__":
    prepare_features()