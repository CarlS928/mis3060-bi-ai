# HW3 Validation

**Student:** Carl Soderman · **Validated:** 2026-09-30

All numbers below come from the final run of the three scripts on 2026-09-30.

---

## 5A — Known-Answer Check: Earnings

**Company / quarter:** NVIDIA, second quarter fiscal 2027 (quarter ended July 26, 2026; 8-K filed 2026-08-26)
**Official source:** NVIDIA Newsroom, [NVIDIA Announces Financial Results for Second Quarter Fiscal 2027](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027) (also syndicated on GlobeNewswire / Nasdaq)

| Check | Official Source | Your CSV | Match? |
|---|---|---|---|
| NVIDIA Q2 FY2027 Revenue | $96.2 billion ($96,221 million in the summary table) | `96.2 billion` | ✅ Yes |
| NVIDIA Q2 FY2027 EPS Diluted | $2.46 (GAAP) | `2.46` | ✅ Yes |

No discrepancy and no `NOT_FOUND`, so no regex fix was needed for this check. Note that the CSV captures **GAAP** EPS ($2.46), not NVIDIA's non-GAAP EPS ($2.22), which appears in the same sentence. The pattern `earnings per diluted share (?:was|were|of) $X` takes the first figure, which is GAAP.

### Regex iterations during the build (before/after)

No company's extraction came back all `NOT_FOUND`, so the assignment's "paste 3,000 characters and ask for a better revenue regex" step was not triggered. The first run did produce two wrong **period** labels, which I fixed:

| Issue | Before | After | Resolved? |
|---|---|---|---|
| NVDA Q4 FY26 release labelled "first quarter fiscal 2027". The headline reads "Fourth Quarter **and** Fiscal 2026", so the pattern skipped it and matched the Q1 FY27 *outlook* paragraph instead | `ORDINAL[ -]quarter (?:of )?fiscal (?:year )?(\d{4})` | `ORDINAL[ -]quarter (?:of \|and )?fiscal (?:year )?(\d{4})` | ✅ now "fourth quarter fiscal 2026" |
| All four WMT periods had no year ("second quarter"). Walmart never writes "fiscal 2027" in prose, only "Q2 FY27" in table headers | *(no pattern)* | `\bQ([1-4]) FY(\d{2})\b` → "second quarter fiscal 2027" | ✅ all four WMT rows labelled |

---

## 5B — Known-Answer Check: Executive Events

**Event checked:** NVDA, filed 2026-04-27. *Appointment:* Scott Gawel, VP and CAO, effective 2026-05-04. The same filing reports the matching *departure* of Donald Robertson.

**News sources:** [Investing.com: NVIDIA names former Intel executive as chief accounting officer](https://www.investing.com/news/assorted/nvidia-names-former-intel-executive-as-chief-accounting-officer-432SI-4639775); [CFO Dive: Nvidia hands new accounting chief $12.9M in RSUs](https://www.cfodive.com/news/nvidia-hands-new-cao-129m-rsus-agenticai/818855/); [MarketScreener: NVIDIA Corporation Announces Executive Changes, Effective May 4, 2026](https://www.marketscreener.com/news/nvidia-corporation-announces-executive-changes-effective-may-4-2026-ce7f58dede89f722)

| Check | News Source Confirms? | Notes |
|---|---|---|
| Person name and title | ✅ Yes | Scott Gawel, Vice President and Chief Accounting Officer (formerly Corporate VP & CAO at Intel). The CSV title is `VP and CAO`, the filing's own abbreviation. |
| Event type (departure/appointment) | ✅ Yes | Appointment. Coverage also confirms Donald Robertson's retirement from the CAO role, which the pipeline captured as a separate `departure` row from the same filing (the "two events in one filing" edge case working on real data). |
| Effective date | ✅ Yes | May 4, 2026 in both the news coverage and the CSV (`2026-05-04`). Robertson's departure is also correctly `2026-05-04`. |

---

## 5C — Cross-Validation: Earnings via Yahoo Finance

Script: `hw03/yf_check.py` (prompt: *"Write Python using yfinance to get the most recent quarterly revenue and net income for NVDA."*). It uses yfinance 1.7.0 and `Ticker("NVDA").quarterly_income_stmt`.

| Metric | From 8-K text extraction | From yfinance | Match? |
|---|---|---|---|
| Revenue | $96.2 billion (headline sentence) | $96,221 million | ✅ Yes ($96,221M rounds to $96.2B) |
| Net Income | $59,688 million (GAAP, from the summary table) | $59,688 million | ✅ Yes (exact) |

The two sources agree. The only visible difference is the date label: yfinance tags the quarter as **2026-07-31**, while NVIDIA's fiscal quarter actually ended **July 26, 2026**. yfinance rounds period ends to month-end, so this is a label difference, not a period mismatch. The revenue difference is only precision: the headline states $96.2B, while the table and yfinance give $96,221M.

---

## 5D — Pipeline Integrity Checks

| Check | Expected | Actual | Pass/Fail |
|---|---|---|---|
| earnings_history.csv row count | Up to 20 (5 companies × 4 quarters) | **20** (4 per company) | ✅ Pass |
| executive_events.csv row count | At least 0 (document actual) | **31** rows from 19 filings: 17 appointment, 10 departure, 1 both, 3 other (AAPL 6, MSFT 4, NVDA 7, JPM 5, WMT 9) | ✅ Pass |
| corporate_events_timeline.csv created | Yes | **Yes**, 31 rows (one per event), 0 blank cells | ✅ Pass |
| Rows with all three fields "NOT_FOUND" | 0 (investigate if > 0) | **0**. No earnings row has any NOT_FOUND field (revenue, EPS, net income and period all extracted) | ✅ Pass |

### Additional checks I ran

- **Edge cases tested with stubbed network calls:**
  - A filing with no press-release exhibit prints a `WARNING … skipping` line and the run continues.
  - A release with no matching text writes `NOT_FOUND` in every field (not blanks).
  - A company with zero 5.02 filings prints `ZERO: No executive events in past 12 months`.
  - A synthetic filing with a CFO resignation plus a new CFO appointment produced **two** rows.
- **The 3 `other` rows are intentional, not failures.** They are Item 5.02(e) compensation-only filings: MSFT 2025-12-08 (2026 Stock Plan), NVDA 2026-03-06 (FY27 variable comp plan) and JPM 2026-01-22 (Jamie Dimon's 2025 pay). They are kept so every filing is visible, and excluded from the timeline counts.
- **9 events have `effective_date = NOT_FOUND`: the 3 `other` rows plus 6 where the filing gives no calendar date.** Kate Adams ("retirement in late 2026"), Art Levinson and Reid Hoffman / Carlos Rodriguez (effective at the annual meeting), Ajay Puri (effective when his successor starts) and Marianne Lake. These are correct: the source text has no date.
- **Hand review of every event row against the Item 5.02 text.** This caught and fixed five issues:
  - Non-compete boilerplate ("if Mr. X's employment is terminated…") created false departures.
  - The noun "appointment" created a false event for McMillon.
  - "Non-Competition Agreements" was read as a person's name.
  - "the Board appointed **Mr.** John R. Furner" was missed because of the honorific.
  - "Effective **Date** was announced on November 14" was read as an effective date.
