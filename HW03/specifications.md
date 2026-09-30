# HW3 Specifications — SEC EDGAR 8-K Pipelines

**Student:** Carl Soderman
**Written:** 2026-09-30, before any code was generated

Both scripts use the same five companies and CIKs exactly as given (no lookup):

| Company | Ticker | CIK |
|---|---|---|
| Apple Inc. | AAPL | 0000320193 |
| Microsoft Corporation | MSFT | 0000789019 |
| NVIDIA Corporation | NVDA | 0001045810 |
| JPMorgan Chase & Co. | JPM | 0000019617 |
| Walmart Inc. | WMT | 0000104169 |

Dependencies: `requests`, `beautifulsoup4` (and the Python standard library: `re`, `csv`, `time`, `datetime`). All output files are written into the same folder as the script (`hw03/`), regardless of the directory the script is run from.

---

## Specification A — Earnings Pipeline (Item 2.02) → `hw03/hw03_earnings.py`

Write a Python script that builds a four-quarter earnings history for the five companies above from their SEC 8-K filings.

**1. HTTP setup.** Define one headers dictionary with `User-Agent: "MIS3060 Villanova csoderma@villanova.edu"` and pass it on **every** `requests.get()` call — the submissions API, the filing index pages, and the exhibit downloads, not just the first request. Route all requests through one helper function so no call can forget the header. Pause about 0.2 seconds between requests to stay under SEC's 10 requests/second limit, use a timeout (~30 s), and retry once on a failed or rate-limited (429/503) response.

**2. Find the filings.** For each company, GET `https://data.sec.gov/submissions/CIK{cik}.json` using the 10-digit zero-padded CIK. Under `filings.recent` the fields `form`, `items`, `filingDate`, `accessionNumber`, and `primaryDocument` are parallel lists — zip them by index. Keep rows where `form == "8-K"` and the `items` string contains `"2.02"` (Results of Operations and Financial Condition). Sort by `filingDate` descending and keep the **four most recent** (one per quarter). Skip 8-K/A amendments.

**3. Locate the press release.** For each filing, build the filing index URL:
`https://www.sec.gov/Archives/edgar/data/{cik without leading zeros}/{accession number without dashes}/{accession number with dashes}-index.htm`.
Parse the document table on that page. The earnings press release is the `.htm` document whose Type is `EX-99.1` (fall back to any `EX-99*` `.htm` exhibit whose description mentions "press release" or "results", then to the first `EX-99*` `.htm`). If no exhibit can be found, print a warning (`WARNING: [Ticker] [filing_date]: press release exhibit not found — skipping`) and continue to the next filing — never crash.

**4. Get plain text.** Download the exhibit, strip HTML with BeautifulSoup (`get_text(" ")`), and collapse whitespace so that table cells become one searchable line of text.

**5. Extract fields with regex** (case-insensitive) from the plain text:
- `period` — the reporting period phrase, e.g. "fourth quarter fiscal 2024", "second quarter of fiscal year 2025", "third-quarter 2025", or "quarter ended June 30, 2025".
- `revenue_reported` — the quarterly revenue (or "net sales" / "total revenues" / "net revenue") as a number, keeping the unit that follows it (e.g. "$94.9 billion" or "$85,777 million"). Prefer the headline sentence ("revenue of $X billion", "revenue was $X billion") over table values.
- `eps_diluted` — diluted earnings per share ("diluted earnings per share of $X", "EPS of $X", "$X per diluted share").
- `net_income` — net income for the quarter ("net income of $X billion", "net income was $X").
Store each value as the number with its unit (e.g. `94.93 billion`). Fields that are not found in the text are stored as the literal string **`"NOT_FOUND"`** — never `None`, `NaN`, or an empty cell, because a blank cell and missing data mean different things.

**6. Print progress.** After each filing, print exactly:
`[Ticker] | [Period] | Revenue: $X | EPS: $X | Net Income: $X`

**7. Save output.** Write all rows to `hw03/earnings_history.csv` with columns, in order:
`company, ticker, cik, filing_date, period, revenue_reported, eps_diluted, net_income`.
Print a final confirmation with the file path and row count. A failure on one company (e.g. an API error) prints a warning and moves on to the next company; the CSV is still written with whatever rows succeeded.

---

## Specification B — Executive Events Pipeline (Item 5.02) → `hw03/hw03_executives.py`

Write a Python script that lists every executive/director departure and appointment the five companies above disclosed in the past 12 months.

**1. HTTP setup.** Same as Spec A: one headers dictionary with `User-Agent: "MIS3060 Villanova csoderma@villanova.edu"` passed on **every** `requests.get()` call through a single helper, ~0.2 s pause between requests, timeout and one retry.

**2. Find the filings.** For each company, GET `https://data.sec.gov/submissions/CIK{cik}.json`. Zip the parallel lists under `filings.recent` and keep rows where `form == "8-K"`, `items` contains `"5.02"` (Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers), and `filingDate` is within the past 12 months (365 days before today's date when the script runs).

**3. No-events case.** If a company has no matching filings, print `[Ticker]: No executive events in past 12 months` and continue. This is valid data, not an error — the script must not crash or skip the company silently.

**4. Get the 8-K text.** For each matching filing, download the primary 8-K document at `https://www.sec.gov/Archives/edgar/data/{cik without leading zeros}/{accession without dashes}/{primaryDocument}`, strip HTML with BeautifulSoup, and collapse whitespace. Isolate the Item 5.02 section: the text from "Item 5.02" to the next "Item X.XX" heading or "SIGNATURE".

**5. Extract events.** Split the Item 5.02 section into sentences. For each sentence describing a change:
- `event_type` — `"departure"` if it uses words like *resign, retire, step down, depart, terminate, will not stand for re-election, cease to serve*; `"appointment"` if it uses *appoint, elect, name, promote, hire, succeed, join*. If one sentence describes both for the **same** person, use `"both"`.
- `person_name` — the individual's full name (e.g. "Mr./Ms./Dr. First Last" or a capitalized "First M. Last" name next to the event verb). Exclude the company's own name.
- `title` — the role, e.g. "Chief Financial Officer", "Senior Vice President", "member of the Board of Directors".
- `effective_date` — the date the change takes effect ("effective March 1, 2026", "effective immediately" → use the filing date), formatted `YYYY-MM-DD`.
If one filing reports several events (e.g. a CFO departure and a new CFO appointment), create **one row per event** (one per person + event type). De-duplicate identical rows within a filing. Any field that cannot be extracted is stored as `"NOT_FOUND"`. Item 5.02 also covers compensation arrangements (5.02(e)), so some filings contain no departure or appointment at all. If a 5.02 filing yields no recognizable departure/appointment, still write one row with `event_type = "other"` and `person_name`, `title`, `effective_date` as `NOT_FOUND`, so the filing is visible in the output but can be excluded from event analysis.

**6. Print progress.** Print each event as it is extracted:
`[Ticker] | [Date] | [Event Type] | [Name] | [Title]`

**7. Save output.** Write all events to `hw03/executive_events.csv` with columns, in order:
`company, ticker, cik, filing_date, event_type, person_name, title, effective_date`.
Write the header row even if there are zero events. Print a final confirmation with the path and row count. Errors on one filing print a warning and continue to the next.
