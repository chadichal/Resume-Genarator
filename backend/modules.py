import re
from collections import Counter

ROLE_KEYWORDS = {
    "Generative AI Intern": [
        "python", "machine learning", "deep learning", "neural network",
        "nlp", "transformer", "large language model", "llm",
        "pytorch", "tensorflow", "huggingface", "prompt engineering",
        "data preprocessing", "model evaluation"
    ],
    "Data Scientist": [
        "python", "statistics", "regression", "classification",
        "sql", "data visualization", "pandas", "scikit-learn"
    ],
    # Add more roles as needed
}

def _tokenize(text: str):
    return re.findall(r"[a-zA-Z]+", text.lower())

def calculate_ats_score(resume_text: str, job_role: str):
    tokens = _tokenize(resume_text)
    freq = Counter(tokens)
    keywords = ROLE_KEYWORDS.get(job_role, [])
    if not keywords:
        return 50.0, 0, 0, {}
    matched = 0
    breakdown = {}
    for kw in keywords:
        count = freq.get(kw.lower(), 0)
        if count > 0:
            matched += 1
        breakdown[kw] = count
    total = len(keywords)
    score = (matched / total) * 100.0
    return round(score, 2), matched, total, breakdown