"""
Diagnostic Script: Investigate Fact_ForecastBudget Table
Run this to understand why the forecast/budget queries return 0 records
"""
import os
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from fabric_connector import FabricConnector

def run_diagnostics():
    """Run diagnostic queries on Fact_ForecastBudget table."""
    
    connector = FabricConnector()
    
    print("=" * 70)
    print("DIAGNOSTIC: Investigating Fact_ForecastBudget Table")
    print("=" * 70)
    
    # -------------------------------------------------------------------------
    # Query 1: Check if table exists and has any data
    # -------------------------------------------------------------------------
    print("\n📊 Query 1: Check total row count in Fact_ForecastBudget")
    print("-" * 50)
    
    query1 = """
    SELECT COUNT(*) AS TotalRows
    FROM Fact_ForecastBudget;
    """
    try:
        result = connector.execute_query(query1)
        print(f"   Total rows: {result['rows'][0]['TotalRows'] if result['rows'] else 'N/A'}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # -------------------------------------------------------------------------
    # Query 2: Check available scenarios in Fact_ForecastBudget
    # -------------------------------------------------------------------------
    print("\n📊 Query 2: Available Scenarios in Fact_ForecastBudget")
    print("-" * 50)
    
    query2 = """
    SELECT DISTINCT s.ScenarioName, s.ScenarioKey, COUNT(*) AS RecordCount
    FROM Fact_ForecastBudget fb
    JOIN Dim_Scenario s ON fb.ScenarioKey = s.ScenarioKey
    GROUP BY s.ScenarioName, s.ScenarioKey
    ORDER BY s.ScenarioName;
    """
    try:
        result = connector.execute_query(query2)
        if result['rows']:
            for row in result['rows']:
                print(f"   - {row['ScenarioName']} (Key: {row['ScenarioKey']}): {row['RecordCount']} records")
        else:
            print("   No scenarios found in Fact_ForecastBudget")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # -------------------------------------------------------------------------
    # Query 3: Check available entities in Fact_ForecastBudget
    # -------------------------------------------------------------------------
    print("\n📊 Query 3: Available Entities in Fact_ForecastBudget")
    print("-" * 50)
    
    query3 = """
    SELECT DISTINCT e.EntityCode, e.EntityName, COUNT(*) AS RecordCount
    FROM Fact_ForecastBudget fb
    JOIN Dim_Entity e ON fb.EntityKey = e.EntityKey
    GROUP BY e.EntityCode, e.EntityName
    ORDER BY RecordCount DESC;
    """
    try:
        result = connector.execute_query(query3)
        if result['rows']:
            print(f"   Found {len(result['rows'])} entities:")
            for row in result['rows'][:10]:  # Show top 10
                entity_code = row.get('EntityCode', 'N/A')
                entity_name = row.get('EntityName', 'N/A')
                count = row.get('RecordCount', 0)
                is_cfg = " ← CFG Ukraine!" if entity_code == 'E250' else ""
                print(f"   - {entity_code}: {entity_name} ({count} records){is_cfg}")
            if len(result['rows']) > 10:
                print(f"   ... and {len(result['rows']) - 10} more entities")
        else:
            print("   No entities found in Fact_ForecastBudget")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # -------------------------------------------------------------------------
    # Query 4: Check if E250 (CFG Ukraine) exists in Fact_ForecastBudget
    # -------------------------------------------------------------------------
    print("\n📊 Query 4: Check CFG Ukraine (E250) in Fact_ForecastBudget")
    print("-" * 50)
    
    query4 = """
    SELECT COUNT(*) AS RecordCount
    FROM Fact_ForecastBudget fb
    JOIN Dim_Entity e ON fb.EntityKey = e.EntityKey
    WHERE e.EntityCode = 'E250';
    """
    try:
        result = connector.execute_query(query4)
        count = result['rows'][0]['RecordCount'] if result['rows'] else 0
        print(f"   E250 (CFG Ukraine) records: {count}")
        if count == 0:
            print("   ⚠️  No forecast/budget data for CFG Ukraine in this table!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # -------------------------------------------------------------------------
    # Query 5: Check available years in Fact_ForecastBudget
    # -------------------------------------------------------------------------
    print("\n📊 Query 5: Available Years in Fact_ForecastBudget")
    print("-" * 50)
    
    query5 = """
    SELECT DISTINCT y.CalendarYear, y.FiscalYearLabel, COUNT(*) AS RecordCount
    FROM Fact_ForecastBudget fb
    JOIN Dim_Year y ON fb.YearKey = y.YearKey
    GROUP BY y.CalendarYear, y.FiscalYearLabel
    ORDER BY y.CalendarYear;
    """
    try:
        result = connector.execute_query(query5)
        if result['rows']:
            for row in result['rows']:
                print(f"   - {row['CalendarYear']} ({row['FiscalYearLabel']}): {row['RecordCount']} records")
        else:
            print("   No years found in Fact_ForecastBudget")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # -------------------------------------------------------------------------
    # Query 6: Sample data from Fact_ForecastBudget (first 5 rows)
    # -------------------------------------------------------------------------
    print("\n📊 Query 6: Sample Data from Fact_ForecastBudget")
    print("-" * 50)
    
    query6 = """
    SELECT TOP 5
        fb.FactForecastBudgetKey,
        e.EntityCode,
        a.FinalParentAccountCode,
        s.ScenarioName,
        y.CalendarYear,
        p.PeriodName,
        fb.Amount
    FROM Fact_ForecastBudget fb
    JOIN Dim_Entity e ON fb.EntityKey = e.EntityKey
    JOIN Dim_Account a ON fb.AccountKey = a.AccountKey
    JOIN Dim_Scenario s ON fb.ScenarioKey = s.ScenarioKey
    JOIN Dim_Year y ON fb.YearKey = y.YearKey
    JOIN Dim_Period p ON fb.PeriodKey = p.PeriodKey
    ORDER BY fb.FactForecastBudgetKey;
    """
    try:
        result = connector.execute_query(query6)
        if result['rows']:
            print(f"   Sample rows:")
            for row in result['rows']:
                print(f"   - Entity: {row.get('EntityCode')}, Account: {row.get('FinalParentAccountCode')}, "
                      f"Scenario: {row.get('ScenarioName')}, Year: {row.get('CalendarYear')}, "
                      f"Period: {row.get('PeriodName')}, Amount: {row.get('Amount')}")
        else:
            print("   No data found in Fact_ForecastBudget")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # -------------------------------------------------------------------------
    # Query 7: Compare with Fact_Actuals - what entities are there?
    # -------------------------------------------------------------------------
    print("\n📊 Query 7: Compare - Entities in Fact_Actuals")
    print("-" * 50)
    
    query7 = """
    SELECT DISTINCT e.EntityCode, e.EntityName, COUNT(*) AS RecordCount
    FROM Fact_Actuals fa
    JOIN Dim_Entity e ON fa.EntityKey = e.EntityKey
    GROUP BY e.EntityCode, e.EntityName
    ORDER BY RecordCount DESC;
    """
    try:
        result = connector.execute_query(query7)
        if result['rows']:
            print(f"   Found {len(result['rows'])} entities in Fact_Actuals:")
            for row in result['rows'][:10]:
                entity_code = row.get('EntityCode', 'N/A')
                entity_name = row.get('EntityName', 'N/A')
                count = row.get('RecordCount', 0)
                is_cfg = " ← CFG Ukraine!" if entity_code == 'E250' else ""
                print(f"   - {entity_code}: {entity_name} ({count} records){is_cfg}")
        else:
            print("   No entities found in Fact_Actuals")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # -------------------------------------------------------------------------
    # Query 8: Check Dim_Scenario for all available scenarios
    # -------------------------------------------------------------------------
    print("\n📊 Query 8: All Scenarios in Dim_Scenario")
    print("-" * 50)
    
    query8 = """
    SELECT ScenarioKey, ScenarioName
    FROM Dim_Scenario
    ORDER BY ScenarioKey;
    """
    try:
        result = connector.execute_query(query8)
        if result['rows']:
            for row in result['rows']:
                print(f"   - Key {row['ScenarioKey']}: {row['ScenarioName']}")
        else:
            print("   No scenarios found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # -------------------------------------------------------------------------
    # Query 9: Check the view structure
    # -------------------------------------------------------------------------
    print("\n📊 Query 9: Check vw_Fact_Actuals_SALIC_Ukraine scenarios")
    print("-" * 50)
    
    query9 = """
    SELECT DISTINCT s.ScenarioName, COUNT(*) AS RecordCount
    FROM vw_Fact_Actuals_SALIC_Ukraine f
    JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
    GROUP BY s.ScenarioName;
    """
    try:
        result = connector.execute_query(query9)
        if result['rows']:
            for row in result['rows']:
                print(f"   - {row['ScenarioName']}: {row['RecordCount']} records")
        else:
            print("   No scenarios found in view")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_diagnostics()