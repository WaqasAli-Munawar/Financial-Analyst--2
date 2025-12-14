"""
Test Script: Verify Forecast vs Budget Query
"""
import os
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from fabric_connector import FabricConnector

def test_queries():
    """Test various queries on Fact_ForecastBudget."""
    
    connector = FabricConnector()
    
    print("=" * 70)
    print("TEST: Forecast vs Budget Queries")
    print("=" * 70)
    
    # Test 1: Simple count with account join
    print("\n📊 Test 1: Count records with valid AccountKey")
    print("-" * 50)
    
    query1 = """
    SELECT COUNT(*) AS TotalWithAccount
    FROM Fact_ForecastBudget fb
    WHERE fb.AccountKey IS NOT NULL;
    """
    try:
        result = connector.execute_query(query1)
        print(f"   Records with AccountKey: {result['rows'][0]['TotalWithAccount']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Count E250 records with valid AccountKey
    print("\n📊 Test 2: E250 records with valid AccountKey")
    print("-" * 50)
    
    query2 = """
    SELECT COUNT(*) AS E250WithAccount
    FROM Fact_ForecastBudget fb
    JOIN Dim_Entity e ON fb.EntityKey = e.EntityKey
    WHERE e.EntityCode = 'E250'
      AND fb.AccountKey IS NOT NULL;
    """
    try:
        result = connector.execute_query(query2)
        print(f"   E250 records with AccountKey: {result['rows'][0]['E250WithAccount']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Sample E250 data with accounts
    print("\n📊 Test 3: Sample E250 Budget data with Account details")
    print("-" * 50)
    
    query3 = """
    SELECT TOP 10
        a.FinalParentAccountCode,
        s.ScenarioName,
        y.CalendarYear,
        SUM(CAST(fb.Amount AS DECIMAL(18,2))) AS TotalAmount
    FROM Fact_ForecastBudget fb
    JOIN Dim_Entity e ON fb.EntityKey = e.EntityKey
    JOIN Dim_Account a ON fb.AccountKey = a.AccountKey
    JOIN Dim_Scenario s ON fb.ScenarioKey = s.ScenarioKey
    JOIN Dim_Year y ON fb.YearKey = y.YearKey
    WHERE e.EntityCode = 'E250'
    GROUP BY a.FinalParentAccountCode, s.ScenarioName, y.CalendarYear
    ORDER BY TotalAmount DESC;
    """
    try:
        result = connector.execute_query(query3)
        print(f"   Found {result['row_count']} account groups")
        if result['rows']:
            for row in result['rows']:
                print(f"   - {row.get('FinalParentAccountCode')}: {row.get('ScenarioName')} = {row.get('TotalAmount'):,.0f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Full forecast vs budget query
    print("\n📊 Test 4: Forecast vs Budget (Apr_Forecast vs OEP_Plan)")
    print("-" * 50)
    
    query4 = """
    SELECT 
        a.FinalParentAccountCode,
        s.ScenarioName,
        SUM(CAST(fb.Amount AS DECIMAL(18,2))) AS Amount
    FROM Fact_ForecastBudget fb
    JOIN Dim_Account a ON fb.AccountKey = a.AccountKey
    JOIN Dim_Entity e ON fb.EntityKey = e.EntityKey
    JOIN Dim_Year y ON fb.YearKey = y.YearKey
    JOIN Dim_Scenario s ON fb.ScenarioKey = s.ScenarioKey
    WHERE e.EntityCode = 'E250'
      AND y.CalendarYear = 2025
    GROUP BY a.FinalParentAccountCode, s.ScenarioName
    ORDER BY a.FinalParentAccountCode, s.ScenarioName;
    """
    try:
        result = connector.execute_query(query4)
        print(f"   Found {result['row_count']} rows")
        if result['rows']:
            # Group by account
            current_account = None
            for row in result['rows'][:20]:
                account = row.get('FinalParentAccountCode', 'N/A')
                scenario = row.get('ScenarioName', 'N/A')
                amount = row.get('Amount', 0)
                if account != current_account:
                    print(f"\n   {account}:")
                    current_account = account
                print(f"      - {scenario}: {amount:,.0f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Check what accounts exist in Fact_ForecastBudget for E250
    print("\n📊 Test 5: All accounts in E250 Forecast/Budget data")
    print("-" * 50)
    
    query5 = """
    SELECT DISTINCT
        a.FinalParentAccountCode,
        COUNT(*) AS RecordCount
    FROM Fact_ForecastBudget fb
    JOIN Dim_Account a ON fb.AccountKey = a.AccountKey
    JOIN Dim_Entity e ON fb.EntityKey = e.EntityKey
    WHERE e.EntityCode = 'E250'
    GROUP BY a.FinalParentAccountCode
    ORDER BY RecordCount DESC;
    """
    try:
        result = connector.execute_query(query5)
        print(f"   Found {result['row_count']} account categories")
        if result['rows']:
            for row in result['rows']:
                print(f"   - {row.get('FinalParentAccountCode')}: {row.get('RecordCount')} records")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_queries()