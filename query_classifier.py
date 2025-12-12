"""
Query Classifier Module - Enhanced Version 2.0
Classifies user queries into: Descriptive, Diagnostic, Predictive, Prescriptive

Uses hybrid approach:
1. Rule-based pre-classification for clear patterns
2. LLM fallback for ambiguous queries

December 2025
"""
from openai import AzureOpenAI
from typing import Dict, Tuple
import re
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
)


# =============================================================================
# SIGNAL WORDS FOR RULE-BASED CLASSIFICATION
# =============================================================================

SIGNAL_PATTERNS = {
    "DESCRIPTIVE": {
        "strong": [
            r"\bwhat (is|are|was|were)\b",
            r"\bshow (me|us)?\b",
            r"\blist\b",
            r"\bdisplay\b",
            r"\btell me\b",
            r"\bhow much\b",
            r"\bhow many\b",
            r"\bwhat('s| is) the (total|current|latest)\b",
            r"\bsummar(y|ize)\b",
            r"\bbreakdown\b",
            r"\bby (month|quarter|year|crop)\b",
            r"\bfor (20\d{2}|FY\d{2}|Q[1-4])\b",
        ],
        "weak": [
            r"\btrend\b",
            r"\bhistor(y|ical)\b",
            r"\bdata\b",
            r"\bnumbers\b",
        ]
    },
    
    "DIAGNOSTIC": {
        "strong": [
            r"\bwhy did\b",
            r"\bwhy (is|are|was|were)\b",
            r"\bexplain\b",
            r"\bwhat (caused|drove|contributed)\b",
            r"\broot cause\b",
            r"\bvariance\b",
            r"\bvs\.? (budget|plan|forecast|last year)\b",
            r"\bcompare(d)? to\b",
            r"\bdifference between\b",
            r"\bbeat(en)? budget\b",
            r"\bmiss(ed)? (budget|target)\b",
            r"\banalyz(e|sis)\b",
            r"\bwhat happened\b",
        ],
        "weak": [
            r"\bchange\b",
            r"\bincrease\b",
            r"\bdecrease\b",
            r"\bup\b",
            r"\bdown\b",
        ]
    },
    
    "PREDICTIVE": {
        "strong": [
            r"\bwhat if\b",
            r"\bif .+ (drop|rise|increase|decrease|change)\b",
            r"\bforecast\b",
            r"\bpredict(ion)?\b",
            r"\bproject(ion|ed)?\b",
            r"\bexpect(ed)?\b",
            r"\bestimate\b",
            r"\bwill (be|happen)\b",
            r"\bnext (month|quarter|year)\b",
            r"\bfuture\b",
            r"\bscenario\b",
            r"\bsensitivity\b",
            r"\bimpact of\b",
            r"\b(drop|rise|fall|increase|decrease) by \d+%\b",
        ],
        "weak": [
            r"\btrend\b",
            r"\boutlook\b",
            r"\bgoing forward\b",
        ]
    },
    
    "PRESCRIPTIVE": {
        "strong": [
            r"\bhow (should|can|do) we\b",
            r"\bwhat should (we|I)\b",
            r"\brecommend\b",
            r"\bsuggest\b",
            r"\boptimiz(e|ation)\b",
            r"\bimprov(e|ement)\b",
            r"\breduce (cost|expense)\b",
            r"\bincrease (revenue|margin|profit)\b",
            r"\bbest (way|approach|strategy)\b",
            r"\baction(s)?\b",
            r"\bstrateg(y|ies)\b",
            r"\bwhere (to|can we)\b",
            r"\badvice\b",
        ],
        "weak": [
            r"\bshould\b",
            r"\bcould\b",
            r"\boption(s)?\b",
        ]
    }
}

# Negative patterns that override classifications
OVERRIDE_PATTERNS = {
    # "What is X" questions are DESCRIPTIVE even if they mention future years
    "DESCRIPTIVE_OVERRIDE": [
        r"^what (is|are|was|were) .*(revenue|expense|cost|margin|income|ebitda)",
    ],
    # "What if" is always PREDICTIVE
    "PREDICTIVE_OVERRIDE": [
        r"\bwhat if\b",
        r"\bif .+ (drop|rise|increase|decrease|change)s? by",
    ]
}


# =============================================================================
# LLM PROMPT
# =============================================================================

CLASSIFICATION_PROMPT = """You are a financial analytics query classifier for CFG Ukraine agricultural operations.

Classify the query into EXACTLY ONE category:

## DESCRIPTIVE - "What happened?" 
Questions asking for facts, data, summaries, or current/historical values.
- "What is the revenue for 2025?"
- "Show me G&A expenses by month"
- "What are the crop areas?"
- "List all account categories"

## DIAGNOSTIC - "Why did it happen?"
Questions seeking to explain causes, variances, or comparisons.
- "Why did net income beat budget?"
- "What drove the revenue increase?"
- "Explain the variance vs last year"
- "Compare actual to budget"

## PREDICTIVE - "What will happen?"
Questions about future outcomes, scenarios, or sensitivities.
- "What if wheat prices drop 15%?"
- "Forecast next quarter EBITDA"
- "What's the impact of yield changes?"
- "Project revenue under drought scenario"

## PRESCRIPTIVE - "What should we do?"
Questions seeking recommendations, optimizations, or actions.
- "How should we optimize crop mix?"
- "Where can we reduce costs?"
- "What actions to improve margin?"
- "Recommend hedging strategy"

CRITICAL RULES:
1. "What is/are/was/were [metric]?" → DESCRIPTIVE (asking for a value)
2. "Why did [something happen]?" → DIAGNOSTIC (asking for explanation)
3. "What if [scenario]?" → PREDICTIVE (asking about hypothetical)
4. "How should/can we [action]?" → PRESCRIPTIVE (asking for advice)

Query: {query}

Respond with ONLY one word: DESCRIPTIVE, DIAGNOSTIC, PREDICTIVE, or PRESCRIPTIVE"""


class QueryClassifier:
    """
    Enhanced Query Classifier using hybrid rule-based and LLM approach.
    
    Classification priority:
    1. Override patterns (highest confidence signals)
    2. Strong signal patterns (clear indicators)
    3. LLM classification (for ambiguous cases)
    4. Weak signal patterns (tiebreaker)
    5. Default to DESCRIPTIVE
    """
    
    def __init__(self):
        """Initialize the classifier with Azure OpenAI client."""
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION
        )
        self.deployment = AZURE_OPENAI_DEPLOYMENT
        self.signal_patterns = SIGNAL_PATTERNS
        self.override_patterns = OVERRIDE_PATTERNS

    def classify(self, query: str) -> str:
        """
        Classify a user query into one of four analytics categories.
        
        Uses hybrid approach:
        1. First check override patterns
        2. Then check strong signal patterns
        3. Fall back to LLM for ambiguous cases
        
        Args:
            query: The user's natural language question
            
        Returns:
            One of: DESCRIPTIVE, DIAGNOSTIC, PREDICTIVE, PRESCRIPTIVE
        """
        query_lower = query.lower().strip()
        
        # Step 1: Check override patterns first
        override_result = self._check_override_patterns(query_lower)
        if override_result:
            return override_result
        
        # Step 2: Check strong signal patterns
        strong_matches = self._check_signal_patterns(query_lower, "strong")
        
        # If exactly one category has strong matches, use it
        if len(strong_matches) == 1:
            return list(strong_matches.keys())[0]
        
        # If multiple strong matches, use LLM to decide
        if len(strong_matches) > 1:
            return self._classify_with_llm(query)
        
        # Step 3: No strong matches - use LLM
        llm_result = self._classify_with_llm(query)
        
        # Step 4: Validate LLM result against weak patterns
        weak_matches = self._check_signal_patterns(query_lower, "weak")
        
        # If LLM result has weak pattern support, trust it
        if llm_result in weak_matches:
            return llm_result
        
        # If LLM result has no pattern support but weak matches exist, consider them
        if weak_matches and llm_result not in weak_matches:
            # Still trust LLM but log for debugging
            pass
        
        return llm_result
    
    def _check_override_patterns(self, query_lower: str) -> str:
        """Check for high-confidence override patterns."""
        
        # Check PREDICTIVE overrides first (what if scenarios)
        for pattern in self.override_patterns.get("PREDICTIVE_OVERRIDE", []):
            if re.search(pattern, query_lower):
                return "PREDICTIVE"
        
        # Check DESCRIPTIVE overrides (what is X questions)
        for pattern in self.override_patterns.get("DESCRIPTIVE_OVERRIDE", []):
            if re.search(pattern, query_lower):
                return "DESCRIPTIVE"
        
        return None
    
    def _check_signal_patterns(self, query_lower: str, strength: str) -> Dict[str, int]:
        """
        Check signal patterns and return categories with match counts.
        
        Args:
            query_lower: Lowercase query string
            strength: "strong" or "weak"
            
        Returns:
            Dict mapping category to number of matches
        """
        matches = {}
        
        for category, patterns in self.signal_patterns.items():
            pattern_list = patterns.get(strength, [])
            match_count = 0
            
            for pattern in pattern_list:
                if re.search(pattern, query_lower):
                    match_count += 1
            
            if match_count > 0:
                matches[category] = match_count
        
        return matches
    
    def _classify_with_llm(self, query: str) -> str:
        """
        Use LLM to classify ambiguous queries.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a query classifier. Respond with exactly one word: DESCRIPTIVE, DIAGNOSTIC, PREDICTIVE, or PRESCRIPTIVE."
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
            
            # Extract just the category if there's extra text
            for cat in ["DESCRIPTIVE", "DIAGNOSTIC", "PREDICTIVE", "PRESCRIPTIVE"]:
                if cat in classification:
                    return cat
            
            # Default fallback
            return "DESCRIPTIVE"
            
        except Exception as e:
            print(f"Classification error: {e}")
            return "DESCRIPTIVE"

    def classify_with_confidence(self, query: str) -> Dict:
        """
        Classify a query and provide detailed reasoning.
        
        Returns:
            dict with 'category', 'confidence', 'method', and 'reasoning'
        """
        query_lower = query.lower().strip()
        
        # Check override patterns
        override_result = self._check_override_patterns(query_lower)
        if override_result:
            return {
                "category": override_result,
                "confidence": "HIGH",
                "method": "override_pattern",
                "reasoning": f"Query matches high-confidence {override_result} pattern"
            }
        
        # Check strong patterns
        strong_matches = self._check_signal_patterns(query_lower, "strong")
        
        if len(strong_matches) == 1:
            category = list(strong_matches.keys())[0]
            return {
                "category": category,
                "confidence": "HIGH",
                "method": "strong_pattern",
                "reasoning": f"Query has {strong_matches[category]} strong signal(s) for {category}"
            }
        
        if len(strong_matches) > 1:
            llm_result = self._classify_with_llm(query)
            return {
                "category": llm_result,
                "confidence": "MEDIUM",
                "method": "llm_tiebreaker",
                "reasoning": f"Multiple patterns matched ({list(strong_matches.keys())}), LLM resolved to {llm_result}"
            }
        
        # LLM classification
        llm_result = self._classify_with_llm(query)
        weak_matches = self._check_signal_patterns(query_lower, "weak")
        
        confidence = "MEDIUM" if llm_result in weak_matches else "LOW"
        
        return {
            "category": llm_result,
            "confidence": confidence,
            "method": "llm",
            "reasoning": f"LLM classified as {llm_result}" + (f" (supported by weak patterns)" if llm_result in weak_matches else "")
        }
    
    def explain_classification(self, query: str) -> str:
        """
        Provide a human-readable explanation of classification.
        """
        result = self.classify_with_confidence(query)
        
        return f"""
Query: "{query}"

Classification: {result['category']}
Confidence: {result['confidence']}
Method: {result['method']}
Reasoning: {result['reasoning']}

Analytics Type Descriptions:
- DESCRIPTIVE: Reports facts and historical data ("What happened?")
- DIAGNOSTIC: Explains causes and variances ("Why did it happen?")
- PREDICTIVE: Forecasts and scenarios ("What will happen?")
- PRESCRIPTIVE: Recommendations and actions ("What should we do?")
"""


# =============================================================================
# TEST SUITE
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  Query Classifier v2.0 - Test Suite")
    print("=" * 70)
    
    classifier = QueryClassifier()
    
    test_cases = [
        # DESCRIPTIVE
        ("What is CFG Ukraine's revenue for 2025?", "DESCRIPTIVE"),
        ("Show me G&A expenses by month", "DESCRIPTIVE"),
        ("What are the crop areas?", "DESCRIPTIVE"),
        ("List all account categories", "DESCRIPTIVE"),
        ("What was EBITDA last quarter?", "DESCRIPTIVE"),
        
        # DIAGNOSTIC
        ("Why did net income beat budget by 56%?", "DIAGNOSTIC"),
        ("What drove the revenue increase?", "DIAGNOSTIC"),
        ("Explain the variance vs last year", "DIAGNOSTIC"),
        ("Compare actual to budget", "DIAGNOSTIC"),
        ("What caused expenses to spike?", "DIAGNOSTIC"),
        
        # PREDICTIVE
        ("What if wheat prices drop by 15%?", "PREDICTIVE"),
        ("Forecast next quarter EBITDA", "PREDICTIVE"),
        ("What's the impact of yield changes?", "PREDICTIVE"),
        ("What will revenue be if prices rise 10%?", "PREDICTIVE"),
        ("Project margin under drought scenario", "PREDICTIVE"),
        
        # PRESCRIPTIVE
        ("How should we optimize the crop mix?", "PRESCRIPTIVE"),
        ("Where can we reduce costs?", "PRESCRIPTIVE"),
        ("What actions should we take to improve margin?", "PRESCRIPTIVE"),
        ("Recommend a hedging strategy", "PRESCRIPTIVE"),
        ("How can we increase profitability?", "PRESCRIPTIVE"),
    ]
    
    correct = 0
    total = len(test_cases)
    
    print("\nRunning classification tests...\n")
    
    for query, expected in test_cases:
        result = classifier.classify(query)
        status = "✓" if result == expected else "✗"
        
        if result == expected:
            correct += 1
        
        print(f"{status} Query: \"{query[:50]}...\"" if len(query) > 50 else f"{status} Query: \"{query}\"")
        print(f"  Expected: {expected}, Got: {result}")
        
        if result != expected:
            detail = classifier.classify_with_confidence(query)
            print(f"  Method: {detail['method']}, Confidence: {detail['confidence']}")
        print()
    
    print("=" * 70)
    print(f"  Results: {correct}/{total} correct ({100*correct/total:.1f}%)")
    print("=" * 70)
