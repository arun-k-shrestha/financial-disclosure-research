import json, hashlib
from typing import Dict, List, Iterable

def stable_hash(s: str) -> str:
    print(hashlib.sha1(s.encode("utf-8")).hexdigest()[:16])
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]

def chunk_text(text: str, max_chars: int = 2200, overlap: int = 200) -> List[str]:
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks

def iter_jsonl(path: str) -> Iterable[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def build_passages(canonical_jsonl: str) -> List[Dict]:
    passages = []
    for row in iter_jsonl(canonical_jsonl):
        doc_key = f'{row["doc_type"]}|{row["ticker"]}|{row.get("period","")}|{row.get("date","")}'
        doc_id = stable_hash(doc_key)

        turn_key = f'{doc_key}|{row.get("section","")}|{row.get("speaker","")}|{stable_hash(row["text"])}'
        turn_id = stable_hash(turn_key)

        for i, ch in enumerate(chunk_text(row["text"])):
            chunk_id = stable_hash(f"{turn_id}|{i}")
            passages.append({
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "doc_type": row["doc_type"],
                "ticker": row["ticker"],
                "period": row.get("period"),
                "date": row.get("date"),
                "section": row.get("section"),
                "speaker": row.get("speaker"),
                "text": ch,
            })
    return passages

try:
    passages = build_passages("canonical_calls.jsonl")
    passage_by_id = {p["chunk_id"]: p for p in passages}
    tickers = sorted({p["ticker"] for p in passages})
    # print(passages)
    print("Tickers:", tickers)
except Exception as e:
    print(e)