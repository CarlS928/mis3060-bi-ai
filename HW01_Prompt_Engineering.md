# HW1: Claude Desktop & Prompt Engineering
## MIS3060 Business Intelligence with AI | Villanova University

**Due:** End of Week 3 (Sunday 11:59 PM)
**Weight:** 5% of final grade
**Submission:** GitHub repository link submitted via Brightspace
**Tools:** Claude Desktop (Claude Cowork), GitHub (browser only — no installs needed)

---

## Overview

This assignment establishes your course GitHub repository and gives you hands-on experience with the most fundamental skill of AI-assisted work: writing effective prompts. By the end of this assignment you will have a working repository, a library of documented prompts, and a clear sense of what separates a useful Claude response from a generic one.

No Python or coding is required for this assignment.

---

## Learning Objectives

- Set up a GitHub repository structured for the full course
- Apply three distinct prompting strategies inside a Claude Cowork project and evaluate their outputs
- Practice the professional discipline of documenting AI tool usage
- Begin building the habit of verifying AI-generated claims

---

## The Wildcat Capital Context

Wildcat Capital is a regional consumer lender with 2,340 loan records. You are the junior BI analyst on the portfolio analytics team. Your job over the course of this semester is to build an end-to-end analytics pipeline for this portfolio — starting with understanding the business.

---

## Part 1 — Set Up Your Course Repository (10 points)

**Everything in this Part happens in your browser — no installs, no git commands, no VS Code.** Later in the course (Week 3+), you'll set up git and VS Code locally for Vibe Coding — that's a more powerful workflow for working with code, but you don't need it for HW1.

**For exact click-by-click steps and troubleshooting, use the companion GitHub Quick-Start Guide posted with this assignment.** What's required for this Part:

1. Create a free GitHub account (skip if you already have one)
2. Create a new **public** repository named `mis3060-bi-ai`, with **"Add a README file"** checked
3. Edit `README.md` directly in GitHub's browser editor and replace the placeholder content with the template below, filling in your own name and GitHub username
4. Commit your change directly to the `main` branch with a message like `HW1: Initial repo setup with course README`

```markdown
# MIS3060 Business Intelligence with AI
Villanova School of Business — Fall 2026

**Student:** [Your Full Name]
**GitHub:** [Your GitHub Username]

## About This Repository
This repository contains all lab exercises, homework assignments, and project
deliverables for MIS3060. Later assignments use the Vibe Coding workflow —
specify in natural language → generate with Claude Code → validate → commit —
introduced once Claude Code is covered later in the course. HW1 has no code.

## Repository Structure
- `data/`       — raw and cleaned datasets (CSV files)
- `scripts/`    — Python analysis scripts
- `hw01/` through `hw08/` — homework submissions
- `app/`        — Streamlit application (Weeks 12–13)
- `visualizations/` — saved chart images

## Course Stack
Claude Desktop · Claude Code · Python · Power BI · Streamlit · GitHub

## Assignment Index
| Assignment | Topic | Status |
|---|---|---|
| HW1 | Prompt Engineering | ✓ Complete |
| HW2 | EDA Script | Pending |
| ... | ... | ... |
```

**Deliverable:** Your `README.md` must be visible and rendered at `github.com/[username]/mis3060-bi-ai`.

---

## Part 2 — Business Context Exploration (20 points)

**Before you start:** Parts 2 and 3 run inside your **Wildcat Capital Cowork project** — the same one you set up in the Week 2 in-class exercises. If you haven't created it yet: build the `Wildcat_Capital` folder with the Section 2 structure, create a Cowork project from that folder ("Use an existing folder"), and add folder instructions plus a `CLAUDE.md`. Then do all prompting for Parts 2 and 3 as new conversations inside that project, not in a standalone chat.

Using Claude Desktop, ask **three strategic questions** about the Wildcat Capital business. These should be grounded in what's actually in `wildcat_loans_clean.csv` — its five loan purposes (Auto, Personal, Home Improvement, Education, Business), four status categories (Current, Paid Off, Default, Delinquent), and borrower attributes (credit score, debt-to-income ratio, annual income) — even though you're not asking Claude to compute anything from the file itself. That's what ICE 2.1 is for; Part 2 is about understanding what these categories *mean* for the business before you start building analytics on them.

**Requirements for your questions:**
- At least one question about credit risk metrics used in consumer lending, applied to the specific attributes in Wildcat's data (credit score, debt-to-income ratio, annual income)
- At least one question about what a portfolio committee typically wants to see in a quarterly review, for a lender with Wildcat's specific loan-purpose mix (Auto, Personal, Home Improvement, Education, Business)
- At least one question about the difference between delinquency and default, and how that maps onto Wildcat's four status categories

**Example of a grounded, strategic question** (for reference — don't reuse verbatim):

> *"Our portfolio has five loan purposes: Auto, Personal, Home Improvement, Education, and Business. Business loans tend to be far larger individually than the other four categories. What credit risk considerations are specific to Business lending that wouldn't apply to something like Auto or Personal loans, and how should that shape what a portfolio committee monitors for that segment?"*

This is "strategic" because it doesn't ask Claude to calculate anything — it asks Claude to reason about the business implications of a category that's actually in the data.

**Deliverable:** Create `hw01/business_context.md` in your repository. For each question, document:
1. The exact prompt you sent
2. A summary of Claude's response (3–5 sentences — do not paste the full response)
3. One follow-up question the response raised for you

---

## Part 3 — Prompt Engineering Comparison (40 points)

Choose **one** of the following analytical questions:

- *"What are the most important metrics for measuring credit risk in a consumer loan portfolio?"*
- *"What should a BI dashboard for a loan portfolio committee include, and why?"*
- *"How should a BI analyst communicate data limitations to a non-technical audience?"*

Ask Claude the question using all **three** prompting strategies below, inside your Wildcat Capital Cowork project. Use a **new conversation within the project** for each version so prior context does not carry over. Since Cowork carries context forward across conversations in a project, do Strategy 1 (zero-shot) first — ideally before you've asked the project anything else related to this question — so it's a genuine zero-shot baseline.

**Strategy 1 — Zero-shot:** Ask the question exactly as written, with no additional context.

**Strategy 2 — Role-assigned (role + audience):** Assign Claude a role and specify an audience before asking the question. Example: *"You are a senior credit risk analyst presenting to a portfolio committee of three senior executives..."*

**Strategy 3 — Few-shot:** Provide one example of the output format you want before asking the question. The example does not need to answer the question — it just shows the structure.

**Deliverable:** Create `hw01/prompt_comparison.md` with the following for each strategy:
1. The complete prompt you sent (copy it exactly)
2. The first 150 words of Claude's response
3. Your evaluation: what did this strategy do well? What was missing or generic?

**Conclusion section (required):** Write 3–5 sentences comparing the three strategies. Which produced the most useful output for a BI analyst, and why?

---

## Part 4 — Fact-Check One Claim (20 points)

From any of Claude's six responses in Parts 2 and 3, identify **one specific factual claim** — a number, a threshold, a definition, or a named standard. It must be something that can be verified with an external source.

Look up the claim using one of:
- CFPB (consumerfinance.gov)
- Federal Reserve (federalreserve.gov)
- FDIC (fdic.gov)
- Investopedia (for definitions)
- A peer-reviewed source

**Deliverable:** Add a `## Fact-Check` section to `hw01/prompt_comparison.md` with:
1. The exact claim Claude made (quote it)
2. The source you used and the URL
3. What the source says
4. Whether they agree — and if not, what you conclude about the reliability of that type of claim from Claude

---

## Part 5 — AI Usage Log (10 points)

Complete the `AI_Usage_Log_Template.md` (available on Brightspace and in the course repo) for this assignment. Save it as `hw01/ai_usage_log.md`.

---

## Submission Checklist

Before submitting your GitHub link on Brightspace, verify:

- [ ] `README.md` visible at your GitHub URL with correct structure
- [ ] `hw01/business_context.md` — 5 questions with prompts, summaries, and follow-ups
- [ ] `hw01/prompt_comparison.md` — 3 prompting strategies with evaluation and conclusion
- [ ] `hw01/prompt_comparison.md` — Fact-Check section included
- [ ] `hw01/ai_usage_log.md` — completed using the course template
- [ ] All files committed and pushed (check github.com — not just VS Code)

**Submit:** Paste your GitHub repository URL into the Brightspace assignment by the deadline.

---

## Grading Rubric

| Component | Points | What earns full credit |
|---|---|---|
| Repository setup | 10 | README visible, correct structure, committed |
| Business context questions | 20 | 5 questions meeting all requirements, thoughtful follow-ups |
| Prompt comparison | 40 | All 3 strategies present, full prompts shown, specific evaluation |
| Fact-check | 20 | Specific claim identified, verified, conclusion stated |
| AI Usage Log | 10 | All sections completed with specifics, not vague |

---


