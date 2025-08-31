# 📊 Vendor Performance Data Analytics Project

End‑to‑end, reproducible pipeline to ingest raw CSVs, build a consolidated **Vendor Sales Summary**, and analyze vendor performance using Python, SQL, and notebooks.

---

## 🔥 Highlights

* **Database ingestion** from `dataset/*.csv` into MySQL with SQLAlchemy.
* **Consolidated summary table** (CTE-based SQL joining purchases, sales, and freight).
* **Feature engineering**: Gross Profit, Profit Margin, Stock Turnover, Sales‑to‑Purchase Ratio.
* **Exploratory analysis** in Jupyter (Pareto charts, distributions, confidence intervals, top N vendors/brands).
* **Logging** to `logs/` for ingestion & summary creation.
* **GitHub‑friendly** structure with guidance for large datasets.

---

## ✅ Prerequisites

* **Python** 3.10+
* **MySQL** 8.0+ (for the MySQL pipeline). SQLite can be used for quick local experiments if you adapt connection code.
* **pip/venv** for dependency management

---

## 📦 Installation

```bash
# 1) Clone the repo
git clone https://github.com/<your-username>/vendor-performance-analysis.git
cd vendor-performance-analysis

# 2) Create & activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt
```

## 🔐 Configure Environment Variables

Create a real `.env` file from the template below:

**`.env.example`**

```
# MySQL connection
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=inventory_db
```

> Never commit your real `.env` to GitHub. `.gitignore` should exclude it.

**Example `.gitignore` entries**

```
# virtual envs
.venv/

# OS/editor junk
.DS_Store
.ipynb_checkpoints/
__pycache__/

# data
*.db
*.zip
*.gz
*.parquet
*.feather
*.sqlite
*.sqlite3

dataset/*
!dataset/sample/

# secrets
.env
logs/
```

---

## 📥 Step 1 — Prepare the Data

Place your raw CSVs inside `dataset/` with the expected names:

* `purchases.csv`
* `sales.csv`
* `vendor_invoice.csv`
* `purchase_prices.csv`

> If you have different filenames/paths, that’s fine—just keep them inside `dataset/` (the ingestion script picks up all `*.csv`) or adjust the code accordingly.

For GitHub, include **tiny samples** in `dataset/sample/` and share links to full datasets in the README.

---

## ⚙️ Step 2 — Ingest to MySQL

The ingestion script loads **every CSV file** in `dataset/` into MySQL, naming each table by the CSV filename (without extension).

**Run:**

```bash
# from repo root
python scripts/ingestion_db.py
```

**What it does:**

* Reads `dataset/*.csv`
* Creates/overwrites MySQL tables named after each CSV
* Logs progress to `logs/ingestion_db.log`

**Common issues & fixes**

* *Connection error*: verify `.env` values and that MySQL is running.
* *No CSVs found*: ensure files are in `dataset/` (not `datasets/`) and end with `.csv`.
* *Datatype quirks*: Pandas will infer types—override dtypes in `read_csv` if needed.

> 💡 Tip: For very large CSVs, consider chunked ingestion (e.g., `chunksize=100_000`) and add `if_exists='append'` in `to_sql` to stream rows.

---

## 🧮 Step 3 — Build the Vendor Sales Summary

The summary pipeline:

1. Uses a **CTE SQL** query to combine purchases, sales, and freight by vendor/brand.
2. Cleans and engineers features.
3. Writes the final DataFrame back to the database (table: `vendor_sales_summary`).

**Run:**

```bash
python scripts/get_vendor_summary.py
```

**What it computes**

* **GrossProfit** = `TotalSalesDollars − TotalPurchaseDollars`
* **ProfitMargin** (%) = `GrossProfit / TotalSalesDollars * 100`
* **StockTurnover** = `TotalSalesQuantity / TotalPurchaseQuantity`
* **SalesToPurchaseRatio** = `TotalSalesDollars / TotalPurchaseDollars`

**Outputs**

* MySQL table: `vendor_sales_summary`
* Log file: `logs/get_vendor_summary.log`

**Troubleshooting**

* *“no such table …”*: ensure ingestion created `purchases`, `sales`, `vendor_invoice`, `purchase_prices` tables.
* *Nulls/NaNs*: the cleaning step fills missing values with zeros. Adjust if business logic requires otherwise.

---

## 🧪 Step 4 — Explore in Notebooks

Open Jupyter and run analyses end‑to‑end, or use the provided notebooks:

```bash
jupyter notebook
```

* **DataBaseIngestion.ipynb** — Validate ingestion, preview tables
* **Exploratory\_Data\_Analytics.ipynb** — EDA, top vendors/brands, distributions
* **vendor\_performance\_analysis.ipynb** — KPIs, Pareto charts, confidence intervals

### Example: Pareto Chart for Vendor Contribution

```python
fig, ax1 = plt.subplots(figsize=(12, 6))
sns.barplot(
    x=top_vendors['VendorName'],
    y=top_vendors['PurchaseContribution (%)'],
    palette='mako', ax=ax1
)
for i, v in enumerate(top_vendors['PurchaseContribution (%)']):
    ax1.text(i, v + 1, f"{v}%", ha='center', fontsize=9)
ax2 = ax1.twinx()
ax2.plot(
    top_vendors['VendorName'],
    top_vendors['Cumulative_Contribution (%)'],
    color='red', linestyle='dashed', marker='o', label='Cumulative %'
)
ax1.set_xticklabels(top_vendors['VendorName'], rotation=90)
ax1.set_ylabel('Purchase Contribution (%)')
ax2.set_ylabel('Cumulative Contribution (%)')
ax1.set_title('Pareto: Vendor Contribution to Total Purchases')
ax2.axhline(80, color='gray', linestyle='dotted', alpha=0.6)  # 80/20 reference
ax2.legend(loc='upper right')
plt.tight_layout(); plt.show()
```

### Example: Confidence Interval Utility

```python
from scipy import stats
import numpy as np

def confidence_interval(series, confidence=0.95):
    series = pd.to_numeric(series, errors='coerce').dropna()
    mean_val = series.mean()
    std_err = series.std(ddof=1) / np.sqrt(len(series))
    t_crit = stats.t.ppf((1 + confidence)/2, df=len(series) - 1)
    moe = t_crit * std_err
    return mean_val, mean_val - moe, mean_val + moe
```

---

## 🛠️ How to Adapt / Extend

* **Rename columns**: If your CSVs use different headers, update the SQL CTE and cleaning logic.
* **Add KPIs**: Extend the feature engineering section to compute lead time, fill rate, returns, etc.
* **Switch databases**: Replace the SQLAlchemy engine with SQLite/Postgres as needed.
* **Automate**: Wrap the pipeline in a `main.py` or Makefile; schedule via cron/Airflow.

---

## 🧷 Reproducibility & Data Policy

* Commit only code, notebooks, and tiny **sample** datasets.
* Host full data externally and link it in the README.
* Use `.env` for secrets; never hard‑code credentials.

---

## 🧹 Housekeeping

* **Logs**: Inspect `logs/ingestion_db.log` and `logs/get_vendor_summary.log` when debugging.
* **Code style**: Optional—add `ruff`/`flake8` and `black` to pre‑commit hooks.
* **Testing**: Optional—add unit tests for cleaning and KPI formulas.

---

## 🚀 Quickstart (TL;DR)

1. `git clone … && cd vendor-performance-analysis`
2. `python -m venv .venv && .venv/Scripts/activate`
3. Create `.env` with MySQL creds
4. Put CSVs in `dataset/` (or use `dataset/sample/`)
5. `pip install -r requirements.txt`
6. `python scripts/ingestion_db.py`
7. `python scripts/get_vendor_summary.py`
8. `jupyter notebook` → open and run the analysis notebooks

---

## ❓FAQ / Troubleshooting

**Q: Git push rejected due to large files**
A: Add big files to `.gitignore`, keep samples only, and host full data externally (Drive/Kaggle). If you must, use Git LFS (paid tiers for multi‑GB).

**Q: `no such table` when building summary**
A: Run the ingestion step first to create the base tables in the database.

**Q: Wrong column names / `KeyError`**
A: Print `df.columns` and align the code (SQL & cleaning) to your schema.

**Q: MySQL auth errors**
A: Verify `.env` values and that the MySQL instance is reachable (port/user/password). Grant privileges if needed.

---

## 📜 License

Choose a license (e.g., MIT) and add it as `LICENSE` in the repo root.

---

## 🙌 Acknowledgements

* Python, Pandas, SQLAlchemy, MySQL, Matplotlib, Seaborn
* Everyone who maintains open‑source tools used in this project
