"""
Query Classifier Module
Classifies user queries into: Descriptive, Diagnostic, Predictive, Prescriptive
"""
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
)

CLASSIFICATION_PROMPT = """You are a financial analytics query classifier. Analyze the user's question and classify it into exactly ONE of these four categories:

1. **DESCRIPTIVE** - "What happened?" questions
   - Historical data, trends, summaries, aggregations
   - Examples: "Show G&A expenses for 2024", "What was total cash last quarter?", "List monthly expenses"

2. **DIAGNOSTIC** - "Why did it happen?" questions  
   - Root cause analysis, variance explanations, comparisons to understand changes
   - Examples: "Why did expenses increase in Q4?", "What caused the cash decrease?", "Explain the variance"

3. **PREDICTIVE** - "What will happen?" questions
   - Forecasts, projections, future estimates, trends extrapolation
   - Examples: "Forecast expenses for next quarter", "What will cash position be in 6 months?", "Project 2025 G&A"

4. **PRESCRIPTIVE** - "What should we do?" questions
   - Recommendations, optimizations, action suggestions, advice
   - Examples: "How can we reduce G&A expenses?", "What should we do to improve cash flow?", "Recommend cost savings"

User Query: {query}

Respond with ONLY the category name in uppercase (DESCRIPTIVE, DIAGNOSTIC, PREDICTIVE, or PRESCRIPTIVE).
"""


class QueryClassifier:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION
        )
        self.deployment = AZURE_OPENAI_DEPLOYMENT

    def classify(self, query: str) -> str:
        """
        Classify a user query into one of four categories.
        
        Args:
            query: The user's natural language question
            
        Returns:
            One of: DESCRIPTIVE, DIAGNOSTIC, PREDICTIVE, PRESCRIPTIVE
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a query classifier. Respond with only the category name."
                    },
                    {
                        "role": "user",
                        "content": CLASSIFICATION_PROMPT.format(query=query)
                    }
                ],
                max_tokens=20,
                temperature=0
            )
            
            classification = response.choices[0].message.content.strip().upper()
            
            # Validate the classification
            valid_categories = ["DESCRIPTIVE", "DIAGNOSTIC", "PREDICTIVE", "PRESCRIPTIVE"]
            if classification not in valid_categories:
                # Default to DESCRIPTIVE if unclear
                return "DESCRIPTIVE"
            
            return classification
            
        except Exception as e:
            print(f"Classification error: {e}")
            return "DESCRIPTIVE"  # Default fallback

    def classify_with_confidence(self, query: str) -> dict:
        """
        Classify a query and provide reasoning.
        
        Returns:
            dict with 'category', 'confidence', and 'reasoning'
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a query classifier. Analyze the query and respond in this exact JSON format:
{
    "category": "DESCRIPTIVE|DIAGNOSTIC|PREDICTIVE|PRESCRIPTIVE",
    "confidence": "HIGH|MEDIUM|LOW",
    "reasoning": "Brief explanation of why this category"
}"""
                    },
                    {
                        "role": "user",
                        "content": CLASSIFICATION_PROMPT.format(query=query)
                    }
                ],
                max_tokens=150,
                temperature=0
            )
            
            import json
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            return {
                "category": "DESCRIPTIVE",
                "confidence": "LOW",
                "reasoning": f"Error during classification: {str(e)}"
            }


# Test the classifier
if __name__ == "__main__":
    classifier = QueryClassifier()
    
    test_queries = [
        "Show me G&A expenses for Q4 2024",
        "Why did cash decrease last month?",
        "What will expenses be next quarter?",
        "How can we reduce administrative costs?"
    ]
    
    for query in test_queries:
        result = classifier.classify(query)
        print(f"Query: {query}")
        print(f"Category: {result}\n")
