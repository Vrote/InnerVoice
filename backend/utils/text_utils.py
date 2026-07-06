# backend/utils/text_utils.py
import re

def clean_text(text: str) -> str:
    """
    Cleans up input text by stripping extra whitespaces and standardizing linebreaks.
    """
    if not text:
        return ""
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Replace multiple newlines with at most two newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
