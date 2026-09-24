# HW02 Validation Record — Wildcat Capital `fact_transactions.csv`

**Author:** Carl Söderman
**Script validated:** `HW02/hw02_eda.py`
**Output validated:** terminal output and `HW02/hw02_profile.txt` from the run on 2026-09-23 (the script finished without errors)

---

## 2A — Known-Answer Benchmarks

The "Your Script Produced" values are copied from the script's output. The section numbers in the Notes column refer to the section headings in the terminal output and `hw02_profile.txt`.

| Check | Expected | Your Script Produced | Match? | Notes |
|---|---|---|---|---|
| Dataset shape | (298772, 9) | 298,772 rows × 9 columns | Yes | Section 3. The Section 15 shape check also printed "OK: shape matches". |
| Null count — security_id | 101,597 | 101,597 | Yes | Section 5. Same count as the nulls in `shares` and `price` (34.0% of rows), which fits cash transactions (Deposit, Withdrawal, Advisory Fee) having no security. |
| Null count — amount | 0 | 0 | Yes | Section 5. Every transaction has a dollar amount. |
| Unique txn_type values | 6 | 6 | Yes | Section 7 lists six types: Buy, Sell, Dividend, Deposit, Advisory Fee, Withdrawal. |
| Count of Buy transactions | 83,556 | 83,556 | Yes | Section 7 (27.97% of rows). Section 12 shows the same count. |
| txn_date data type | object | `str` | Yes (equivalent) | Section 4. The column loaded as text, not as a date, which is what this check confirms. The label is `str` instead of `object` because the course environment uses pandas 3.0, which reads text columns as its new string type by default. Earlier pandas versions label the same column `object`. See the discrepancy notes below. |
| Earliest txn_date | 2020-01-01 | 2020-01-01 | Yes | Section 9. |
| Latest txn_date | 2024-12-30 | 2024-12-30 | Yes | Section 9. |
| Duplicate txn_id count | 0 | 0 | Yes | Section 10. Every transaction ID is unique. |
| Mean amount | $54,075.17 | $54,075.17 | Yes | Section 11. |
| Median amount | $41,220.48 | $41,220.49 | Yes (rounding) | Section 11. The exact median is $41,220.485, halfway between two cents. The benchmark rounded it down and the script rounded it up. Section 6 of the same output shows 41220.48. See the discrepancy notes below. |
| Skewness of amount | 1.15 | 1.15 (right-skewed) | Yes | Section 11. The unrounded value is 1.1463. |
| Correlation shares–amount | 0.65 | 0.65 | Yes | Section 13. The strongest correlation of the three pairs. |
| Correlation price–amount | 0.64 | 0.64 | Yes | Section 13. The second-strongest correlation. |
| Correlation shares–price | 0.00 | 0.00 | Yes | Section 13. No linear relationship between shares and price. |
| Negative shares count (Buy only) | 836 | 836 (all Buy) | Yes | Section 14. Buy is the only type with negative shares (minimum −499.6323). Dividend and Sell have none, and cash types have no shares data. |
| Profile file created | Yes | Yes | Yes | `HW02/hw02_profile.txt` (3.7 KB) was created and contains Sections 3–15. |
| Chart files created (3) | Yes | Yes | Yes | `HW02/charts/hist_amount.png`, `box_amount_by_type.png`, and `scatter_shares_amount.png` were all created and open correctly. |

**Result:** all 18 checks match. No row is a "No". Two rows show the same result written differently; they are explained below.

### Discrepancy notes

**txn_date data type (`object` expected, `str` produced).** This is a labeling difference, not a data problem. The benchmark asks whether `txn_date` was loaded as a string rather than a date type, and it was. pandas 3.0, installed from `Requirements.txt`, stores text columns with a dedicated string type that it reports as `str`, while pandas 2.x and earlier report text columns as `object`. In both cases the dates are plain text and would need `pd.to_datetime()` before any date calculations. To confirm, loading the file with `dtype={"txn_date": object}` reports `object` for the same column.

**Median amount ($41,220.48 expected, $41,220.49 produced).** The dataset has an even number of rows (298,772), so the median is the average of the two middle values, which is exactly $41,220.485. The script's dollar formatting rounded the half-cent up to $41,220.49. The benchmark, and the script's own descriptive statistics table in Section 6, show $41,220.48. The underlying value is identical, so this is a rounding difference of half a cent.

---

## 2B — Explain the Code and Output

I used a Claude session separate from the one that generated the script, and sent two prompts in sequence. **Prompt 1** contained the complete `hw02_eda.py` and asked Claude to walk through each section and list the expected output. **Prompt 2** contained the complete terminal output and asked what each value means and what to investigate. The full responses, plus the follow-up question, are in [`2B_claude_session.md`](2B_claude_session.md).

### 1. Did Claude's predicted outputs (Prompt 1) match what I actually saw in the terminal? List any discrepancies.

Mostly yes. Claude did not have the data in Prompt 1, so it split its predictions into values **fixed by the code** and values that **depend on the data**. All the fixed values matched exactly:

- The opening lines, the section headings (Sections 3–15), and the order of the sections.
- Nine columns, with the names Claude listed.
- The "OK: shape matches…" line in Section 15.
- The "top 3" correlation list containing all three pairs, since there are only three variables.
- The final `=== Done ===` block listing the four saved files, shown in the terminal but not in `hw02_profile.txt`.

Most of the data-dependent predictions were also correct:

| Section | Claude predicted | Actual output | Match? |
|---|---|---|---|
| 3 — Shape | 298,772 rows × 9 columns | 298,772 × 9 | Yes |
| 4 — Data types | IDs `int64`; `security_id` `float64` (blanks force decimals); `txn_date` and `txn_type` `object` on pandas 2.x or `str` on pandas 3.x; `shares`, `price`, `amount` `float64` | Exactly this, with `str` for the text columns (pandas 3.0) | Yes |
| 5 — Missing values | 0 missing except `security_id`, `shares`, `price`, which would have identical counts equal to Deposit + Withdrawal + Advisory Fee | 101,597 in each of the three, which equals 35,981 + 29,850 + 35,766 | Yes |
| 6 — Descriptive stats | ID columns included (meaningless); `shares` and `price` counts below 298,772; `shares` minimum possibly negative | All three true; the `shares` minimum is −499.63 | Yes |
| 7 — Transaction types | 6 types, counts sum to 298,772, trades most common | 6 types; Buy (27.97%) and Sell (20.00%) are the top two | Yes |
| 9 — Date range | January 2020 to December 2024; correct only if dates are YYYY-MM-DD | 2020-01-01 to 2024-12-30, in ISO format | Yes |
| 10 — Duplicates | 0 | 0 | Yes |
| 11 — Amount distribution | Mean above median, "right-skewed"; Section 6 and Section 11 medians could differ by one cent if the median is a half-cent | Mean $54,075.17 above median $41,220.49; skewness 1.15, "right-skewed"; Section 6 shows 41,220.48, one cent apart as predicted | Yes |
| 12 — Group counts | Counts equal Section 7's | Identical | Yes |
| 13 — Correlation | shares–amount and price–amount clearly positive; shares–price near 0 | 0.65, 0.64, 0.00 | Yes |
| 14 — Cash types | `n/a`, `n/a`, 0 for Deposit, Withdrawal, Advisory Fee | Exactly this | Yes |

**Discrepancies:**

1. **Section 12 — order by mean amount.** Claude predicted that Dividends, like Advisory Fees, would be near the **bottom**, because real dividends are only a few percent of a position's value. In fact **Dividend has the highest mean** ($64,077.30), just above Buy ($63,738.49) and Sell ($63,635.55). Claude got Advisory Fee at the bottom right ($7,375.17). It also said that if Dividends ranked near the top, that should be flagged, and it did flag it in Prompt 2.
2. **Section 14 — where the negative shares are.** Claude said negative shares would only be legitimate as a way of recording sells, in which case they would all be in the **Sell** row. In fact Sell has none, and **all 836 negative values are Buy transactions**. Claude had said negatives in the Buy row would be data errors, which is how they were then treated.
3. **Section 4 — `object` vs. `str` (minor).** Claude hedged between the two labels. The actual output shows `str` because the environment runs pandas 3.0. The 2A benchmark expects `object`; see the 2A discrepancy notes.

Discrepancies 1 and 2 are the useful ones. Claude predicted what realistic wealth management data would look like, and this data didn't match. Both became flags in Prompt 2.

### 2. What did Claude flag as potentially unexpected or worth investigating (Prompt 2)?

Claude flagged seven items, most important first:

1. **836 Buy transactions with negative shares.** This is the one real anomaly. Sells use positive shares, so the negatives aren't a way of recording sells. The amounts are still positive, and the negative range (down to −499.63) mirrors the positive range (up to 500), which looks like a sign flip. They are about 1% of Buys. Claude recommended checking |shares| × price against amount and looking for clustering, then choosing and documenting a treatment before calculating any holdings.
2. **Dividends have the highest average amount ($64,077.30).** Real dividends are about 1–4% of a position a year, but here they match Buy and Sell almost exactly. This suggests dividend amounts are calculated as shares × price, the whole position's value, so they shouldn't be reported as realistic income.
3. **Advisory Fees are heavily skewed.** The mean is $7,375.17 against a median of $859.12. A few very large fees pull the average up and should be checked before reporting "average fee revenue".
4. **Signs the data is simulated:**
   - The type percentages are very close to round numbers (28 / 20 / 18 / 12 / 12 / 10%).
   - The shares–price correlation is exactly 0.00.
   - The quartiles of shares and price are evenly spaced.
   - The maximum amount is just under 500 shares × $500.

   Claude warned not to read business meaning into relationships built into the data, such as the 0.65 and 0.64 correlations.
5. **Client IDs go up to 3,192, but only 2,700 clients have transactions.** About 492 IDs never appear, so per-client averages must state which base they use.
6. **Dates need conversion and a sanity check.** `txn_date` is text. Claude suggested checking for trades on weekends and holidays; the data starts on January 1, a market holiday. It also noted the data ends on December 30, not December 31.
7. **The correlation mixes transaction types.** It pools Buy, Sell, and Dividend rows, including the 836 negative rows. Claude suggested recalculating it on Buy and Sell only, after handling flag #1.

Claude also pointed out that **every `amount` is positive**, including withdrawals and fees. The direction of money is recorded only in `txn_type`, so net cash-flow calculations must subtract withdrawals and fees explicitly.

### 3. Did Claude mention the 101,597 null values in security_id? What explanation did it give?

**Yes.** Claude noted that `security_id`, `shares`, and `price` are each missing in exactly 101,597 rows (34.0%), and showed that this equals the combined count of the three cash transaction types:

> Deposit + Advisory Fee + Withdrawal = 35,981 + 35,766 + 29,850 = **101,597**

Its explanation was that the nulls are **structural, not a data quality problem**. Deposits, withdrawals, and advisory fees are cash movements that involve no security, so there is no security ID, share count, or price to record. The blanks are expected and shouldn't be filled in or dropped.

Claude connected this to two other results. The blanks are why `security_id` is stored as `float64` rather than `int64` (harmless, but convert it to `Int64` before joining on it). And they are why the `shares` and `price` counts in Section 6 are 197,175 instead of 298,772. In Prompt 1, before seeing any data, Claude had already predicted that the three null counts would be identical and would equal the cash-transaction total. The output confirmed that prediction exactly.

### 4. Did Claude flag the txn_date column as a concern? Why would that matter for a time-series analysis?

**Yes, in both prompts:**

- **Prompt 1:** Claude warned that `txn_date` is loaded as text, not a date. It said Section 9's `min()` and `max()` compare the dates **alphabetically**, which gives the right answer only because the dates are YYYY-MM-DD. Any other format would give wrong results without an error.
- **Prompt 2:** Claude pointed out that `txn_date` is `str` and "not a date type", so it needs `pd.to_datetime()` before any time-based work (flag #6). It also suggested checking for trades on weekends and market holidays, and noted the data ends on December 30.

The follow-up (question 6) confirmed that all 298,772 dates convert without errors. It also found that **28.4% of Buy and Sell transactions fall on a Saturday or Sunday**, which real trades can't do.

**Why this matters for time-series analysis:** while `txn_date` is text, pandas cannot treat it as time.

- **Grouping by period:** calculating monthly deposits, quarterly fee revenue, or year-over-year growth needs `.dt.month`, `.dt.quarter`, or `.dt.year`, which only work on a real date type.
- **Resampling and rolling windows:** `resample("M")` and time-based rolling averages need a date index.
- **Correct ordering:** text sorts alphabetically. That works only for ISO dates, and a single badly formatted value would sort into the wrong place without any error.
- **Date math:** days between transactions, client tenure, and time since the last trade can't be calculated from strings.
- **Charts:** a text date axis spaces every label evenly, so gaps in time (weekends, missing months) aren't shown correctly and trends look distorted.
- **Data quality checks:** converting with `errors="coerce"` reveals invalid dates as `NaT`. Checking weekdays and trading calendars, like the weekend-trade finding above, needs real dates.

So `txn_date` must be converted before any trend, seasonality, or period-over-period analysis. Weekend trades should be handled explicitly in any day-of-week or trading-calendar analysis.

### 5. Open your three chart files. Does what you see in each image match Claude's explanation of that section of the output? Note any differences.

**`charts/hist_amount.png`: matches, with two details Claude did not mention.**
- As Claude described, the chart is a 100-bin histogram with a red dashed **mean** line ($54,075.17) to the **right** of an orange solid **median** line ($41,220.49), with both values in the legend. The bars have a long right tail out to about $250,000, which fits the "right-skewed" label.
- **Not mentioned: a very tall first bar.** About 33,000 transactions fall in the lowest bin (under about $2,500), and 24,035 of them are Advisory Fees. Claude said the distribution has "a tail of large ones", but the chart's peak is at the smallest amounts, because advisory fees dominate the bottom bin.
- **Not mentioned: a sharp drop at $100,000.** Deposits and Withdrawals never exceed $100,000 (maximums $99,990.86 and $99,996.46), so the bars fall off sharply at that point.

**`charts/box_amount_by_type.png`: matches, with one detail not mentioned.**
- As Claude described, there is one horizontal box per type in Section 12's order (Dividend at the top, Advisory Fee at the bottom), with the median line inside each box and outliers shown as dots.
- It supports flag #2: the Dividend, Buy, and Sell boxes are almost identical.
- It supports flag #3: the Advisory Fee box is squeezed against $0, with a long line of outliers out to about $143,000.
- **Not mentioned:** Deposit and Withdrawal have **no outliers** and both stop at $100,000. That looks like a built-in cap on cash transactions.

**`charts/scatter_shares_amount.png`: matches Claude's explanation closely.**
- Only **Buy, Dividend, and Sell** appear, as predicted, because cash types have no shares. The points are tiny and partly transparent.
- As Claude predicted for amount = shares × price, the positive-share points form a **fan starting at the origin**. Its straight upper edge is amount = shares × $500, the maximum price.
- As Claude warned, the **type drawn last (Sell) covers the others**. The Buy and Dividend points on the right are almost completely hidden, so the colors can't be used to compare types there. The overlap itself fits flag #2: dividends look exactly like trades.
- **Something Prompt 1 couldn't predict:** the 836 negative-share Buy rows form a separate, **mirror-image triangle to the left of zero**. This makes flag #1 easy to see and fits the sign-flip explanation confirmed in question 6.

### 6. Paste one follow-up question you asked Claude, and Claude's answer.

**My question:**

> For the 836 Buy transactions with negative shares: does the absolute value of shares × price equal the amount on those rows? And do they cluster by advisor, client, or date, or are they spread evenly?

**Claude's answer:**

> I ran the check on `fact_transactions.csv`. **The negative shares look like simple sign flips, spread randomly through the data. They are not a pattern tied to any advisor, client, or time period.**
>
> **1. |shares| × price = amount on every one of the 836 rows.** The largest difference is $0.005, which is rounding to the cent. This isn't limited to the negative rows. `amount` equals shares × price on **all 197,175 rows that have shares**: every Buy, Sell, and Dividend. So the dollar amounts on the 836 rows are correct; only the **sign of `shares`** is wrong. This also confirms flag #2: Dividend amounts are exactly shares × price, the full market value of the position, not a realistic dividend payout.
>
> **2. No clustering, so there's no systematic cause.**
>
> | Dimension | Result |
> |---|---|
> | Advisors | All **25** advisors have at least one. The most any advisor has is 47, against an average of about 33, which is ordinary random variation. |
> | Clients | **692** different clients, with **no client having more than 4**. |
> | Securities | **422** different securities. |
> | Year | Every year is 0.9–1.1% of that year's Buys (2020: 1.01%, 2021: 0.91%, 2022: 1.07%, 2023: 0.96%, 2024: 1.04%). |
>
> Example: `txn_id` 272, shares −261.9719 × price $441.71 = $115,715.61, which is exactly the recorded amount.
>
> **What this means.** An error that about 1% of rows share evenly, across every advisor, client, security, and year, fits a **random data-entry or system error on the `shares` sign**, not cancelled trades or mislabeled sells. A reversal would normally come with a matching original trade, and mislabeled sells would likely cluster somewhere. The simplest defensible treatment is to **flip the sign to positive (take the absolute value) and document it**, since amount and price already agree with the positive value. Keep a flag column so the change can be traced.
>
> **One more thing from the same check:** after converting `txn_date` to a date, **40,649 of 143,311 Buy and Sell transactions (28.4%) fall on a Saturday or Sunday**. That's almost exactly 2/7 (28.6%), the share you'd get if trade dates were picked at random across the calendar. Real trades can't settle on weekends, so this is further evidence the data is simulated. All 298,772 dates converted successfully, with no invalid dates.

---

## 2C — Business Check & Cross-Validation

### Business-reasonableness questions

#### 1. Which three transaction types would you expect to have no security, and why? Do the counts add up to 101,597?

**Deposit, Withdrawal, and Advisory Fee.** All three move **cash** into or out of a client's account without buying, selling, or holding a specific investment meaning it is less likely any security code is needed:

- **Deposit:** the client adds money to the account. The cash arrives before it is invested, so there is no security, share count, or price yet.
- **Withdrawal:** the client takes money out. Any securities would have been sold in a separate Sell transaction first, so the withdrawal itself is cash only.
- **Advisory Fee:** Wildcat Capital charges the client for its services, usually as a percentage of assets under management. The fee is taken from the account's cash and isn't tied to any one holding.

The other three types all involve a specific security. A **Buy** or **Sell** trades shares of it, and a **Dividend** is paid *because* the client holds shares of it. It makes sense that those rows have a `security_id`, `shares`, and `price`.

**The counts add up exactly:**

| txn_type | Count |
|---|---|
| Deposit | 35,981 |
| Withdrawal | 29,850 |
| Advisory Fee | 35,766 |
| **Total** | **101,597** |

The total matches the null count in `security_id`, `shares`, and `price` exactly. That means the nulls are **structural, not missing data**: they are blank because a value doesn't exist for that kind of transaction, not because it wasn't recorded therefore the dataset should be correct. These values should stay blank rather than be filled in or dropped. 

#### 2. What does it mean for a wealth management firm to have significantly more Buys (83,556) than Sells (59,755) over five years?

Buys outnumber Sells. The ratio is around 1.40–1.41 from 2021 to 2024, so this is a steady pattern.

**What it means for the business:**

- **Clients are net accumulators.** Over five years, they have mostly been net investing in the market. That fits clients in a saving and growth stage (for example, working professionals building retirement savings), and a firm that practices long-term, buy-and-hold investing.
- **Assets under management (AUM) are growing.** The dollar totals confirm it: about **$5.33 billion bought vs. $3.80 billion sold**, a net **$1.52 billion** moved into securities. Wildcat Capital's advisory fees are most likely a percentage of AUM, so growing invested assets means growing fee revenue. That's a healthy sign for the firm.
- **It fits normal advisory activity.** Advisors typically buy when new deposits arrive, reinvest dividends, and add to positions a little at a time (dollar-cost averaging). All of these create many Buys. Sells happen mainly for rebalancing, tax-loss harvesting, or to raise cash for withdrawals, which is less frequent.


**Extra Notes from Claude for Q3**
**Caveats before drawing conclusions:**

- **A count is not dollars.** Many small Buys and a few large Sells could still mean money flowing out. Here the dollar totals point the same way as the counts, but the dollar figures are what should be reported.
- **The money has to come from somewhere.** Net deposits were only about $0.33 billion ($1.82B deposited − $1.49B withdrawn). Most of the cash for net buying therefore came from **Dividends ($3.45B)**. As 2B showed, those dividend amounts are equal to full position values (shares × price), not realistic payouts. So the size of the net-buying story depends on dividend data that is not believable.
- **The 836 negative-share Buys are counted as Buys.** They are only 1% of Buys and don't change the conclusion, but they should be fixed before any holdings calculation.
- **Buys and Sells can't be turned into holdings from this file alone.** In 15,175 of 38,813 client–security combinations, clients sold more shares than they bought between 2020 and 2024. This suggests they held positions from before 2020, or that the data is simulated. Either way, calculating current holdings would need a starting balance.

#### 3. If Claude Cowork generated code to compute the average number of days between transactions, what would go wrong if the dates remained as strings?

This question I wasn't sure about so I received assistance from Claude
Computing "days between transactions" means **subtracting one date from another**, and text can't be subtracted. Several things could go wrong:

1. **The code crashes.** Subtracting two strings, or calling `.diff()` on a text column, raises `TypeError: unsupported operand type(s) for -: 'str' and 'str'`. I tested this in the course environment. This is the *good* outcome, because at least the error is visible.
2. **A "workaround" gives silently wrong answers.** If the code tried to make the dates numbers by removing the dashes, `2020-02-01` − `2020-01-31` would be computed as 20200201 − 20200131 = **70 "days"**, when the real gap is **1 day**. Every gap across a month or year boundary would be inflated, and the script would still run and print a plausible-looking average. This is the dangerous outcome.
3. **Ordering can be wrong.** "Days between transactions" only makes sense after sorting each client's transactions in time order. Text sorts alphabetically, which only works because this file uses YYYY-MM-DD. If any dates were in `MM/DD/YYYY` format, `01/15/2020` would sort *before* `12/01/2019`, and the gaps would be wrong, with no error.
4. **Real calendar logic is missing.** Text has no idea of month lengths, leap years (2020 and 2024 are both leap years in this data), or weekdays. That means no business-day gaps and no weekend checks.

**Fix:** convert the column with `pd.to_datetime(df["txn_date"], errors="coerce")` first. Check for any `NaT` (invalid dates), sort by client and date, and take the difference in days within each client. Done correctly on this data, the average gap between a client's transactions is about **13.1 days**.

#### 4. Is 2,700 clients served by 25 advisors (about 108 clients per advisor) plausible for a registered investment advisory firm?

**Yes, it's possible, but it seems high so it depends on the structure of the organization.**

- **In this data, every client has exactly one advisor**, and the load is fairly even: **87 to 129 clients per advisor** (median 106). No advisor is badly overloaded or underused.
- **Industry benchmarks:** Kitces Research found the average lead advisor at an RIA serves about **71 clients**, and considers **50–100 clients** a sustainable range. Advisors who report "thriving" average about 75 clients. Load rises with team support: the median is about 40 clients for solo advisors, 70 for 2-person teams, and **98 for 3-person teams**. A 2025 Kitces report put the typical range at roughly 65 to 277 clients.
- **What this means for Wildcat Capital:** about 108 clients per advisor is realistic if advisors are **supported by associate advisors, paraplanners, or client-service staff**, or if many clients are smaller accounts served mainly through model portfolios. If each advisor works alone and provides full financial planning, 108 relationships would be a heavy load, and service quality or advisor burnout could become a concern.
- **One thing to confirm:** whether a "client" means an individual or a household. If `client_id` is individuals and several belong to one household, the real number of relationships per advisor is lower and even more comfortable.

Sources: [Kitces — How Do Financial Advisors Actually Spend Their Time?](https://www.kitces.com/blog/how-do-financial-advisors-spend-time-research-study-productivity-capacity-efficiency/); [Kitces — Financial Advisor Success Requires Just 50 Great Clients](https://www.kitces.com/blog/50-great-clients-how-many-clients-does-a-financial-advisor-need/); [SmartAsset — Average Number of Clients per Financial Advisor](https://smartasset.com/advisor-resources/average-number-of-clients-per-financial-advisor)

#### 5. What are two plausible business explanations for a negative share count on a Buy, and what would you do next to determine which is more likely?

**Explanation 1: data-entry error.** The trade was a normal purchase, but the share quantity was recorded with a minus sign. In this case the purchase really happened, and the only wrong value is the sign of `shares`.

Used Claude for this explanation
**Explanation 2: a legitimate correction or reversal entry.** Some portfolio systems don't delete a mistaken or cancelled trade. Instead they post an offsetting entry, a "negative Buy" that backs out an earlier Buy (a trade cancellation, a failed trade, or a corrected allocation between accounts). In that case the row is *intentional*. It should cancel out an original Buy, not be "fixed".

**What the evidence says so far:**

I had a hunch that it made more sense that it was a sign flip so I had claude run a test
| Test | If sign error | If reversal | What I found |
|---|---|---|---|
| Is there a matching original Buy (same client, same security, same number of shares)? | No | Yes, every reversal should have one | **0 of 836** have a match |
| Does `amount` reverse too? | No, the amount stays positive | Usually yes, the cash is refunded (negative or offsetting amount) | **All 836 amounts are positive** and equal \|shares\| × price exactly |
| Are they clustered (one advisor, one period, one system change)? | Random, spread evenly | Often clustered around operational events | **Spread evenly:** all 25 advisors, 692 clients (max 4 each), about 1% of Buys in every year |

**All three tests point to Explanation 1, a sign error.** A reversal should have an original trade to reverse, and its cash amount should reverse too. Neither is true here.

**Next steps:**

1. **Trace a sample to the source.** Take 10–20 of these `txn_id`s to operations and compare them with trade confirmations, the order management system, and the custodian's statements. Did the client actually buy these shares on that date?
2. **Reconcile against positions.** For affected client–security pairs, check whether counting the row as −shares or +shares makes the resulting holdings match the custodian's reported position.
3. **Ask the data owner** how corrections and cancellations are recorded in the portfolio system. If reversals use a separate transaction type or a flag, a negative Buy is not the expected format.
4. **Until confirmed:** keep all 836 rows (don't delete them), add a flag column, and use the absolute value of `shares` in any holdings analysis. Document the decision so it can be reversed if operations finds they really are reversals.

This is an unexplained pattern in 1% of Buys, so it's a **finding to report**, not something to quietly drop. It is also a data quality issue to raise with operations, because a systematic sign error could affect client statements.

### Cross-validation: count of Buy transactions

I ran two independent scripts from the VS Code terminal. Both are saved in `HW02/scripts/`.

- **Prompt A**, [`scripts/crossval_a_direct.py`](scripts/crossval_a_direct.py): counts rows where `txn_type` equals exactly `"Buy"`.
- **Prompt B**, [`scripts/crossval_b_subtraction.py`](scripts/crossval_b_subtraction.py): counts all rows, then subtracts the rows whose `txn_type` is Sell, Deposit, Withdrawal, Dividend, or Advisory Fee.

#### What did each script return?

**Script A:**
```
Approach A (direct filter): Buy transactions = 83,556
```

**Script B:**
```
Total rows:                         298,772
  minus Sell                        59,755
  minus Deposit                     35,981
  minus Withdrawal                  29,850
  minus Dividend                    53,864
  minus Advisory Fee                35,766
Rows of the five other types:       215,216
Approach B (subtraction): Buy transactions = 83,556
```

#### Do the results agree?

**Yes.** Both return **83,556**, which also matches the known-answer benchmark and Section 7 of the EDA output. Script B's arithmetic checks out: 298,772 − 215,216 = 83,556. That means:

- The six transaction types are **exhaustive**: every row belongs to one of them. There is no seventh category and no blank `txn_type`.
- The labels are **clean**: there are no variants such as `"buy"`, `"BUY"`, or `"Buy "` with a trailing space. I confirmed that the column contains exactly six distinct values.

#### Why is it useful to verify a count using subtraction rather than direct filtering?

Because the two methods **fail in different ways**, a mistake that fools one of them is caught by the other:

- **Direct filtering only counts what it's told to look for.** If some Buys were stored as `"buy"`, `"Buy "`, or `"Purchase"`, filtering for `"Buy"` would silently leave them out. You'd get a smaller number with no warning.
- **Subtraction counts everything that *isn't* something else.** Those same mislabeled Buys, or any unexpected category or blank value, would end up in the Buy count. The two results would then disagree, which is the signal that something is wrong.
- **Subtraction also checks the data's structure.** If the numbers agree, the category list is complete and the categories don't overlap. That confirms the six types account for every row, not just that the "Buy" filter works.

So agreement between the two scripts gives much more confidence than running the same filter twice. It confirms both the count and the assumption that there are exactly six clean transaction types.

Sources:
Kitces — How Do Financial Advisors Actually Spend Their Time?
Kitces — Financial Advisor Success Requires Just 50 Great Clients
SmartAsset — Average Number of Clients per Financial Advisor
