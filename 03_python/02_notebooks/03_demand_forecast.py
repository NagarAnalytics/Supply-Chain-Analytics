# 03_demand_forecast.py
# Demand Forecasting using Facebook Prophet
# ─────────────────────────────────────────────

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
import os
from db_connection import run_query

# ── Setup ─────────────────────────────────────
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHARTS_DIR = os.path.join('03_outputs', 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)

print("📈 Starting Demand Forecasting...")
print("=" * 50)

# ── Section 2: Load and Prepare Data ──────────
print("\n📦 Loading Sales data from SQL Server...")

# Load sales data
sales = run_query("SELECT Order_Date, Revenue_USD FROM Sales")

print(f" Loaded: {len(sales):,} rows")
print(f" Columns: {list(sales.columns)}")
print(f" Data range: {sales['Order_Date'].min()}"
      f"to {sales['Order_Date'].max()}")

# Convert Order_Date to datetime
sales['Order_Date'] = pd.to_datetime(sales['Order_Date'])

# Aggregate daily revenue
# Prophet need one row per date
daily_sales = sales.groupby('Order_Date').agg(Revenue = ('Revenue_USD', 'sum')).reset_index()

# Rename columns to what Prophet expects
# ds = date, y = value to forecast
daily_sales = daily_sales.rename(columns = {'Order_Date': 'ds', 'Revenue': 'y'})

print(f"\n  ✅ Daily aggregation complete")
print(f"  Total days: {len(daily_sales):,}")
print(f"  Avg daily revenue: "
      f"${daily_sales['y'].mean():,.2f}")
print(f"  Max daily revenue: "
      f"${daily_sales['y'].max():,.2f}")
print(f"  Min daily revenue: "
      f"${daily_sales['y'].min():,.2f}")

# Quick preview
print(f"\n  Sample data (first 5 rows):")
print(daily_sales.head().to_string(index=False))


# ── Section 3: Clean Data Before Training ─────
print("\n🔧 Cleaning data for forecasting...")

# Remove last month (Feb 2021) as it's incomplete
# This prevents end-of-data bias
daily_sales_clean = daily_sales[
    daily_sales['ds'] < '2021-02-01'
].copy()

# Remove outliers — days with unusually low revenue
# (below 5th percentile — likely data gaps)
low_threshold = daily_sales_clean['y'].quantile(0.05)
daily_sales_clean = daily_sales_clean[
    daily_sales_clean['y'] > low_threshold
].copy()

print(f"  Original rows:  {len(daily_sales):,}")
print(f"  Cleaned rows:   {len(daily_sales_clean):,}")
print(f"  Removed rows:   "
      f"{len(daily_sales) - len(daily_sales_clean):,}")
print(f"  Low threshold:  ${low_threshold:,.2f}")
print(f"  New date range: "
      f"{daily_sales_clean['ds'].min()} to "
      f"{daily_sales_clean['ds'].max()}")


# ── Section 3b: Train Prophet Model ───────────
print("\n🤖 Training Prophet model...")
print("  This may take 30-60 seconds...")

# floor and cap tell Prophet never go below 0
# This prevents negative predictions
daily_sales_clean['floor'] = 0
daily_sales_clean['cap'] = (
    daily_sales_clean['y'].max() * 1.5
)

model = Prophet(
    seasonality_mode='multiplicative',
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    changepoint_prior_scale=0.01,
    growth='logistic'
)

# Add monthly seasonality
model.add_seasonality(
    name='monthly',
    period=30.5,
    fourier_order=5
)

# Train on cleaned data
model.fit(daily_sales_clean)
print("  ✅ Model trained successfully!")

# ── Section 4: Make Future Predictions ────────
print("\n🔮 Generating future predictions...")

# Create future dataframe — 6 months ahead
future = model.make_future_dataframe(
    periods=180,
    freq='D'
)

# Must set floor and cap on future dataframe too
future['floor'] = 0
future['cap']   = daily_sales_clean['cap'].iloc[0]

# Generate predictions
forecast = model.predict(future)

# Cap any remaining negatives at 0
forecast['yhat']       = forecast['yhat'].clip(lower=0)
forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0)
forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0)

# Keep important columns
forecast_clean = forecast[[
    'ds', 'yhat', 'yhat_lower',
    'yhat_upper', 'trend',
    'yearly', 'weekly'
]].round(2)

# Separate historical vs future
historical_forecast = forecast_clean[
    forecast_clean['ds'] <= '2021-01-31'
]
future_forecast = forecast_clean[
    forecast_clean['ds'] > '2021-01-31'
]

print(f"  ✅ Predictions generated!")
print(f"  Historical: {len(historical_forecast):,} days")
print(f"  Future:     {len(future_forecast):,} days")

# Show next 30 days
print(f"\n  📅 Next 30 days revenue forecast:")
print(f"  {'Date':<15} {'Predicted':>12} "
      f"{'Lower':>12} {'Upper':>12}")
print("  " + "-" * 55)

for _, row in future_forecast.head(30).iterrows():
    print(f"  {str(row['ds'])[:10]:<15} "
          f"${row['yhat']:>11,.2f} "
          f"${row['yhat_lower']:>11,.2f} "
          f"${row['yhat_upper']:>11,.2f}")

# Summary
print(f"\n  📊 6-Month Forecast Summary:")
print(f"  Avg Daily Revenue:       "
      f"${future_forecast['yhat'].mean():,.2f}")
print(f"  Total Predicted Revenue: "
      f"${future_forecast['yhat'].sum():,.2f}")
print(f"  Best Day Predicted:      "
      f"${future_forecast['yhat'].max():,.2f}")
print(f"  Worst Day Predicted:     "
      f"${future_forecast['yhat'].min():,.2f}")


# ── Section 5: Visualizations ─────────────────
print("\n📊 Generating forecast charts...")

# ── Chart 1: Full Forecast Plot ────────────────
fig, ax = plt.subplots(figsize=(16, 7))

# Plot historical actual data
ax.plot(
    daily_sales_clean['ds'],
    daily_sales_clean['y'],
    color='#2196F3',
    linewidth=0.8,
    alpha=0.7,
    label='Historical Revenue'
)

# Plot predicted values
ax.plot(
    forecast_clean['ds'],
    forecast_clean['yhat'],
    color='#FF9800',
    linewidth=1.5,
    label='Predicted Revenue'
)

# Plot confidence interval
ax.fill_between(
    forecast_clean['ds'],
    forecast_clean['yhat_lower'],
    forecast_clean['yhat_upper'],
    alpha=0.15,
    color='#FF9800',
    label='Confidence Interval'
)

# Add vertical line showing forecast start
ax.axvline(
    x=pd.Timestamp('2021-02-01'),
    color='red',
    linestyle='--',
    linewidth=1.5,
    label='Forecast Start'
)

ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Daily Revenue (USD)', fontsize=12)
ax.set_title(
    'Supply Chain Revenue Forecast — 6 Months Ahead',
    fontsize=14, fontweight='bold'
)
ax.legend(fontsize=11)
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(
        lambda x, p: f'${x:,.0f}'
    )
)
plt.tight_layout()
plt.savefig(
    os.path.join(CHARTS_DIR,
                 '10_revenue_forecast.png'),
    dpi=150
)
plt.show()
print("  ✅ Chart 10 saved: revenue_forecast.png")

# ── Chart 2: Future Only ───────────────────────
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(
    future_forecast['ds'],
    future_forecast['yhat'],
    color='#FF9800',
    linewidth=2,
    marker='o',
    markersize=3,
    label='Predicted Revenue'
)

ax.fill_between(
    future_forecast['ds'],
    future_forecast['yhat_lower'],
    future_forecast['yhat_upper'],
    alpha=0.2,
    color='#FF9800',
    label='80% Confidence Interval'
)

# Add horizontal line for historical average
ax.axhline(
    y=daily_sales_clean['y'].mean(),
    color='#2196F3',
    linestyle='--',
    linewidth=1.5,
    label=f'Historical Avg '
          f'(${daily_sales_clean["y"].mean():,.0f})'
)

ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Daily Revenue (USD)', fontsize=12)
ax.set_title(
    '6-Month Revenue Forecast (Feb — Aug 2021)',
    fontsize=14, fontweight='bold'
)
ax.legend(fontsize=11)
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(
        lambda x, p: f'${x:,.0f}'
    )
)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(
    os.path.join(CHARTS_DIR,
                 '11_future_forecast.png'),
    dpi=150
)
plt.show()
print("  ✅ Chart 11 saved: future_forecast.png")

# ── Chart 3: Seasonality Components ───────────
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# Yearly seasonality
yearly_data = forecast_clean[
    ['ds', 'yearly']
].copy()
yearly_data['month'] = yearly_data['ds'].dt.month
monthly_seasonal = yearly_data.groupby(
    'month')['yearly'].mean()

month_names = [
    'Jan', 'Feb', 'Mar', 'Apr',
    'May', 'Jun', 'Jul', 'Aug',
    'Sep', 'Oct', 'Nov', 'Dec'
]

colors = [
    '#F44336' if v > 0 else '#2196F3'
    for v in monthly_seasonal.values
]

axes[0].bar(
    month_names,
    monthly_seasonal.values,
    color=colors
)
axes[0].axhline(
    y=0, color='black',
    linewidth=0.8, linestyle='-'
)
axes[0].set_title(
    'Yearly Seasonality — Revenue Impact by Month',
    fontsize=13, fontweight='bold'
)
axes[0].set_ylabel('Seasonality Effect')
axes[0].yaxis.set_major_formatter(
    plt.FuncFormatter(
        lambda x, p: f'${x:,.0f}'
    )
)

# Weekly seasonality
weekly_data = forecast_clean[
    ['ds', 'weekly']
].copy()
weekly_data['dayofweek'] = \
    weekly_data['ds'].dt.dayofweek
daily_seasonal = weekly_data.groupby(
    'dayofweek')['weekly'].mean()

day_names = [
    'Mon', 'Tue', 'Wed',
    'Thu', 'Fri', 'Sat', 'Sun'
]

colors_week = [
    '#F44336' if v > 0 else '#2196F3'
    for v in daily_seasonal.values
]

axes[1].bar(
    day_names,
    daily_seasonal.values,
    color=colors_week
)
axes[1].axhline(
    y=0, color='black',
    linewidth=0.8, linestyle='-'
)
axes[1].set_title(
    'Weekly Seasonality — Revenue Impact by Day',
    fontsize=13, fontweight='bold'
)
axes[1].set_ylabel('Seasonality Effect')
axes[1].yaxis.set_major_formatter(
    plt.FuncFormatter(
        lambda x, p: f'${x:,.0f}'
    )
)

plt.tight_layout()
plt.savefig(
    os.path.join(CHARTS_DIR,
                 '12_seasonality.png'),
    dpi=150
)
plt.show()
print("  ✅ Chart 12 saved: seasonality.png")

# ── Export Forecast to CSV ─────────────────────
future_forecast[[
    'ds', 'yhat',
    'yhat_lower', 'yhat_upper'
]].rename(columns={
    'ds':          'Date',
    'yhat':        'Predicted_Revenue',
    'yhat_lower':  'Lower_Bound',
    'yhat_upper':  'Upper_Bound'
}).to_csv(
    os.path.join(
        '03_outputs',
        'revenue_forecast.csv'
    ),
    index=False
)
print("\n  ✅ Forecast exported: revenue_forecast.csv")