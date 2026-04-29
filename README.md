# 📦 Supply Chain Performance Analytics

## 🎯 Project Overview
End-to-end data analytics project analyzing 
supply chain performance of a global electronics company 
retailer across 6 years (2016-2021).

## 🛠️ Tools Used
| Tool | Purpose |
|------|---------|
| Excel / Power Query | Data cleaning |
| SQL Server (SSMS) | Data modeling & analysis |
| Python 3.10 | EDA, forecasting, optimization |
| Power BI | Interactive dashboard |

## 📊 Dataset
- **Source 1:** Maven Analytics — Global Electronics Retailer
- **Source 2:** Figshare Brunel University — Supply Chain Logistics
- **Size:** 62,884 sales transactions + 9,215 freight orders
- **Period:** 2016 — 2021

## 🔑 Key Findings
- 💰 Total Revenue: **$55.76M**
- 📦 On-Time Delivery Rate: **47.28%** (Critical Issue)
- 🏆 Top Category: **Computers ($19.3M — 34.6%)**
- 🌎 Top Region: **North America**
- 📅 Peak Month: **February (Valentine's Day)**
- 🚚 Best Carrier: **V444_0 (Score: 70/100)**
- 🛒 Online vs In-Store: **20.4% vs 79.6%**

## 📁 Project Structure
supply_chain_analytics/
├── 01_data/          — Raw and cleaned datasets
├── 02_excel/         — Power Query workbook
├── 03_sql/           — Schema and queries
├── 04_python/        — Analysis scripts
├── 05_outputs/       — Charts and CSV exports
└── 06_powerbi/       — Dashboard file

## 🗄️ SQL Analysis
- 8 analytical queries
- 3 advanced queries (CTEs, Window Functions)
- Key metrics: Revenue, Delivery Rate, Carrier Performance

## 🐍 Python Analysis
- EDA with 15 visualizations
- Carrier performance scorecard
- 6-month demand forecast (Facebook Prophet)
- Inventory optimization (EOQ model)

## 📊 Power BI Dashboard
5 interactive pages:
1. Executive Summary
2. Sales Performance
3. Delivery & Carrier Analysis
4. Demand Forecast
5. Inventory Optimizer

## 💡 Business Recommendations
1. **Delivery** — Only 47% on-time rate needs urgent fix
2. **Carrier** — Review V44_3 contract (lowest score)
3. **Inventory** — 7% critical risk products need attention
4. **Online** — Grow online channel (currently only 20%)
5. **Seasonality** — Increase stock before February peak

## 🚀 How to Run
1. Clone the repository
2. Install Python libraries: `pip install -r requirements.txt.`
3. Update SQL connection in `db_connection.py.`
4. Run Python scripts in order (01 to 04)
5. Open the Power BI file and refresh data
