"""Runtime URL and sender feature extraction used by the API and ML model."""

import ipaddress
import re
from urllib.parse import urlparse

import tldextract


URL_PATTERN = re.compile(r'(?:https?://|www\.)[^\s<>"\'\]\)]+', re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"[\w.\-+%]+@([\w.\-]+\.[a-z]{2,})", re.IGNORECASE)
FULL_EMAIL_PATTERN = re.compile(r"[\w.\-+%]+@[\w.\-]+\.[a-z]{2,}", re.IGNORECASE)
DISPLAY_NAME_PATTERN = re.compile(
    r"^(.+?)\s*<([\w.\-+%]+@[\w.\-]+\.[a-z]{2,})>$",
    re.IGNORECASE,
)
# Use the bundled suffix snapshot without a shared cache. API requests must not
# perform network access or wait on a cache lock.
TLD_EXTRACTOR = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)

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

SUSPICIOUS_WORDS = {
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
}

FINAL_ML_FEATURES = [
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


def _clean_url(url: str) -> str:
    return url.rstrip(".,;:!?)]}'\"")


def _hostname(url: str) -> str:
    normalized = f"http://{url}" if url.lower().startswith("www.") else url
    try:
        return (urlparse(normalized).hostname or "").lower()
    except ValueError:
        return ""


def _is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def _base_domain(domain: str) -> str:
    if not domain or _is_ip(domain):
        return domain.lower()
    extracted = TLD_EXTRACTOR(domain)
    if not extracted.domain or not extracted.suffix:
        return domain.lower()
    return f"{extracted.domain}.{extracted.suffix}".lower()


def _extract_urls(body: str) -> list[str]:
    return [_clean_url(url) for url in URL_PATTERN.findall(str(body or ""))]


def _sender_details(sender: str) -> tuple[str, str, int]:
    sender = str(sender or "").strip()
    email_match = FULL_EMAIL_PATTERN.search(sender)
    email = email_match.group(0) if email_match else ""
    domain_match = EMAIL_PATTERN.search(sender)
    domain = domain_match.group(1).lower() if domain_match else ""
    has_display_name = int(bool(DISPLAY_NAME_PATTERN.search(sender)))
    return email, domain, has_display_name


def _extract_features(sender: str, body: str) -> dict[str, int | str | list[str]]:
    urls = _extract_urls(body)
    domains = [_hostname(url) for url in urls]
    email, sender_domain, sender_has_display_name = _sender_details(sender)

    max_subdomains = 0
    for domain in domains:
        if domain and not _is_ip(domain):
            max_subdomains = max(max_subdomains, max(0, len(domain.split(".")) - 2))

    parameter_count = 0
    for url in urls:
        normalized = f"http://{url}" if url.lower().startswith("www.") else url
        query = urlparse(normalized).query
        parameter_count += len([part for part in query.split("&") if part])

    sender_base_domain = _base_domain(sender_domain)
    domain_mismatch = int(
        bool(sender_base_domain)
        and any(
            domain and _base_domain(domain) != sender_base_domain
            for domain in domains
        )
    )

    local_part = email.split("@", 1)[0] if email else ""
    return {
        "url_count": len(urls),
        "max_url_length": max((len(url) for url in urls), default=0),
        "has_https": int(any(url.lower().startswith("https://") for url in urls)),
        "has_http": int(any(url.lower().startswith("http://") for url in urls)),
        "has_at_in_url": int(any("@" in url for url in urls)),
        "has_shortened_url": int(
            any(
                domain in SHORTENER_DOMAINS
                or any(domain.endswith(f".{shortener}") for shortener in SHORTENER_DOMAINS)
                for domain in domains
            )
        ),
        "has_ip_url": int(any(domain and _is_ip(domain) for domain in domains)),
        "max_subdomain_count": max_subdomains,
        "url_parameter_count": parameter_count,
        "has_suspicious_characters": int(any(char in url for url in urls for char in "@%_")),
        "has_suspicious_url_word": int(
            any(word in url.lower() for url in urls for word in SUSPICIOUS_WORDS)
        ),
        "sender_email_length": len(email),
        "sender_domain_length": len(sender_domain),
        "sender_local_part_length": len(local_part),
        "sender_has_display_name": sender_has_display_name,
        "sender_domain": sender_domain,
        "domain_mismatch": domain_mismatch,
        "cleaned_urls": urls,
    }


def analyze_single_email(sender: str, body: str) -> dict[str, object]:
    """Extract model features and human-readable indicators for one input."""
    result = _extract_features(sender, body)
    features = {name: result[name] for name in FINAL_ML_FEATURES}
    indicators: list[str] = []

    checks = [
        (result["has_ip_url"] == 1, "URL contains an IP address"),
        (result["has_shortened_url"] == 1, "URL uses a shortened URL service"),
        (result["has_at_in_url"] == 1, "URL contains @ character"),
        (result["has_suspicious_url_word"] == 1, "URL contains suspicious words"),
        (result["has_suspicious_characters"] == 1, "URL contains suspicious characters"),
        (result["max_subdomain_count"] >= 3, "URL contains many subdomains"),
        (result["url_parameter_count"] >= 5, "URLs contain many parameters"),
        (result["domain_mismatch"] == 1, "Sender domain differs from URL domain"),
        (result["has_http"] == 1, "URL uses HTTP instead of HTTPS"),
    ]
    indicators.extend(message for condition, message in checks if condition)

    return {
        "features": features,
        "sender_domain": result["sender_domain"],
        "extracted_urls": result["cleaned_urls"],
        "domain_mismatch": result["domain_mismatch"],
        "risk_indicators": indicators,
        "indicator_count": len(indicators),
    }
