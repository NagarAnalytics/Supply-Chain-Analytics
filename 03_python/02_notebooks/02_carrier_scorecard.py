# 02_carrier_scorecard.py
# Carrier Performance Scorecard
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
print("🚚 Starting Carrier Scorecard Analysis...")
print("=" * 50)

# ── Load Data ─────────────────────────────────
print("\n📦 Loading OrderList and FreightRates...")
orderlist = run_query("SELECT * FROM OrderList")
freight   = run_query("SELECT * FROM FreightRates")

print(f"  ✅ OrderList: {len(orderlist):,} rows")
print(f"  ✅ FreightRates: {len(freight):,} rows")

# ── Step 1: Calculate Carrier Metrics ─────────
print("\n📊 Step 1: Calculating carrier metrics...")

carrier_metrics = orderlist.groupby('Carrier').agg(
    Total_Orders    = ('Order_ID',          'count'),
    Avg_Delay       = ('Total_Delay_Days',  'mean'),
    Total_Delay     = ('Total_Delay_Days',  'sum'),
    Late_Orders     = ('On_Time_Status',
                       lambda x: (x == 'Late').sum()),
    On_Time_Orders  = ('On_Time_Status',
                       lambda x: (x == 'On Time').sum()),
    Early_Orders    = ('On_Time_Status',
                       lambda x: (x == 'Early').sum()),
    Avg_TPT         = ('TPT',              'mean'),
).reset_index()

# Calculate percentages
carrier_metrics['Late_Pct'] = (
    carrier_metrics['Late_Orders'] /
    carrier_metrics['Total_Orders'] * 100
).round(2)

carrier_metrics['On_Time_Pct'] = (
    carrier_metrics['On_Time_Orders'] /
    carrier_metrics['Total_Orders'] * 100
).round(2)

carrier_metrics['Avg_Delay'] = \
    carrier_metrics['Avg_Delay'].round(2)
carrier_metrics['Avg_TPT']   = \
    carrier_metrics['Avg_TPT'].round(2)

print(carrier_metrics[[
    'Carrier', 'Total_Orders', 
    'On_Time_Pct', 'Late_Pct', 
    'Avg_Delay', 'Avg_TPT'
]].to_string(index=False))

# ── Step 2: Add Freight Cost per Carrier ──────
print("\n📊 Step 2: Adding freight cost data...")

avg_freight = freight.groupby('Carrier').agg(
    Avg_Rate        = ('Rate',          'mean'),
    Min_Rate        = ('Rate',          'min'),
    Max_Rate        = ('Rate',          'max'),
    Avg_Min_Cost    = ('Minimum_Cost',  'mean')
).reset_index()

avg_freight['Avg_Rate']     = \
    avg_freight['Avg_Rate'].round(4)
avg_freight['Avg_Min_Cost'] = \
    avg_freight['Avg_Min_Cost'].round(2)

print(avg_freight.to_string(index=False))

# ── Step 3: Merge Metrics + Freight Cost ──────
print("\n📊 Step 3: Merging metrics...")

scorecard = carrier_metrics.merge(
    avg_freight, on='Carrier', how='left'
)

# ── Step 4: Calculate Performance Score ───────
print("\n📊 Step 4: Calculating performance scores...")

# Normalize each metric to 0-100 scale
# Higher is better for On_Time_Pct
# Lower is better for Late_Pct, Avg_Delay, Avg_Rate

def normalize_higher_better(series):
    """Normalize where higher value = better score."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series))
    return ((series - min_val) / 
            (max_val - min_val) * 100).round(2)

def normalize_lower_better(series):
    """Normalize where lower value = better score."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series))
    return ((max_val - series) / 
            (max_val - min_val) * 100).round(2)

# Calculate individual scores
scorecard['Score_OnTime']   = normalize_higher_better(
    scorecard['On_Time_Pct'])
scorecard['Score_Delay']    = normalize_lower_better(
    scorecard['Avg_Delay'])
scorecard['Score_Cost']     = normalize_lower_better(
    scorecard['Avg_Rate'].fillna(
        scorecard['Avg_Rate'].mean()))

# Weighted final score
# On-Time = 50%, Delay = 30%, Cost = 20%
scorecard['Final_Score'] = (
    scorecard['Score_OnTime'] * 0.50 +
    scorecard['Score_Delay']  * 0.30 +
    scorecard['Score_Cost']   * 0.20
).round(2)

# Add performance grade
def get_grade(score):
    if score >= 80: return 'A — Excellent'
    if score >= 60: return 'B — Good'
    if score >= 40: return 'C — Average'
    if score >= 20: return 'D — Poor'
    return 'F — Critical'

scorecard['Grade'] = scorecard['Final_Score'].apply(
    get_grade)

# Sort by final score
scorecard = scorecard.sort_values(
    'Final_Score', ascending=False)

# ── Print Final Scorecard ──────────────────────
print("\n" + "=" * 60)
print("🏆 CARRIER PERFORMANCE SCORECARD")
print("=" * 60)

for _, row in scorecard.iterrows():
    print(f"\n  Carrier:      {row['Carrier']}")
    print(f"  Grade:        {row['Grade']}")
    print(f"  Final Score:  {row['Final_Score']}/100")
    print(f"  On-Time:      {row['On_Time_Pct']:.1f}%")
    print(f"  Late:         {row['Late_Pct']:.1f}%")
    print(f"  Avg Delay:    {row['Avg_Delay']:.1f} days")
    print(f"  Avg Rate:     ${row['Avg_Rate']:.4f}" 
          if pd.notna(row['Avg_Rate']) 
          else "  Avg Rate:     N/A")
    print(f"  Total Orders: {row['Total_Orders']:,}")
    print("  " + "-" * 40)

# ── Chart 1: Final Score by Carrier ───────────
print("\n📊 Generating charts...")

colors = scorecard['Final_Score'].apply(
    lambda x: '#4CAF50' if x >= 60
    else '#FF9800' if x >= 40
    else '#F44336'
)

plt.figure(figsize=(12, 6))
bars = plt.barh(
    scorecard['Carrier'],
    scorecard['Final_Score'],
    color=colors
)
plt.axvline(x=60, color='green',
            linestyle='--', alpha=0.7,
            label='Good threshold (60)')
plt.axvline(x=40, color='orange',
            linestyle='--', alpha=0.7,
            label='Average threshold (40)')
plt.xlabel('Performance Score (0-100)')
plt.title('Carrier Performance Scorecard',
          fontsize=14, fontweight='bold')
plt.legend()

for bar, val in zip(bars, scorecard['Final_Score']):
    plt.text(
        bar.get_width() + 0.5,
        bar.get_y() + bar.get_height()/2,
        f'{val:.1f}',
        va='center', fontweight='bold'
    )

plt.tight_layout()
plt.savefig(os.path.join(
    CHARTS_DIR, '07_carrier_scorecard.png'), dpi=150)
plt.show()
print("  ✅ Chart 7 saved: carrier_scorecard.png")

# ── Chart 2: On-Time vs Late % ────────────────
fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(scorecard))
width = 0.35

bars1 = ax.bar(x - width/2,
               scorecard['On_Time_Pct'],
               width, label='On Time %',
               color='#4CAF50')
bars2 = ax.bar(x + width/2,
               scorecard['Late_Pct'],
               width, label='Late %',
               color='#F44336')

ax.set_xlabel('Carrier')
ax.set_ylabel('Percentage (%)')
ax.set_title('On-Time vs Late Percentage by Carrier',
             fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scorecard['Carrier'],
                   rotation=45, ha='right')
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(
    CHARTS_DIR, '08_carrier_ontime_vs_late.png'),
    dpi=150)
plt.show()
print("  ✅ Chart 8 saved: carrier_ontime_vs_late.png")

# ── Chart 3: Avg Delay Heatmap ────────────────
pivot_data = orderlist.pivot_table(
    values='Total_Delay_Days',
    index='Carrier',
    columns='Service_Level',
    aggfunc='mean'
).round(2)

plt.figure(figsize=(12, 6))
sns.heatmap(
    pivot_data,
    annot=True, fmt='.1f',
    cmap='RdYlGn_r',
    linewidths=0.5,
    cbar_kws={'label': 'Avg Delay Days'}
)
plt.title('Average Delay Days — Carrier vs Service Level',
          fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(
    CHARTS_DIR, '09_delay_heatmap.png'), dpi=150)
plt.show()
print("  ✅ Chart 9 saved: delay_heatmap.png")

# ── Export Scorecard to CSV ────────────────────
export_cols = [
    'Carrier', 'Grade', 'Final_Score',
    'Total_Orders', 'On_Time_Pct', 'Late_Pct',
    'Avg_Delay', 'Avg_TPT', 'Avg_Rate'
]
scorecard[export_cols].to_csv(
    os.path.join('03_outputs',
                 'carrier_scorecard.csv'),
    index=False
)
print("\n  ✅ Scorecard exported: carrier_scorecard.csv")

# ── Summary ───────────────────────────────────
print("\n" + "=" * 50)
print("✅ Carrier Scorecard Complete!")
best    = scorecard.iloc[0]
worst   = scorecard.iloc[-1]
print(f"\n  🏆 Best Carrier:  {best['Carrier']} "
      f"(Score: {best['Final_Score']}/100 "
      f"— {best['Grade']})")
print(f"  ⚠️  Worst Carrier: {worst['Carrier']} "
      f"(Score: {worst['Final_Score']}/100 "
      f"— {worst['Grade']})")
print(f"\n  3 charts saved to 03_outputs/charts/")
print(f"  1 CSV saved to 03_outputs/")
print("=" * 50)