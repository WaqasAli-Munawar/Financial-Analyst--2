# CFG Ukraine Financial Analytics Agent - Demo Script v3.0

## Executive Summary

This demo showcases an **Agentic AI Financial Analytics System** for CFG Ukraine that combines:
- **Microsoft Fabric** (real-time data warehouse)
- **Azure OpenAI GPT-4o** (natural language understanding)
- **Knowledge Base** (business context and forecasts)
- **Value-Driver Tree** (financial calculations)

---

## Demo Flow (15-20 minutes)

### Opening (2 minutes)

**Talking Points:**
- "This is a proof-of-concept AI agent for financial analytics"
- "It connects directly to our Microsoft Fabric data warehouse"
- "Users can ask questions in natural language - no SQL knowledge required"
- "The system classifies queries into 4 analytics types: Descriptive, Diagnostic, Predictive, Prescriptive"

---

## Demo Questions (Recommended Order)

### 🟢 Question 1: Hybrid Data Query (Start Strong!)

**Ask:** 
> "How does forecast compare to budget?"

**Expected Response:**
- Classification: DIAGNOSTIC
- Data Source: **Fabric (55 records from Fact_ForecastBudget)**
- Shows variance table with ↑/↓ indicators
- Executive summary and root cause analysis
- KB context with scenario explanations

**Key Points to Highlight:**
- ✅ Real data from Fabric warehouse (not mocked)
- ✅ Automatic variance calculation
- ✅ Business context added from Knowledge Base
- ✅ CFO-ready formatting

---

### 🟢 Question 2: Financial Performance Overview

**Ask:**
> "What is CFG Ukraine's financial performance for FY2025?"

**Expected Response:**
- Classification: DESCRIPTIVE
- Shows YTD, Forecast, Budget with variances
- Key performance indicators
- Performance drivers explanation

**Key Points to Highlight:**
- ✅ Combines multiple data sources
- ✅ Executive-level summary
- ✅ Actionable insights

---

### 🟢 Question 3: Diagnostic Deep-Dive

**Ask:**
> "Why did net income beat budget by 56%?"

**Expected Response:**
- Classification: DIAGNOSTIC
- Variance decomposition (Price, Volume, Cost effects)
- Root cause: Commodity price tailwinds
- Specific price drivers (OSR +$85/t, Sunflower +$114/t)

**Key Points to Highlight:**
- ✅ Explains "why" not just "what"
- ✅ Value-Driver Tree analysis
- ✅ Quantified drivers

---

### 🟢 Question 4: Predictive Scenario

**Ask:**
> "What if wheat prices drop by 15%?"

**Expected Response:**
- Classification: PREDICTIVE
- Impact calculation: ~$24.8M reduction in gross margin
- Risk assessment (Low/Medium/High)
- Hedging recommendations

**Key Points to Highlight:**
- ✅ Real-time sensitivity analysis
- ✅ Quantified risk impact
- ✅ Actionable recommendations

---

### 🟢 Question 5: Prescriptive Recommendations

**Ask:**
> "How should we optimize the crop mix?"

**Expected Response:**
- Classification: PRESCRIPTIVE
- Crop profitability ranking (GM/ha)
- Optimization recommendations
- Scenario impact (e.g., "Shifting 5,000 ha adds $3.9M")

**Key Points to Highlight:**
- ✅ Data-driven recommendations
- ✅ Quantified impact
- ✅ Actionable next steps

---

### 🟢 Question 6: Live Fabric Query

**Ask:**
> "Show me all account categories and their balances"

**Expected Response:**
- Classification: DESCRIPTIVE
- Real-time data from Fabric (12 accounts)
- Hybrid response with KB context

**Key Points to Highlight:**
- ✅ Live SQL query to Fabric
- ✅ Real account data
- ✅ Automatic number formatting

---

## Backup Questions (If Time Permits)

| Question | Type | Data Source |
|----------|------|-------------|
| "What is the gross margin for winter wheat?" | DESCRIPTIVE | Knowledge Base |
| "What drove the EBITDA improvement?" | DIAGNOSTIC | Knowledge Base |
| "What is the impact if yields decrease by 10%?" | PREDICTIVE | Knowledge Base |
| "What actions should we take to improve profitability?" | PRESCRIPTIVE | Knowledge Base |

---

## Technical Architecture (For Technical Audience)

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interface (HTML)                        │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Query     │  │    SQL      │  │     Response            │  │
│  │ Classifier  │  │  Generator  │  │     Generator           │  │
│  │  (GPT-4o)   │  │  (GPT-4o)   │  │  (Hybrid: Fabric+KB)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌───────────────────────────┐   ┌───────────────────────────────┐
│   Microsoft Fabric        │   │   Knowledge Base              │
│   ┌─────────────────┐     │   │   ┌─────────────────────┐     │
│   │ Fact_Actuals    │     │   │   │ FY2025 Baseline     │     │
│   │ (328 records)   │     │   │   │ Budget/Forecast     │     │
│   ├─────────────────┤     │   │   │ Crop Data           │     │
│   │Fact_ForecastBudg│     │   │   │ Value-Driver Tree   │     │
│   │ (5,282 records) │     │   │   └─────────────────────┘     │
│   └─────────────────┘     │   └───────────────────────────────┘
└───────────────────────────┘
```

---

## Key Differentiators

| Feature | Traditional BI | This AI Agent |
|---------|---------------|---------------|
| Query Method | Click through dashboards | Natural language |
| Data Access | Pre-built reports only | Any question, any data |
| Analysis | Manual interpretation | AI-generated insights |
| Recommendations | None | Prescriptive actions |
| Learning Curve | High (tool-specific) | Low (just ask) |

---

## Handling Q&A

### "Is this using real data?"
> "Yes, the system connects directly to Microsoft Fabric. The forecast vs budget comparison shows 55 real records from the Fact_ForecastBudget table."

### "How accurate is the AI?"
> "The AI classifies queries and generates SQL. All numerical data comes directly from Fabric - we don't hallucinate numbers. The Knowledge Base provides validated business context."

### "Can this scale to other subsidiaries?"
> "Yes, the architecture is designed to be entity-agnostic. We filter by EntityCode (E250 for CFG Ukraine). Adding other entities is a configuration change."

### "What about security?"
> "Authentication uses Azure Service Principal. Data never leaves Microsoft ecosystem. All queries are logged and auditable."

### "What's next?"
> "Phase 2 includes: visualizations, trend analysis, alerts, and expansion to other SALIC subsidiaries."

---

## Demo Checklist

Before demo:
- [ ] API running (`python api.py`)
- [ ] Fabric connection verified (green indicator)
- [ ] Test one query to warm up
- [ ] Browser open to chat interface

During demo:
- [ ] Start with "How does forecast compare to budget?" (strongest response)
- [ ] Highlight data source badges
- [ ] Point out formatting (tables, ↑/↓ indicators)
- [ ] Mention the 4 analytics types

After demo:
- [ ] Collect feedback
- [ ] Note any questions for follow-up
- [ ] Share demo recording if applicable

---

## Contact

**Developer:** Waqas Ali  
**Team:** Data Analytics, SALIC  
**Date:** December 2025

---

*This demo represents a pilot project for AI-powered financial analytics at SALIC.*