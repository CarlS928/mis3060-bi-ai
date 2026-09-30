"""
HW3 Part 3 — Executive Events Pipeline (8-K Item 5.02)

For five companies, find 8-K filings from the past 12 months that report
Item 5.02 (Departure of Directors or Certain Officers; Election of Directors;
Appointment of Certain Officers), download the 8-K, isolate the Item 5.02
section, and extract one row per person per event: event type, name, title
and effective date. Missing fields are stored as "NOT_FOUND".

Output: hw03/executive_events.csv
Run:    python hw03/hw03_executives.py
"""

import csv
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
HEADERS = {"User-Agent": "MIS3060 Villanova csoderma@villanova.edu"}
REQUEST_PAUSE = 0.2          # SEC allows 10 requests/second
LOOKBACK_DAYS = 365
NOT_FOUND = "NOT_FOUND"

OUT_DIR = Path(__file__).resolve().parent
OUT_CSV = OUT_DIR / "executive_events.csv"
COLUMNS = ["company", "ticker", "cik", "filing_date", "event_type",
           "person_name", "title", "effective_date"]

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
# Step 1 — find Item 5.02 8-K filings in the lookback window
# ---------------------------------------------------------------------------
def executive_filings(cik, cutoff):
    data = sec_get(f"https://data.sec.gov/submissions/CIK{cik}.json").json()
    recent = data["filings"]["recent"]
    rows = zip(recent["form"], recent["items"], recent["filingDate"],
               recent["accessionNumber"], recent["primaryDocument"])
    matches = [
        {"filing_date": fdate, "accession": acc, "document": doc}
        for form, items, fdate, acc, doc in rows
        if form == "8-K" and "5.02" in items and fdate >= cutoff.isoformat()
    ]
    matches.sort(key=lambda r: r["filing_date"], reverse=True)
    return matches


def filing_text(cik, filing):
    acc = filing["accession"]
    url = (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
           f"{acc.replace('-', '')}/{filing['document']}")
    return html_to_text(sec_get(url).text)


def item_502_section(text):
    """Text from 'Item 5.02' to the next 'Item X.XX' heading or SIGNATURE.
    The longest match is used so a table-of-contents mention is ignored."""
    sections = re.findall(r"Item\s*5\.02(.*?)(?=Item\s*\d\.\d{2}|SIGNATURES?\b)",
                          text, re.S | re.I)
    return max(sections, key=len) if sections else text


# ---------------------------------------------------------------------------
# Step 2 — sentence splitting and name detection
# ---------------------------------------------------------------------------
ABBREVIATIONS = ["Messrs.", "Mrs.", "Mr.", "Ms.", "Dr.", "Inc.", "Corp.", "Co.",
                 "U.S.", "No.", "Jr.", "Sr.", "St."]
PLACEHOLDER = "§"   # temporarily replaces dots that don't end a sentence


def split_sentences(text):
    for abbr in ABBREVIATIONS:
        text = text.replace(abbr, abbr.replace(".", PLACEHOLDER))
    text = re.sub(r"\b([A-Z])\.(?=\s[A-Z])", r"\1" + PLACEHOLDER, text)  # middle initials
    parts = re.split(r"\.\s+(?=[A-Z(“\"])", text)
    return [p.replace(PLACEHOLDER, ".").strip() for p in parts if p.strip()]


# Capitalized words that are never part of a person's name in these filings
STOP_WORDS = set("""
On The In Since From Prior Effective Following Beginning Additionally As At For Upon Under With
After During Until This That These There Pursuant Each All Any Its His Her Their Our We Lastly
January February March April May June July August September October November December
Board Directors Director Company Committee Committees Audit Compensation Nominating Governance
Chief Executive Officer Officers Vice President Presidents Senior Principal Accounting Financial
Operating Technology Hardware Engineering General Counsel Chair Chairman Lead Independent
Annual Meeting Shareholders Shareholder Regulation Item Exhibit Plan Stock Securities Exchange
Commission Form Current Report Worldwide Field Operations Corporate Controller Treasurer Tax
Walmart International Club Apple Microsoft NVIDIA Intel Oracle Amazon JPMorgan JPMorganChase
Chase Firm CIB CCB CEO CFO COO VP CAO Co-CEOs Co-CEO Co-Presidents Co-President Inc Corporation
Commercial Investment Bank Banking Consumer Community Asset Wealth Management Development Group
Coles Supply Chain Innovation Automation Product Deputy Transition Date Separation Position
Global Partner Solutions Sales Industry Business Mr Ms Dr Mrs Messrs Retention Continuity Awards
Award Restricted Units Performance Share Shares PSUs RSUs Policy Proxy Statement New York Park
Avenue Standard Composite Index Equity Incentive Variable Fiscal Year Named Target Opportunity
Base Achievement Salary Services Recoupment Bonus Vesting Condition Protection-based Non-Compete
Agreement Post-Termination Covenant Compete MIP CMDC ROTCE CET1 Tier Solutions Communications
Non-Competition Agreements Microsoft’s Apple’s NVIDIA’s Walmart’s Firm’s Company’s Board’s Hardware Assistant Revenue
""".split())

NAME_TOKEN = r"(?:[A-Z]\.|[A-Z][a-z][\w’'\-]*|[A-Z]{2}[a-z][\w’'\-]*)"
NAME_RUN_RE = re.compile(NAME_TOKEN + r"(?:\s" + NAME_TOKEN + r")*")
HONORIFIC_RE = re.compile(r"\b(?:Mr|Ms|Mrs|Dr)\.\s+(" + NAME_TOKEN + r"(?:\s" + NAME_TOKEN + r")*)")


# A capitalized run followed by one of these is an organization, not a person
CORP_SUFFIXES = {"Inc", "Corporation", "Corp", "Co", "LLC", "Ltd", "Group", "Company", "Holdings"}
STOP_WORDS |= CORP_SUFFIXES


def clean_token(tok):
    return re.sub(r"[’']s?$", "", tok)


def full_names_in(text):
    """Return [(name, start, end)] for capitalized runs that look like 2–4 word names."""
    found = []
    for m in NAME_RUN_RE.finditer(text):
        tokens = m.group(0).split(" ")
        # break the run at stop words and keep sub-runs of 2–4 name tokens
        pos = m.start()
        run, run_start = [], None
        for tok in tokens + [None]:
            if tok is not None and clean_token(tok) not in STOP_WORDS and tok not in STOP_WORDS:
                if not run:
                    run_start = pos
                run.append(tok)
            else:
                is_company = tok is not None and clean_token(tok).rstrip(".") in CORP_SUFFIXES
                if (2 <= len(run) <= 4 and any(len(t) > 2 for t in run)
                        and not run[-1].endswith(".") and not is_company):
                    name = " ".join(run[:-1] + [clean_token(run[-1])])
                    found.append((name, run_start, run_start + len(" ".join(run))))
                run, run_start = [], None
            if tok is not None:
                pos += len(tok) + 1
    return found


def people_in_sentence(sentence, known_names):
    """All person mentions in a sentence, resolved to full names, ordered by position."""
    people = [(n, s, e) for n, s, e in full_names_in(sentence)]
    for m in HONORIFIC_RE.finditer(sentence):
        ref = " ".join(clean_token(t) for t in m.group(1).split(" ")
                       if clean_token(t) not in STOP_WORDS)
        if not ref:
            continue
        if any(s <= m.start(1) < e for _, s, e in people):   # already a full-name hit
            continue
        full = next((n for n in known_names if n.endswith(ref)), None)
        if full:
            people.append((full, m.start(), m.end()))
    people.sort(key=lambda p: p[1])
    # merge consecutive mentions of the same person
    merged = []
    for p in people:
        if merged and merged[-1][0] == p[0] and p[1] - merged[-1][2] < 3:
            continue
        merged.append(p)
    return merged


# ---------------------------------------------------------------------------
# Step 3 — event type, title, effective date
# ---------------------------------------------------------------------------
DEPARTURE_RE = re.compile(
    r"\b(resign\w*|retire\w*|step(?:s|ped|ping)? down|depart\w*|"
    r"not (?:to )?stand for re-?election|will not stand|cease\w* to serve|"
    r"separat\w* from|transition\w* from (?:his|her|their) role)\b", re.I)
APPOINTMENT_RE = re.compile(
    r"\b(appointed|appoints|appoint|elected|elect|named|promot\w*|hired|become|becomes)\b", re.I)
# "transition from his role as CEO to Executive Chair" is a departure and an appointment
ROLE_CHANGE_RE = re.compile(r"transition\w* from (?:his|her|their) role as .+? to [A-Z]", re.I)

TITLE_WORDS = re.compile(r"officer|president|counsel|chair|director|controller|board|"
                         r"\bceo\b|\bcfo\b|\bcoo\b|\bvp\b|\bcao\b|treasurer|head\b", re.I)
TITLE_STOP = (r"(?=,\s*effective|\seffective\b|,\s*in each case|\(|;|,\s*age\b|"
              r"\sand the\b|\sand as\b|\son the\b|\son [A-Z][a-z]+ \d|,\s*and\s|,\s*which\b|$)")
TITLE_AFTER_VERB = re.compile(
    r"(?:\bas|\bto(?=\s+(?:the\s+|its\s+|a\s+)?[A-Z])(?! the Company)|\bfrom(?=\s+(?:the\s+)?[A-Z])|\bbecome|\bbecomes|(?:been|was|were) (?:appointed|elected|named))\s+"
    r"(?:the\s+|a\s+|an\s+|its\s+|sole\s+|[A-Z][\w.]*[’']s\s+)?(?P<t>.+?)" + TITLE_STOP)
TITLE_COMPANY_TAIL = re.compile(
    r"\s+of (?:the Company|the Firm|[A-Z][\w.&]*(?:\s[A-Z][\w.&]*){0,2}\s(?:Corporation|Inc\.?|Co\.))\s*$")

MONTH_DATE = (r"((?:January|February|March|April|May|June|July|August|September|October|"
              r"November|December) \d{1,2}, \d{4})")


def clean_title(title):
    title = title.strip(" ,.")
    title = TITLE_COMPANY_TAIL.sub("", title)
    title = re.sub(r"^(?:current|a|an|the)\s+", "", title, flags=re.I)
    title = re.sub(r"^[A-Z][\w.]*[’']s\s+", "", title)      # "Company’s Executive VP" -> "Executive VP"
    title = re.sub(r"Presidents\b", "President", title)    # "elected Co-Presidents" -> one row each
    if re.fullmatch(r"(?:its\s+)?Board(?: of Directors)?", title, re.I):
        title = "member of the Board of Directors"
    return title.strip(" ,.")


def extract_title(after, before):
    """Title from 'as X' / 'become X' / 'was appointed X', else the appositive after the name."""
    for m in TITLE_AFTER_VERB.finditer(after):
        t = m.group("t")
        if TITLE_WORDS.search(t) and len(t) < 120:
            return clean_title(t)
    appositive = re.match(r",\s*(?:age\s*)?(?:\d{2},\s*)?(.+?)"
                          r"(?=\(|\snotified|\sinformed|\swill\b|\shas\b|\shave\b|,\s*or\b|"
                          r"\ssince\b|\sof [A-Z][\w.&]*\s(?:Corporation|Inc))", after)
    if appositive and TITLE_WORDS.search(appositive.group(1)) and len(appositive.group(1)) < 120:
        return clean_title(appositive.group(1))
    if re.search(r"\bBoard\b|\bdirector\b", after, re.I):
        return "member of the Board of Directors"
    return NOT_FOUND


def to_iso(text_date):
    try:
        return datetime.strptime(text_date, "%B %d, %Y").date().isoformat()
    except ValueError:
        return NOT_FOUND


def defined_dates(section):
    """Map defined terms like (the “Transition Date”) to the date just before them."""
    return {term.lower(): to_iso(d) for d, term in
            re.findall(MONTH_DATE + r"[^()]{0,20}\(the\s*[“\"]([^”\"]*Date)[”\"]\)", section)}


def extract_effective_date(window, sentence, filing_date, terms):
    m = re.search(r"effective(?!\s+date)[^.;]{0,120}?" + MONTH_DATE, window, re.I)
    if m:
        return to_iso(m.group(1))
    m = re.search(r"(?:effective|as of)\s+(?:on\s+|as of\s+)?the\s+([\w\s]*Date)", window, re.I)
    if m and m.group(1).lower() in terms:
        return terms[m.group(1).lower()]
    if re.search(r"effective immediately", window, re.I):
        on = re.match(r"On " + MONTH_DATE, sentence)
        return to_iso(on.group(1)) if on else filing_date
    m = re.search(r"(?:become|becomes|retire\w*|separat\w*)[^.;]{0,60}?\bon " + MONTH_DATE, window, re.I)
    if m:
        return to_iso(m.group(1))
    return NOT_FOUND


# ---------------------------------------------------------------------------
# Step 4 — turn one Item 5.02 section into event rows
# ---------------------------------------------------------------------------
def extract_events(section, filing_date):
    sentences = split_sentences(section)
    known_names = []
    for s in sentences:
        for name, _, _ in full_names_in(s):
            if name not in known_names:
                known_names.append(name)
    terms = defined_dates(section)

    events = {}   # (person, event_type) -> event; first mention wins
    for idx, sentence in enumerate(sentences):
        people = people_in_sentence(sentence, known_names)
        pending = []   # people joined by "and" to the next person ("A, 61, and B, 56, were elected")
        for i, (name, start, end) in enumerate(people):
            next_start = people[i + 1][1] if i + 1 < len(people) else len(sentence)
            prev_end = people[i - 1][2] if i > 0 else 0
            after = sentence[end:next_start]
            before = sentence[max(prev_end, start - 40):start]

            if i + 1 < len(people) and re.fullmatch(r"[,\s\d]*(?:age\s*\d+,?\s*)?and\s*", after):
                pending.append(name)
                continue

            dep = DEPARTURE_RE.search(after)
            app = APPOINTMENT_RE.search(after) or re.search(
                r"(?:appointed|elected|named|promoted)\s+(?:(?:Mr|Ms|Mrs|Dr)\.\s*)?$", before, re.I)
            if (dep and app) or ROLE_CHANGE_RE.search(after):
                event_type = "both"
            elif dep:
                event_type = "departure"
            elif app:
                event_type = "appointment"
            else:
                pending = []
                continue

            title = extract_title(after, before)
            eff = extract_effective_date(after, sentence, filing_date, terms)
            if eff == NOT_FOUND and len(people) == 1:
                # "Effective January 8, 2026, the Board appointed X" — date precedes the name
                eff = extract_effective_date(sentence, sentence, filing_date, terms)
            if eff == NOT_FOUND:
                # look for a date in later sentences that mention the same person
                surname = name.split(" ")[-1]
                for later in sentences[idx + 1:]:
                    if surname in later:
                        eff = extract_effective_date(later, later, filing_date, terms)
                        if eff != NOT_FOUND:
                            break

            for person in pending + [name]:
                key = (person, event_type)
                if key not in events:
                    events[key] = {"event_type": event_type, "person_name": person,
                                   "title": title, "effective_date": eff}
            pending = []

    if not events:
        return [{"event_type": "other", "person_name": NOT_FOUND,
                 "title": NOT_FOUND, "effective_date": NOT_FOUND}]
    return list(events.values())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    sys.stdout.reconfigure(encoding="utf-8")    # names contain curly apostrophes
    cutoff = date.today() - timedelta(days=LOOKBACK_DAYS)
    print(f"Item 5.02 8-K filings on or after {cutoff.isoformat()}\n")

    rows = []
    for company, ticker, cik in COMPANIES:
        try:
            filings = executive_filings(cik, cutoff)
        except Exception as exc:
            print(f"WARNING: {ticker}: could not read submissions API ({exc}) — skipping company")
            continue
        if not filings:
            print(f"{ticker}: No executive events in past 12 months")
            continue

        for filing in filings:
            try:
                section = item_502_section(filing_text(cik, filing))
                events = extract_events(section, filing["filing_date"])
            except Exception as exc:
                print(f"WARNING: {ticker} {filing['filing_date']}: could not process filing ({exc}) — skipping")
                continue
            for ev in events:
                row = {"company": company, "ticker": ticker, "cik": cik,
                       "filing_date": filing["filing_date"], **ev}
                rows.append(row)
                print(f"{ticker} | {row['filing_date']} | {row['event_type']} | "
                      f"{row['person_name']} | {row['title']}")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
