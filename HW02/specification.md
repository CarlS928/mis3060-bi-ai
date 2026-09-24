# HW02 Specification — EDA Script for Wildcat Capital Transactions

**Author:** Carl Söderman
**Course:** MIS3060 Business Intelligence with AI
**Purpose:** Instructions for Claude Cowork to generate a single exploratory data analysis (EDA) script.

---

## What I need

Write **one Python script** that performs a complete exploratory data analysis of Wildcat Capital's transaction history. Everything described below must live in that one file and run from start to finish in a single execution. Do not split the work into multiple scripts, notebooks, or helper modules.

Save the script as `HW02/hw02_eda.py`.

## Background on the data

The file `fact_transactions.csv` contains every client transaction recorded in Wildcat Capital's portfolio management system from January 2020 through December 2024. Each row is one transaction event of one of six types: Buy, Sell, Deposit, Withdrawal, Dividend, or Advisory Fee.

The file has nine columns:

| Column | Meaning |
|---|---|
| `txn_id` | Unique identifier for each transaction |
| `client_id` | The client who made the transaction |
| `advisor_id` | The advisor responsible for the client |
| `security_id` | The security involved (blank for cash movements such as deposits, withdrawals, and fees) |
| `txn_date` | Date of the transaction, in YYYY-MM-DD format |
| `txn_type` | One of the six transaction types listed above |
| `shares` | Number of shares involved (blank when no security is involved) |
| `price` | Price per share (blank when no security is involved) |
| `amount` | Dollar value of the transaction |

Some blanks are expected, because cash transactions have no security, shares, or price. The script should report blanks, not remove or fill them. The script must **not** modify, clean, or overwrite the raw data file in any way. It only reads and reports.

## Environment and file locations

- The script is run from a Windows PowerShell terminal in VS Code, with the project's virtual environment activated. Use only libraries listed in `Requirements.txt` (pandas, numpy, matplotlib, seaborn, and so on).
- All file paths should be worked out relative to the `HW02` folder. Base them on the script's own location, so the script works no matter which folder it is launched from.
- **Input:** the raw data is at `HW02/02_Data/Raw/fact_transactions.csv`. The course instructions call this folder `data/raw/`, but in this repository it is `02_Data/Raw/`.
- **Charts:** save to `HW02/charts/`. Create the folder if it does not exist.
- **Text summary:** save to `HW02/hw02_profile.txt`.
- Running the script again should overwrite the charts and summary file, not add duplicates.

## Steps the script must perform, in order

Each step should print a clear section heading to the terminal (for example, "=== 3. Missing Values ===") so the output is easy to read and match to this list.

1. **Header comment block.** At the very top of the file, include a comment block giving the script name, what it does, the dataset it analyzes (`fact_transactions.csv`, Wildcat Capital transactions 2020–2024), the author (Carl Söderman), and the date the script was generated.

2. **Load the data.** Read `fact_transactions.csv` into a pandas DataFrame. Load `txn_date` as it is stored in the file, as text, and do not convert it to a date type while loading. One of the things we are checking is how the date is stored.

3. **Shape.** Print the number of rows and the number of columns.

4. **Column names and data types.** Print every column name alongside its data type as pandas loaded it.

5. **Missing values.** Print the count of missing values for every column, including columns with zero missing values.

6. **Descriptive statistics.** For every numeric column, print the count, mean, standard deviation, minimum, 25th percentile, median, 75th percentile, and maximum.

7. **Transaction type breakdown.** For `txn_type`, print how many transactions fall into each type and what percentage of all transactions that represents. Sort from most frequent to least frequent. Round percentages to two decimal places.

8. **Unique entities.** Print the number of distinct clients (`client_id`), distinct advisors (`advisor_id`), and distinct securities (`security_id`, ignoring blanks) that appear in the file.

9. **Date range.** Print the earliest and the latest `txn_date` in the dataset.

10. **Duplicate check.** Count how many `txn_id` values appear more than once and print that count. Zero is the expected result, but the script should report whatever it finds.

11. **Amount distribution.** Print the mean, median, and skewness of the `amount` column. Show mean and median as dollar values rounded to two decimal places. Show skewness to two decimal places, followed by a short plain-English label: "right-skewed" if positive, "left-skewed" if negative, or "approximately symmetric" if close to zero.

12. **Amount by transaction type.** Group the data by `txn_type`. For each type, show the number of transactions and the mean and median `amount`, with amounts rounded to two decimal places. Sort the table by mean amount, highest first, and print it.

13. **Correlations.** Compute the correlation matrix for `shares`, `price`, and `amount`, round it to two decimal places, and print it. Then find the three strongest correlations between *different* variables. Ignore each variable's correlation with itself, count each pair only once, and rank by strength regardless of sign. Print them in order, naming both variables and the correlation value.

14. **Negative shares.** For the `shares` column, broken out by `txn_type`, print the minimum value, the maximum value, and how many rows have a negative value. Include every transaction type in the output, even those with no shares data or no negative values.

15. **Shape check.** If the dataset's shape is not exactly 298,772 rows by 9 columns, print a clearly visible warning that states the expected shape and the actual shape. If the shape matches, print a short confirmation that it matches.

16. **Charts.** Create and save three charts as PNG files in `HW02/charts/`. Each chart needs a descriptive title, labeled axes, and readable text:
    - **`hist_amount.png`**: a histogram of `amount`, with one vertical line at the mean and a second at the median. Use a different color or line style for each line, and include a legend identifying which is the mean and which is the median, with their dollar values.
    - **`box_amount_by_type.png`**: a horizontal box plot of `amount`, with one box for each `txn_type`.
    - **`scatter_shares_amount.png`**: a scatter plot with `shares` on the x-axis and `amount` on the y-axis, with points colored by `txn_type` and a legend. With almost 300,000 rows, use small, partly transparent points so the chart stays readable. Rows with no shares value will not appear, which is expected.

    Save the charts to file without opening pop-up windows, so the script finishes on its own. Close each figure after saving it.

17. **Text summary file.** Write a plain-text summary of the results of steps 3 through 15 (shape, data types, missing values, descriptive statistics, transaction type breakdown, unique entities, date range, duplicates, amount distribution, amount by type, correlations, negative shares, and the shape check) to `HW02/hw02_profile.txt`. It should use the same section headings and contain the same numbers that were printed to the terminal, so the file can be read on its own without re-running the script.

At the end of the run, print a short message confirming that the script finished and listing the paths of the three charts and the summary file it saved.

## Quality expectations

- **One script, one run.** All seventeen steps run together in one file, in one execution, with no manual steps in between.
- **Readable code.** Use short comments marking each numbered step, so each part of the output can be traced back to the code that produced it.
- **Readable output.** Print tables with aligned columns. Format dollar amounts with commas and two decimal places.
- **No hard-coded results.** Every number must be calculated from the data when the script runs. The only fixed value allowed is the expected shape (298,772 × 9) used in step 15.
- **Read-only.** Do not change, clean, or overwrite the raw CSV file.
