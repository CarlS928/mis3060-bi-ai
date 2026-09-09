# Prompt Comparison — [Question chosen]

## Strategy 1 — Zero-shot

**Prompt sent:**
"What are the most important metrics for measuring credit risk in a consumer loan portfolio?"

**First 150 words of Claude's response:**
Credit risk in a consumer loan portfolio is usually assessed through a mix of borrower-level, loan-level, and portfolio-level metrics.

Borrower-level indicators start with the credit score (FICO or VantageScore) at origination and how it drifts over time, debt-to-income ratio, and payment history depth. Probability of default (PD) models translate these into a forward-looking risk estimate for each borrower or segment.

Loan-level indicators include loan-to-value ratio for secured products, the interest rate relative to risk tier, and loss given default (LGD) and exposure at default (EAD) — the three components that combine into expected loss (EL = PD × LGD × EAD).

Portfolio performance metrics are what most risk teams watch day to day: delinquency rates broken out by bucket (30, 60, 90+ days past due), net charge-off rate, roll

**Evaluation:**
What it did well: The response organizes credit risk assessment into a clean three-level structure — borrower-level, loan-level, portfolio-level — which is a genuinely useful mental model rather than a flat list of terms. It uses accurate, industry-standard vocabulary (PD, LGD, EAD, the EL = PD × LGD × EAD identity, LTV, roll rates, net charge-off) and gets the relationships right — e.g., correctly separating "backward-looking" indicators (credit score, payment history) from "forward-looking" ones (PD models). It also shows a bit of sophistication by noting that credit score isn't just a static origination number but something that drifts over time.

What's missing or generic: This reads as a textbook definitions dump rather than an answer shaped for Wildcat specifically. It never touches the things that make Wildcat's portfolio distinct — the five loan purposes (Auto, Personal, Home Improvement, Education, Business) or the secured-vs-unsecured split that matters a lot when the same DTI or credit score means different real-world risk depending on what's being financed. It's purely descriptive: it lists what the standard metrics are, but never critiques them — no mention of blind spots like income volatility (gig/seasonal work), the fact that a high income can mask a high DTI, or that these metrics say nothing about loan purpose or collateral. Compare that to the grounded response logged in business_context.md for this same question, which explicitly flagged those limitations — this response stops at "here's what exists" and never gets to "here's where this breaks down." That gap is the signature of a zero-shot, context-free prompt: comprehensive and correct, but generic.

---

## Strategy 2 — Role-assigned (role + audience)

**Prompt sent:**
You are a senior credit risk analyst at a large commercial bank presenting to a portfolio committee of three senior executives. The committee is reviewing the performance and risk profile of the bank’s consumer loan portfolio and wants to identify potential signs of deteriorating credit quality before they result in significant losses. The executives understand finance and banking but are not specialists in day-to-day credit risk modeling. Focus on metrics that are most useful for monitoring portfolio health, identifying emerging risk, forecasting potential losses, and supporting lending and risk-management decisions. For each metric, briefly explain what it measures, why it matters, and what an unfavorable trend could indicate.

"What are the most important metrics for measuring credit risk in a consumer loan portfolio?"

**First 150 words of Claude's response:**
A useful way to organize this for a committee is around four questions: how is the portfolio built today, how is it performing right now, where is it heading, and how much could it cost if things go wrong. Below are the metrics that map to those questions, tailored for a portfolio spanning multiple loan purposes (e.g., secured products like Auto and unsecured products like Personal loans) with varying risk profiles.

Delinquency rate by bucket (30/60/90+ days past due). Measures the share of the portfolio that has missed one or more payments, broken into severity tiers rather than one blended number. It matters because early buckets (30-day) are the leading edge of trouble — most problem loans pass through them before anything worse happens.

**Evaluation:**
What it did well: This response is clearly shaped by an audience and a purpose — it opens by organizing the whole answer around four questions a committee would actually ask (built, performing, heading, cost), rather than a bare list of terms. That framing carries through: every metric gets a "why it matters" and, notably, a sentence on what a trend in that metric would signal (e.g., "a rising 30-day bucket while 90+ stays flat is often the first visible sign of deterioration"), which moves it from definition to interpretation — genuinely useful for a decision-making audience. It's also tailored to Wildcat specifically in ways Response 1 wasn't: it names the five loan purposes, distinguishes secured (Auto, Home Improvement) from unsecured products, ties LTV directly to LGD, and explicitly flags that a smaller, higher-balance segment like Business can swing losses disproportionately — echoing the concentration-risk nuance from the grounded Q2 answer in business_context.md. It also cleanly separates lagging/realized indicators (NCO, delinquency, roll rate) from leading/forward-looking ones (PD, EL, origination-quarter score/DTI trends, FPD), which is a distinction Response 1 only gestured at.

What's missing or generic: The response is comprehensive to a fault — roughly 14 metrics across five categories is closer to a reference glossary than something a committee would review in one sitting; a more audience-tuned answer would curate down to the handful that matter most and say so explicitly, rather than presenting everything with equal weight. It also never circles back to the limitations/blind-spots angle that was the explicit ask in the Q1 prompt (data quality issues behind these metrics, model risk in PD estimates, survivorship bias in vintage curves, the fact that "Delinquent" as a flat status may hide severity) — it's strong on what to track and why but silent on where these numbers could mislead the committee. Education loans, despite being named, get no purpose-specific treatment (e.g., deferment periods, third-party disbursement) the way Auto and Business do. So relative to Response 1, this reads as far less generic and much better audience-fitted, but it trades one weakness (no business context) for a new one (exhaustiveness without prioritization, and no critical/limitations framing).

---

## Strategy 3 — Few-shot

**Prompt sent:**
Use the following example to guide the structure and level of detail of your response. The example is about a different topic and is only meant to demonstrate the desired output format.
Example format:
Metric: Customer Retention Rate
What it measures: The percentage of customers who continue using a company’s services over a given period.
Why it matters: Helps evaluate customer loyalty and the stability of the company’s customer base.
What to watch for: A sustained decline could indicate increasing customer dissatisfaction or competitive pressure.
Use this framework to answer the following question: "What are the most important metrics for measuring credit risk in a consumer loan portfolio?"

**First 150 words of Claude's response:**
Metric: Order Fill Rate

What it measures: The percentage of customer orders fulfilled completely and accurately from available inventory, without stockouts or backorders.

Why it matters: Directly reflects how well supply planning matches actual demand; low fill rates signal inventory shortfalls that drive lost sales and customer attrition.

What to watch for: A declining trend alongside rising inventory levels can indicate a demand-forecasting mismatch rather than a true supply shortage.

Metric: Inventory Turnover Ratio

What it measures: How many times inventory is sold and replaced over a given period, calculated as cost of goods sold divided by average inventory.

Why it matters: Balances the cost of holding stock against the risk of stockouts

**Evaluation:**
What it did well: The format itself is well-executed. Each entry follows a consistent, useful structure — Metric / What it measures / Why it matters / What to watch for — and the "what to watch for" line consistently does the hard work of turning a static definition into an interpretive signal (e.g., "rising landed cost despite stable unit purchase prices points to freight, tariff, or warehousing cost creep"). That's the same kind of trend-to-implication reasoning that made Response 2 strong. The metric definitions themselves (fill rate, inventory turnover, perfect order rate, cash-to-cash cycle, supplier OTD, landed cost) are also accurate and correctly explained on their own terms.

What's missing: This response doesn't answer the credit risk question at all. Every metric here (order fill rate, inventory turnover, perfect order rate, cash-to-cash cycle time, supplier on-time delivery, landed cost per unit) is a supply chain / operations KPI — there's nothing here about credit score, DTI, PD/LGD/EAD, delinquency or default rates, or loan portfolio segmentation. If this was meant to answer the same underlying question as Responses 1 and 2 (credit risk metrics for Wildcat's consumer loan portfolio), it's a complete domain miss, not just a generic answer.

---

## Conclusion
Across the three strategies, the role-assigned prompt (Strategy 2) produced the most useful output for a BI analyst: it organized metrics around what a portfolio committee actually needs to see, tailored each metric to Wildcat's specific loan purposes and secured/unsecured split, and — critically — paired every metric with a "what to watch for" interpretation that turns a raw number into an actionable signal. The zero-shot response (Strategy 1) was technically accurate and well-organized into borrower/loan/portfolio levels, but it read as a generic textbook answer with no connection to Wildcat's data or business context, and it never addressed the limitations of the metrics it listed. The few-shot response (Strategy 3) was the clear failure of the three: rather than adapting the exemplar format to the credit risk question, it inherited the exemplars' domain and produced a complete list of supply chain KPIs with no relevance to a consumer loan portfolio at all. This suggests that for this kind of task, giving Claude a role and an audience is more reliable than giving it examples, unless those examples are carefully matched to the target domain. For a BI analyst who needs to go straight from prompt to a dashboard or committee deck, Strategy 2's output required the least rework and the most direct translation into reportable metrics.

## Fact-Check
I fact-checked a claim from the delinquency-vs-default response.

Claim: Claude said default is triggered "commonly 90+ days" after non-payment.

Source: Federal Reserve's Uniform Retail-Credit Classification and Account-Management Policy.

What the source says: 90 days past due is actually the threshold for classifying a loan as substandard (seriously delinquent) — the charge-off/loss threshold for closed-end consumer loans (Auto, Personal, Home Improvement, Education — most of Wildcat's book) is 120 days, and 180 days for credit cards.

Verdict: Partial agreement — Claude was in the right ballpark and appropriately hedged, but conflated two distinct regulatory milestones, understating the actual default/charge-off threshold by 30 days. The write-up concludes that hedged numeric claims from Claude are fine for conversational framing but should be verified against primary sources before being used in a report or baked into a model.

Sources:

Uniform Retail-Credit Classification and Account-Management Policy (Federal Reserve)