# 04_inventory_optimizer.py
# Inventory Optimization using EOQ Model
# ─────────────────────────────────────────────

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from db_connection import run_query

# ── Setup ─────────────────────────────────────
os.chdir(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CHARTS_DIR = os.path.join('03_outputs', 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)

sns.set_theme(style='whitegrid')
print("📦 Starting Inventory Optimization...")
print("=" * 50)

# ── Section 1: Load Data ───────────────────────
print("\n📦 Loading data from SQL Server...")

sales    = run_query("SELECT * FROM Sales")
products = run_query("SELECT * FROM Products")
wh_costs = run_query("SELECT * FROM WhCosts")
wh_cap   = run_query("SELECT * FROM WhCapacities")
freight  = run_query("SELECT * FROM FreightRates")

print(f"  ✅ Sales:        {len(sales):,} rows")
print(f"  ✅ Products:     {len(products):,} rows")
print(f"  ✅ WhCosts:      {len(wh_costs):,} rows")
print(f"  ✅ WhCapacities: {len(wh_cap):,} rows")
print(f"  ✅ FreightRates: {len(freight):,} rows")

# ── Section 2: Fix Data Types ──────────────────
print("\n🔧 Fixing data types...")

products['Unit_Cost_USD'] = pd.to_numeric(
    products['Unit_Cost_USD'], errors='coerce')
products['Unit_Price_USD'] = pd.to_numeric(
    products['Unit_Price_USD'], errors='coerce')
sales['Quantity'] = pd.to_numeric(
    sales['Quantity'], errors='coerce')
sales['Revenue_USD'] = pd.to_numeric(
    sales['Revenue_USD'], errors='coerce')
freight['Minimum_Cost'] = pd.to_numeric(
    freight['Minimum_Cost'], errors='coerce')
freight['Rate'] = pd.to_numeric(
    freight['Rate'], errors='coerce')
wh_costs['Cost_Unit'] = pd.to_numeric(
    wh_costs['Cost_Unit'], errors='coerce')

# Fix fillna using correct pandas syntax
products['Unit_Cost_USD'] = products[
    'Unit_Cost_USD'].fillna(
    products['Unit_Cost_USD'].median())
products['Unit_Price_USD'] = products[
    'Unit_Price_USD'].fillna(
    products['Unit_Price_USD'].median())
freight['Minimum_Cost'] = freight[
    'Minimum_Cost'].fillna(
    freight['Minimum_Cost'].median())
wh_costs['Cost_Unit'] = wh_costs[
    'Cost_Unit'].fillna(
    wh_costs['Cost_Unit'].median())

print(f"  ✅ Unit_Cost_USD:  "
      f"{products['Unit_Cost_USD'].dtype}")
print(f"  ✅ Minimum_Cost:   "
      f"{freight['Minimum_Cost'].dtype}")
print(f"  ✅ Cost_Unit:      "
      f"{wh_costs['Cost_Unit'].dtype}")
print(f"  ✅ Quantity:       "
      f"{sales['Quantity'].dtype}")

# ── Section 3: Calculate Annual Demand ────────
print("\n📊 Section 3: Calculating annual demand...")

sales['Order_Date'] = pd.to_datetime(
    sales['Order_Date'])

total_days = (
    sales['Order_Date'].max() -
    sales['Order_Date'].min()
).days
total_years = total_days / 365.25

print(f"  Dataset spans: {total_years:.2f} years")

product_demand = sales.groupby('ProductKey').agg(
    Total_Units_Sold = ('Quantity',      'sum'),
    Total_Revenue    = ('Revenue_USD',   'sum'),
    Total_Orders     = ('Order_Number',  'count')
).reset_index()

product_demand['Annual_Demand'] = (
    product_demand['Total_Units_Sold'] /
    total_years
).round(2)

product_demand = product_demand.merge(
    products[[
        'ProductKey', 'Product_Name',
        'Category',   'Subcategory',
        'Brand',      'Unit_Cost_USD',
        'Unit_Price_USD'
    ]],
    on='ProductKey',
    how='left'
)

print(f"  ✅ Annual demand calculated!")
print(f"  Total products: {len(product_demand):,}")
print(f"\n  Top 5 by annual demand:")
print(product_demand.nlargest(5, 'Annual_Demand')[[
    'Product_Name',
    'Annual_Demand',
    'Total_Units_Sold'
]].to_string(index=False))

# ── Section 4: Calculate EOQ ───────────────────
print("\n📊 Section 4: Calculating EOQ...")

# ── Cost Parameters ────────────────────────────
ordering_cost     = freight['Minimum_Cost'].mean()
holding_pct       = 0.25  # 25% of unit cost per year

print(f"  Avg Ordering Cost: ${ordering_cost:.2f} per order")
print(f"  Holding Cost Rate: {holding_pct*100:.0f}% of unit cost per year")

# ── Annual Holding Cost per Unit ───────────────
# Industry standard = 25% of unit cost per year
product_demand['Holding_Cost_Annual'] = (
    product_demand['Unit_Cost_USD'] * holding_pct
).round(4)

# ── Remove products with zero cost ─────────────
product_demand = product_demand[
    product_demand['Holding_Cost_Annual'] > 0
].copy()

print(f"  Products with valid cost: "
      f"{len(product_demand):,}")

# ── EOQ Formula: √(2 × D × S / H) ─────────────
product_demand['EOQ'] = np.sqrt(
    2 *
    product_demand['Annual_Demand'] *
    ordering_cost /
    product_demand['Holding_Cost_Annual']
).round(0)

# ── Clean EOQ Values ───────────────────────────
product_demand['EOQ'] = product_demand[
    'EOQ'].replace(
    [0, np.inf, -np.inf], np.nan)

product_demand['EOQ'] = product_demand.groupby(
    'Category')['EOQ'].transform(
    lambda x: x.fillna(x.median()))

product_demand['EOQ'] = product_demand[
    'EOQ'].round(0)

# ── Average Lead Time from OrderList ───────────
avg_lead_time = run_query(
    "SELECT AVG(CAST(TPT AS FLOAT)) "
    "AS Avg_Lead_Time FROM OrderList"
)['Avg_Lead_Time'][0]

print(f"  Avg Lead Time: {avg_lead_time:.1f} days")

# ── Daily Demand and Reorder Point ─────────────
product_demand['Daily_Demand'] = (
    product_demand['Annual_Demand'] / 365
).round(4)

product_demand['Reorder_Point'] = (
    product_demand['Daily_Demand'] *
    avg_lead_time
).round(0)

# ── Safety Stock (95% service level) ───────────
daily_std = sales.groupby('ProductKey').agg(
    Demand_Std = ('Quantity', 'std')
).reset_index().fillna(0)

product_demand = product_demand.merge(
    daily_std, on='ProductKey', how='left')

Z = 1.65  # 95% service level
product_demand['Safety_Stock'] = (
    Z *
    product_demand['Demand_Std'] *
    np.sqrt(avg_lead_time)
).round(0)

product_demand['Final_Reorder_Point'] = (
    product_demand['Reorder_Point'] +
    product_demand['Safety_Stock']
).round(0)

# ── Annual Inventory Costs ─────────────────────
product_demand['Annual_Order_Cost'] = (
    (product_demand['Annual_Demand'] /
     product_demand['EOQ']) *
    ordering_cost
).round(2)

product_demand['Annual_Holding_Cost'] = (
    (product_demand['EOQ'] / 2) *
    product_demand['Holding_Cost_Annual']
).round(2)

product_demand['Total_Inventory_Cost'] = (
    product_demand['Annual_Order_Cost'] +
    product_demand['Annual_Holding_Cost']
).round(2)

# ── Clean infinite values ──────────────────────
product_demand['Total_Inventory_Cost'] = \
    product_demand['Total_Inventory_Cost'].replace(
    [np.inf, -np.inf], np.nan)

product_demand['Total_Inventory_Cost'] = \
    product_demand['Total_Inventory_Cost'].fillna(
    product_demand['Total_Inventory_Cost'].median())

# ── Results ────────────────────────────────────
print(f"\n  ✅ EOQ Calculated!")
print(f"\n  Sample EOQ Results:")
print(product_demand[[
    'Product_Name',
    'Annual_Demand',
    'EOQ',
    'Final_Reorder_Point',
    'Total_Inventory_Cost'
]].head(10).to_string(index=False))

print(f"\n  📊 EOQ Summary:")
print(f"  Avg EOQ:           "
      f"{product_demand['EOQ'].mean():.0f} units")
print(f"  Avg Safety Stock:  "
      f"{product_demand['Safety_Stock'].mean():.0f} units")
print(f"  Avg Reorder Point: "
      f"{product_demand['Final_Reorder_Point'].mean():.0f} units")
print(f"  Total Annual Cost: "
      f"${product_demand['Total_Inventory_Cost'].sum():,.2f}")


# ── Section 5: Inventory Risk Analysis ────────
print("\n📊 Section 5: Inventory risk analysis...")

# Classify products by risk
'''product_demand['Risk_Level'] = pd.cut(
    product_demand['Total_Inventory_Cost'],
    bins=[0, 1000, 5000, 10000, float('inf')],
    labels=['Low', 'Medium', 'High', 'Critical']
)'''

# NEW — adjusted for our data scale
product_demand['Risk_Level'] = pd.cut(
    product_demand['Total_Inventory_Cost'],
    bins=[0, 20, 50, 100, float('inf')],
    labels=['Low', 'Medium', 'High', 'Critical']
)

risk_summary = product_demand.groupby(
    'Risk_Level', observed=True
).agg(
    Product_Count   = ('ProductKey',           'count'),
    Avg_EOQ         = ('EOQ',                  'mean'),
    Total_Cost      = ('Total_Inventory_Cost', 'sum')
).reset_index()

print(f"\n  Risk Distribution:")
print(risk_summary.to_string(index=False))

# ── Section 6: Charts ──────────────────────────
print("\n📊 Generating charts...")

# Chart 1: Top 15 Products by EOQ
top15 = product_demand.nlargest(15, 'EOQ')

plt.figure(figsize=(14, 7))
bars = plt.barh(
    top15['Product_Name'].str[:40],
    top15['EOQ'],
    color=sns.color_palette(
        'Blues_d', len(top15))
)
plt.xlabel('Economic Order Quantity (Units)')
plt.title(
    'Top 15 Products by Economic Order Quantity',
    fontsize=14, fontweight='bold'
)
for bar, val in zip(bars, top15['EOQ']):
    plt.text(
        bar.get_width() + 0.5,
        bar.get_y() + bar.get_height()/2,
        f'{val:.0f}',
        va='center', fontsize=9
    )
plt.tight_layout()
plt.savefig(os.path.join(
    CHARTS_DIR, '13_eoq_top15.png'), dpi=150)
plt.show()
print("  ✅ Chart 13 saved: eoq_top15.png")

# Chart 2: EOQ by Category
category_eoq = product_demand.groupby(
    'Category'
).agg(
    Avg_EOQ         = ('EOQ',                  'mean'),
    Total_Cost      = ('Total_Inventory_Cost', 'sum'),
    Product_Count   = ('ProductKey',           'count')
).reset_index().sort_values(
    'Avg_EOQ', ascending=False)

fig, ax1 = plt.subplots(figsize=(12, 6))

bars = ax1.bar(
    category_eoq['Category'],
    category_eoq['Avg_EOQ'],
    color=sns.color_palette(
        'Set2', len(category_eoq))
)
ax1.set_xlabel('Category')
ax1.set_ylabel('Average EOQ (Units)', color='black')
ax1.set_title(
    'Average EOQ and Total Inventory Cost by Category',
    fontsize=14, fontweight='bold'
)
plt.xticks(rotation=30, ha='right')

ax2 = ax1.twinx()
ax2.plot(
    category_eoq['Category'],
    category_eoq['Total_Cost'],
    color='red',
    marker='o',
    linewidth=2,
    label='Total Inventory Cost'
)
ax2.set_ylabel(
    'Total Inventory Cost (USD)', color='red')
ax2.tick_params(axis='y', labelcolor='red')
ax2.legend(loc='upper right')

plt.tight_layout()
plt.savefig(os.path.join(
    CHARTS_DIR, '14_eoq_by_category.png'), dpi=150)
plt.show()
print("  ✅ Chart 14 saved: eoq_by_category.png")

# Chart 3: Risk Distribution
plt.figure(figsize=(10, 6))
colors_risk = {
    'Low':      '#4CAF50',
    'Medium':   '#FF9800',
    'High':     '#F44336',
    'Critical': '#9C27B0'
}
plt.pie(
    risk_summary['Product_Count'],
    labels=risk_summary['Risk_Level'],
    autopct='%1.1f%%',
    colors=[colors_risk.get(r, '#9E9E9E')
            for r in risk_summary['Risk_Level']],
    startangle=90
)
plt.title(
    'Product Inventory Risk Distribution',
    fontsize=14, fontweight='bold'
)
plt.tight_layout()
plt.savefig(os.path.join(
    CHARTS_DIR, '15_risk_distribution.png'), dpi=150)
plt.show()
print("  ✅ Chart 15 saved: risk_distribution.png")

# ── Section 7: Export Results ──────────────────
export_cols = [
    'ProductKey',           'Product_Name',
    'Category',             'Brand',
    'Annual_Demand',        'EOQ',
    'Daily_Demand',         'Safety_Stock',
    'Final_Reorder_Point',  'Annual_Order_Cost',
    'Annual_Holding_Cost',  'Total_Inventory_Cost',
    'Risk_Level'
]

product_demand[export_cols].to_csv(
    os.path.join(
        '03_outputs',
        'inventory_optimizer.csv'
    ),
    index=False
)
print("\n  ✅ Results exported: inventory_optimizer.csv")

# ── Summary ───────────────────────────────────
print("\n" + "=" * 50)
print("✅ Inventory Optimization Complete!")
print(f"\n  📊 Key Findings:")
print(f"  Total Products Analyzed: "
      f"{len(product_demand):,}")
print(f"  Avg EOQ:                 "
      f"{product_demand['EOQ'].mean():.0f} units")
print(f"  Avg Safety Stock:        "
      f"{product_demand['Safety_Stock'].mean():.0f} "
      f"units")
print(f"  Avg Reorder Point:       "
      f"{product_demand['Final_Reorder_Point'].mean():.0f}"
      f" units")
print(f"  Total Inventory Cost:    "
      f"${product_demand['Total_Inventory_Cost'].sum():,.2f}")
print(f"\n  📁 Files saved:")
print(f"  • 03_outputs/charts/13_eoq_top15.png")
print(f"  • 03_outputs/charts/14_eoq_by_category.png")
print(f"  • 03_outputs/charts/15_risk_distribution.png")
print(f"  • 03_outputs/inventory_optimizer.csv")
print("=" * 50)