# 01_eda.py
# Supply Chain EDA — Exploratory Data Analysis
# ─────────────────────────────────────────────

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from db_connection import run_query


# Fix paths — works regardless of where script is run from
import os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"📁 Working directory: {os.getcwd()}")

# ── Setup ─────────────────────────────────────
# Create output folder for charts
os.makedirs('03_outputs/charts', exist_ok=True)

# Set visual style
sns.set_theme(style='whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12

print("🔍 Starting Exploratory Data Analysis...")
print("=" * 50)

# ── Load Data ─────────────────────────────────
print("\n📦 Loading data from SQL Server...")

sales = run_query("SELECT * FROM Sales")
products = run_query("SELECT * FROM Products")
customers = run_query("SELECT * FROM Customers")
stores = run_query("SELECT * FROM Stores")
orderlist = run_query("SELECT * FROM OrderList")
freight = run_query("SELECT * FROM FreightRates")

print(f"  ✅ Sales: {len(sales):,} rows")
print(f"  ✅ Products: {len(products):,} rows")
print(f"  ✅ Customers: {len(customers):,} rows")
print(f"  ✅ Stores: {len(stores):,} rows")
print(f"  ✅ OrderList: {len(orderlist):,} rows")
print(f"  ✅ FreightRates: {len(freight):,} rows")

# ── Section 1: Sales Overview ─────────────────
print("\n📊 Section 1: Sales Overview")
print("-" * 40)

total_revenue = sales['Revenue_USD'].sum()
total_orders = sales['Order_Number'].nunique()
avg_order_value = sales['Revenue_USD'].mean()
online_pct = (sales['Sales_Channel'] == 'Online').mean() * 100

print(f"  Total Revenue:      ${total_revenue:,.2f}")
print(f"  Total Orders:       {total_orders:,}")
print(f"  Avg Order Value:    ${avg_order_value:,.2f}")
print(f"  Online Orders:      {online_pct:.1f}%")

# ── Chart 1: Revenue by Sales Channel ─────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Pie chart
channel_revenue = sales.groupby('Sales_Channel')['Revenue_USD'].sum()
axes[0].pie(
    channel_revenue,
    labels=channel_revenue.index,
    autopct='%1.1f%%',
    colors=['#2196F3', '#FF9800'],
    startangle=90
)
axes[0].set_title('Revenue by Sales Channel',
                   fontsize=14, fontweight='bold')

# Bar chart
channel_orders = sales.groupby('Sales_Channel')['Order_Number'].count()
axes[1].bar(
    channel_orders.index,
    channel_orders.values,
    color=['#2196F3', '#FF9800']
)
axes[1].set_title('Orders by Sales Channel',
                   fontsize=14, fontweight='bold')
axes[1].set_ylabel('Number of Orders')

plt.tight_layout()
plt.savefig('03_outputs/charts/01_sales_channel.png', dpi=150)
plt.show()
print("  ✅ Chart 1 saved: sales_channel.png")

# ── Section 2: Revenue by Category ───────────
print("\n📊 Section 2: Revenue by Category")
print("-" * 40)

sales_products = sales.merge(
    products[['ProductKey', 'Category',
               'Subcategory', 'Brand']],
    on='ProductKey'
)

category_revenue = sales_products.groupby('Category')\
    ['Revenue_USD'].sum().sort_values(ascending=False)

for cat, rev in category_revenue.items():
    pct = rev / total_revenue * 100
    print(f"  {cat:<30} ${rev:>12,.2f}  ({pct:.1f}%)")

# Chart 2: Revenue by Category
plt.figure(figsize=(12, 6))
bars = plt.barh(
    category_revenue.index[::-1],
    category_revenue.values[::-1],
    color=sns.color_palette('Blues_d',
                             len(category_revenue))
)
plt.xlabel('Revenue (USD)')
plt.title('Revenue by Product Category',
           fontsize=14, fontweight='bold')

# Add value labels
for bar, val in zip(bars,
                     category_revenue.values[::-1]):
    plt.text(
        bar.get_width() + 50000,
        bar.get_y() + bar.get_height()/2,
        f'${val/1e6:.1f}M',
        va='center', fontsize=10
    )

plt.tight_layout()
plt.savefig('03_outputs/charts/02_category_revenue.png',
             dpi=150)
plt.show()
print("  ✅ Chart 2 saved: category_revenue.png")

# ── Section 3: Monthly Revenue Trend ─────────
print("\n📊 Section 3: Monthly Revenue Trend")
print("-" * 40)

sales['Order_Date'] = pd.to_datetime(sales['Order_Date'])
monthly = sales.groupby(
    sales['Order_Date'].dt.to_period('M')
)['Revenue_USD'].sum().reset_index()
monthly['Order_Date'] = monthly['Order_Date'].astype(str)

# Chart 3: Monthly Trend
plt.figure(figsize=(16, 6))
plt.plot(
    monthly['Order_Date'],
    monthly['Revenue_USD'],
    color='#2196F3', linewidth=2, marker='o',
    markersize=4
)
plt.fill_between(
    monthly['Order_Date'],
    monthly['Revenue_USD'],
    alpha=0.1, color='#2196F3'
)
plt.xticks(
    monthly['Order_Date'][::3],
    rotation=45, ha='right'
)
plt.xlabel('Month')
plt.ylabel('Revenue (USD)')
plt.title('Monthly Revenue Trend',
           fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('03_outputs/charts/03_monthly_trend.png',
             dpi=150)
plt.show()
print("  ✅ Chart 3 saved: monthly_trend.png")

# ── Section 4: Delivery Performance ──────────
print("\n📊 Section 4: Delivery Performance")
print("-" * 40)

delivery = orderlist['On_Time_Status']\
    .value_counts(normalize=True) * 100

for status, pct in delivery.items():
    print(f"  {status:<15} {pct:.1f}%")

# Chart 4: Delivery Status
colors = {
    'On Time': '#4CAF50',
    'Early':   '#2196F3',
    'Late':    '#F44336'
}
plt.figure(figsize=(10, 6))
bars = plt.bar(
    delivery.index,
    delivery.values,
    color=[colors.get(s, '#9E9E9E')
           for s in delivery.index]
)
plt.ylabel('Percentage (%)')
plt.title('Delivery Performance — On Time vs Late',
           fontsize=14, fontweight='bold')

for bar, val in zip(bars, delivery.values):
    plt.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height() + 0.5,
        f'{val:.1f}%',
        ha='center', fontweight='bold'
    )

plt.tight_layout()
plt.savefig('03_outputs/charts/04_delivery_status.png',
             dpi=150)
plt.show()
print("  ✅ Chart 4 saved: delivery_status.png")

# ── Section 5: Carrier Performance ───────────
print("\n📊 Section 5: Carrier Performance")
print("-" * 40)

carrier_perf = orderlist.groupby('Carrier').agg(
    Total_Orders   = ('Order_ID', 'count'),
    Avg_Delay      = ('Total_Delay_Days', 'mean'),
    Total_Delay    = ('Total_Delay_Days', 'sum'),
    Late_Orders    = ('On_Time_Status',
                      lambda x: (x=='Late').sum())
).reset_index()

carrier_perf['Late_Pct'] = (
    carrier_perf['Late_Orders'] /
    carrier_perf['Total_Orders'] * 100
).round(2)

carrier_perf = carrier_perf.sort_values(
    'Avg_Delay', ascending=False
)

print(carrier_perf.to_string(index=False))

# Chart 5: Carrier Performance
# Chart 5: Carrier Performance
plt.figure(figsize=(14, 8))
plt.subplots_adjust(bottom=0.25)
bars = plt.bar(
    carrier_perf['Carrier'],
    carrier_perf['Avg_Delay'],
    color=sns.color_palette('Reds_d',
                             len(carrier_perf))
)
plt.xlabel('Carrier')
plt.ylabel('Average Delay Days')
plt.title('Average Delay Days by Carrier',
           fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')

for bar, val in zip(bars,
                     carrier_perf['Avg_Delay']):
    plt.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height() + 0.1,
        f'{val:.1f}',
        ha='center', fontsize=10
    )

plt.tight_layout()
plt.savefig('03_outputs/charts/05_carrier_performance.png',
             dpi=150)
plt.show()
print("  ✅ Chart 5 saved: carrier_performance.png")

# ── Section 6: Customer Geography ────────────
print("\n📊 Section 6: Customer Geography")
print("-" * 40)

sales_customers = sales.merge(
    customers[['CustomerKey', 'Country',
                'Continent']],
    on='CustomerKey'
)

continent_revenue = sales_customers.groupby('Continent')\
    ['Revenue_USD'].sum().sort_values(ascending=False)

for cont, rev in continent_revenue.items():
    pct = rev / total_revenue * 100
    print(f"  {cont:<20} ${rev:>12,.2f}  ({pct:.1f}%)")

# Chart 6: Revenue by Continent
plt.figure(figsize=(10, 6))
plt.bar(
    continent_revenue.index,
    continent_revenue.values,
    color=sns.color_palette('Set2',
                             len(continent_revenue))
)
plt.xlabel('Continent')
plt.ylabel('Revenue (USD)')
plt.title('Revenue by Continent',
           fontsize=14, fontweight='bold')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig('03_outputs/charts/06_continent_revenue.png',
             dpi=150)
plt.show()
print("  ✅ Chart 6 saved: continent_revenue.png")

# ── Summary ───────────────────────────────────
print("\n" + "=" * 50)
print("✅ EDA Complete!")
print(f"  6 charts saved to 03_outputs/charts/")
print("\n🔑 Key Findings:")
print(f"  • Total Revenue: ${total_revenue:,.2f}")
print(f"  • On-Time Rate: {delivery.get('On Time', 0):.1f}%")
print(f"  • Top Category: {category_revenue.index[0]}")
print(f"  • Top Continent: {continent_revenue.index[0]}")
print(f"  • Worst Carrier: {carrier_perf.iloc[0]['Carrier']}")
print(f"  • Online Orders: {online_pct:.1f}%")
print("=" * 50)