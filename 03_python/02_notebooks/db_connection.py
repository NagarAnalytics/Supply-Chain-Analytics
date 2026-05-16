# db_connection.py
import pandas as pd
from sqlalchemy import create_engine, text

def get_engine():
    """Create SQLAlchemy engine for SQL Server."""
    engine = create_engine(
        "mssql+pyodbc://localhost/SupplyChainDB"
        "?driver=SQL+Server&trusted_connection=yes"
    )
    return engine

def run_query(query):
    """Run a SQL query and return a DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df

# Test connection
if __name__ == "__main__":
    engine = get_engine()
    print("✅ Connected to SupplyChainDB!")

    tables = [
        'Customers', 'Products', 'Stores',
        'Exchange_Rates', 'Sales', 'OrderList',
        'FreightRates', 'PlantPorts',
        'ProductsPerPlant', 'WhCapacities', 'WhCosts'
    ]

    for table in tables:
        df = run_query(f"SELECT COUNT(*) AS Rows FROM {table}")
        print(f"  ✅ {table}: {df['Rows'][0]:,} rows")