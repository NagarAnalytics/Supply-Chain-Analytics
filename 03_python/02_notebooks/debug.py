# ── Debug — Check Data Types ───────────────────
print("\n🔍 Debug: Checking data types...")
print(f"  Annual_Demand dtype:      "
      f"{product_demand['Annual_Demand'].dtype}")
print(f"  Holding_Cost_Annual dtype:"
      f"{product_demand['Holding_Cost_Annual'].dtype}")
print(f"  Unit_Cost_USD dtype:      "
      f"{product_demand['Unit_Cost_USD'].dtype}")
print(f"  ordering_cost type:       "
      f"{type(ordering_cost)}")

# Check for non-numeric values
print(f"\n  Non-numeric Unit_Cost_USD:")
print(product_demand[
    pd.to_numeric(
        product_demand['Unit_Cost_USD'],
        errors='coerce'
    ).isna()
][['ProductKey', 'Product_Name',
   'Unit_Cost_USD']].head(10))

print(f"\n  Non-numeric Minimum_Cost:")
print(freight[
    pd.to_numeric(
        freight['Minimum_Cost'],
        errors='coerce'
    ).isna()
][['Carrier', 'Minimum_Cost']].head(10))