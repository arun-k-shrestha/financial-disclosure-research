from pathlib import Path
import json
import time
import requests

API_BASE = "https://financialmodelingprep.com/stable"
API_KEY = "#"

ROOT = Path("data")

SYMBOLS = ["PCTY", "CFLT"]

YEARS = range(2023, 2026)  #2023, 2024, 2025
QUARTERS = [1, 2, 3, 4]

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def write_json(path: Path, data) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def fetch_json(endpoint: str, params: dict) -> dict:
    url = f"{API_BASE}/{endpoint}"
    full_params = dict(params)
    full_params["apikey"] = API_KEY

    r = requests.get(url, params=full_params, timeout=60)
    r.raise_for_status()
    return r.json()


def transcript_path(symbol: str, year: int, quarter: int) -> Path:
    return ROOT / "earnings_call_transcripts" / symbol / f"{year}_Q{quarter}.json"

def tenk_path(symbol: str, year: int) -> Path:
    # FY report JSON (commonly aligned to annual report / 10-K-style data)
    return ROOT / "10K_filing" / symbol / f"{year}_FY.json"

def download_earnings_call_transcript(symbol: str, year: int, quarter: int) -> bool:
    data = fetch_json(
        endpoint="earning-call-transcript",
        params={"symbol": symbol, "year": year, "quarter": quarter},
    )

    if not data:
        return False

    out = transcript_path(symbol, year, quarter)
    write_json(out, data)
    return True


def download_annual_report_json(symbol: str, year: int) -> bool:
    data = fetch_json(
        endpoint="financial-reports-json",
        params={"symbol": symbol, "year": year, "period": "FY"},
    )

    if not data:
        return False

    out = tenk_path(symbol, year)
    write_json(out, data)
    return True

def main() -> None:
    # Earnings call transcripts (year + quarter)
    for symbol in SYMBOLS:
        for year in YEARS:
            for quarter in QUARTERS:
                saved = download_earnings_call_transcript(symbol, year, quarter)
                print(f"[transcript] {symbol} {year} Q{quarter}: {'OK' if saved else 'no data'}")


    #Annual financial report JSON (year, FY)
    for symbol in SYMBOLS:
        for year in YEARS:
            saved = download_annual_report_json(symbol, year)
            print(f"[FY report]  {symbol} {year}: {'OK' if saved else 'no data'}")


if __name__ == "__main__":
    main()
