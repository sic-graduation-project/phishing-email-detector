"""Type-specific phishing risk policies."""
from __future__ import annotations
import re
from typing import Any

URGENT_WORDS = {"urgent", "immediately", "suspended", "locked", "expire", "expired", "alert"}
CREDENTIAL_WORDS = {"password", "credential", "credentials", "login", "account", "bank", "wallet", "payment"}
ACTION_WORDS = {"verify", "confirm", "update", "click", "signin", "sign-in", "log-in", "open"}
REWARD_WORDS = {"winner", "prize", "free", "congratulations", "reward", "gift"}

def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+(?:-[a-z]+)?", text.lower()))

def _deduplicate(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))

def score_url_analysis(analysis: dict[str, Any]) -> tuple[float, list[str]]:
    """Score URL features without applying the email-trained model."""
    features = analysis.get("features", {})
    reasons = list(analysis.get("risk_indicators", []))
    floors = [5.0]
    if features.get("has_ip_url"): floors.append(90)
    if features.get("has_at_in_url"): floors.append(85)
    if features.get("has_shortened_url"): floors.append(70)
    if features.get("max_subdomain_count", 0) >= 3: floors.append(65)
    if features.get("url_parameter_count", 0) >= 5: floors.append(60)
    if features.get("has_suspicious_characters") and features.get("has_suspicious_url_word"):
        floors.append(70)
    elif features.get("has_suspicious_url_word"):
        floors.append(60)
    if features.get("has_http") and features.get("has_suspicious_url_word"):
        floors.append(75)
    elif features.get("has_http"):
        floors.append(25)
    if analysis.get("indicator_count", 0) >= 3: floors.append(85)
    elif analysis.get("indicator_count", 0) >= 2: floors.append(65)
    return round(min(max(floors), 100), 2), _deduplicate(reasons)

def score_text_analysis(text: str, analysis: dict[str, Any]) -> tuple[float, list[str]]:
    """Score explicit social-engineering language and embedded URLs."""
    words = _words(text)
    reasons: list[str] = []
    floors = [5.0]
    urgent = bool(words & URGENT_WORDS)
    credential = bool(words & CREDENTIAL_WORDS)
    action = bool(words & ACTION_WORDS)
    reward = bool(words & REWARD_WORDS)
    if urgent and credential and action:
        floors.append(85)
        reasons.append("Uses urgent language to request account or credential action")
    elif credential and action:
        floors.append(65)
        reasons.append("Requests an account or credential-related action")
    elif urgent and action:
        floors.append(45)
        reasons.append("Uses urgent language with a call to action")
    if reward and action:
        floors.append(70)
        reasons.append("Uses a reward lure with a call to action")
    if analysis.get("features", {}).get("url_count", 0):
        url_score, url_reasons = score_url_analysis(analysis)
        floors.append(url_score)
        reasons.extend(url_reasons)
    return round(min(max(floors), 100), 2), _deduplicate(reasons)

def apply_email_risk_policy(model_score: float, text: str, analysis: dict[str, Any]) -> tuple[float, list[str]]:
    """Combine the in-distribution email model with conservative safety floors."""
    features = analysis.get("features", {})
    reasons = list(analysis.get("risk_indicators", []))
    words = _words(text)
    floors = [float(model_score)]
    if features.get("url_count", 0):
        url_score, _ = score_url_analysis(analysis)
        floors.append(url_score)
    if bool(words & URGENT_WORDS) and bool(words & CREDENTIAL_WORDS) and bool(words & ACTION_WORDS):
        floors.append(85)
        reasons.append("Uses urgent language to request account or credential action")
    if bool(words & REWARD_WORDS) and bool(words & ACTION_WORDS):
        floors.append(70)
        reasons.append("Uses a reward lure with a call to action")
    return round(min(max(floors), 100), 2), _deduplicate(reasons)

apply_risk_policy = apply_email_risk_policy
