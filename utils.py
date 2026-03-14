from config import LANGUAGE
from locales import STOPWORDS


def extract_keywords(text):
    stopwords = STOPWORDS.get(LANGUAGE, STOPWORDS["en"])
    words = text.lower().split()
    keywords = []
    seen = set()
    for w in words:
        clean = w.strip(".,!?'\";:")
        if clean not in stopwords and len(clean) > 3 and clean not in seen:
            seen.add(clean)
            keywords.append(clean)
    return keywords[:8]