"""
HW3 Part 2 — Earnings Pipeline (8-K Item 2.02)

For five companies, pull the four most recent 8-K filings that report
Results of Operations (Item 2.02), download the earnings press release
exhibit (EX-99.1), and extract revenue, diluted EPS, net income and the
reporting period with regex. Missing fields are stored as "NOT_FOUND".

Output: hw03/earnings_history.csv
Run:    python hw03/hw03_earnings.py
"""

import csv
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
HEADERS = {"User-Agent": "MIS3060 Villanova csoderma@villanova.edu"}
REQUEST_PAUSE = 0.2          # SEC allows 10 requests/second
FILINGS_PER_COMPANY = 4
NOT_FOUND = "NOT_FOUND"

OUT_DIR = Path(__file__).resolve().parent
OUT_CSV = OUT_DIR / "earnings_history.csv"
COLUMNS = ["company", "ticker", "cik", "filing_date", "period",
           "revenue_reported", "eps_diluted", "net_income"]

COMPANIES = [
    ("Apple Inc.",            "AAPL", "0000320193"),
    ("Microsoft Corporation", "MSFT", "0000789019"),
    ("NVIDIA Corporation",    "NVDA", "0001045810"),
    ("JPMorgan Chase & Co.",  "JPM",  "0000019617"),
    ("Walmart Inc.",          "WMT",  "0000104169"),
]


# ---------------------------------------------------------------------------
# HTTP — every request goes through this helper so the User-Agent is never lost
# ---------------------------------------------------------------------------
def sec_get(url):
    """GET a URL with the SEC User-Agent header; one retry on failure/throttle."""
    for attempt in range(2):
        time.sleep(REQUEST_PAUSE)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code in (429, 503) and attempt == 0:
                time.sleep(2)
                continue
            resp.raise_for_status()
            return resp
        except requests.RequestException:
            if attempt == 1:
                raise
            time.sleep(2)


def html_to_text(html):
    """Strip HTML tags and collapse whitespace into one searchable string."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(" ").replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# Step 1 — find Item 2.02 8-K filings
# ---------------------------------------------------------------------------
def earnings_filings(cik):
    """Return the most recent 8-K filings whose items include 2.02."""
    data = sec_get(f"https://data.sec.gov/submissions/CIK{cik}.json").json()
    recent = data["filings"]["recent"]
    rows = zip(recent["form"], recent["items"], recent["filingDate"],
               recent["accessionNumber"])
    matches = [
        {"filing_date": date, "accession": acc}
        for form, items, date, acc in rows
        if form == "8-K" and "2.02" in items   # "8-K/A" amendments excluded
    ]
    matches.sort(key=lambda r: r["filing_date"], reverse=True)
    return matches[:FILINGS_PER_COMPANY]


# ---------------------------------------------------------------------------
# Step 2 — locate the press release exhibit on the filing index page
# ---------------------------------------------------------------------------
def find_press_release_url(cik, accession):
    """Return the URL of the EX-99.1 press release .htm, or None if absent."""
    folder = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}"
    index_url = f"{folder}/{accession}-index.htm"
    soup = BeautifulSoup(sec_get(index_url).text, "html.parser")

    docs = []
    for tr in soup.select("table.tableFile tr"):
        cells = tr.find_all("td")
        link = tr.find("a")
        if len(cells) < 4 or link is None:
            continue
        href = link["href"].split("?doc=")[-1]      # strip inline-XBRL viewer prefix
        docs.append({
            "description": cells[1].get_text(" ", strip=True).lower(),
            "type": cells[3].get_text(strip=True).upper(),
            "url": "https://www.sec.gov" + href,
        })

    htm = [d for d in docs if d["url"].lower().endswith((".htm", ".html"))]
    exhibits = [d for d in htm if d["type"].startswith("EX-99")]
    for rule in (
        lambda d: d["type"] == "EX-99.1",
        lambda d: "press release" in d["description"] or "results" in d["description"],
        lambda d: True,
    ):
        hits = [d for d in exhibits if rule(d)]
        if hits:
            return hits[0]["url"]
    return None


# ---------------------------------------------------------------------------
# Step 3 — regex extraction
# Patterns are tried in order; the first match wins. Headline sentences come
# first, financial-statement table rows (values in millions) are fallbacks.
# ---------------------------------------------------------------------------
MONEY = r"\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)"
UNIT = r"\s*(billion|million)"

REVENUE_PATTERNS = [
    # "revenue of $109.4 billion", "Revenue was $90.0 billion",
    # "reported revenue for the second quarter ended July 26, 2026, of $96.2 billion"
    r"(?<![\w-])(?:quarterly |reported |total |net )?(?:revenues?|net sales)"
    r"(?: for the [^$•]{0,70}?)?,?\s(?:was|were|of|totaled|reached)?\s?" + MONEY + UNIT,
    # table fallbacks (in millions)
    r"Total net sales\s*" + MONEY,
    r"Total net revenue\s*" + MONEY,
    r"Total revenues?\s*" + MONEY,
    r"\bRevenue\s*" + MONEY,
]

NET_INCOME_PATTERNS = [
    r"net income (?:was|of|were|totaled)\s?" + MONEY + UNIT,
    # table fallbacks (in millions)
    r"Consolidated net income attributable to \w+\s*" + MONEY,
    r"\bNet income\s*" + MONEY,
]

EPS_PATTERNS = [
    r"diluted earnings per share (?:was|of|were)\s?\$\s?(\d+\.\d{2})",
    r"earnings per diluted share (?:was|were|of)\s?\$\s?(\d+\.\d{2})",
    r"\$\s?(\d+\.\d{2}) per diluted share",
    r"GAAP EPS of \$\s?(\d+\.\d{2})",
    r"\(\s?\$\s?(\d+\.\d{2}) per share\)",
    # table fallbacks
    r"Earnings per share\s*-\s*diluted\s*\$?\s?(\d+\.\d{2})",
    r"Diluted net income per common share attributable to \w+\s*\$?\s?(\d+\.\d{2})",
    r"\bDiluted\s*\$\s?(\d+\.\d{2})",
]

ORDINAL = r"(first|second|third|fourth)"
DATE = r"((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})"


def first_match(patterns, text):
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m
    return None


def extract_money(patterns, text):
    """Return e.g. '109.4 billion' (headline) or '29,789 million' (table)."""
    m = first_match(patterns, text)
    if not m:
        return NOT_FOUND
    unit = m.group(2).lower() if m.lastindex and m.lastindex >= 2 else "million"
    return f"{m.group(1)} {unit}"


def extract_eps(text):
    m = first_match(EPS_PATTERNS, text)
    return m.group(1) if m else NOT_FOUND


def extract_period(text):
    """Normalize to e.g. 'third quarter fiscal 2026' or 'second quarter 2026'."""
    head = text[:6000]      # the period is always stated near the top
    m = re.search(r"fiscal (\d{4}) " + ORDINAL + r" quarter", head, re.I)          # Apple
    if m:
        return f"{m.group(2).lower()} quarter fiscal {m.group(1)}"
    # NVDA: "Second Quarter Fiscal 2027", "Fourth Quarter and Fiscal 2026"
    m = re.search(ORDINAL + r"[ -]quarter (?:of |and )?fiscal (?:year )?(\d{4})", head, re.I)
    if m:
        return f"{m.group(1).lower()} quarter fiscal {m.group(2)}"
    m = re.search(r"\bQ([1-4]) FY(\d{2})\b", text)                                 # WMT tables
    if m:
        quarter = ["first", "second", "third", "fourth"][int(m.group(1)) - 1]
        return f"{quarter} quarter fiscal 20{m.group(2)}"
    m = re.search(ORDINAL + r"[ -]quarter (?:of )?(\d{4})", head, re.I)            # JPM
    if m:
        return f"{m.group(1).lower()} quarter {m.group(2)}"
    ordinal = re.search(ORDINAL + r"[ -]quarter", head, re.I)                      # MSFT, WMT
    ended = re.search(r"(?:quarter|three months) ended,? " + DATE, head, re.I)
    if ordinal and ended:
        return f"{ordinal.group(1).lower()} quarter (ended {ended.group(1)})"
    if ended:
        return f"quarter ended {ended.group(1)}"
    if ordinal:
        return f"{ordinal.group(1).lower()} quarter"
    return NOT_FOUND


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def fmt(value):
    return value if value == NOT_FOUND else f"${value}"


def main():
    sys.stdout.reconfigure(encoding="utf-8")    # Windows console can't print curly quotes etc.
    rows = []
    for company, ticker, cik in COMPANIES:
        try:
            filings = earnings_filings(cik)
        except Exception as exc:                       # keep going on API failure
            print(f"WARNING: {ticker}: could not read submissions API ({exc}) — skipping company")
            continue
        if not filings:
            print(f"WARNING: {ticker}: no Item 2.02 8-K filings found")
            continue

        for filing in filings:
            try:
                url = find_press_release_url(cik, filing["accession"])
                if url is None:
                    print(f"WARNING: {ticker} {filing['filing_date']}: press release exhibit not found — skipping")
                    continue
                text = html_to_text(sec_get(url).text)
            except Exception as exc:
                print(f"WARNING: {ticker} {filing['filing_date']}: download failed ({exc}) — skipping")
                continue

            row = {
                "company": company,
                "ticker": ticker,
                "cik": cik,
                "filing_date": filing["filing_date"],
                "period": extract_period(text),
                "revenue_reported": extract_money(REVENUE_PATTERNS, text),
                "eps_diluted": extract_eps(text),
                "net_income": extract_money(NET_INCOME_PATTERNS, text),
            }
            rows.append(row)
            print(f"{ticker} | {row['period']} | Revenue: {fmt(row['revenue_reported'])} | "
                  f"EPS: {fmt(row['eps_diluted'])} | Net Income: {fmt(row['net_income'])}")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
