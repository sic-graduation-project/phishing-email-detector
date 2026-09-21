import pandas as pd
from sklearn.model_selection import train_test_split


DATA_PATH = "data/processed/cleaned_dataset.csv"

df = pd.read_csv(DATA_PATH, keep_default_na=False)

# نفس التقسيم الحالي المستخدم في الـ ML
train_df, test_df = train_test_split(
    df,
    test_size=0.30,
    random_state=42,
    stratify=df["label"],
)

print("=" * 60)
print("DATA LEAKAGE CHECK")
print("=" * 60)

# 1. Sender overlap
train_senders = set(train_df["sender"])
test_senders = set(test_df["sender"])

common_senders = train_senders.intersection(test_senders)

print("\n1. SENDER OVERLAP")
print("Train unique senders:", len(train_senders))
print("Test unique senders:", len(test_senders))
print("Common senders:", len(common_senders))

# 2. Exact body duplicates
train_bodies = set(train_df["body"])
test_bodies = set(test_df["body"])

common_bodies = train_bodies.intersection(test_bodies)
common_bodies.discard("")

print("\n2. EXACT BODY DUPLICATES")
print("Exact duplicate bodies between Train/Test:", len(common_bodies))

# 3. Exact subject + body duplicates
train_pairs = set(
    zip(
        train_df["subject"].astype(str),
        train_df["body"].astype(str),
    )
)

test_pairs = set(
    zip(
        test_df["subject"].astype(str),
        test_df["body"].astype(str),
    )
)

common_pairs = train_pairs.intersection(test_pairs)

print("\n3. EXACT SUBJECT + BODY DUPLICATES")
print("Exact subject+body duplicates between Train/Test:", len(common_pairs))

print("\n" + "=" * 60)
print("CHECK FINISHED")
print("=" * 60)