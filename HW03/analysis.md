# HW3 Analysis — Do Executive Changes Precede or Follow Earnings?

**Data:** 28 personnel events (3 compensation-only "other" rows excluded) from 16 Item 5.02 filings, Sept 2025 – Sept 2026, each matched to the nearest of that company's four earnings filings (`corporate_events_timeline.csv`).

In my data, executive changes mostly **precede** earnings announcements: 20 of 28 events came before the nearest earnings filing, 6 came after and 2 fell in the same week (by filing, so Walmart's five-person January reshuffle doesn't dominate: 11 before, 4 after, 1 same week). The most consequential changes clustered 1–3 weeks ahead of earnings:
- Walmart's CEO succession (McMillon to Furner) was filed 6 days before its Q3 results.
- JPMorgan's Co-President promotions and Marianne Lake's retirement came 19 days before Q2.
- Apple's Cook-to-Ternus CEO transition came 10 days before its fiscal Q2 report.

This pattern suggests these companies disclose major leadership news ahead of the earnings call, so executives can address it on the call rather than letting it overshadow the numbers. The pattern varies by company, though. Walmart, JPMorgan and NVIDIA were almost entirely "before", while Microsoft's changes were all board seats (Rodriguez, Di Sibio, Hoffman) that follow its annual-meeting calendar rather than its earnings cycle, and 2 of its 3 fell after earnings; with only 16 filings, and roughly 90 days between earnings dates, this is a pattern worth watching, not a statistically established effect.
