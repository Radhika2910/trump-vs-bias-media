from __future__ import annotations

import re


def clean_text(text: str) -> str:
    text = str(text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"[^A-Za-z0-9\s'.,!?-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

