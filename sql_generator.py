"""
SQL Generator Module - Enhanced Version 2.0
Converts natural language queries to SQL for Microsoft Fabric
Analytics-aware with Value-Driver Tree query patterns

December 2025
"""
from openai import AzureOpenAI
from typing import Dict, List, Optional, Tuple
import re
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
)


# =============================================================================
# ENHANCED SCHEMA DEFINITION
# =============================================================================

ENHANCED_SCHEMA_INFO = """
## CFG Ukraine Database Schema (Microsoft Fabric)

### FACT TABLES

#### vw_Fact_Actuals_SALIC_Ukraine (Primary Financial Facts)
Main view for financial actuals, budget, and forecast data.

| Column | Type | Description |
|--------|------|-------------|
| FactActualsKey | bigint | Primary key |
| AccountKey | bigint | FK to Dim_Account |
| EntityKey | bigint | FK to Dim_Entity (E250 = CFG Ukraine) |
| PeriodKey | bigint | FK to Dim_Period (1-12) |
| ScenarioKey | bigint | FK to Dim_Scenario |
| YearKey | bigint | FK to Dim_Year |
| Amount | varchar | Financial amount (MUST CAST to DECIMAL) |

### DIMENSION TABLES

#### Dim_Account
| Column | Type | Use |
|--------|------|-----|
| AccountKey | bigint | Join key |
| AccountCode | varchar | Detail account |
| FinalParentAccountCode | varchar | **USE THIS** for grouping |
| Description | varchar | Account name |

#### Dim_Period
| Column | Type | Use |
|--------|------|-----|
| PeriodKey | bigint | 1-12 for Jan-Dec |
| PeriodName | varchar | Jan, Feb, Mar... |
| PeriodNumber | int | Use for ORDER BY |
| FiscalQuarter | varchar | Q1, Q2, Q3, Q4 |

#### Dim_Year
| Column | Type | Use |
|--------|------|-----|
| YearKey | bigint | 1=FY24, 2=FY25, 3=FY26 |
| CalendarYear | int | 2024, 2025, 2026 |
| FiscalYearLabel | varchar | FY24, FY25, FY26 |

#### Dim_Scenario
| Column | Type | Use |
|--------|------|-----|
| ScenarioKey | bigint | 1=Actual, 2=Forecast, 3=Budget |
| ScenarioName | varchar | Actual, Apr_Forecast, OEP_Plan |

### AVAILABLE ACCOUNT CATEGORIES (FinalParentAccountCode)

**Revenue & Margin:**
- Revenue
- Cost of Sales
- Gross Margin

**Operating Expenses:**
- General and administrative expenses
- Selling and distribution expenses
- Finance charge

**Balance Sheet:**
- Cash and cash_equivalents
- Trade and other payables
- Trade and other receivables
- Intangible assets, net
- Property plant and equipment

**Equity:**
- FCCS_Owners Equity
- FCCS_Retained Earnings
- FCCS_Other Reserves
- FX Reserve

### IMPORTANT: AVAILABLE TABLES ONLY
The only fact table available is vw_Fact_Actuals_SALIC_Ukraine.
Do NOT reference vw_Crop_Performance, vw_Sales_Detail, or any crop-specific views.
All crop/operational data must come from the knowledge base, not SQL queries.

### DATA RANGES
- Financial Years: FY2024 (partial), FY2025 (full)
- Scenarios: Actual, Apr_Forecast, OEP_Plan (Budget)
"""


# =============================================================================
# QUERY TEMPLATES BY ANALYTICS TYPE
# =============================================================================

QUERY_TEMPLATES = {
    "financial_summary": """
SELECT 
    a.FinalParentAccountCode,
    SUM(CAST(f.Amount AS DECIMAL(18,2))) AS TotalAmount
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Year y ON f.YearKey = y.YearKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE s.ScenarioName = 'Actual'
  AND y.CalendarYear = {year}
GROUP BY a.FinalParentAccountCode
ORDER BY TotalAmount DESC;
""",

    "monthly_financials": """
SELECT 
    y.CalendarYear,
    p.PeriodName,
    p.PeriodNumber,
    p.FiscalQuarter,
    a.FinalParentAccountCode,
    SUM(CAST(f.Amount AS DECIMAL(18,2))) AS Amount
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Period p ON f.PeriodKey = p.PeriodKey
JOIN Dim_Year y ON f.YearKey = y.YearKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE a.FinalParentAccountCode = '{account_category}'
  AND s.ScenarioName = 'Actual'
  AND y.CalendarYear = {year}
GROUP BY y.CalendarYear, p.PeriodName, p.PeriodNumber, p.FiscalQuarter, a.FinalParentAccountCode
ORDER BY p.PeriodNumber;
""",

    "budget_vs_actual": """
SELECT 
    a.FinalParentAccountCode,
    SUM(CASE WHEN s.ScenarioName = 'Actual' THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) AS Actual,
    SUM(CASE WHEN s.ScenarioName = 'OEP_Plan' THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) AS Budget,
    SUM(CASE WHEN s.ScenarioName = 'Actual' THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) -
    SUM(CASE WHEN s.ScenarioName = 'OEP_Plan' THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) AS Variance
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Year y ON f.YearKey = y.YearKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE y.CalendarYear = {year}
GROUP BY a.FinalParentAccountCode
ORDER BY ABS(SUM(CASE WHEN s.ScenarioName = 'Actual' THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) -
    SUM(CASE WHEN s.ScenarioName = 'OEP_Plan' THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END)) DESC;
""",

    "quarterly_summary": """
SELECT 
    y.CalendarYear,
    p.FiscalQuarter,
    a.FinalParentAccountCode,
    SUM(CAST(f.Amount AS DECIMAL(18,2))) AS Amount
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Period p ON f.PeriodKey = p.PeriodKey
JOIN Dim_Year y ON f.YearKey = y.YearKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE s.ScenarioName = 'Actual'
  AND y.CalendarYear = {year}
GROUP BY y.CalendarYear, p.FiscalQuarter, a.FinalParentAccountCode
ORDER BY p.FiscalQuarter, a.FinalParentAccountCode;
""",

    "variance_analysis": """
WITH actuals AS (
    SELECT 
        a.FinalParentAccountCode,
        SUM(CAST(f.Amount AS DECIMAL(18,2))) AS actual_amount
    FROM vw_Fact_Actuals_SALIC_Ukraine f
    JOIN Dim_Account a ON f.AccountKey = a.AccountKey
    JOIN Dim_Year y ON f.YearKey = y.YearKey
    JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
    WHERE s.ScenarioName = 'Actual' AND y.CalendarYear = {year}
    GROUP BY a.FinalParentAccountCode
),
budget AS (
    SELECT 
        a.FinalParentAccountCode,
        SUM(CAST(f.Amount AS DECIMAL(18,2))) AS budget_amount
    FROM vw_Fact_Actuals_SALIC_Ukraine f
    JOIN Dim_Account a ON f.AccountKey = a.AccountKey
    JOIN Dim_Year y ON f.YearKey = y.YearKey
    JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
    WHERE s.ScenarioName = 'OEP_Plan' AND y.CalendarYear = {year}
    GROUP BY a.FinalParentAccountCode
)
SELECT 
    COALESCE(a.FinalParentAccountCode, b.FinalParentAccountCode) AS AccountCategory,
    COALESCE(a.actual_amount, 0) AS Actual,
    COALESCE(b.budget_amount, 0) AS Budget,
    COALESCE(a.actual_amount, 0) - COALESCE(b.budget_amount, 0) AS Variance,
    CASE 
        WHEN COALESCE(b.budget_amount, 0) != 0 
        THEN ((COALESCE(a.actual_amount, 0) / b.budget_amount) - 1) * 100 
        ELSE 0 
    END AS Variance_Pct
FROM actuals a
FULL OUTER JOIN budget b ON a.FinalParentAccountCode = b.FinalParentAccountCode
ORDER BY ABS(COALESCE(a.actual_amount, 0) - COALESCE(b.budget_amount, 0)) DESC;
""",

    "yoy_comparison": """
SELECT 
    a.FinalParentAccountCode,
    SUM(CASE WHEN y.CalendarYear = {year} THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) AS CurrentYear,
    SUM(CASE WHEN y.CalendarYear = {prior_year} THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) AS PriorYear,
    SUM(CASE WHEN y.CalendarYear = {year} THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) -
    SUM(CASE WHEN y.CalendarYear = {prior_year} THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) AS YoY_Change
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Year y ON f.YearKey = y.YearKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE s.ScenarioName = 'Actual'
  AND y.CalendarYear IN ({year}, {prior_year})
GROUP BY a.FinalParentAccountCode
ORDER BY ABS(SUM(CASE WHEN y.CalendarYear = {year} THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) -
    SUM(CASE WHEN y.CalendarYear = {prior_year} THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END)) DESC;
""",

    "account_summary": """
SELECT 
    a.FinalParentAccountCode,
    SUM(CAST(f.Amount AS DECIMAL(18,2))) AS TotalAmount
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE s.ScenarioName = 'Actual'
GROUP BY a.FinalParentAccountCode
ORDER BY TotalAmount DESC;
"""
}


# =============================================================================
# SQL GENERATION PROMPT
# =============================================================================

SQL_GENERATION_PROMPT = """You are an expert SQL analyst for Microsoft Fabric Data Warehouse. 
Generate SQL queries for CFG Ukraine financial and operational data.

{schema_info}

## CRITICAL RULES:
1. ALWAYS use table aliases (f=fact, a=account, p=period, y=year, s=scenario)
2. ALWAYS CAST Amount: SUM(CAST(f.Amount AS DECIMAL(18,2))) AS Amount
3. ALWAYS join dimension tables for readable names
4. Default to ScenarioName = 'Actual' unless asked for budget/forecast
5. Use PeriodNumber for ORDER BY (not PeriodName)
6. Use FinalParentAccountCode for account filtering
7. NEVER reference vw_Crop_Performance or vw_Sales_Detail - these tables DO NOT EXIST
8. For crop-specific questions, use only vw_Fact_Actuals_SALIC_Ukraine with Revenue accounts

## ANALYTICS-SPECIFIC PATTERNS:

### DESCRIPTIVE Queries (What happened?)
- Simple aggregations with GROUP BY
- Include relevant dimensions for breakdown
- Order by time or amount

### DIAGNOSTIC Queries (Why did it happen?)
- Compare Actual vs Budget using CASE WHEN
- Calculate variances and percentage changes
- Use CTEs for clean variance decomposition

### PREDICTIVE Queries (What will happen?)
- Include historical trends (multiple years)
- Calculate averages, growth rates
- Use Apr_Forecast scenario for forecasts

### PRESCRIPTIVE Queries (What should we do?)
- Rank by profitability or efficiency metrics
- Include multiple dimensions for drill-down
- Calculate ratios and benchmarks

## EXAMPLE QUERIES:

### Monthly Expenses:
```sql
SELECT 
    y.CalendarYear,
    p.PeriodName,
    p.PeriodNumber,
    SUM(CAST(f.Amount AS DECIMAL(18,2))) AS Amount
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Period p ON f.PeriodKey = p.PeriodKey
JOIN Dim_Year y ON f.YearKey = y.YearKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE a.FinalParentAccountCode = 'General and administrative expenses'
  AND s.ScenarioName = 'Actual'
GROUP BY y.CalendarYear, p.PeriodName, p.PeriodNumber
ORDER BY y.CalendarYear, p.PeriodNumber;
```

### Budget vs Actual Variance:
```sql
SELECT 
    a.FinalParentAccountCode,
    SUM(CASE WHEN s.ScenarioName = 'Actual' THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) AS Actual,
    SUM(CASE WHEN s.ScenarioName = 'OEP_Plan' THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) AS Budget,
    SUM(CASE WHEN s.ScenarioName = 'Actual' THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) -
    SUM(CASE WHEN s.ScenarioName = 'OEP_Plan' THEN CAST(f.Amount AS DECIMAL(18,2)) ELSE 0 END) AS Variance
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Year y ON f.YearKey = y.YearKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE y.CalendarYear = 2025
GROUP BY a.FinalParentAccountCode
ORDER BY ABS(Variance) DESC;
```

### Revenue Summary:
```sql
SELECT 
    a.FinalParentAccountCode,
    SUM(CAST(f.Amount AS DECIMAL(18,2))) AS TotalAmount
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Year y ON f.YearKey = y.YearKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE a.FinalParentAccountCode = 'Revenue'
  AND s.ScenarioName = 'Actual'
  AND y.CalendarYear = 2025
GROUP BY a.FinalParentAccountCode;
```

## CURRENT QUERY CONTEXT:
Analytics Type: {analytics_type}

User Question: {question}

Generate ONLY the SQL query. No explanations, no markdown code blocks, just the raw SQL.
If the question is about crop-specific data (yields, prices, volumes by crop), return a simple financial summary query instead - crop details will come from the knowledge base.
"""


class SQLGenerator:
    """
    Enhanced SQL Generator for CFG Ukraine Financial Analytics.
    
    Features:
    - Analytics-type aware query generation
    - Pre-built templates for common patterns
    - Validation and safety checks
    
    Note: Crop-specific operational data (yields, prices, volumes by crop)
    is NOT available in SQL. That data comes from the agent's knowledge base.
    """
    
    def __init__(self):
        """Initialize the SQL generator with Azure OpenAI client."""
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION
        )
        self.deployment = AZURE_OPENAI_DEPLOYMENT
        self.templates = QUERY_TEMPLATES
    
    def generate_sql(
        self, 
        question: str, 
        context: list = None,
        analytics_type: str = "DESCRIPTIVE"
    ) -> str:
        """
        Generate SQL from a natural language question.
        
        Args:
            question: Natural language question about CFG Ukraine
            context: Optional list of previous conversation turns
            analytics_type: DESCRIPTIVE, DIAGNOSTIC, PREDICTIVE, or PRESCRIPTIVE
            
        Returns:
            SQL query string
        """
        # First, try to match to a template
        template_sql = self._try_template_match(question)
        if template_sql:
            return template_sql
        
        # Otherwise, generate via LLM
        messages = [
            {
                "role": "system",
                "content": "You are an expert SQL generator for Microsoft Fabric. Generate only valid T-SQL. No explanations."
            }
        ]
        
        # Add conversation context if provided
        if context:
            for turn in context[-3:]:
                if isinstance(turn, dict):
                    messages.append({"role": "user", "content": turn.get("user_query", turn.get("question", ""))})
                    if turn.get("sql"):
                        messages.append({"role": "assistant", "content": turn["sql"]})
        
        # Add the current question with full context
        messages.append({
            "role": "user",
            "content": SQL_GENERATION_PROMPT.format(
                schema_info=ENHANCED_SCHEMA_INFO,
                analytics_type=analytics_type,
                question=question
            )
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=1000,
                temperature=0
            )
            
            sql = response.choices[0].message.content.strip()
            
            # Clean up markdown code blocks if present
            sql = self._clean_sql(sql)
            
            # Validate and fix common issues
            sql = self._fix_common_issues(sql)
            
            return sql
            
        except Exception as e:
            raise Exception(f"SQL generation failed: {str(e)}")
    
    def _try_template_match(self, question: str) -> Optional[str]:
        """
        Try to match question to a pre-built template.
        
        Returns SQL from template if match found, None otherwise.
        """
        question_lower = question.lower()
        current_year = 2025
        prior_year = 2024
        
        # Extract year if mentioned
        year_match = re.search(r'20\d{2}', question)
        if year_match:
            current_year = int(year_match.group())
            prior_year = current_year - 1
        
        # Match patterns to templates
        if any(word in question_lower for word in ["budget vs actual", "budget variance", "vs budget"]):
            return self.templates["budget_vs_actual"].format(year=current_year)
        
        if any(word in question_lower for word in ["variance analysis", "explain variance", "why did"]):
            return self.templates["variance_analysis"].format(year=current_year)
        
        if any(word in question_lower for word in ["year over year", "yoy", "compared to last year"]):
            return self.templates["yoy_comparison"].format(year=current_year, prior_year=prior_year)
        
        if any(word in question_lower for word in ["quarterly", "by quarter"]):
            return self.templates["quarterly_summary"].format(year=current_year)
        
        # For crop-specific questions, return financial summary (crop details from knowledge base)
        if any(word in question_lower for word in ["crop", "wheat", "barley", "osr", "maize", "soybean", "sunflower", "yield", "harvest"]):
            # Return a general financial summary - crop specifics come from knowledge base
            return self.templates["financial_summary"].format(year=current_year)
        
        if any(word in question_lower for word in ["all accounts", "account summary", "account categories"]):
            return self.templates["account_summary"]
        
        # Check for specific account categories - map keywords to actual FinalParentAccountCode values
        account_keywords = {
            "g&a": "General and administrative expenses",
            "g & a": "General and administrative expenses",
            "admin": "General and administrative expenses",
            "administrative": "General and administrative expenses",
            "general and admin": "General and administrative expenses",
            "cash": "Cash and cash_equivalents",
            "cash equivalent": "Cash and cash_equivalents",
            "finance charge": "Finance charge",
            "interest": "Finance charge",
            "payables": "Trade and other payables",
            "trade payables": "Trade and other payables",
            "exchange loss": "Exchange loss",
            "fx loss": "Exchange loss",
            "intangible": "Intangible assets, net",
            "equity": "FCCS_Owners Equity",
            "liabilities": "FCCS_Current Liabilities",
            "reserves": "FCCS_Other Reserves",
            "retained earnings": "FCCS_Retained Earnings"
        }
        
        # Check for monthly/trend queries with account filter
        for keyword, account in account_keywords.items():
            if keyword in question_lower:
                if any(word in question_lower for word in ["monthly", "by month", "trend", "expenses", "balance", "show"]):
                    return self.templates["monthly_financials"].format(
                        account_category=account,
                        year=current_year
                    )
        
        return None
    
    def _clean_sql(self, sql: str) -> str:
        """Clean up SQL by removing markdown and extra whitespace."""
        # Remove markdown code blocks
        sql = re.sub(r'```sql\s*', '', sql)
        sql = re.sub(r'```\s*', '', sql)
        
        # Remove leading/trailing whitespace
        sql = sql.strip()
        
        return sql
    
    def _fix_common_issues(self, sql: str) -> str:
        """Fix common SQL generation issues."""
        # Ensure Amount is cast properly
        if "f.Amount" in sql and "CAST(f.Amount" not in sql:
            sql = sql.replace("f.Amount", "CAST(f.Amount AS DECIMAL(18,2))")
        
        # Fix invalid table references - replace with valid fact table
        invalid_tables = [
            ("vw_Crop_Performance", "vw_Fact_Actuals_SALIC_Ukraine"),
            ("vw_Sales_Detail", "vw_Fact_Actuals_SALIC_Ukraine"),
            ("crop_performance", "vw_Fact_Actuals_SALIC_Ukraine"),
        ]
        
        for invalid, valid in invalid_tables:
            if invalid in sql:
                # This query tried to use a non-existent table
                # Return a simple financial summary instead
                return """SELECT 
    a.FinalParentAccountCode,
    SUM(CAST(f.Amount AS DECIMAL(18,2))) AS TotalAmount
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Year y ON f.YearKey = y.YearKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE s.ScenarioName = 'Actual'
  AND y.CalendarYear = 2025
GROUP BY a.FinalParentAccountCode
ORDER BY TotalAmount DESC;"""
        
        return sql
    
    def validate_sql(self, sql: str) -> Dict[str, any]:
        """
        Validate generated SQL for safety and correctness.
        
        Returns:
            dict with 'valid' boolean, 'issues' list, and 'warnings' list
        """
        issues = []
        warnings = []
        
        sql_upper = sql.upper()
        
        # Check for dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER", "CREATE", "EXEC"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper and keyword + " " in sql_upper:
                issues.append(f"Dangerous operation detected: {keyword}")
        
        # Check for non-existent tables
        invalid_tables = ["vw_Crop_Performance", "vw_Sales_Detail", "vw_Crop", "crop_performance", "sales_detail"]
        for table in invalid_tables:
            if table.lower() in sql.lower():
                issues.append(f"Invalid table reference: {table} does not exist. Use vw_Fact_Actuals_SALIC_Ukraine instead.")
        
        # Check for required elements (for financial queries)
        if "vw_Fact_Actuals_SALIC_Ukraine" in sql:
            if "CAST" not in sql_upper and "AMOUNT" in sql_upper:
                warnings.append("Amount should be CAST to DECIMAL for accuracy")
            
            if "JOIN" not in sql_upper:
                warnings.append("Missing dimension joins - results may show keys instead of names")
            
            if "SCENARIONAME" not in sql_upper and "SCENARIOKEY" not in sql_upper:
                warnings.append("No scenario filter - may mix Actual, Budget, and Forecast data")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def explain_sql(self, sql: str) -> str:
        """
        Generate a plain English explanation of what the SQL does.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": """Explain this SQL query in simple business terms for a CFO.
Be concise (2-3 sentences max).
Focus on what data is being retrieved and how it's organized."""
                    },
                    {
                        "role": "user",
                        "content": f"Explain this SQL:\n{sql}"
                    }
                ],
                max_tokens=150,
                temperature=0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Could not explain SQL: {str(e)}"
    
    def get_suggested_queries(self, analytics_type: str) -> List[str]:
        """
        Get suggested queries based on analytics type.
        """
        suggestions = {
            "DESCRIPTIVE": [
                "Show me revenue by crop for 2025",
                "What were G&A expenses by month?",
                "List all account categories with totals"
            ],
            "DIAGNOSTIC": [
                "Why did net income beat budget?",
                "Show budget vs actual variance by account",
                "Compare this year to last year"
            ],
            "PREDICTIVE": [
                "Show historical trend for revenue",
                "What's the forecast for Q4?",
                "Project expenses based on current trend"
            ],
            "PRESCRIPTIVE": [
                "Which crops have highest margin?",
                "Where can we reduce costs?",
                "Rank accounts by variance"
            ]
        }
        
        return suggestions.get(analytics_type, suggestions["DESCRIPTIVE"])


# =============================================================================
# TEST SUITE
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  SQL Generator v2.0 - Test Suite")
    print("=" * 70)
    
    generator = SQLGenerator()
    
    test_cases = [
        ("Show me G&A expenses by month for 2025", "DESCRIPTIVE"),
        ("Why did expenses increase vs budget?", "DIAGNOSTIC"),
        ("What's the budget vs actual variance?", "DIAGNOSTIC"),
        ("Show crop revenue breakdown", "DESCRIPTIVE"),
        ("Compare 2025 to 2024 year over year", "DIAGNOSTIC"),
    ]
    
    for question, analytics_type in test_cases:
        print(f"\n{'='*70}")
        print(f"Question: {question}")
        print(f"Analytics Type: {analytics_type}")
        print("-" * 70)
        
        try:
            sql = generator.generate_sql(question, analytics_type=analytics_type)
            print(f"Generated SQL:\n{sql}")
            
            validation = generator.validate_sql(sql)
            print(f"\nValidation: {'✓ Valid' if validation['valid'] else '✗ Invalid'}")
            if validation['issues']:
                print(f"Issues: {validation['issues']}")
            if validation['warnings']:
                print(f"Warnings: {validation['warnings']}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 70)
    print("  Tests Complete")
    print("=" * 70)