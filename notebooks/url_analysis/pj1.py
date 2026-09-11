import os
import re

import contractions
import pandas as pd
import unicodedata2 as unicodedata

csv_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "src", "nlp", "CEAS_08.csv"
)
df = pd.read_csv(csv_path)

# Keep only the "body" feature plus the label for now
data = df[["body", "label"]].dropna()


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


features_df = data["body"].apply(extract_phishing_features).apply(pd.Series)  # Extract phishing features from the email body
data = pd.concat([data, features_df], axis=1)  # Concatenate the original data with the extracted features

data["normalized_body"] = data["body"].apply(normalize_text)
data["clean_body"] = data["normalized_body"].apply(clean_text)

print(data.shape)
print(data[["body", "normalized_body", "clean_body"]].head())