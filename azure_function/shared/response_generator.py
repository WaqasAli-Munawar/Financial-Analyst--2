"""
Response Generator Module
Generates natural language responses from SQL query results
"""
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
)

class ResponseGenerator:
    """
    Generates natural language responses based on query results and category.
    """
    
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION
        )
        self.deployment = AZURE_OPENAI_DEPLOYMENT
    
    def generate_descriptive_response(
        self, 
        question: str, 
        data: dict, 
        sql: str = None
    ) -> str:
        """
        Generate a descriptive response explaining what the data shows.
        """
        prompt = f"""You are a financial analyst for CFG Ukraine. The user asked a descriptive question about financial data.

User Question: {question}

Data Retrieved:
Columns: {data.get('columns', [])}
Rows: {data.get('rows', [])}
Total Records: {data.get('row_count', 0)}

Provide a clear, professional response that:
1. Directly answers the user's question
2. Summarizes the key numbers and trends
3. Highlights any notable patterns (e.g., highest/lowest values, trends)
4. Uses proper number formatting (e.g., $1,234,567.89)
5. Is concise but complete

If the data is empty, explain that no data was found for the query criteria.
"""
        
        return self._generate_response(prompt)
    
    def generate_diagnostic_response(
        self, 
        question: str, 
        data: dict, 
        sql: str = None
    ) -> str:
        """
        Generate a diagnostic response explaining why something happened.
        """
        prompt = f"""You are a financial analyst for CFG Ukraine. The user asked a diagnostic question to understand why something happened.

User Question: {question}

Data Retrieved:
Columns: {data.get('columns', [])}
Rows: {data.get('rows', [])}
Total Records: {data.get('row_count', 0)}

Provide an analytical response that:
1. Identifies the key drivers or factors visible in the data
2. Compares relevant periods/categories to identify changes
3. Calculates variances or percentage changes where relevant
4. Suggests possible reasons based on the data patterns
5. Notes any limitations (if full diagnostic requires additional data)

If the data doesn't fully explain the 'why', acknowledge this and suggest what additional analysis might help.
"""
        
        return self._generate_response(prompt)
    
    def generate_predictive_response(
        self, 
        question: str, 
        data: dict, 
        sql: str = None
    ) -> str:
        """
        Generate a predictive response with forecasts and projections.
        """
        prompt = f"""You are a financial analyst for CFG Ukraine. The user asked a predictive question about future outcomes.

User Question: {question}

Historical Data Retrieved:
Columns: {data.get('columns', [])}
Rows: {data.get('rows', [])}
Total Records: {data.get('row_count', 0)}

Provide a forward-looking response that:
1. Analyzes the historical trend from the data
2. Projects future values based on the trend (simple extrapolation)
3. Clearly states assumptions made for the projection
4. Provides a range or scenarios (optimistic, base, pessimistic) if appropriate
5. Adds appropriate caveats about forecast uncertainty

Note: This is a simplified forecast based on available data. For more sophisticated predictions, recommend proper forecasting models.
"""
        
        return self._generate_response(prompt)
    
    def generate_prescriptive_response(
        self, 
        question: str, 
        data: dict, 
        sql: str = None
    ) -> str:
        """
        Generate a prescriptive response with recommendations.
        """
        prompt = f"""You are a financial analyst and advisor for CFG Ukraine. The user asked for recommendations or advice.

User Question: {question}

Current Data Context:
Columns: {data.get('columns', [])}
Rows: {data.get('rows', [])}
Total Records: {data.get('row_count', 0)}

Provide actionable recommendations that:
1. Are grounded in the data provided
2. Are specific and actionable (not generic advice)
3. Consider both quick wins and strategic improvements
4. Include potential impact or benefits where estimable
5. Prioritize recommendations by feasibility/impact

Structure your response with clear, numbered recommendations. Be professional but practical.
"""
        
        return self._generate_response(prompt)
    
    def _generate_response(self, prompt: str) -> str:
        """
        Internal method to call Azure OpenAI and generate response.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional financial analyst assistant for CFG Ukraine. 
Your responses should be:
- Clear and professional
- Data-driven and accurate
- Properly formatted with numbers
- Concise but thorough
- In a conversational but professional tone

Use bullet points sparingly - prefer natural paragraphs for explanations.
Format currency values properly (e.g., $1,234.56 or SAR 1,234.56).
Round percentages to 1-2 decimal places."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I apologize, but I encountered an error generating the response: {str(e)}"
    
    def generate_error_response(self, question: str, error: str) -> str:
        """
        Generate a helpful response when an error occurs.
        """
        return f"""I apologize, but I encountered an issue while processing your question:

**Your Question:** {question}

**Issue:** {error}

This might be because:
- The specific data you're asking about isn't available in the CFG Ukraine dataset
- The query requires data that doesn't exist for the specified time period
- There was a technical issue connecting to the data warehouse

**Suggestions:**
- Try asking about available categories: G&A expenses, Cash, Trade payables, Finance charges
- Specify time periods within 2024 (Q3-Q4 data is available)
- Rephrase your question to be more specific

Would you like me to help you reformulate your question?"""

    def generate_followup_suggestions(self, question: str, category: str, data: dict) -> list:
        """
        Generate suggested follow-up questions based on the current query.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "Generate 3 brief follow-up questions. Return only the questions, one per line."
                    },
                    {
                        "role": "user",
                        "content": f"""Based on this {category.lower()} question about CFG Ukraine financials: "{question}"
                        
And this data summary: {len(data.get('rows', []))} records about {data.get('columns', [])}

Generate 3 natural follow-up questions the user might want to ask next."""
                    }
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip().lstrip('0123456789.-) ') for s in suggestions if s.strip()][:3]
            
        except Exception:
            return [
                "Can you break this down by quarter?",
                "How does this compare to last year?",
                "What's driving these numbers?"
            ]


# Test the response generator
if __name__ == "__main__":
    generator = ResponseGenerator()
    
    sample_data = {
        "columns": ["CalendarYear", "PeriodName", "FiscalQuarter", "Amount"],
        "rows": [
            {"CalendarYear": 2024, "PeriodName": "Sep", "FiscalQuarter": "Q3", "Amount": 218927.84},
            {"CalendarYear": 2024, "PeriodName": "Oct", "FiscalQuarter": "Q4", "Amount": 9322.16},
            {"CalendarYear": 2024, "PeriodName": "Nov", "FiscalQuarter": "Q4", "Amount": 9154.40},
            {"CalendarYear": 2024, "PeriodName": "Dec", "FiscalQuarter": "Q4", "Amount": -891.92}
        ],
        "row_count": 4
    }
    
    question = "What were the G&A expenses for CFG Ukraine in 2024?"
    
    print("Testing Descriptive Response:")
    print("-" * 50)
    response = generator.generate_descriptive_response(question, sample_data)
    print(response)
