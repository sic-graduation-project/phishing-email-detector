import pandas as pd
import re
import ipaddress
from urllib.parse import urlparse

# ==========================================
# 1. Load Dataset
# ==========================================
import os

DATASET_PATH = r"C:\Users\User\Documents\GitHub\phishing-email-detector\data\processed\cleaned_dataset.csv"

OUTPUT_FILE = r"C:\Users\User\Documents\GitHub\phishing-email-detector\data\features\url_sender_features_output.csv"


df = pd.read_csv(DATASET_PATH)
print("\n==========================================")
print("DATASET INFORMATION")
print("==========================================")
print("Total Emails:", len(df))
print("Number of Columns:", len(df.columns))
print("Columns:")
print(df.columns.tolist())


# ==========================================
# 2. Extract URLs from Email Body
# Supports:
# http://
# https://
# www.
# ==========================================
def ExtractURLs(text):

    if pd.isna(text):
        return []

    pattern = r'(?:https?://|www\.)[^\s<>"\'\]\)]+'

    return re.findall(pattern, str(text))


# ==========================================
# 3. Clean URL
# ==========================================
def CleanURL(url):
    if not url:
        return ""
    return url.rstrip(".,;:!?)]}'\"")


# ==========================================
# 4. Normalize URL
# urlparse needs a scheme for www.
# ==========================================
def NormalizeURL(url):
    url = CleanURL(url)

    if not url:
        return ""

    if url.lower().startswith("www."):
        return "http://" + url

    return url


# ==========================================
# 5. Safe URL Parsing
# Prevent malformed URLs from stopping program
# ==========================================
def GetParsedURL(url):
    try:
        url = NormalizeURL(url)

        if not url:
            return None

        return urlparse(url)

    except Exception:

        return None


# ==========================================
# 6. Extract URL Domain
# ==========================================
def ExtractURLDomain(url):

    parsed = GetParsedURL(url)

    if parsed is None:
        return ""

    try:

        hostname = parsed.hostname

        if hostname:
            return hostname.lower()

    except Exception:
        pass

    return ""


# 7. Count URLs
def CountURLs(urls):

    return len(urls)


# 8. Maximum URL Length
def MaxURLLength(urls):

    if not urls:
        return 0

    return max(len(url) for url in urls)


# 9. Has HTTPS
def HasHTTPS(urls):

    for url in urls:

        if url.lower().startswith("https://"):
            return 1

    return 0


# 10. Has HTTP
def HasHTTP(urls):

    for url in urls:

        if url.lower().startswith("http://"):
            return 1

    return 0


# 11. Has @ In URL
def HasAtInURL(urls):

    for url in urls:

        if "@" in url:
            return 1

    return 0


# ==========================================
# 12. Has Shortened URL
# Detect:
# bit.ly
# www.bit.ly
# sub.bit.ly
# etc.
# ==========================================

SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "tiny.cc",
    "cutt.ly",
    "rb.gy",
    "shorturl.at",
    "rebrand.ly",
    "lnkd.in",
}


def HasShortenedURL(urls):
    for url in urls:
        domain = ExtractURLDomain(url)
        if not domain:
            continue

        # Exact shortener domain
        if domain in SHORTENER_DOMAINS:
            return 1

        # Subdomain of shortener
        for shortener in SHORTENER_DOMAINS:

            if domain.endswith("." + shortener):
                return 1

    return 0


# 13. Has IP Address In URL
def HasIPInURL(urls):

    for url in urls:

        hostname = ExtractURLDomain(url)

        if not hostname:
            continue

        try:

            ipaddress.ip_address(hostname)

            return 1

        except ValueError:

            continue

    return 0


# ==========================================
# 14. Count Subdomains
#
# Example:
# mail.example.com
# -> 1 subdomain
#
# login.secure.mail.example.com
# -> 3 subdomains
# ==========================================


def CountSubdomains(urls):

    maximum_subdomains = 0

    for url in urls:

        hostname = ExtractURLDomain(url)

        if not hostname:
            continue

        # IP address is not treated as subdomain
        try:

            ipaddress.ip_address(hostname)

            continue

        except ValueError:
            pass

        parts = hostname.split(".")

        if len(parts) > 2:

            subdomain_count = len(parts) - 2

            if subdomain_count > maximum_subdomains:
                maximum_subdomains = subdomain_count

    return maximum_subdomains


# ==========================================
# 15. Count URL Parameters
#
# Total number of parameters across ALL URLs
# ==========================================


def CountURLParameters(urls):

    total_parameters = 0

    for url in urls:

        parsed = GetParsedURL(url)

        if parsed is None:
            continue

        query = parsed.query

        if query:

            parameters = query.split("&")

            parameters = [parameter for parameter in parameters if parameter]

            total_parameters += len(parameters)

    return total_parameters


# ==========================================
# 16. Suspicious Characters
#
# Heuristic:
# @
# %
# _
# ==========================================


def HasSuspiciousCharacters(urls):

    suspicious_characters = ["@", "%", "_"]

    for url in urls:

        for char in suspicious_characters:

            if char in url:
                return 1

    return 0


# ==========================================
# 17. Suspicious Words
# ==========================================

SUSPICIOUS_WORDS = [
    "login",
    "log-in",
    "signin",
    "sign-in",
    "verify",
    "verification",
    "secure",
    "security",
    "account",
    "update",
    "confirm",
    "confirmation",
    "password",
    "bank",
    "paypal",
    "billing",
    "payment",
    "wallet",
    "credential",
]


def HasSuspiciousWords(urls):

    for url in urls:

        url_lower = url.lower()

        for word in SUSPICIOUS_WORDS:

            if word in url_lower:
                return 1

    return 0


# ==========================================
# 18. Extract Sender Domain
# ==========================================


def ExtractSenderDomain(sender):

    if pd.isna(sender):
        return ""

    sender = str(sender).strip().lower()

    pattern = r"[\w.\-+%]+@([\w.\-]+\.[a-z]{2,})"

    match = re.search(pattern, sender)

    if match:

        return match.group(1)

    return ""


# ==========================================
# 19. Sender Email Length
# ==========================================


def SenderEmailLength(sender):

    if pd.isna(sender):
        return 0

    sender = str(sender).strip()

    pattern = r"[\w.\-+%]+@[\w.\-]+\.[a-z]{2,}"

    match = re.search(pattern, sender)

    if match:

        email = match.group(0)

        return len(email)

    return 0


# ==========================================
# 20. Sender Domain Length
# ==========================================


def SenderDomainLength(sender_domain):

    if not sender_domain:
        return 0

    return len(sender_domain)


# ==========================================
# 21. Sender Has IP
# ==========================================


def SenderHasIP(sender_domain):

    if not sender_domain:
        return 0

    try:

        ipaddress.ip_address(sender_domain)

        return 1

    except ValueError:

        return 0


# ==========================================
# 22. Sender Local Part Length
#
# Example:
#
# support@example.com
#
# local part = support
# ==========================================
def SenderLocalPartLength(sender):

    if pd.isna(sender):
        return 0

    sender = str(sender).strip()

    pattern = r"([\w.\-+%]+)@[\w.\-]+\.[a-z]{2,}"

    match = re.search(pattern, sender)

    if match:

        local_part = match.group(1)

        return len(local_part)

    return 0


# ==========================================
# 23. Sender Has Display Name
#
# Example:
#
# Amir <amir@example.com> -> 1
#
# Amir <> -> 0
#
# support@example.com -> 0
# ==========================================


def SenderHasDisplayName(sender):

    if pd.isna(sender):
        return 0

    sender = str(sender).strip()

    pattern = r"^(.+?)\s*<" r"([\w.\-+%]+@[\w.\-]+\.[a-z]{2,})" r">$"

    match = re.search(pattern, sender, re.IGNORECASE)

    if match:

        display_name = match.group(1).strip()

        if display_name:
            return 1

    return 0


# ==========================================
# 24. Get Base Domain
#
# Simple heuristic:
#
# example.com
# mail.example.com -> example.com
# ==========================================


def GetBaseDomain(domain):
if not domain:
return ""

try:
ipaddress.ip_address(domain)
return domain.lower()

except ValueError:
pass

extracted = tldextract.extract(domain)

if not extracted.domain or not extracted.suffix:
return domain.lower()

return f"{extracted.domain}.{extracted.suffix}".lower()


# ==========================================
# 25. Check Domain Mismatch
#
# Sender domain != URL domain
#
# Risk Indicator only.
# NOT part of ML features.
# ==========================================


def CheckDomainMismatch(sender_domain, urls):

    if not sender_domain:
        return 0

    sender_base_domain = GetBaseDomain(sender_domain)

    if not sender_base_domain:
        return 0

    for url in urls:

        url_domain = ExtractURLDomain(url)

        if not url_domain:
            continue

        url_base_domain = GetBaseDomain(url_domain)

        if not url_base_domain:
            continue

        if url_base_domain != sender_base_domain:

            return 1

    return 0


# ==========================================
# 26. Extract All Features
# ==========================================


def ExtractFeatures(sender, body):

    # --------------------------------------
    # Extract URLs from body
    # --------------------------------------

    urls = ExtractURLs(body)

    # --------------------------------------
    # Clean URLs
    # --------------------------------------

    cleaned_urls = []

    for url in urls:

        cleaned_url = CleanURL(url)

        if cleaned_url:

            cleaned_urls.append(cleaned_url)

    urls = cleaned_urls

    # --------------------------------------
    # Sender Domain
    # --------------------------------------

    sender_domain = ExtractSenderDomain(sender)

    # --------------------------------------
    # URL Features
    # --------------------------------------

    url_count = CountURLs(urls)

    max_url_length = MaxURLLength(urls)

    has_https = HasHTTPS(urls)

    has_http = HasHTTP(urls)

    has_at_in_url = HasAtInURL(urls)

    has_shortened_url = HasShortenedURL(urls)

    has_ip_url = HasIPInURL(urls)

    max_subdomain_count = CountSubdomains(urls)

    url_parameter_count = CountURLParameters(urls)

    has_suspicious_characters = HasSuspiciousCharacters(urls)

    has_suspicious_url_word = HasSuspiciousWords(urls)

    # --------------------------------------
    # Sender Features
    # --------------------------------------

    sender_email_length = SenderEmailLength(sender)

    sender_domain_length = SenderDomainLength(sender_domain)

    sender_has_ip = SenderHasIP(sender_domain)

    sender_local_part_length = SenderLocalPartLength(sender)

    sender_has_display_name = SenderHasDisplayName(sender)

    # --------------------------------------
    # Cross Feature
    #
    # Risk Indicator only
    # --------------------------------------

    domain_mismatch = CheckDomainMismatch(sender_domain, urls)

    # --------------------------------------
    # Return all features
    # --------------------------------------

    return {
        # URL Features
        "url_count": url_count,
        "max_url_length": max_url_length,
        "has_https": has_https,
        "has_http": has_http,
        "has_at_in_url": has_at_in_url,
        "has_shortened_url": has_shortened_url,
        "has_ip_url": has_ip_url,
        "max_subdomain_count": max_subdomain_count,
        "url_parameter_count": url_parameter_count,
        "has_suspicious_characters": has_suspicious_characters,
        "has_suspicious_url_word": has_suspicious_url_word,
        # Sender Features
        "sender_email_length": sender_email_length,
        "sender_domain_length": sender_domain_length,
        "sender_has_ip": sender_has_ip,
        "sender_local_part_length": sender_local_part_length,
        "sender_has_display_name": sender_has_display_name,
        # Other
        "sender_domain": sender_domain,
        "domain_mismatch": domain_mismatch,
        "cleaned_urls": urls,
    }


# ==========================================
# 27. Define URL Features
# ==========================================

url_features = [
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
]


# ==========================================
# 28. Define Sender Features
#
# sender_has_ip is kept for analysis,
# but later excluded from ML because
# it is constant in this dataset.
# ==========================================

sender_features = [
    "sender_email_length",
    "sender_domain_length",
    "sender_has_ip",
    "sender_local_part_length",
    "sender_has_display_name",
]


# ==========================================
# 29. Cross Feature
#
# Risk Indicator only
# NOT part of ML features
# ==========================================

cross_features = ["domain_mismatch"]


# ==========================================
# 30. Final ML Features
#
# Exactly 15 features
#
# 11 URL Features
# +
# 4 Sender Features
#
# Excluded:
#
# sender_has_ip
# domain_mismatch
# ==========================================

FINAL_ML_FEATURES = [
    # URL Features
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
    # Sender Features
    "sender_email_length",
    "sender_domain_length",
    "sender_local_part_length",
    "sender_has_display_name",
]


print("\nNumber of URL Features:", len(url_features))

print("Number of Sender Features:", len(sender_features))

print("Number of Final ML Features:", len(FINAL_ML_FEATURES))

print("Domain mismatch is Risk Indicator only.")


# ==========================================
# 31. Apply Feature Extraction To Dataset
# ==========================================

print("\n==========================================")
print("EXTRACTING URL + SENDER FEATURES")
print("==========================================")


features = df.apply(lambda row: ExtractFeatures(row["sender"], row["body"]), axis=1)


# ==========================================
# 32. Convert Features To DataFrame
# ==========================================

features_df = pd.DataFrame(list(features))


# ==========================================
# 33. Validate Feature Extraction
#
# This prevents silent errors.
# ==========================================

expected_feature_columns = FINAL_ML_FEATURES + [
    "sender_has_ip",
    "domain_mismatch",
    "sender_domain",
    "cleaned_urls",
]


missing_feature_columns = [
    column for column in expected_feature_columns if column not in features_df.columns
]


if missing_feature_columns:

    raise ValueError(
        "Feature extraction failed. " "Missing columns: " + str(missing_feature_columns)
    )


print("\nFeature extraction completed successfully.")

print("Extracted Feature Columns:", features_df.columns.tolist())


# ==========================================
# 34. Merge Features With Original Dataset
# ==========================================

df["cleaned_urls"] = features_df["cleaned_urls"]

df["sender_domain"] = features_df["sender_domain"]


for column in features_df.columns:

    if column not in ["cleaned_urls", "sender_domain"]:

        df[column] = features_df[column]


# ==========================================
# 35. Show Feature Examples
# ==========================================

print("\n==========================================")
print("FEATURE EXAMPLES")
print("==========================================")


print(
    df[["email_id"] + FINAL_ML_FEATURES + ["domain_mismatch", "sender_domain"]].head()
)


# ==========================================
# 36. URL Statistics
# ==========================================

print("\n==========================================")
print("URL STATISTICS")
print("==========================================")


print("Emails with extracted URLs:", (df["url_count"] > 0).sum())


print("Emails without extracted URLs:", (df["url_count"] == 0).sum())


print("Total extracted URLs:", df["url_count"].sum())


print("Maximum URLs in one email:", df["url_count"].max())


# ==========================================
# 37. Compare Original urls Column
# With Extracted URLs
# ==========================================

print("\n==========================================")
print("ORIGINAL URL INDICATOR VS EXTRACTION")
print("==========================================")


if "urls" in df.columns:

    print("\nOriginal urls column:")

    print(df["urls"].value_counts(dropna=False))

    print(
        "\nRows with urls = 1 " "but url_count = 0:",
        ((df["urls"] == 1) & (df["url_count"] == 0)).sum(),
    )

    print(
        "Rows with urls = 0 " "but url_count > 0:",
        ((df["urls"] == 0) & (df["url_count"] > 0)).sum(),
    )


# ==========================================
# 38. Sender Statistics
# ==========================================

print("\n==========================================")
print("SENDER STATISTICS")
print("==========================================")


print("Sender domains extracted:", (df["sender_domain"] != "").sum())


print("Sender domains missing:", (df["sender_domain"] == "").sum())


print("Sender display names:", df["sender_has_display_name"].sum())


print("Sender IP:", df["sender_has_ip"].sum())


# ==========================================
# 39. Feature Means By Label
# ==========================================

print("\n==========================================")
print("FEATURE MEANS BY LABEL")
print("==========================================")


if "label" in df.columns:

    feature_means = df.groupby("label")[FINAL_ML_FEATURES].mean().round(4)

    print(feature_means)


# ==========================================
# 40. Correlation With Label
# ==========================================

print("\n==========================================")
print("CORRELATION WITH LABEL")
print("==========================================")


if "label" in df.columns:

    correlations = (
        df[FINAL_ML_FEATURES + ["label"]]
        .corr()["label"]
        .drop("label")
        .sort_values(key=abs, ascending=False)
    )

    print(correlations.round(6))


# ==========================================
# 41. Missing Values
# ==========================================

print("\n==========================================")
print("MISSING VALUES")
print("==========================================")


print(df[FINAL_ML_FEATURES].isnull().sum())


# ==========================================
# 42. Check Constant Features
# ==========================================

print("\n==========================================")
print("CONSTANT FEATURES")
print("==========================================")


constant_features = []


for feature in FINAL_ML_FEATURES:

    if df[feature].nunique(dropna=False) <= 1:

        constant_features.append(feature)


if constant_features:

    print("Constant features:", constant_features)

else:

    print("No constant features.")


# ==========================================
# 43. Risk Indicator Statistics
# ==========================================

print("\n==========================================")
print("RISK INDICATORS")
print("==========================================")


risk_features = [
    "has_ip_url",
    "has_shortened_url",
    "has_at_in_url",
    "has_suspicious_url_word",
    "has_suspicious_characters",
    "max_subdomain_count",
    "url_parameter_count",
    "domain_mismatch",
    "has_http",
]


for feature in risk_features:

    print(feature, "=>", int(df[feature].sum()))


# ==========================================
# 44. Save Dataset
#
# Keep email_id so NLP + URL features
# can later be merged using email_id.
#
# domain_mismatch is also saved because
# it is useful as a Risk Indicator.
# ==========================================

output_columns = (
    ["email_id"] + FINAL_ML_FEATURES + ["sender_domain", "domain_mismatch", "label"]
)


output_df = df[output_columns].copy()


output_df = df[output_columns].copy()

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

output_df.to_csv(OUTPUT_FILE, index=False)

print("Saved to:", os.path.abspath(OUTPUT_FILE))


print("\n==========================================")
print("OUTPUT FILE")
print("==========================================")


print("Saved:", OUTPUT_FILE)


print("Output Shape:", output_df.shape)


print("Output Columns:", output_df.columns.tolist())


# ==========================================
# 45. Backend Function
#
# Used later by Flask / FastAPI
#
# Input:
# sender + body
#
# Output:
# 15 ML Features
# +
# sender domain
# +
# extracted URLs
# +
# domain mismatch
# +
# risk indicators
# ==========================================


def analyze_single_email(sender, body):

    # --------------------------------------
    # Extract all features
    # --------------------------------------

    result = ExtractFeatures(sender, body)

    # --------------------------------------
    # Exactly the 15 ML Features
    # --------------------------------------

    features = {feature: result[feature] for feature in FINAL_ML_FEATURES}

    # --------------------------------------
    # Risk Indicators
    # --------------------------------------

    risk_indicators = []

    # IP URL

    if result["has_ip_url"] == 1:

        risk_indicators.append("URL contains an IP address")

    # Shortened URL

    if result["has_shortened_url"] == 1:

        risk_indicators.append("URL uses a shortened URL service")

    # @ symbol

    if result["has_at_in_url"] == 1:

        risk_indicators.append("URL contains @ character")

    # Suspicious words

    if result["has_suspicious_url_word"] == 1:

        risk_indicators.append("URL contains suspicious words")

    # Suspicious characters

    if result["has_suspicious_characters"] == 1:

        risk_indicators.append("URL contains suspicious characters")

    # Many subdomains

    if result["max_subdomain_count"] >= 3:

        risk_indicators.append("URL contains many subdomains")

    # Many parameters

    if result["url_parameter_count"] >= 5:

        risk_indicators.append("URLs contain many parameters")

    # Domain mismatch

    if result["domain_mismatch"] == 1:

        risk_indicators.append("Sender domain differs from URL domain")

    # HTTP

    if result["has_http"] == 1:

        risk_indicators.append("URL uses HTTP instead of HTTPS")

    # --------------------------------------
    # Return Backend Result
    # --------------------------------------

    return {
        "features": features,
        "sender_domain": result["sender_domain"],
        "extracted_urls": result["cleaned_urls"],
        "domain_mismatch": result["domain_mismatch"],
        "risk_indicators": risk_indicators,
        "indicator_count": len(risk_indicators),
    }


# ==========================================
# 46. Test Backend Function
# ==========================================

print("\n==========================================")
print("BACKEND FUNCTION TEST")
print("==========================================")


test_sender = "support@example.com"


test_body = """

Hello,

Please verify your account.

http://192.168.1.10/login

www.example.com

https://bit.ly/example

Thank you.

"""


test_result = analyze_single_email(test_sender, test_body)


print("\nSender Domain:")

print(test_result["sender_domain"])


print("\nExtracted URLs:")

print(test_result["extracted_urls"])


print("\nML Features:")

print(test_result["features"])


print("\nDomain Mismatch:")

print(test_result["domain_mismatch"])


print("\nRisk Indicators:")


for indicator in test_result["risk_indicators"]:

    print("-", indicator)


print("\nIndicator Count:")

print(test_result["indicator_count"])


# ==========================================
# 47. Finished
# ==========================================

print("\n==========================================")
print("DONE")
print("==========================================")
