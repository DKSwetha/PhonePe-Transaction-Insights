# PhonePe Transaction Insights

An end-to-end data analysis project on PhonePe's transaction, user, and insurance data from 2018 to 2024. This project extracts data from the PhonePe Pulse GitHub repository, loads it into a SQLite database, performs exploratory data analysis, and presents findings through an interactive Streamlit dashboard.

---

## Project Structure
```
phonepe-transaction-insights/
├── phonepe_extraction.py       # Data extraction & SQLite DB creation
├── business_case_queries.py    # SQL queries for 5 business case studies
├── PhonePe_EDA.ipynb           # EDA notebook with 20 charts
└── phonepe_dashboard.py        # Interactive Streamlit dashboard
```
---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Data extraction, analysis |
| SQLite | Database (no server needed) |
| Pandas | Data manipulation |
| Matplotlib & Seaborn | EDA visualisations |
| Plotly | Interactive charts |
| Streamlit | Dashboard |
| Jupyter Notebook | EDA submission |

---
## Data Source

- **PhonePe Pulse GitHub:** https://github.com/PhonePe/pulse
- **Data Period:** 2018 Q1 – 2024 Q4
- **Coverage:** 36 States & UTs across India

  ---

## Database Schema

9 tables are created in `phonepe.db`:

| Table | Rows | Description |
|-------|------|-------------|
| `aggregated_transaction` | 5,034 | State-level transaction data by payment type |
| `aggregated_user` | 1,008 | State-level registered users & app opens |
| `aggregated_insurance` | 682 | State-level insurance transaction data |
| `map_transaction` | 20,604 | District-level transaction data |
| `map_user` | 20,608 | District-level user data |
| `map_insurance` | 13,876 | District-level insurance data |
| `top_transaction` | 18,279 | Top districts & pincodes by transactions |
| `top_user` | 18,296 | Top districts & pincodes by registered users |
| `top_insurance` | 12,261 | Top districts & pincodes by insurance |

---

## Business Case Studies

| # | Case Study | Key Finding |
|---|-----------|-------------|
| 1 | Transaction Dynamics | Merchant Payments lead in volume (781B); P2P leads in value (avg ₹3,134) |
| 4 | Market Expansion | Andaman & Nicobar grew 34,683% from 2018→2024; Lakshadweep is biggest opportunity |
| 5 | User Engagement | Meghalaya has highest engagement rate (174 app opens/user) |
| 7 | Top States & Districts | Bengaluru Urban is #1 district — nearly 2x Hyderabad by transaction amount |
| 8 | User Registration | Maharashtra leads with 4.57B registered users; 2024 Q2 was record quarter |

---

## Dashboard Pages

| Page | Features |
|------|---------|
| Home | KPI cards, quarterly growth, payment type pie, top states |
| Case 1 | Year/Quarter filters, payment type charts, trend analysis |
| Case 2 | Growth % by state, expansion map, YoY comparison |
| Case 3 | Year slider, engagement rate, district breakdown |
| Case 4 | Tabs for States / Districts / Pincodes, treemap |
| Case 5 | Year-Quarter filter, top registration areas with data tables |

---

## Data Quality

| Table | Missing Values | Action |
|-------|---------------|--------|
| 7 tables | 0 | No action needed |
| `top_transaction` | 16 (entity_name) | Dropped — Ladakh pincode names missing in source JSON |
| `top_insurance` | 15 (entity_name) | Dropped — same root cause |

> **Root Cause:** Ladakh was a newly created UT in 2019 with incomplete pincode mapping in the PhonePe Pulse source data.

---

## Key Insights

- Transactions grew **210x** from 2018 Q1 to 2024 Q4
- **Bengaluru Urban** is the #1 district by both transactions and user registrations
- **Peer-to-peer payments** have the highest average value (₹3,134) despite fewer transactions
- **Meghalaya** leads in app engagement (174 opens per user)
- Top 3 states (Karnataka, Maharashtra, Telangana) account for ~40% of all transactions
- Insurance on PhonePe is post-2021 — massive untapped potential in northeastern states




