import re
from typing import List, Dict
from pathlib import Path
import json

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


def split_into_turns_with_offsets(content: str):
    matches = list(SPEAKER_RE.finditer(content))
    if not matches:
        return [{"speaker": "unknown", "text": content.strip(), "start": 0}]

    turns = []
    for i, m in enumerate(matches):
        speaker = m.group("speaker").strip()
        start_text = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        text = content[start_text:end].strip()
        if text:
            turns.append({"speaker": speaker, "text": text, "start": start_text})
    return turns



def canonical_period(year: int, period: str) -> str:
    # input period is "Q1" in your example
    return f"{year}_{period.upper()}"

def calls_to_canonical_rows(call_objs):
    rows = []
    for call in call_objs:
        ticker = call.get("symbol")
        year = call.get("year")
        period = call.get("period")
        date = call.get("date")
        content = call.get("content", "")

        period_key = canonical_period(year, period)
        qa_start = find_qa_start_index(content)
        turns = split_into_turns_with_offsets(content)

        for t in turns:
            section = "prepared"
            if qa_start is not None and t["start"] >= qa_start:
                section = "qa"

            rows.append({
                "doc_type": "earnings_call",
                "ticker": ticker,
                "period": period_key,
                "date": date,
                "section": section,
                "speaker": t["speaker"],
                "text": t["text"],
            })
    return rows

def write_jsonl(path: str, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

# call_objs = json.load(open("data/earnings_call_transcripts/CFLT/2023_Q1.json","r",encoding="utf-8"))
# rows = calls_to_canonical_rows(call_objs)
# write_jsonl("canonical_calls.jsonl", rows)

ALL_ROWS = []

BASE_DIR = Path("data/earnings_call_transcripts")

for ticker_dir in BASE_DIR.iterdir():          # CFLT/, PCTY/, ...
    if not ticker_dir.is_dir():
        continue

    for json_file in ticker_dir.glob("*.json"):  # 2023_Q1.json, 2024_Q2.json, ...
        print(f"Loading {json_file}")

        with open(json_file, "r", encoding="utf-8") as f:
            call_objs = json.load(f)

        rows = calls_to_canonical_rows(call_objs)
        ALL_ROWS.extend(rows)

write_jsonl("canonical_calls.jsonl", ALL_ROWS)