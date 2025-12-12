"""
Configuration for CFG Ukraine Financial Analytics Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(".env", override=True)

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://salic-azure-aifoundry.cognitiveservices.azure.com/")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

# Microsoft Fabric SQL Configuration
FABRIC_SQL_ENDPOINT = os.getenv("FABRIC_SQL_ENDPOINT", "your-fabric-endpoint.datawarehouse.fabric.microsoft.com")
FABRIC_DATABASE = "salic_finance_warehouse"
FABRIC_SQL_USER = os.getenv("FABRIC_SQL_USER", "")  # Leave empty if using Service Principal
FABRIC_SQL_PASSWORD = os.getenv("FABRIC_SQL_PASSWORD", "")

# Target view for CFG Ukraine data
TARGET_VIEW = "vw_Fact_Actuals_SALIC_Ukraine"

# Available account categories in the data
AVAILABLE_ACCOUNTS = [
    "Cash and cash_equivalents",
    "Exchange loss",
    "FCCS_Current Liabilities",
    "FCCS_Other Reserves",
    "FCCS_Owners Equity",
    "FCCS_Retained Earnings",
    "FCCS_Total Non Cash",
    "FX Reserve",
    "Finance charge",
    "General and administrative expenses",
    "Intangible assets, net",
    "Trade and other payables"
]

# Schema information for the LLM
SCHEMA_INFO = """
## Database Schema for CFG Ukraine Financial Data

### Main Fact View: vw_Fact_Actuals_SALIC_Ukraine
This view contains financial actuals for CFG Ukraine (Entity E250).

Columns:
- FactActualsKey (bigint): Primary key
- AccountKey (bigint): Foreign key to Dim_Account
- DepartmentKey (bigint): Foreign key to Dim_Department
- EntityKey (bigint): Foreign key to Dim_Entity
- IntercompanyKey (bigint): Foreign key for intercompany transactions
- PeriodKey (bigint): Foreign key to Dim_Period (1-12 for Jan-Dec)
- ScenarioKey (bigint): Foreign key to Dim_Scenario
- YearKey (bigint): Foreign key to Dim_Year
- CurrencyKey (bigint): Foreign key to Dim_Currency
- Amount (varchar): The financial amount (needs CAST to DECIMAL)

### Dimension Tables:

#### Dim_Account
- AccountKey (bigint)
- AccountCode (varchar)
- ParentAccountCode (varchar)
- Description (varchar)
- FinalParentAccountCode (varchar) - USE THIS for grouping (e.g., 'General and administrative expenses')

#### Dim_Period
- PeriodKey (bigint): 1-12
- PeriodName (varchar): Jan, Feb, Mar, etc.
- PeriodNumber (int): 1-12
- FiscalQuarter (varchar): Q1, Q2, Q3, Q4

#### Dim_Year
- YearKey (bigint): 1=FY24, 2=FY25, 3=FY26
- FiscalYearLabel (varchar): FY24, FY25, FY26
- CalendarYear (int): 2024, 2025, 2026

#### Dim_Scenario
- ScenarioKey (bigint): 1=Actual, 2=Apr_Forecast, 3=OEP_Plan
- ScenarioName (varchar): Actual, Apr_Forecast, OEP_Plan

#### Dim_Entity
- EntityKey (bigint)
- EntityCode (varchar): E250 = CFG Ukraine

### Available Financial Categories (FinalParentAccountCode):
- Cash and cash_equivalents
- Exchange loss
- FCCS_Current Liabilities
- FCCS_Other Reserves
- FCCS_Owners Equity
- FCCS_Retained Earnings
- FCCS_Total Non Cash
- FX Reserve
- Finance charge
- General and administrative expenses
- Intangible assets, net
- Trade and other payables

### Data Range:
- Years: 2024 (Q3-Q4 available)
- Scenarios: Primarily "Actual"

### Important SQL Notes:
1. Always CAST Amount to DECIMAL: CAST(f.Amount AS DECIMAL(18,2))
2. Always join dimensions to get readable names
3. Use PeriodNumber for ordering (not PeriodName)
4. Filter by ScenarioName = 'Actual' for actual data
"""
