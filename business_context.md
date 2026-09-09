# Business Context — Wildcat Capital (ICE Part 2)

Three strategic questions posed to Claude, grounded in the structure of `wildcat_loans_clean.csv` (five loan purposes: Auto, Personal, Home Improvement, Education, Business; four status categories: Current, Paid Off, Default, Delinquent; borrower attributes: credit score, debt-to-income ratio, annual income). No calculations were requested — these questions ask Claude to reason about what these categories mean for the business before any analytics work begins.

---

## Question 1: Credit risk metrics in consumer lending

**Prompt sent:**
"Wildcat's loan data includes credit score, debt-to-income ratio, and annual income for each borrower. In consumer lending, how are these three attributes typically used together to assess credit risk, and are there known limitations or blind spots when relying on them — especially for a portfolio that spans Auto, Personal, Home Improvement, Education, and Business loans?"

**Summary of response:**
Claude explained that credit score, DTI, and income are usually read as a triangle rather than independently: credit score signals repayment history and behavior over time, DTI signals current capacity to take on additional debt, and income anchors both in dollar terms. Lenders often combine them into tiered risk buckets (e.g., prime/near-prime/subprime) rather than using any single metric as a cutoff, since a high income can mask a high DTI and a good credit score can lag a recent income shock. Claude flagged that these three attributes say little about loan purpose or collateral, which matters a lot when purposes range from a secured Auto loan to an unsecured Personal loan — the same borrower profile can carry very different real-world risk depending on what's being financed. It also noted these metrics are backward- or point-in-time looking and don't capture volatility in income (e.g., gig or seasonal work) or intent behind the loan.

**Follow-up question this raised:**
Does Wildcat's data include any loan-purpose-specific risk adjustment (like a different DTI threshold for Business vs. Auto), or is one blended risk model applied across all five categories?

---

## Question 2: Quarterly portfolio committee review

**Prompt sent:**
"Wildcat Capital's loan portfolio is split across five purposes — Auto, Personal, Home Improvement, Education, and Business — with very different typical loan sizes and risk profiles. What does a portfolio committee at a lender like this typically want to see in a quarterly review, and how might the reporting need to differ by purpose segment rather than just looking at the portfolio as a whole?"

**Summary of response:**
Claude described a typical quarterly review as covering portfolio composition and growth (balances and unit counts by segment), performance trends (delinquency and default rates, often with vintage or cohort views), concentration risk, and profitability or yield by segment. It emphasized that a committee usually wants segment-level breakdowns rather than a single blended number, because a healthy overall default rate can hide a deteriorating segment — Business loans in particular warrant closer scrutiny given they tend to be larger and fewer in number, so a handful of defaults can swing the segment's numbers disproportionately. Claude suggested Education and Home Improvement loans might get attention for different reasons (e.g., longer terms, seasonality, or tied to third-party disbursement), and that committees often ask for trend lines (quarter-over-quarter) rather than single snapshots so they can see direction, not just current state.

**Follow-up question this raised:**
Given Business loans are fewer but larger, should the committee deck weight segments by dollar exposure, by loan count, or show both side by side to avoid a misleading picture?

---

## Question 3: Delinquency vs. default, mapped to Wildcat's status categories

**Prompt sent:**
"Wildcat's loan status field has four categories: Current, Paid Off, Default, and Delinquent. In consumer lending, what's the practical difference between delinquency and default, and how should a lender think about the relationship between those two categories — for example, does every delinquent loan eventually become a default, or are they more distinct outcomes?"

**Summary of response:**
Claude explained that delinquency is typically a timing status — a borrower has missed one or more scheduled payments but the loan is still considered active and potentially recoverable — while default is a more severe, often terminal classification triggered after a longer period of non-payment (commonly 90+ days, though the exact threshold varies by lender and loan type) or a formal declaration that the borrower is unlikely to repay. It noted that delinquency and default aren't strictly sequential in a dataset snapshot: a loan can be delinquent and later cure (return to Current) without ever reaching Default, so the two aren't just "early stage" and "late stage" of the same outcome. Claude also pointed out that for a static snapshot like Wildcat's CSV, "Delinquent" likely represents a fluid, transitional state, while "Default" and "Paid Off" are closer to terminal states, which matters for how you'd model transition probabilities between statuses.

**Follow-up question this raised:**
Does Wildcat's Delinquent category capture how many days past due a loan is, or is it a flat status with no severity tiering — and if it's flat, is that a gap worth flagging before building risk models on top of it?
