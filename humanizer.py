"""
Humanizer & Dramatic Word-Stretching Engine
Implements Phrase-Final Lengthening, Terminal Deceleration, and Vowel Stretching
to eliminate the 'reading off a script' robotic feel.
"""

import re

ABBREVIATIONS = {
    r"\be\.g\.\b": "for example",
    r"\bi\.e\.\b": "that is",
    r"\betc\.\b": "etcetera",
    r"\bvs\.\b": "versus",
    r"\bDr\.\b": "Doctor",
    r"\bMr\.\b": "Mister",
    r"\bMrs\.\b": "Missus",
    r"\bMs\.\b": "Mizz",
    r"\bProf\.\b": "Professor",
    r"\bapprox\.\b": "approximately",
}

CURRENCIES = [
    (r"\$(\d+(?:\.\d{1,2})?)\s*(?:M|m|million)\b", r"\1 million dollars"),
    (r"\$(\d+(?:\.\d{1,2})?)\s*(?:B|b|billion)\b", r"\1 billion dollars"),
    (r"\$(\d+(?:\.\d{1,2})?)\b", r"\1 dollars"),
    (r"₹(\d+(?:\.\d{1,2})?)\s*(?:Cr|cr|crore)\b", r"\1 crore rupees"),
    (r"₹(\d+(?:\.\d{1,2})?)\s*(?:L|l|lakh)\b", r"\1 lakh rupees"),
    (r"₹(\d+(?:\.\d{1,2})?)\b", r"\1 rupees"),
]

# Words that sound 10x more dramatic when elongated slightly
EMPHASIS_KEYWORDS = [
    "never", "nothing", "everything", "forever", "always",
    "impossible", "secret", "truth", "lie", "dead", "alive",
    "destroy", "vanish", "silence", "alone", "nowhere", "finally"
]

def normalize_text(text: str) -> str:
    """Expands numbers, currencies, abbreviations, and acronyms."""
    cleaned = text.strip()
    for pattern, replacement in ABBREVIATIONS.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    for pattern, replacement in CURRENCIES:
        cleaned = re.sub(pattern, replacement, cleaned)
    cleaned = re.sub(r"(\d+(?:\.\d+)?)%", r"\1 percent", cleaned)

    acronyms = ["AI", "API", "UI", "UX", "CEO", "CTO", "CFO", "NASA", "URL", "HTML", "SQL"]
    for acr in acronyms:
        cleaned = re.sub(r"\b" + acr + r"\b", ".".join(list(acr)) + ".", cleaned)
    return cleaned

def stretch_dramatic_words(text: str) -> str:
    """
    Applies vowel elongation and pause anchors to emphasize key words.
    E.g., *never* -> 'nev... er' or 'never...'
    """
    # 1. Custom user emphasis markup: *word* -> word... (forces phoneme hold)
    text = re.sub(r"\*([a-zA-Z]+)\*", r"\1...", text)

    # 2. Key dramatic words get subtle pause anchoring if they appear near sentence ends
    for kw in EMPHASIS_KEYWORDS:
        pattern = r"\b(" + kw + r")([.!?])"
        text = re.sub(pattern, r"\1... \2", text, flags=re.IGNORECASE)

    return text

def apply_terminal_lengthening(text: str) -> str:
    """
    Fixes the 'abrupt script reading' flaw at sentence endings.
    In human speech (Phrase-Final Lengthening), the final stressed syllable
    is held 50% longer with a decaying pitch glide. Adding trailing ellipses
    and breath commas prevents the neural model from slamming into an abrupt <EOS>.
    """
    # Replace hard period with trailing thought if it sounds too abrupt
    sentences = re.split(r"(?<=[.!?])\s+", text)
    enhanced = []

    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # If sentence ends with single period, replace with soft trailing pause
        if s.endswith(".") and not s.endswith("..."):
            s = s[:-1] + "..."
        enhanced.append(s)

    return " ".join(enhanced)

def humanize_cadence(text: str, stretch: bool = True) -> str:
    """
    Complete pipeline: normalizes text, injects breathing pauses, and applies
    phrase-final lengthening to stop the robotic script-reading effect.
    """
    normalized = normalize_text(text)
    normalized = normalized.replace(";", "... ")
    normalized = re.sub(r"\s*—\s*", "... ", normalized)
    normalized = re.sub(r"\s*-\s*", " - ", normalized)

    if stretch:
        normalized = stretch_dramatic_words(normalized)
        normalized = apply_terminal_lengthening(normalized)

    return normalized
