"""
SQL Generator Module
Converts natural language queries to SQL for Microsoft Fabric
"""
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    SCHEMA_INFO,
    AVAILABLE_ACCOUNTS
)

SQL_GENERATION_PROMPT = """You are an expert SQL analyst for Microsoft Fabric Data Warehouse. Generate SQL queries for CFG Ukraine financial data.

{schema_info}

## RULES:
1. ALWAYS use table aliases (f for fact, a for account, p for period, y for year, s for scenario)
2. ALWAYS CAST Amount to DECIMAL: SUM(CAST(f.Amount AS DECIMAL(18,2))) AS Amount
3. ALWAYS join the necessary dimension tables to get readable names
4. ALWAYS filter by s.ScenarioName = 'Actual' unless specifically asked for forecast/budget
5. Use PeriodNumber in ORDER BY for correct month ordering
6. Include PeriodNumber in GROUP BY if you use it in ORDER BY
7. Use FinalParentAccountCode for account filtering (not AccountCode)

## EXAMPLE QUERIES:

### Monthly G&A Expenses:
```sql
SELECT 
    y.CalendarYear,
    p.PeriodName,
    p.FiscalQuarter,
    p.PeriodNumber,
    a.FinalParentAccountCode,
    SUM(CAST(f.Amount AS DECIMAL(18,2))) AS Amount
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Period p ON f.PeriodKey = p.PeriodKey
JOIN Dim_Year y ON f.YearKey = y.YearKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE a.FinalParentAccountCode = 'General and administrative expenses'
  AND s.ScenarioName = 'Actual'
GROUP BY y.CalendarYear, p.PeriodName, p.FiscalQuarter, p.PeriodNumber, a.FinalParentAccountCode
ORDER BY y.CalendarYear, p.PeriodNumber;
```

### Quarterly Summary:
```sql
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
GROUP BY y.CalendarYear, p.FiscalQuarter, a.FinalParentAccountCode
ORDER BY y.CalendarYear, p.FiscalQuarter;
```

### All Account Categories Summary:
```sql
SELECT 
    a.FinalParentAccountCode,
    SUM(CAST(f.Amount AS DECIMAL(18,2))) AS TotalAmount
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN Dim_Account a ON f.AccountKey = a.AccountKey
JOIN Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
WHERE s.ScenarioName = 'Actual'
GROUP BY a.FinalParentAccountCode
ORDER BY TotalAmount DESC;
```

User Question: {question}

Generate ONLY the SQL query. No explanations, no markdown code blocks, just the raw SQL.
"""


class SQLGenerator:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION
        )
        self.deployment = AZURE_OPENAI_DEPLOYMENT

    def generate_sql(self, question: str, context: list = None) -> str:
        """
        Generate SQL from a natural language question.
        
        Args:
            question: Natural language question about CFG Ukraine financials
            context: Optional list of previous conversation turns
            
        Returns:
            SQL query string
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert SQL generator. Generate only valid T-SQL for Microsoft Fabric. No explanations."
            }
        ]
        
        # Add conversation context if provided
        if context:
            for turn in context[-3:]:  # Last 3 turns for context
                messages.append({"role": "user", "content": turn.get("question", "")})
                if turn.get("sql"):
                    messages.append({"role": "assistant", "content": turn["sql"]})
        
        # Add the current question
        messages.append({
            "role": "user",
            "content": SQL_GENERATION_PROMPT.format(
                schema_info=SCHEMA_INFO,
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
            
            # Clean up the SQL if it has markdown code blocks
            sql = sql.replace("```sql", "").replace("```", "").strip()
            
            return sql
            
        except Exception as e:
            raise Exception(f"SQL generation failed: {str(e)}")

    def validate_sql(self, sql: str) -> dict:
        """
        Basic validation of generated SQL.
        
        Returns:
            dict with 'valid' boolean and 'issues' list
        """
        issues = []
        
        # Check for required elements
        if "vw_Fact_Actuals_SALIC_Ukraine" not in sql:
            issues.append("Missing main fact view")
        
        if "CAST" not in sql and "Amount" in sql:
            issues.append("Amount should be CAST to DECIMAL")
        
        if "JOIN" not in sql:
            issues.append("Missing dimension joins - results will show keys not names")
        
        # Check for dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER", "CREATE"]
        for keyword in dangerous_keywords:
            if keyword in sql.upper():
                issues.append(f"Dangerous operation detected: {keyword}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
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
                        "content": "Explain this SQL query in simple business terms. Be concise."
                    },
                    {
                        "role": "user",
                        "content": f"Explain this SQL:\n{sql}"
                    }
                ],
                max_tokens=200,
                temperature=0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Could not explain SQL: {str(e)}"


# Test the SQL generator
if __name__ == "__main__":
    generator = SQLGenerator()
    
    test_questions = [
        "Show me G&A expenses by month for 2024",
        "What is the total cash position?",
        "Compare Q3 and Q4 expenses"
    ]
    
    for question in test_questions:
        print(f"Question: {question}")
        print("-" * 50)
        sql = generator.generate_sql(question)
        print(f"SQL:\n{sql}")
        print(f"\nValidation: {generator.validate_sql(sql)}")
        print("=" * 70 + "\n")
