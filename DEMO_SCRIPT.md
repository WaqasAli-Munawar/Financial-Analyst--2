# CFG Ukraine Financial Analytics Agent - Demo Script

## Management Presentation Guide

**Duration:** 15-20 minutes  
**Audience:** SALIC Management  
**Purpose:** Demonstrate AI-powered financial analytics capabilities

---

## Opening (2 minutes)

> "This demo showcases our new conversational AI agent for CFG Ukraine financial analytics. The system can answer questions across four analytics types - describing what happened, explaining why, predicting what could happen, and recommending what we should do."

---

## Demo Flow: 10 Curated Questions

### Part 1: DESCRIPTIVE Analytics - "What Happened?" (3 min)

#### Question 1: High-Level Overview
```
What is CFG Ukraine's financial performance for FY2025?
```
**Expected Response:** Revenue, EBITDA, Net Income summary with YTD and forecast figures from knowledge base.

#### Question 2: Account-Level Detail (Uses SQL)
```
Show me all account categories and their balances
```
**Expected Response:** Table showing all 12 account categories with amounts from Fabric warehouse (Cash, G&A expenses, Liabilities, etc.).

#### Question 3: Crop-Specific Data
```
What is the gross margin for winter wheat?
```
**Expected Response:** Area (39,573 ha), yield (6.78 t/ha), volume, price ($249.85/t), GM, GM%, GM/ha from knowledge base.

---

### Part 2: DIAGNOSTIC Analytics - "Why Did It Happen?" (4 min)

#### Question 4: Variance Explanation
```
Why did net income beat budget by 56%?
```
**Expected Response:** Variance decomposition showing Price Effect (+70%), Cost Effect, Yield Effect with specific crop price variances (OSR +$85/t, Sunflower +$114/t). Uses knowledge base.

#### Question 5: Root Cause Analysis
```
What drove the EBITDA improvement?
```
**Expected Response:** Analysis of revenue growth, cost management, and margin improvement using VDT framework.

#### Question 6: Budget Comparison (Knowledge Base Fallback)
```
How does forecast compare to budget?
```
**Expected Response:** Table showing Revenue (+52%), EBITDA (+4%), Net Income (+56%) vs budget with key drivers. **Note:** Uses knowledge base fallback since database only has Actuals.

---

### Part 3: PREDICTIVE Analytics - "What Will Happen?" (3 min)

#### Question 7: Scenario Analysis
```
What if wheat prices drop by 15%?
```
**Expected Response:** Sensitivity analysis showing ~$24.8m USD impact on 660,983 tons volume.

#### Question 8: Multi-Factor Scenario
```
What is the impact if yields decrease by 10% due to drought?
```
**Expected Response:** ~$30m impact across all crops with breakdown by crop type.

---

### Part 4: PRESCRIPTIVE Analytics - "What Should We Do?" (3 min)

#### Question 9: Optimization
```
How should we optimize the crop mix for next season?
```
**Expected Response:** Ranking by GM/ha (winter_osr > sunflower > soybean > winter_wheat), with rotation constraints and recommendations.

#### Question 10: Action Items
```
What actions should we take to improve profitability?
```
**Expected Response:** Prioritized recommendations with quantified impact, timeline, and trade-offs.

---

## Key Talking Points

### Value-Driver Tree Framework
> "The system uses the Value-Driver Tree framework to connect operational metrics to financial outcomes:
> - **Gross Margin = Revenue - Cost of Production**
> - **Revenue = Area × Yield × Price**
> - This allows us to decompose any variance into its root causes."

### Hybrid Data Architecture
> "The agent intelligently combines two data sources:
> - **Microsoft Fabric** for transactional actuals
> - **Embedded Knowledge Base** for budget, forecast, and operational benchmarks
> 
> When the database doesn't have certain data (like budget scenarios), the agent automatically falls back to the knowledge base."

### Analytics Capabilities
| Type | Question | Business Value |
|------|----------|----------------|
| Descriptive | "What happened?" | Reporting & monitoring |
| Diagnostic | "Why?" | Root cause analysis |
| Predictive | "What if?" | Risk management |
| Prescriptive | "What should we do?" | Decision support |

### Technical Highlights
- **Microsoft-native:** Built entirely within Azure AI Foundry + Microsoft Fabric
- **Real-time data:** Connected to SALIC_Finance_Warehouse (Actuals)
- **Conversational:** Natural language interface, no SQL knowledge required
- **Contextual:** Remembers conversation history for follow-up questions
- **Resilient:** Falls back to knowledge base when SQL data unavailable

---

## Data Availability Note

The current Fabric view (`vw_Fact_Actuals_SALIC_Ukraine`) contains **Actual data only** (328 records). Budget and Forecast scenarios are not yet loaded. The agent handles this gracefully by:

1. Attempting SQL query first
2. Detecting zero results for budget comparisons
3. Falling back to embedded knowledge base
4. Clearly noting the data source in response

**Future Enhancement:** Once Budget/Forecast data is loaded to Fabric, the agent will automatically use the richer SQL-based analysis.

---

## Handling Q&A

### "How accurate are the predictions?"
> "The predictions use sensitivity analysis based on historical data and the Value-Driver Tree model. They show directional impact and order of magnitude. For precise forecasting, we'd integrate with our formal planning models."

### "Can it access other subsidiaries?"
> "Currently configured for CFG Ukraine. The architecture can be extended to other entities by connecting additional data sources."

### "Why does it sometimes say 'from knowledge base'?"
> "The Fabric database currently contains only Actual scenario data. For budget comparisons, the agent uses our embedded knowledge base which contains the FY2025 budget and forecast figures. Once budget data is loaded to Fabric, it will use that directly."

### "How is data security handled?"
> "The system uses Service Principal authentication with read-only access. No data leaves Microsoft's ecosystem - it stays within Azure and Fabric."

---

## Closing (2 minutes)

> "This demonstrates how conversational AI can transform financial analytics from static reports to interactive, on-demand insights. The system empowers business users to explore data naturally without waiting for analyst support."

**Next Steps to Discuss:**
1. Load Budget/Forecast data to Fabric for richer comparisons
2. Expand to other SALIC subsidiaries
3. Integrate external market data APIs
4. Add automated alerts and reporting
5. Power BI visualization integration

---

## Demo Checklist

### Before the Demo
- [ ] Start the API server: `python api.py`
- [ ] Open SALIC_Chat_Interface_v2.html in browser
- [ ] Clear any previous conversation
- [ ] Test one query to confirm connectivity
- [ ] Have this script open for reference

### During the Demo
- [ ] Speak clearly, pause after each response
- [ ] Highlight the analytics type classification
- [ ] Point out specific numbers and insights
- [ ] Show follow-up suggestions feature
- [ ] Mention knowledge base fallback when it occurs

### Backup Plan
If connectivity issues occur:
- Have screenshots of successful responses ready
- Explain the architecture conceptually
- Offer to schedule a follow-up demo

---

*Demo Script v2.0 - December 2025*
