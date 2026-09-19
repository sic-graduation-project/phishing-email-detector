import re
from pathlib import Path

import pandas as pd
import contractions

try:
    import unicodedata2 as unicodedata
except ImportError:
    import unicodedata


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cleaned_dataset.csv"
)


# ============================================================
# NLP features used by the ML component
# ============================================================

NLP_NUMERIC_FEATURES = [
    "body_num_urls",
    "body_uppercase_ratio",
    "body_num_exclamations",
    "subject_num_urls",
    "subject_uppercase_ratio",
    "subject_num_exclamations",
    "keyword_count",
    "body_word_count",
]


PHISHING_KEYWORDS = [
    "verify",
    "urgent",
    "account",
    "password",
    "click",
    "login",
    "suspended",
    "confirm",
    "update",
    "security",
    "bank",
    "winner",
    "congratulations",
    "free",
    "prize",
    "limited",
    "expire",
    "alert",
]


# ============================================================
# Text normalization
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text before cleaning.

    This follows the NLP preprocessing logic used by the
    team NLP component.
    """
    if pd.isna(text):
        return ""

    text = str(text)

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = contractions.fix(text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


# ============================================================
# Text cleaning
# ============================================================

def clean_text(text: str) -> str:
    """
    Prepare normalized text for TF-IDF.

    URLs, emails, numbers and selected symbols are replaced
    with meaningful tokens before other characters are removed.
    """
    text = normalize_text(text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Replace URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " urltoken ",
        text,
    )

    # Replace email addresses
    text = re.sub(
        r"\b[\w.\-+%]+@[\w.\-]+\.[a-z]{2,}\b",
        " emailtoken ",
        text,
    )

    # Replace numbers
    text = re.sub(r"\d+", " numtoken ", text)

    # Replace important phishing-related symbols
    text = text.replace("!", " exclamationtoken ")
    text = text.replace("?", " questiontoken ")
    text = text.replace("$", " dollartoken ")
    text = text.replace("%", " percenttoken ")

    # Keep letters and spaces only
    text = re.sub(r"[^a-z\s]", " ", text)

    # Remove duplicated whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ============================================================
# Basic phishing text features
# ============================================================

def extract_phishing_features(text: str) -> dict:
    if pd.isna(text):
        text = ""

    text = str(text)

    num_urls = len(
        re.findall(
            r"http\S+|www\.\S+",
            text,
            flags=re.IGNORECASE,
        )
    )

    num_emails = len(
        re.findall(
            r"\S+@\S+",
            text,
        )
    )

    num_digits = sum(
        character.isdigit()
        for character in text
    )

    num_exclamations = text.count("!")
    num_questions = text.count("?")
    num_dollar = text.count("$")
    num_percent = text.count("%")

    num_html_tags = len(
        re.findall(r"<[^>]+>", text)
    )

    uppercase_letters = sum(
        character.isupper()
        for character in text
    )

    alphabetic_letters = sum(
        character.isalpha()
        for character in text
    )

    if alphabetic_letters > 0:
        uppercase_ratio = (
            uppercase_letters / alphabetic_letters
        )
    else:
        uppercase_ratio = 0.0

    text_length = len(text)
    num_words = len(text.split())

    return {
        "num_urls": num_urls,
        "num_emails": num_emails,
        "num_digits": num_digits,
        "num_exclamations": num_exclamations,
        "num_questions": num_questions,
        "num_dollar": num_dollar,
        "num_percent": num_percent,
        "num_html_tags": num_html_tags,
        "uppercase_ratio": uppercase_ratio,
        "text_length": text_length,
        "num_words": num_words,
    }


# ============================================================
# Keyword feature
# ============================================================

def count_phishing_keywords(clean_body: str) -> int:
    """
    Count phishing keywords that appear in the cleaned body.
    """
    words = set(clean_body.split())

    return sum(
        keyword in words
        for keyword in PHISHING_KEYWORDS
    )


# ============================================================
# Statistical text features
# ============================================================

def statistical_features(
    clean_body: str,
    normalized_body: str,
) -> dict:
    words = clean_body.split()

    word_count = len(words)

    if word_count > 0:
        unique_word_ratio = (
            len(set(words)) / word_count
        )

        avg_word_length = (
            sum(len(word) for word in words)
            / word_count
        )
    else:
        unique_word_ratio = 0.0
        avg_word_length = 0.0

    sentences = [
        sentence.strip()
        for sentence in normalized_body.split(".")
        if sentence.strip()
    ]

    sentence_count = len(sentences)

    if sentence_count > 0:
        avg_sentence_length = (
            word_count / sentence_count
        )
    else:
        avg_sentence_length = 0.0

    return {
        "word_count": word_count,
        "unique_word_ratio": unique_word_ratio,
        "avg_word_length": avg_word_length,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
    }


# ============================================================
# Build NLP feature dataset
# ============================================================

def build_nlp_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    required_columns = [
        "email_id",
        "body",
        "subject",
        "label",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{missing_columns}"
        )

    result = df[
        ["email_id", "body", "subject", "label"]
    ].copy()

    result["body"] = result["body"].fillna("")
    result["subject"] = result["subject"].fillna("")

    print("Normalizing body text...")

    result["normalized_body"] = (
        result["body"].apply(normalize_text)
    )

    print("Cleaning body text...")

    result["clean_body"] = (
        result["body"].apply(clean_text)
    )

    # --------------------------------------------------------
    # Body phishing features
    # --------------------------------------------------------

    print("Extracting body features...")

    body_features = pd.DataFrame(
        result["body"]
        .apply(extract_phishing_features)
        .tolist(),
        index=result.index,
    )

    body_features = body_features.add_prefix("body_")

    # --------------------------------------------------------
    # Subject phishing features
    # --------------------------------------------------------

    print("Extracting subject features...")

    subject_features = pd.DataFrame(
        result["subject"]
        .apply(extract_phishing_features)
        .tolist(),
        index=result.index,
    )

    subject_features = subject_features.add_prefix(
        "subject_"
    )

    # --------------------------------------------------------
    # Keyword feature
    # --------------------------------------------------------

    print("Extracting phishing keyword feature...")

    result["keyword_count"] = (
        result["clean_body"]
        .apply(count_phishing_keywords)
    )

    # --------------------------------------------------------
    # Statistical features
    # --------------------------------------------------------

    print("Extracting statistical features...")

    statistics = result.apply(
        lambda row: statistical_features(
            row["clean_body"],
            row["normalized_body"],
        ),
        axis=1,
        result_type="expand",
    )

    statistics = statistics.add_prefix("body_")

    # --------------------------------------------------------
    # Combine feature groups
    # --------------------------------------------------------

    result = pd.concat(
        [
            result,
            body_features,
            subject_features,
            statistics,
        ],
        axis=1,
    )

    # Validate final features
    missing_features = [
        feature
        for feature in NLP_NUMERIC_FEATURES
        if feature not in result.columns
    ]

    if missing_features:
        raise ValueError(
            f"NLP feature extraction failed. "
            f"Missing: {missing_features}"
        )

    if result[NLP_NUMERIC_FEATURES].isna().any().any():
        raise ValueError(
            "NLP numeric features contain missing values."
        )

    return result


# ============================================================
# Main validation
# ============================================================

def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    print("=" * 60)
    print("NLP FEATURE BUILDER")
    print("=" * 60)

    df = pd.read_csv(DATA_PATH)

    print(f"Input rows: {len(df):,}")

    nlp_df = build_nlp_features(df)

    print("\n" + "=" * 60)
    print("NLP FEATURE VALIDATION")
    print("=" * 60)

    print(f"Rows: {len(nlp_df):,}")
    print(
        f"Unique email_id: "
        f"{nlp_df['email_id'].nunique():,}"
    )
    print(
        f"Duplicate email_id: "
        f"{nlp_df['email_id'].duplicated().sum()}"
    )

    print("\nNLP numeric features:")

    for index, feature in enumerate(
        NLP_NUMERIC_FEATURES,
        start=1,
    ):
        print(f"{index:>2}. {feature}")

    print(
        "\nClean body sample:"
    )
    print(
        nlp_df["clean_body"].iloc[0][:300]
    )

    print(
        "\nNLP feature generation "
        "completed successfully."
    )


if __name__ == "__main__":
    main()