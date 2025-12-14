"""
Schema Discovery Script: Find actual column names in tables
"""
import os
from dotenv import load_dotenv
load_dotenv()

from fabric_connector import FabricConnector

def discover_schema():
    """Discover actual column names in key tables."""
    
    connector = FabricConnector()
    
    print("=" * 70)
    print("SCHEMA DISCOVERY: Finding Actual Column Names")
    print("=" * 70)
    
    tables_to_check = [
        "Dim_Entity",
        "Dim_Account", 
        "Dim_Department",
        "Dim_Period",
        "Dim_Year",
        "Dim_Scenario",
        "Dim_Currency",
        "Fact_Actuals",
        "Fact_ForecastBudget"
    ]
    
    for table in tables_to_check:
        print(f"\n📋 Table: {table}")
        print("-" * 50)
        
        # Get column info using INFORMATION_SCHEMA
        query = f"""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table}'
        ORDER BY ORDINAL_POSITION;
        """
        
        try:
            result = connector.execute_query(query)
            if result['rows']:
                for row in result['rows']:
                    nullable = "NULL" if row.get('IS_NULLABLE') == 'YES' else "NOT NULL"
                    print(f"   - {row['COLUMN_NAME']} ({row['DATA_TYPE']}) {nullable}")
            else:
                # Try alternative - SELECT TOP 0 to get column names
                print(f"   Trying alternative method...")
                alt_query = f"SELECT TOP 1 * FROM {table};"
                alt_result = connector.execute_query(alt_query)
                if alt_result['columns']:
                    print(f"   Columns found: {', '.join(alt_result['columns'])}")
                else:
                    print(f"   Could not retrieve columns")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            # Try alternative
            try:
                alt_query = f"SELECT TOP 1 * FROM {table};"
                alt_result = connector.execute_query(alt_query)
                if alt_result['columns']:
                    print(f"   Columns from sample: {', '.join(alt_result['columns'])}")
            except Exception as e2:
                print(f"   ❌ Alternative also failed: {e2}")
    
    # Also check the view
    print(f"\n📋 View: vw_Fact_Actuals_SALIC_Ukraine")
    print("-" * 50)
    try:
        query = "SELECT TOP 1 * FROM vw_Fact_Actuals_SALIC_Ukraine;"
        result = connector.execute_query(query)
        if result['columns']:
            print(f"   Columns: {', '.join(result['columns'])}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test a working query on Fact_ForecastBudget
    print("\n" + "=" * 70)
    print("TEST: Query Fact_ForecastBudget for E250")
    print("=" * 70)
    
    test_query = """
    SELECT TOP 5 *
    FROM Fact_ForecastBudget fb
    JOIN Dim_Entity e ON fb.EntityKey = e.EntityKey
    WHERE e.EntityCode = 'E250';
    """
    try:
        result = connector.execute_query(test_query)
        print(f"   Columns returned: {result['columns']}")
        print(f"   Rows returned: {result['row_count']}")
        if result['rows']:
            print(f"   Sample row: {result['rows'][0]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        
        # Try simpler query
        print("\n   Trying simpler query...")
        simple_query = "SELECT TOP 5 * FROM Fact_ForecastBudget;"
        try:
            result = connector.execute_query(simple_query)
            print(f"   Columns: {result['columns']}")
            if result['rows']:
                print(f"   Sample: {result['rows'][0]}")
        except Exception as e2:
            print(f"   ❌ Simple query also failed: {e2}")
    
    print("\n" + "=" * 70)
    print("SCHEMA DISCOVERY COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    discover_schema()