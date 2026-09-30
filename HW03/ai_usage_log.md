# AI Usage Log
**Assignment:** HW3 — SEC EDGAR 8-K Pipelines
**Student:** Carl Soderman
**Date:** 9/30/26

**Tool used:** The course workflow calls for Claude Cowork. For this assignment I used **Claude Code** (Claude Opus 5.5, in VS Code) instead. Claude Code drafted both specifications from the assignment requirements and saved them to `specifications.md` *before* any script was generated. It then generated each script from its specification, ran it against live EDGAR data, checked the output against the filing text, and iterated. I directed the work and reviewed the results. The only change to a specification after it was written was one clarification to Spec B about compensation-only 5.02 filings (see below), made before any code existed. The prompts below are the final specification text the scripts were generated from.

---

## Prompt 1 — Specification A (earnings pipeline → `hw03_earnings.py`)

The shared header (company/CIK table and output-folder rule) was sent with both specs:


Both scripts use the same five companies and CIKs exactly as given (no lookup):

| Company | Ticker | CIK |
|---|---|---|
| Apple Inc. | AAPL | 0000320193 |
| Microsoft Corporation | MSFT | 0000789019 |
| NVIDIA Corporation | NVDA | 0001045810 |
| JPMorgan Chase & Co. | JPM | 0000019617 |
| Walmart Inc. | WMT | 0000104169 |

Dependencies: `requests`, `beautifulsoup4` (and the Python standard library: `re`, `csv`, `time`, `datetime`). All output files are written into the same folder as the script (`hw03/`), regardless of the directory the script is run from.


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


## Prompt 2 — Specification B (executive events pipeline → `hw03_executives.py`)

Sent as a separate generation step with the same shared header. Before any code was generated, one clarification was added: compensation-only filings get `event_type = "other"`.


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

## Prompt 3 — Timeline (→ `hw03_timeline.py`)

> Write a Python script that reads hw03/earnings_history.csv and hw03/executive_events.csv. Do the following:
> 1. For each executive event in the events table, calculate the number of days between the executive event's filing_date and the nearest earnings filing date for the same company in the earnings table. Call this days_to_nearest_earnings.
> 2. Add a column event_timing that categorizes each executive event as: 'before earnings' if the event came before the nearest earnings filing, 'after earnings' if it came after, or 'same week' if within 7 days of an earnings filing.
> 3. Save the combined table to hw03/corporate_events_timeline.csv with all columns from both source tables plus days_to_nearest_earnings and event_timing.
> 4. Print a summary: for each company, list any executive events and whether they occurred before or after the nearest earnings announcement.
> 5. Print a final count: how many events occurred before vs. after an earnings announcement across all five companies.

Plus the Part 5C prompt: *"Write Python using yfinance to get the most recent quarterly revenue and net income for NVDA."* → `yf_check.py`

---

## Which extractions required iteration

**Earnings:**
- No company returned all `NOT_FOUND`. All 20 rows extracted revenue, EPS and net income on the first run, so the "ask for a better revenue regex" step was never needed.
- Two companies needed **period** regex fixes (before/after patterns are in `validation.md`):
  - **NVDA:** "Fourth Quarter *and* Fiscal 2026" was mislabelled as Q1 FY27, because the pattern matched the outlook paragraph.
  - **WMT:** Walmart only writes "Q2 FY27" in table headers, so its periods had no year.
- Before writing any regex, Claude Code first pulled and read the raw text from all five press releases, because each company words its results differently:
  - Apple and Walmart never state net income in prose, so the regex falls back to the income-statement table (values in millions).
  - JPM puts EPS in the headline as "($7.70 PER SHARE)".
  - NVDA says "revenue for the second quarter ended July 26, 2026, of $96.2 billion".

**Executive events (most iteration).** The first run produced 37 rows; after fixes, 31. The fixes:
- **WMT:** Non-compete boilerplate ("if Mr. Milum's employment is terminated…") created fake departures for Milum, Nicholas, Watkins and Furner, so `terminat*` was removed as a departure verb. The noun "appointment" ("the appointment of Mr. Furner") created a fake appointment for McMillon, so only verb forms are matched now. "Non-Competition Agreements" was read as a person. "the Board appointed **Mr.** John R. Furner" was missed because of the honorific, so his title came out as "member of the Board of Directors" instead of "president and chief executive officer". "Effective **Date** was announced on November 14" was parsed as an effective date.
- **AAPL:** Tim Cook's "transition from his role as CEO to Executive Chair" was first labelled `departure`; it is now `both`.
- **NVDA / JPM:** Titles came out as "retire from his role as VP and CAO" and "resign as a member of the Board", because the word "to" in "intention to retire" was treated as the start of a title. JPM's "Co-Presidents" was normalized to one "Co-President" per person.
- **WMT (Mehrotra):** The date came before the name ("Effective January 8, 2026, the Board appointed…"), so it was initially missed.
- A synthetic test ("Jane Q. Smith, CFO of Both Co Inc.") showed that a company name could be read as a person. a corporate-suffix filter was added (Inc/Corp/Co/LLC…).

---

## One thing the generated script did that I wouldn't have thought to specify

For the executive pipeline, the generated script **resolves "defined terms" to dates**. SEC filings often write "effective on the Transition Date" and define it elsewhere, as in "effective September 1, 2026 (the "Transition Date")". The script builds a lookup of every `(the "… Date")` definition in the Item 5.02 section and uses it when a sentence only refers to the term. Without this, John Ternus's appointment as Apple CEO, and David Guggina's and Christopher Nicholas's appointments at Walmart, would all have come back `NOT_FOUND` for effective date. **Was it correct?** Mostly yes: Ternus → 2026-09-01 and Nicholas → 2026-02-01 match the filings. It needed one adjustment. The general "effective … [date]" regex ran first and treated the phrase "Effective **Date** was announced … on November 14, 2025" as a date, which gave John Furner a wrong effective date of 2025-11-14. Adding a `(?!\s+date)` guard fixed it to 2026-02-01.

A second unrequested choice: the timeline script **excludes the 3 compensation-only `other` rows from the final before/after count** and prints a note saying so. I agree with it, because a stock-plan approval isn't an executive change. It also stored a `signed_days` column next to the required absolute `days_to_nearest_earnings`, so the direction is visible without re-deriving it.

---

**Reflection:** The biggest lesson is that regex over prose is fast to build and easy to fool. The earnings figures validated perfectly against both NVIDIA's press release and yfinance. In the executive pipeline, though, every one of the five bugs produced *plausible-looking* output, and they were only caught by reading each row against the filing text. Next time I would write the edge-case tests (two events in one filing, a company name next to a person, a date before the name) into the specification itself, rather than discovering them after the first run.
