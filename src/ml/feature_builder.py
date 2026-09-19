from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASE_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_dataset.csv"
URL_FEATURES_PATH = (
    PROJECT_ROOT / "data" / "FEATURES" / "url_sender_features_output.csv"
)


URL_SENDER_FEATURES = [
    "url_count",
    "max_url_length",
    "has_https",
    "has_http",
    "has_at_in_url",
    "has_shortened_url",
    "has_ip_url",
    "max_subdomain_count",
    "url_parameter_count",
    "has_suspicious_characters",
    "has_suspicious_url_word",
    "sender_email_length",
    "sender_domain_length",
    "sender_local_part_length",
    "sender_has_display_name",
]


def load_csv(path: Path, name: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{name} not found: {path}")

    return pd.read_csv(path)


def validate_email_ids(df: pd.DataFrame, name: str) -> None:
    if "email_id" not in df.columns:
        raise ValueError(f"{name} does not contain 'email_id'.")

    if df["email_id"].isna().any():
        raise ValueError(f"{name} contains missing email_id values.")

    duplicate_count = df["email_id"].duplicated().sum()

    if duplicate_count:
        raise ValueError(
            f"{name} contains {duplicate_count} duplicate email_id values."
        )


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    name: str,
) -> None:
    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{name} is missing required columns: {missing}"
        )


def build_feature_dataset() -> pd.DataFrame:
    base_df = load_csv(BASE_DATA_PATH, "Cleaned dataset")
    url_df = load_csv(URL_FEATURES_PATH, "URL/Sender feature dataset")

    validate_email_ids(base_df, "Cleaned dataset")
    validate_email_ids(url_df, "URL/Sender feature dataset")

    validate_required_columns(
        base_df,
        ["email_id", "body", "subject", "label"],
        "Cleaned dataset",
    )

    validate_required_columns(
        url_df,
        ["email_id", "label", *URL_SENDER_FEATURES],
        "URL/Sender feature dataset",
    )

    label_check = base_df[["email_id", "label"]].merge(
        url_df[["email_id", "label"]],
        on="email_id",
        how="outer",
        suffixes=("_base", "_url"),
        indicator=True,
        validate="one_to_one",
    )

    unmatched = label_check["_merge"].ne("both").sum()

    if unmatched:
        raise ValueError(
            f"Found {unmatched} unmatched email_id values."
        )

    label_mismatches = (
        label_check["label_base"] != label_check["label_url"]
    ).sum()

    if label_mismatches:
        raise ValueError(
            f"Found {label_mismatches} label mismatches."
        )

    url_ml_df = url_df[
        ["email_id", *URL_SENDER_FEATURES]
    ].copy()

    merged_df = base_df.merge(
        url_ml_df,
        on="email_id",
        how="inner",
        validate="one_to_one",
    )

    if len(merged_df) != len(base_df):
        raise ValueError(
            "Merged dataset row count differs from cleaned dataset."
        )

    if merged_df[URL_SENDER_FEATURES].isna().any().any():
        raise ValueError(
            "Missing values found in URL/Sender ML features."
        )

    return merged_df


def main() -> None:
    df = build_feature_dataset()

    print("=" * 60)
    print("ML FEATURE DATASET VALIDATION")
    print("=" * 60)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {df.shape[1]}")
    print(f"Unique email_id: {df['email_id'].nunique():,}")
    print(
        f"Duplicate email_id: "
        f"{df['email_id'].duplicated().sum()}"
    )

    print("\nLabel distribution:")
    print(df["label"].value_counts().sort_index())

    print("\nURL/Sender ML features:")

    for index, feature in enumerate(
        URL_SENDER_FEATURES,
        start=1,
    ):
        print(f"{index:>2}. {feature}")

    print("\nFeature integration completed successfully.")


if __name__ == "__main__":
    main()