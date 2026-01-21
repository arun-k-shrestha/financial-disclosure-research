import re
from typing import List, Dict

SPEAKER_RE = re.compile(
    r'(?m)(^|\n)(?P<speaker>[A-Z][A-Za-z0-9 .,\-()&/]+):\s*'
)


def split_into_turns(content:str):
    if not content or not content.strip():
        return []
    matches = list(SPEAKER_RE.finditer(content))

    if not matches:
        # fallback: treat as one blob
        return [{"speaker": "unknown", "text": content.strip()}]
    
    turns =[]
    for i, m in enumerate(matches):
        speaker = m.group("speaker").strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        text = content[start:end].strip()
        if text:
            turns.append({"speaker": speaker, "text": text})
    return turns



QA_MARKERS = [
    "question-and-answer session",
    "question and answer session",
    "questions and answers",
    "q&a session",
    "we will now take questions",
    "we will now begin the q&a",

    # your company-specific phrases
    "first question",
    "we're now ready for questions",
    "we are now ready for questions",
    "will take your question",
    "will take your questions",
]

def find_qa_start_index(content: str) -> int | None:
    lower = content.lower()
    idxs = [lower.find(m) for m in QA_MARKERS if lower.find(m) != -1]
    return min(idxs) if idxs else None





