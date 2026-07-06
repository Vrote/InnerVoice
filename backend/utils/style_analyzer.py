# backend/utils/style_analyzer.py
import re

HINGLISH_WORDS = {
    "yaar", "bhai", "kya", "kyun", "kaise", "hai", "nahi", "haan", "aur", "phir", "abhi", "kal", "aaj", "sab", 
    "kuch", "bahut", "thoda", "bohot", "theek", "accha", "areh", "arre", "yeh", "woh", "mera", "tera", "apna", 
    "karein", "karo", "hua", "thi", "tha", "gaya", "gayi", "laga", "raha", "rahi", "pata", "lagta", "saamne", 
    "saath", "baad", "pehle", "toh", "par", "lekin", "sirf", "bas", "bhi", "mat", "zyada", "pata nahi", "kya bolu", 
    "honestly", "seriously", "bro"
}

def analyze_style_pure_python(text: str) -> dict:
    """
    Analyzes a block of text for sentence length, formality, Hinglish ratio, 
    ellipses, emoji usage, exclamation count, question count, and vocabulary richness.
    """
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    num_sentences = len(sentences) if sentences else 1
    
    words = [w.strip(".,!?;:\"'") for w in text.split() if w.strip()]
    num_words = len(words)
    
    if num_words == 0:
        return {
            "avg_sentence_length": 0.0,
            "avg_entry_length": 0.0,
            "formality_score": 0.5,
            "hinglish_ratio": 0.0,
            "uses_english_only": True,
            "detected_languages": "english",
            "uses_ellipsis": False,
            "uses_caps_emphasis": False,
            "uses_emoji": False,
            "exclamation_ratio": 0.0,
            "question_ratio": 0.0,
            "dominant_tone": "neutral",
            "vocabulary_richness": 0.5,
        }
    
    avg_sentence_length = num_words / num_sentences
    avg_entry_length = num_words
    
    uses_ellipsis = "..." in text
    
    # Capitalized emphasis (e.g. LITERALLY, OMG, excludes 'I', 'A')
    caps_words = [w for w in words if w.isupper() and len(w) > 1 and not w.isdigit()]
    uses_caps_emphasis = len(caps_words) > 0
    
    # Basic unicode range check for emojis
    emoji_pattern = re.compile(r'[\U00010000-\U0010ffff\u2600-\u27bf]', flags=re.UNICODE)
    uses_emoji = bool(emoji_pattern.search(text))
    
    exclamation_count = text.count("!")
    question_count = text.count("?")
    exclamation_ratio = exclamation_count / num_sentences
    question_ratio = question_count / num_sentences
    
    hinglish_count = sum(1 for w in words if w.lower() in HINGLISH_WORDS)
    hinglish_ratio = hinglish_count / num_words
    uses_english_only = hinglish_ratio < 0.05
    detected_languages = "english" if uses_english_only else "english, hinglish"
    
    informal_markers = {"don't", "can't", "won't", "bruh", "bro", "yaar", "literally", "seriously", "honestly", "maybe", "like"}
    informal_count = sum(1 for w in words if w.lower() in informal_markers)
    formality_score = max(0.0, min(1.0, 1.0 - (informal_count / (num_words / 10 + 1))))
    
    dominant_tone = "casual" if hinglish_ratio > 0.1 or informal_count > 1 else "neutral"
    vocabulary_richness = len(set(w.lower() for w in words)) / num_words
    
    return {
        "avg_sentence_length": avg_sentence_length,
        "avg_entry_length": float(avg_entry_length),
        "formality_score": formality_score,
        "hinglish_ratio": hinglish_ratio,
        "uses_english_only": uses_english_only,
        "detected_languages": detected_languages,
        "uses_ellipsis": uses_ellipsis,
        "uses_caps_emphasis": uses_caps_emphasis,
        "uses_emoji": uses_emoji,
        "exclamation_ratio": exclamation_ratio,
        "question_ratio": question_ratio,
        "dominant_tone": dominant_tone,
        "vocabulary_richness": vocabulary_richness,
    }
