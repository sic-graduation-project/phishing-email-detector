"""Safety policy layered over the statistical model.

The model remains the primary signal. High-confidence phishing patterns set a
risk floor so an under-confident model cannot label an obviously dangerous
input as legitimate.
"""

from __future__ import annotations

import re
from typing import Any

URGENT_WORDS = {"urgent", "immediately", "suspended", "locked", "expire", "expired", "alert"}
CREDENTIAL_WORDS = {"password", "credential", "login", "account", "bank", "wallet", "payment"}
ACTION_WORDS = {"verify", "confirm", "update", "click", "signin", "sign-in", "log-in"}
REWARD_WORDS = {"winner", "prize", "free", "congratulations"}


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+(?:-[a-z]+)?", text.lower()))


def apply_risk_policy(
    model_score: float,
    text: str,
    analysis: dict[str, Any],
) -> tuple[float, list[str]]:
    """Return the conservative score and human-readable reasons."""
    features = analysis.get("features", {})
    indicators = list(analysis.get("risk_indicators", []))
    words = _words(text)
    floors: list[float] = [float(model_score)]

    if features.get("has_ip_url"):
        floors.append(82)
    if features.get("has_at_in_url"):
        floors.append(78)
    if features.get("has_shortened_url"):
        floors.append(65)
    if features.get("max_subdomain_count", 0) >= 3:
        floors.append(65)
    if features.get("url_parameter_count", 0) >= 5:
        floors.append(60)
    if features.get("has_suspicious_characters") and features.get("has_suspicious_url_word"):
        floors.append(62)
    if analysis.get("indicator_count", 0) >= 3:
        floors.append(75)
    elif analysis.get("indicator_count", 0) >= 2:
        floors.append(58)

    social_engineering = bool(words & URGENT_WORDS) and bool(words & CREDENTIAL_WORDS) and bool(words & ACTION_WORDS)
    reward_lure = bool(words & REWARD_WORDS) and bool(words & ACTION_WORDS)
    if social_engineering:
        floors.append(72)
        indicators.append("Uses urgent language to request account or credential action")
    if reward_lure:
        floors.append(65)
        indicators.append("Uses a reward lure with a call to action")

    # Preserve order while removing repeated explanations.
    reasons = list(dict.fromkeys(indicators))
    return round(min(max(floors), 100), 2), reasons
