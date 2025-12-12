"""
Response Generator Module - Enhanced Version 2.0
Generates professional financial responses using Value-Driver Tree framework
Optimized for CFG Ukraine agricultural analytics

December 2025
"""
from openai import AzureOpenAI
from typing import Dict, List, Optional, Any
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
)


# =============================================================================
# CFG UKRAINE CONTEXT (Embedded for Response Generation)
# =============================================================================

CFG_UKRAINE_CONTEXT = """
## CFG Ukraine Business Context

CFG Ukraine is SALIC's agricultural subsidiary operating ~180,624 hectares in Ukraine.

### Crop Portfolio (FY2025):
| Crop | Area (ha) | Yield (t/ha) | Price ($/t) |
|------|-----------|--------------|-------------|
| Winter Wheat | 39,573 | 6.78 | $249.85 |
| Winter Barley | 11,527 | 6.22 | $241.55 |
| Winter OSR | 31,500 | 3.22 | $567.60 |
| Maize | 26,457 | 10.34 | $235.51 |
| Soybean | 49,766 | 3.24 | $478.29 |
| Sunflower | 17,312 | 3.24 | $518.75 |

### FY2025 Financial Performance:
- Revenue Forecast: 2,928m SAR (Budget: 1,920m, +52%)
- EBITDA Forecast: 397m SAR (Budget: 383m, +4%)
- Net Income Forecast: 151m SAR (Budget: 97m, +56%)

### Key Price Variances vs Budget:
- OSR: +$85/t (best performer)
- Sunflower: +$114/t
- Wheat: +$16/t
- Maize: -$7/t
- Soybean: -$15/t
- Barley: -$10/t

### Value-Driver Tree Formula:
Gross Margin = Revenue - Cost of Production
- Revenue = Volume × Net Sales Price
- Volume = Crop Area (ha) × Yield (t/ha)
- Cost of Production = Volume × Production Cost per ton
- Production Cost ($/t) = Direct Costs ($/ha) ÷ Yield (t/ha)
"""

# =============================================================================
# SYSTEM PROMPTS BY ANALYTICS TYPE
# =============================================================================

SYSTEM_PROMPT_BASE = """You are a senior financial analyst for CFG Ukraine, SALIC's agricultural subsidiary. 
You provide professional, CFO-ready analysis using the Value-Driver Tree framework.

Your responses should be:
- Executive-level: Clear, concise, and actionable
- Data-driven: Always reference specific numbers
- Properly formatted: Use SAR for SALIC reporting, USD for operational metrics
- Structured: Use the appropriate template for each analytics type
- Insightful: Go beyond the numbers to provide business context

Key conventions:
- Format large numbers with commas (e.g., 1,234,567)
- Use 'm' for millions, 'k' for thousands (e.g., 846m SAR)
- Round percentages to 1 decimal place
- Always show variance as both absolute and percentage
- Reference the Value-Driver Tree when explaining causality

""" + CFG_UKRAINE_CONTEXT


DESCRIPTIVE_SYSTEM_PROMPT = SYSTEM_PROMPT_BASE + """

## Response Template for DESCRIPTIVE Analytics ("What happened?")

Structure your response as:

**[Metric Name]: [Value] [Unit]**

[1-2 sentence summary of what this means]

**Context:**
- vs Budget: [variance amount] ([variance %])
- vs Prior Year: [if available]

**Breakdown:** [if multi-dimensional data]
[Present key components in a clear format]

**Key Observation:** [One insight about the data]
"""


DIAGNOSTIC_SYSTEM_PROMPT = SYSTEM_PROMPT_BASE + """

## Response Template for DIAGNOSTIC Analytics ("Why did it happen?")

Structure your response as:

**Variance Analysis: [Metric] ([Period])**

Total Variance: **[Amount]** ([Percentage]%)

**Driver Decomposition:**

1. **[Largest Driver]:** [±Amount] ([% of total variance])
   → [Root cause explanation using Value-Driver Tree logic]

2. **[Second Driver]:** [±Amount] ([% of total variance])
   → [Root cause explanation]

3. **[Third Driver]:** [±Amount] ([% of total variance])
   → [Root cause explanation]

**Value-Driver Tree Analysis:**
[Explain how the drivers connect: Area → Yield → Volume → Price → Revenue → GM]

**Conclusion:** [2-3 sentence summary of the key takeaway]

Always decompose variances into these effects when applicable:
- Price Effect: Change in selling prices
- Volume Effect: Change in quantity sold
- Yield Effect: Change in tons per hectare
- Cost Effect: Change in production costs
- Mix Effect: Change in crop composition
- FX Effect: Currency translation impact
"""


PREDICTIVE_SYSTEM_PROMPT = SYSTEM_PROMPT_BASE + """

## Response Template for PREDICTIVE Analytics ("What will happen?")

Structure your response as:

**[Metric] Forecast: [Period]**

**Base Case:** [Value]
- P10 (Downside): [Value] — [scenario description]
- P90 (Upside): [Value] — [scenario description]

**Sensitivity Analysis:**

| Driver | Change | Impact on [Metric] |
|--------|--------|-------------------|
| [Driver 1] | ±10% | [±Amount] |
| [Driver 2] | ±10% | [±Amount] |
| [Driver 3] | ±10% | [±Amount] |

**Key Risks:**
1. [Risk with probability and impact]
2. [Risk with probability and impact]

**Key Opportunities:**
1. [Opportunity with probability and upside]

**Assumptions:**
- [List key assumptions underlying the forecast]

When calculating sensitivities, use these approximations:
- Wheat price ±10% → ~$16.5m impact (660k tons volume)
- OSR price ±10% → ~$5.8m impact
- Maize price ±10% → ~$6.4m impact
- Yield ±10% → ~$30m impact across all crops
- FX (USD/UAH) ±10% → ~8% revenue impact
"""


PRESCRIPTIVE_SYSTEM_PROMPT = SYSTEM_PROMPT_BASE + """

## Response Template for PRESCRIPTIVE Analytics ("What should we do?")

Structure your response as:

**Recommendation: [Action Summary in 5-10 words]**

Expected Benefit: **[+Amount]** vs current plan

**Proposed Actions:**

1. **[Action Name]**
   - What: [Specific action]
   - Impact: [Quantified benefit]
   - Timeline: [When to implement]
   - Owner: [Suggested responsibility]

2. **[Action Name]**
   - What: [Specific action]
   - Impact: [Quantified benefit]
   - Timeline: [When to implement]

3. **[Action Name]**
   - What: [Specific action]
   - Impact: [Quantified benefit]
   - Timeline: [When to implement]

**Trade-offs to Consider:**
- [Trade-off 1]
- [Trade-off 2]

**Implementation Priority:**
[High/Medium/Low] priority based on [impact vs effort analysis]

**Risk if No Action:**
[What happens if we maintain status quo]

When recommending crop optimization, consider:
- Current profitability ranking: OSR > Sunflower > Soybean > Wheat > Maize > Barley
- Rotation constraints (max ~20% for OSR)
- Working capital requirements by crop
- Hedging opportunities based on price volatility
"""


class ResponseGenerator:
    """
    Enhanced Response Generator for CFG Ukraine Financial Analytics.
    
    Generates professional, CFO-ready responses using:
    - Value-Driver Tree framework
    - Structured templates by analytics type
    - CFG Ukraine-specific context and benchmarks
    """
    
    def __init__(self):
        """Initialize the response generator with Azure OpenAI client."""
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
        sql: str = None,
        vdt_context: str = None
    ) -> str:
        """
        Generate a descriptive response explaining what the data shows.
        
        Args:
            question: User's original question
            data: Query results with columns, rows, row_count
            sql: SQL query used (optional, for context)
            vdt_context: Value-driver tree analysis results (optional)
        
        Returns:
            Formatted descriptive response
        """
        prompt = f"""Answer this DESCRIPTIVE analytics question about CFG Ukraine.

**User Question:** {question}

**Data Retrieved:**
- Columns: {data.get('columns', [])}
- Row Count: {data.get('row_count', 0)}
- Data: {self._format_data_for_prompt(data)}

{f"**Value-Driver Tree Context:** {vdt_context}" if vdt_context else ""}

Provide a clear, executive-level response following the DESCRIPTIVE template.
Focus on answering the question directly with specific numbers.
If the data is empty or insufficient, acknowledge this and provide what context you can from the baseline data.
"""
        
        return self._generate_response(prompt, DESCRIPTIVE_SYSTEM_PROMPT)
    
    def generate_diagnostic_response(
        self, 
        question: str, 
        data: dict, 
        sql: str = None,
        vdt_context: str = None
    ) -> str:
        """
        Generate a diagnostic response explaining why something happened.
        
        Uses variance decomposition framework to break down drivers.
        """
        prompt = f"""Answer this DIAGNOSTIC analytics question about CFG Ukraine.

**User Question:** {question}

**Data Retrieved:**
- Columns: {data.get('columns', [])}
- Row Count: {data.get('row_count', 0)}
- Data: {self._format_data_for_prompt(data)}

{f"**Value-Driver Tree Analysis:** {vdt_context}" if vdt_context else ""}

Provide a variance analysis following the DIAGNOSTIC template.
Decompose the variance into driver effects (Price, Volume, Yield, Cost, Mix, FX).
Rank drivers by magnitude and explain root causes using Value-Driver Tree logic.
If full decomposition isn't possible with available data, explain what's visible and what additional data would help.
"""
        
        return self._generate_response(prompt, DIAGNOSTIC_SYSTEM_PROMPT)
    
    def generate_predictive_response(
        self, 
        question: str, 
        data: dict, 
        sql: str = None,
        vdt_context: str = None
    ) -> str:
        """
        Generate a predictive response with forecasts and scenarios.
        
        Includes sensitivity analysis and risk/opportunity assessment.
        """
        prompt = f"""Answer this PREDICTIVE analytics question about CFG Ukraine.

**User Question:** {question}

**Historical/Current Data:**
- Columns: {data.get('columns', [])}
- Row Count: {data.get('row_count', 0)}
- Data: {self._format_data_for_prompt(data)}

{f"**Sensitivity Analysis:** {vdt_context}" if vdt_context else ""}

Provide a forward-looking response following the PREDICTIVE template.
Include base case, P10/P90 scenarios, and sensitivity analysis.
Use the sensitivity factors provided in the context for quantification.
Clearly state assumptions and highlight key risks and opportunities.
"""
        
        return self._generate_response(prompt, PREDICTIVE_SYSTEM_PROMPT)
    
    def generate_prescriptive_response(
        self, 
        question: str, 
        data: dict, 
        sql: str = None,
        vdt_context: str = None
    ) -> str:
        """
        Generate a prescriptive response with actionable recommendations.
        
        Includes quantified benefits, trade-offs, and implementation guidance.
        """
        prompt = f"""Answer this PRESCRIPTIVE analytics question about CFG Ukraine.

**User Question:** {question}

**Current Data Context:**
- Columns: {data.get('columns', [])}
- Row Count: {data.get('row_count', 0)}
- Data: {self._format_data_for_prompt(data)}

{f"**Optimization Analysis:** {vdt_context}" if vdt_context else ""}

Provide actionable recommendations following the PRESCRIPTIVE template.
Quantify expected benefits for each recommendation.
Consider crop profitability rankings, rotation constraints, and risk factors.
Prioritize by impact and feasibility.
Include trade-offs and implementation guidance.
"""
        
        return self._generate_response(prompt, PRESCRIPTIVE_SYSTEM_PROMPT)
    
    def _format_data_for_prompt(self, data: dict, max_rows: int = 20) -> str:
        """
        Format data dictionary for inclusion in prompt.
        Limits rows to avoid token overflow.
        """
        rows = data.get('rows', [])
        if not rows:
            return "No data rows returned"
        
        # Limit rows
        if len(rows) > max_rows:
            rows = rows[:max_rows]
            truncated = True
        else:
            truncated = False
        
        # Format as simple table
        formatted = str(rows)
        
        if truncated:
            formatted += f"\n... (showing first {max_rows} of {data.get('row_count', 0)} rows)"
        
        return formatted
    
    def _generate_response(self, prompt: str, system_prompt: str) -> str:
        """
        Internal method to call Azure OpenAI and generate response.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I apologize, but I encountered an error generating the response: {str(e)}"
    
    def generate_error_response(self, question: str, error: str) -> str:
        """
        Generate a helpful, professional error response.
        """
        return f"""I encountered an issue while processing your question.

**Your Question:** {question}

**Issue:** {error}

**What I Can Help With:**

| Analytics Type | Example Questions |
|---------------|-------------------|
| **Descriptive** | "What was revenue in Q2?", "Show crop areas" |
| **Diagnostic** | "Why did GM beat budget?", "Explain the yield variance" |
| **Predictive** | "What if wheat prices drop 10%?", "Forecast Q4 EBITDA" |
| **Prescriptive** | "How to optimize crop mix?", "Where to reduce costs?" |

**Available Data:**
- Crops: Wheat, Barley, OSR, Maize, Soybean, Sunflower
- Metrics: Revenue, EBITDA, Net Income, Gross Margin, Yields, Prices
- Periods: FY2025 (Budget, Actual YTD, Forecast)

Would you like to rephrase your question?"""

    def generate_followup_suggestions(
        self, 
        question: str, 
        category: str, 
        data: dict,
        vdt_result: dict = None
    ) -> List[str]:
        """
        Generate intelligent follow-up questions based on analytics type and results.
        """
        # Define category-specific follow-ups
        category_suggestions = {
            "DESCRIPTIVE": [
                "How does this compare to budget?",
                "Can you break this down by crop?",
                "What's the trend over the past 3 years?"
            ],
            "DIAGNOSTIC": [
                "What actions can we take to address this?",
                "How sensitive are we to price changes?",
                "Which crop contributed most to this variance?"
            ],
            "PREDICTIVE": [
                "What's the worst-case scenario?",
                "How should we hedge against this risk?",
                "What if we also consider yield variability?"
            ],
            "PRESCRIPTIVE": [
                "What are the trade-offs of this recommendation?",
                "What's the implementation timeline?",
                "How does this affect our risk profile?"
            ]
        }
        
        # Start with category defaults
        suggestions = category_suggestions.get(category, category_suggestions["DESCRIPTIVE"]).copy()
        
        # Add context-specific suggestions based on VDT results
        if vdt_result:
            vdt_type = vdt_result.get("type", "")
            
            if vdt_type == "variance_decomposition":
                suggestions.insert(0, "Break down the price effect by individual crop")
            elif vdt_type == "sensitivity_analysis":
                suggestions.insert(0, "Show combined impact of multiple drivers changing")
            elif vdt_type == "optimization_ranking":
                suggestions.insert(0, "What are the rotation constraints for expanding OSR?")
            elif vdt_type == "gross_margin_calculation":
                suggestions.insert(0, "How does this GM compare to industry benchmarks?")
        
        # Try to generate custom suggestions via LLM
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": """Generate 3 specific follow-up questions for CFG Ukraine financial analysis.
Questions should be:
- Directly related to the conversation
- Progressively deeper (descriptive → diagnostic → predictive → prescriptive)
- Actionable and specific to agricultural business

Return only the questions, one per line, no numbering."""
                    },
                    {
                        "role": "user",
                        "content": f"""Original {category.lower()} question: "{question}"
Data context: {len(data.get('rows', []))} records about {data.get('columns', [])}

Generate 3 natural follow-up questions a CFO would ask next."""
                    }
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            llm_suggestions = response.choices[0].message.content.strip().split('\n')
            llm_suggestions = [s.strip().lstrip('0123456789.-) ') for s in llm_suggestions if s.strip()]
            
            # Blend LLM suggestions with defaults
            if llm_suggestions:
                suggestions = llm_suggestions[:2] + suggestions[:1]
            
        except Exception:
            pass  # Fall back to default suggestions
        
        return suggestions[:3]
    
    def generate_summary_response(
        self,
        question: str,
        classification: str,
        data: dict,
        vdt_result: dict = None
    ) -> str:
        """
        Generate a complete response by routing to appropriate method.
        
        This is a convenience method that routes based on classification.
        """
        # Build VDT context string if available
        vdt_context = None
        if vdt_result:
            vdt_context = self._format_vdt_context(vdt_result)
        
        # Route to appropriate generator
        if classification == "DESCRIPTIVE":
            return self.generate_descriptive_response(question, data, vdt_context=vdt_context)
        elif classification == "DIAGNOSTIC":
            return self.generate_diagnostic_response(question, data, vdt_context=vdt_context)
        elif classification == "PREDICTIVE":
            return self.generate_predictive_response(question, data, vdt_context=vdt_context)
        elif classification == "PRESCRIPTIVE":
            return self.generate_prescriptive_response(question, data, vdt_context=vdt_context)
        else:
            return self.generate_descriptive_response(question, data, vdt_context=vdt_context)
    
    def _format_vdt_context(self, vdt_result: dict) -> str:
        """
        Format Value-Driver Tree result for inclusion in prompt.
        """
        if not vdt_result:
            return ""
        
        vdt_type = vdt_result.get("type", "")
        result = vdt_result.get("result", {})
        
        if vdt_type == "variance_decomposition":
            drivers = result.get("drivers", {})
            return f"""
Variance Decomposition Results:
- Total Variance: {result.get('total_variance', 0):,.0f} SAR ({result.get('variance_pct', 0):.1f}%)
- Price Effect: {drivers.get('price_effect', {}).get('amount', 0):,.0f} SAR
- Cost Effect: {drivers.get('cost_effect', {}).get('amount', 0):,.0f} SAR
- Yield Effect: {drivers.get('yield_effect', {}).get('amount', 0):,.0f} SAR
- Volume Effect: {drivers.get('volume_effect', {}).get('amount', 0):,.0f} SAR
"""
        
        elif vdt_type == "sensitivity_analysis":
            if "error" in result:
                return f"Sensitivity analysis error: {result['error']}"
            return f"""
Sensitivity Analysis Results:
- Driver: {result.get('driver', 'Unknown')}
- Change: {result.get('change_pct', 0)}%
- Impact: {result.get('impact_amount', 0):.1f} {result.get('impact_unit', '')}
- Base Volume: {result.get('base_volume', 'N/A')}
"""
        
        elif vdt_type == "optimization_ranking":
            rankings = result[:5] if isinstance(result, list) else []
            ranking_text = "\n".join([
                f"  {i+1}. {r['crop']}: ${r['gm_per_ha']:.0f}/ha, {r['gm_percent']:.1f}% margin"
                for i, r in enumerate(rankings)
            ])
            return f"""
Crop Profitability Ranking (by GM/ha):
{ranking_text}
"""
        
        elif vdt_type == "gross_margin_calculation":
            if result.get("crop") == "all":
                return f"""
Total Portfolio Gross Margin:
- Total Area: {result.get('total_area_ha', 0):,} ha
- Total GM: ${result.get('total_gross_margin_usd', 0):,.0f}
- GM %: {result.get('gm_percent', 0):.1f}%
- GM per ha: ${result.get('gm_per_ha', 0):.0f}/ha
"""
            else:
                return f"""
{result.get('crop', 'Crop')} Gross Margin Analysis:
- Area: {result.get('area_ha', 0):,} ha
- Yield: {result.get('yield_t_ha', 0):.2f} t/ha
- Volume: {result.get('volume_tons', 0):,.0f} tons
- Price: ${result.get('price_usd_t', 0):.2f}/t
- Revenue: ${result.get('revenue_usd', 0):,.0f}
- GM: ${result.get('gross_margin_usd', 0):,.0f}
- GM %: {result.get('gm_percent', 0):.1f}%
"""
        
        return ""


# =============================================================================
# TEST SUITE
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  Response Generator v2.0 - Test Suite")
    print("=" * 70)
    
    generator = ResponseGenerator()
    
    # Sample data for testing
    sample_data = {
        "columns": ["crop_type", "revenue_sar", "volume_tons", "price_usd"],
        "rows": [
            {"crop_type": "Winter Wheat", "revenue_sar": 250000000, "volume_tons": 268396, "price_usd": 249.85},
            {"crop_type": "Winter OSR", "revenue_sar": 216000000, "volume_tons": 101565, "price_usd": 567.60},
            {"crop_type": "Maize", "revenue_sar": 241000000, "volume_tons": 273665, "price_usd": 235.51},
            {"crop_type": "Soybean", "revenue_sar": 289000000, "volume_tons": 161445, "price_usd": 478.29},
        ],
        "row_count": 4
    }
    
    # Test 1: Descriptive
    print("\n" + "-" * 70)
    print("TEST 1: DESCRIPTIVE Response")
    print("-" * 70)
    response = generator.generate_descriptive_response(
        "What is the revenue breakdown by crop for FY2025?",
        sample_data
    )
    print(response)
    
    # Test 2: Diagnostic
    print("\n" + "-" * 70)
    print("TEST 2: DIAGNOSTIC Response")
    print("-" * 70)
    response = generator.generate_diagnostic_response(
        "Why did net income beat budget by 56%?",
        sample_data,
        vdt_context="Price Effect: +35m SAR (70%), Cost Effect: +20m SAR (40%), Volume Effect: -5m SAR (-10%)"
    )
    print(response)
    
    # Test 3: Predictive
    print("\n" + "-" * 70)
    print("TEST 3: PREDICTIVE Response")
    print("-" * 70)
    response = generator.generate_predictive_response(
        "What if wheat prices drop by 15%?",
        sample_data,
        vdt_context="Sensitivity: Wheat price -15% → -$24.8m USD impact on revenue"
    )
    print(response)
    
    # Test 4: Prescriptive
    print("\n" + "-" * 70)
    print("TEST 4: PRESCRIPTIVE Response")
    print("-" * 70)
    response = generator.generate_prescriptive_response(
        "How should we optimize the crop mix for next season?",
        sample_data,
        vdt_context="Ranking: 1. OSR ($320/ha), 2. Sunflower ($285/ha), 3. Soybean ($240/ha)"
    )
    print(response)
    
    print("\n" + "=" * 70)
    print("  Tests Complete")
    print("=" * 70)
