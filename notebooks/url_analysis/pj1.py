import os
import re
import numpy as np
import contractions
import pandas as pd
import unicodedata2 as unicodedata
from sklearn.model_selection import train_test_split
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
# nltk.download("punkt")
# nltk.download("punkt_tab") 
from nltk.tokenize import word_tokenize
from scipy.sparse import hstack, csr_matrix , save_npz
import joblib
from sklearn.feature_selection import chi2 


csv_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "src", "nlp", "CEAS_08.csv"
)
df = pd.read_csv(csv_path)


data = df[["body","subject","label"]].copy()  # Create a copy of the DataFrame with only the "body" and "label" and "subject" columns

def extract_phishing_features(text):
    # Extracts features from the email body text that may indicate phishing attempts.
    features = {}
    features["num_urls"] = len(re.findall(r"http\S+|www\.\S+", text))  # Count the number of URLs in the text
    features["num_emails"] = len(re.findall(r"\S+@\S+", text))  # Count the number of email addresses in the text
    features["num_digits"] = len(re.findall(r"\d", text))  # Count the number of digits in the text
    features["num_exclamations"] = text.count("!")  # Count the number of exclamation marks in the text
    features["num_questions"] = text.count("?")  # Count the number of question marks in the text
    features["num_dollar"] = text.count("$")  # Count the number of dollar signs in the text
    features["num_percent"] = text.count("%")  # Count the number of percent signs in the text
    features["num_html_tags"] = len(re.findall(r"<.*?>", text, flags=re.DOTALL))  # Count the number of HTML tags in the text
    features["uppercase_ratio"] = (
        sum(1 for c in text if c.isupper()) / len(text) if len(text) > 0 else 0
    )
    features["text_length"] = len(text)  # Count the number of characters in the text
    features["num_words"] = len(text.split())  # Count the number of words in the text
    return features


def normalize_text(text): # i needed to add this function to normalize the text before cleaning it bcz of unicode issues
    text = unicodedata.normalize("NFKC", text)  # Unicode normalization
    text = text.lower()
    text = contractions.fix(text)  # Expand contractions (needs the apostrophes still in place)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_text(text):
    text = re.sub(r"<.*?>", " ", text, flags=re.DOTALL)  # Remove HTML tags
    text = re.sub(r"http\S+|www\.\S+", " urltoken ", text)  # Replace URLs with a token
    text = re.sub(r"\S+@\S+", " emailtoken ", text)  # Replace email addresses with a token
    text = re.sub(r"\d+", " numtoken ", text)  # Replace digits with a token
    text = text.replace("!", " exclamationtoken ")  # Replace exclamation marks with a token
    text = text.replace("?", " questiontoken ")  # Replace question marks with a token
    text = text.replace("$", " dollartoken ")  # Replace dollar signs with a token
    text = text.replace("%", " percenttoken ")  # Replace percent signs with a token

    text = re.sub(r"[^a-z\s]", " ", text)  # Remove remaining punctuation
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra whitespace
    return text

def tokenize_text(text):
    tokens = word_tokenize(text)  # Split the cleaned text into word tokens
    return tokens

body_features = data["body"].apply(extract_phishing_features).apply(pd.Series)
body_features.columns = ["body_" + c for c in body_features.columns]
data = pd.concat([data, body_features], axis=1)
print(data.shape)

subject_features = data["subject"].apply(extract_phishing_features).apply(pd.Series)
subject_features.columns = ["subject_" + c for c in subject_features.columns]
data = pd.concat([data, subject_features], axis=1)

data["normalized_body"] = data["body"].apply(normalize_text)
data["clean_body"] = data["normalized_body"].apply(clean_text)

data["normalized_subject"] = data["subject"].apply(normalize_text)
data["clean_subject"] = data["normalized_subject"].apply(clean_text)

data["body_tokens"] = data["clean_body"].apply(tokenize_text)
data["subject_tokens"] = data["clean_subject"].apply(tokenize_text)

print(data.shape)
print(data[["body", "normalized_body", "clean_body", "body_tokens", "body_num_words"]].tail())
print(data[["subject", "normalized_subject", "clean_subject", "subject_tokens", "subject_num_words"]].tail())

#split the data into train and test sets
train_data, test_data = train_test_split(data, test_size=0.3, random_state=42, stratify=data["label"])
train_data = train_data.copy()
test_data = test_data.copy()
print("Train:", train_data.shape, "Test:", test_data.shape)

#tfidf vectorization to know the most important words in the body of the emails
tfidf_analyse = TfidfVectorizer(max_features=5000, ngram_range=(1, 2),stop_words="english", min_df=3, max_df=0.9, sublinear_tf=True)
X_train_tfidf = tfidf_analyse.fit_transform(train_data["clean_body"]) #apply TF-IDF vectorization to the training data only to avoid data leakage
#i used the chi2 test to find the most discriminative words between phishing and legitimate emails
# it is just an additional analysis to understand the data better, it is not used in the final model
tfidf_chi = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    stop_words="english",
    min_df=3,
    max_df=0.9,
    sublinear_tf=True
)
X_train_chi = tfidf_chi.fit_transform(train_data["clean_body"])
y_train_chi = train_data["label"].values

chi2_scores, p_values = chi2(X_train_chi, y_train_chi)

feature_names = np.array(tfidf_chi.get_feature_names_out())
top_indices = chi2_scores.argsort()[::-1][:30]
print("Top discriminative words:")
print(feature_names[top_indices])

#comparing the top words for phishing and legitimate emails separately
#note: chi2 needs two classes to compare against, so it can't be used within
#a single-label subset - mean TF-IDF per word is used instead to rank words within each class
for label_value, label_name in [(1, "Phishing"), (0, "Legitimate")]:
    mask = train_data["label"] == label_value
    X_subset = tfidf_chi.transform(train_data.loc[mask, "clean_body"])
    mean_scores = np.asarray(X_subset.mean(axis=0)).ravel()
    top_idx = mean_scores.argsort()[::-1][:20]
    print(f"\nTop words for {label_name}:")
    print(feature_names[top_idx])

# Get the feature names and their corresponding mean TF-IDF scores
feature_names = np.array(tfidf_analyse.get_feature_names_out())
mean_tfidf = np.asarray(X_train_tfidf.mean(axis=0)).ravel()
top_indices = mean_tfidf.argsort()[::-1][:30]
print(feature_names[top_indices])

#most common words in legitimate and phishing emails 
PHISHING_KEYWORDS = [
    "verify", "urgent", "account", "password", "click", "login",
    "suspended", "confirm", "update", "security", "bank", "winner",
    "congratulations", "free", "prize", "limited", "expire", "alert"
]

def count_phishing_keywords(text):
    text_lower = text.lower()
    return sum(1 for kw in PHISHING_KEYWORDS if kw in text_lower)

train_data["keyword_count"] = train_data["clean_body"].apply(count_phishing_keywords)
test_data["keyword_count"] = test_data["clean_body"].apply(count_phishing_keywords)

#Statistical text features
def statistical_features(clean_body, normalized_body):
    # sentence boundaries ("." ) are stripped from clean_body, so sentence count
    # must be computed from normalized_body (before punctuation removal)
    words = clean_body.split()
    sentences = [s for s in normalized_body.split(".") if s.strip()]
    sentence_count = len(sentences) if sentences else 1
    return {
        "word_count": len(words),
        "unique_word_ratio": len(set(words)) / len(words) if words else 0,
        "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "sentence_count": sentence_count,
        "avg_sentence_length": len(words) / sentence_count,
    }


stats_train = train_data.apply(lambda row: statistical_features(row["clean_body"], row["normalized_body"]), axis=1).apply(pd.Series)
stats_test = test_data.apply(lambda row: statistical_features(row["clean_body"], row["normalized_body"]), axis=1).apply(pd.Series)

stats_train.columns = ["body_" + c for c in stats_train.columns]
stats_test.columns = ["body_" + c for c in stats_test.columns]

train_data = pd.concat([train_data, stats_train], axis=1)
test_data = pd.concat([test_data, stats_test], axis=1)

print(train_data.shape)
print(test_data.shape) 


#using TF-IDF vectorization to convert the text data into numerical features for machine learning models
tfidf_final = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    min_df=3,
    max_df=0.9,
    sublinear_tf=True
)

X_train_tfidf = tfidf_final.fit_transform(train_data["clean_body"])
X_test_tfidf = tfidf_final.transform(test_data["clean_body"])

#choosing the numeric columns to be used as features for the machine learning model
numeric_cols = [
    "body_num_urls", "body_uppercase_ratio", "body_num_exclamations",
    "subject_num_urls", "subject_uppercase_ratio", "subject_num_exclamations",
    "keyword_count", "body_word_count"
]

X_train_numeric = csr_matrix(train_data[numeric_cols].values)
X_test_numeric = csr_matrix(test_data[numeric_cols].values)


X_train_final = hstack([X_train_tfidf, X_train_numeric]).tocsr()
X_test_final = hstack([X_test_tfidf, X_test_numeric]).tocsr()

y_train = train_data["label"].values
y_test = test_data["label"].values

print("Final train shape:", X_train_final.shape)
print("Final test shape:", X_test_final.shape)

#for modling purposes, i will save the final train and test data as sparse matrices and numpy arrays

output_dir = os.path.dirname(os.path.abspath(__file__))
artifacts_dir = os.path.join(output_dir, "artifacts")
os.makedirs(artifacts_dir, exist_ok=True)

joblib.dump(tfidf_final, os.path.join(artifacts_dir, "tfidf_vectorizer.pkl"))
save_npz(os.path.join(artifacts_dir, "X_train_final.npz"), X_train_final)
save_npz(os.path.join(artifacts_dir, "X_test_final.npz"), X_test_final)
np.save(os.path.join(artifacts_dir, "y_train.npy"), y_train)
np.save(os.path.join(artifacts_dir, "y_test.npy"), y_test)

train_data.to_csv(os.path.join(artifacts_dir, "train_data.csv"), index=False)
test_data.to_csv(os.path.join(artifacts_dir, "test_data.csv"), index=False)
