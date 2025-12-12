# CFG Ukraine Financial Analytics Knowledge Base
## For SALIC Data Analytics Multi-Agent AI System

---

## 1. VALUE-DRIVER TREE FRAMEWORK

### 1.1 Core Formula Chain

```
GROSS MARGIN = Revenue - Cost of Production

Where:
├── Revenue = Volume × Net Sales Price
│   ├── Volume = Crop Area (ha) × Yield (t/ha)
│   │   ├── Crop Area → Decision variable (planned hectares)
│   │   └── Yield → f(Agronomy, Soil, Weather)
│   └── Net Sales Price → f(Commodity Prices, FX Rates, Macro)
│
└── Cost of Production = Volume × Production Cost per ton
    └── Production Cost ($/t) = Direct Costs ($/ha) ÷ Yield (t/ha)
        └── Direct Costs → f(Input Prices, Agronomy Practices, FX)
```

### 1.2 Variable Classification

| Category | Variables | Role |
|----------|-----------|------|
| **Independent (External)** | Commodity prices, FX rates, weather, soil conditions | Features/Inputs |
| **Decision Variables** | Crop area, agronomy practices, hedging strategy | Controllable |
| **Intermediate (Modeled)** | Yield, Net Sales Price, Direct Costs | Calculated |
| **Financial Outputs** | Revenue, Cost of Production, Gross Margin, EBITDA | Targets |

---

## 2. DATA SOURCES & MAPPING

### 2.1 Internal Data (Microsoft Fabric)

| Data Source | Table/View | Key Metrics |
|-------------|------------|-------------|
| Ukraine Performance Report | vw_Fact_Actuals_SALIC_Ukraine | Actuals, Budget, Forecast |
| Financial Warehouse | SALIC_Finance_Warehouse | P&L, Balance Sheet, Cash Flow |
| Tech Cards | Internal Reports | Crop plans, application rates |
| BI Reports | Power BI | Operational KPIs |

### 2.2 External Data Sources (6 Storylines)

**Storyline 1: Macroeconomic Environment**
| Variable | Source | API Available |
|----------|--------|---------------|
| USD/UAH Exchange Rate | Trading Economics | Yes (subscription) |
| Ukraine GDP Growth | IMF/World Bank | Yes |
| CPI Inflation | IMF/NBU | Yes |
| Policy Interest Rate | NBU | Yes |
| FX Reserves | NBU | Yes |
| Unemployment Rate | State Statistics | Limited |

**Storyline 2: Operational Capacity**
| Variable | Source | API Available |
|----------|--------|---------------|
| Land under cultivation (ha) | Internal BI | Internal |
| Seed production capacity | Internal | Internal |
| Fertilizer/fuel prices | Argus Media | Subscription |

**Storyline 3: Climate & Weather**
| Variable | Source | API Available |
|----------|--------|---------------|
| Temperature/precipitation | World Bank/Hydromet | Research datasets |
| Quality indicators | Internal Tech Reports | Internal |
| Extreme weather events | ReliefWeb/Reuters | Yes |

**Storyline 4: Sustainability**
| Variable | Source | API Available |
|----------|--------|---------------|
| Soil degradation | FAO/UN | Published reports |
| ESG metrics | Internal | Internal |

**Storyline 5: Storage & Infrastructure**
| Variable | Source | API Available |
|----------|--------|---------------|
| Potato storage (106,200t) | Internal | Internal |
| Grain elevator capacity (603,000t) | Internal | Internal |

**Storyline 6: Commodity Markets**
| Variable | Source | API Available |
|----------|--------|---------------|
| Wheat cash price | UkrAgroConsult/Agricensus | Limited |
| Corn cash price | UkrAgroConsult | Limited |
| Barley cash price | UkrAgroConsult | Limited |
| Commodity futures | Trading Economics | Yes (subscription) |
| Export volumes | UN Comtrade | Yes |

---

## 3. ANALYTICS QUERY PATTERNS

### 3.1 DESCRIPTIVE ("What happened?")

**Template Questions:**
- "What was the gross margin for [crop] in [period]?"
- "Show me YTD revenue by crop"
- "What are the current crop areas?"

**SQL Pattern:**
```sql
SELECT 
    crop_type,
    SUM(revenue_sar) as total_revenue,
    SUM(volume_tons) as total_volume,
    AVG(yield_per_ha) as avg_yield
FROM vw_Fact_Actuals_SALIC_Ukraine
WHERE fiscal_year = 2025
GROUP BY crop_type
```

**Response Framework:**
1. State the metric value clearly
2. Provide period-over-period comparison
3. Highlight significant items

---

### 3.2 DIAGNOSTIC ("Why did it happen?")

**Template Questions:**
- "Why did gross margin increase vs budget?"
- "What drove the revenue variance in Q2?"
- "Explain the yield gap between actual and plan"

**Variance Decomposition Formula:**
```
ΔGross Margin = ΔArea Effect + ΔYield Effect + ΔPrice Effect + ΔCost Effect + ΔFX Effect

Where:
- ΔArea Effect = (Actual Area - Budget Area) × Budget Yield × Budget Price
- ΔYield Effect = Actual Area × (Actual Yield - Budget Yield) × Budget Price
- ΔPrice Effect = Actual Volume × (Actual Price - Budget Price)
- ΔCost Effect = Actual Volume × (Budget Cost/t - Actual Cost/t)
- ΔFX Effect = Calculated using constant FX baseline
```

**Response Framework:**
1. State total variance
2. Decompose into driver effects (rank by magnitude)
3. Provide root cause for top 2-3 drivers
4. Reference specific data points

**Example Diagnostic Response:**
```
June YTD Net Income variance: +49.9m SAR vs Budget

Key Drivers:
1. Price Effect (+35m): Higher commodity prices
   - OSR: +$85/t vs budget
   - Sunflower: +$114/t vs budget
   - Wheat: +$16/t vs budget

2. Volume Effect (-15m): Lower sales volume
   - Sales structure shifted to later periods
   - 118kt below budget

3. Cost Effect (+30m): Favorable production costs
   - Lower direct costs per ha
   - Better yield efficiency
```

---

### 3.3 PREDICTIVE ("What will happen?")

**Template Questions:**
- "What is the expected gross margin for FY2025?"
- "If wheat prices drop 10%, what happens to revenue?"
- "Forecast yield under drought scenario"

**Scenario Variables:**
| Variable | Base Case | Bull Case | Bear Case |
|----------|-----------|-----------|-----------|
| Wheat Price ($/t) | 250 | 280 | 220 |
| OSR Price ($/t) | 510 | 570 | 450 |
| USD/UAH | 42.05 | 40.00 | 45.00 |
| Yield (vs plan) | 100% | 105% | 90% |

**Sensitivity Formula:**
```
ΔMetric = Base_Value × Elasticity × Δ%_Driver

Example:
- If Wheat Price +10% → Revenue impact = 660,983t × $25/t = $16.5m
- If Yield -5% → Volume impact = Total Area × (−5%) × Price
```

**Response Framework:**
1. State base case forecast with confidence range
2. Show sensitivity to key variables
3. Identify top risks and opportunities
4. Provide P10/P50/P90 scenarios

---

### 3.4 PRESCRIPTIVE ("What should we do?")

**Template Questions:**
- "How should we optimize crop mix for next season?"
- "What hedging strategy maximizes risk-adjusted returns?"
- "Where should we reduce costs?"

**Optimization Framework:**
```
Maximize: E[Gross Margin] - λ × Risk(GM)

Subject to:
- Total Area ≤ 180,624 ha
- Rotation constraints (max % same crop)
- Working capital limits
- Risk policy (P10 GM > threshold)
```

**Decision Variables:**
1. Crop area allocation by crop/region
2. Input intensity (fertilizer, seed quality)
3. Hedging percentage (% volume pre-sold)
4. Sales timing strategy

**Response Framework:**
1. Recommend specific actions
2. Quantify expected benefit vs current plan
3. Show risk profile comparison
4. Explain key constraints/trade-offs

---

## 4. CFG UKRAINE 2025 BASELINE DATA

### 4.1 Crop Structure (FY2025 Forecast)

| Crop | Area (ha) | Yield (t/ha) | Volume (t) | Price ($/t) |
|------|-----------|--------------|------------|-------------|
| Winter Wheat | 39,573 | 6.78 | 268,396 | 249.85 |
| Winter Barley | 11,527 | 6.22 | 71,687 | 241.55 |
| Winter OSR | 31,500 | 3.22 | 101,565 | 567.60 |
| Maize | 26,457 | 10.34 | 273,665 | 235.51 |
| Soybean | 49,766 | 3.24 | 161,445 | 478.29 |
| Sunflower | 17,312 | 3.24 | 56,059 | 518.75 |
| **Total** | **180,624** | - | - | - |

### 4.2 Financial Performance (May 2025 YTD)

| Metric | Actual | Budget | Variance |
|--------|--------|--------|----------|
| Revenue | 846m SAR | 603m SAR | +40% |
| EBITDA | 164m SAR | 10m SAR | +154m |
| Net Income | 65m SAR | -85m SAR | +150m |

### 4.3 Full Year 2025 Forecast

| Metric | Forecast | Budget | Variance |
|--------|----------|--------|----------|
| Revenue | 2,928m SAR | 1,920m SAR | +52% |
| EBITDA | 397m SAR | 383m SAR | +4% |
| Net Income | 151m SAR | 97m SAR | +56% |

### 4.4 Cost Structure (FY2025 Forecast)

| Category | Amount | Notes |
|----------|--------|-------|
| COGS | -228.7m USD | -7.0m vs budget (favorable) |
| G&A | -23.3m USD | Flat vs budget |
| S&D | -12.5m USD | -2.8m vs budget (unfavorable) |
| Finance Costs | -27.6m USD | +2.4m vs budget (favorable) |

---

## 5. KEY RATIOS & KPIs

### 5.1 Profitability Metrics

| KPI | Formula | Benchmark |
|-----|---------|-----------|
| Gross Margin % | (Revenue - COGS) / Revenue | Target: 35%+ |
| EBITDA Margin | EBITDA / Revenue | Target: 15%+ |
| Cost per ton | Direct Costs / Volume | Varies by crop |
| GM per hectare | Gross Margin / Total Area | Target: $200+/ha |

### 5.2 Operational Metrics

| KPI | Formula | Benchmark |
|-----|---------|-----------|
| Yield Index | Actual Yield / Budget Yield | Target: 100%+ |
| Capacity Utilization | Volume Sold / Storage Capacity | Target: 90%+ |
| Sales Realization | % Harvest Contracted | Target: 80%+ |

### 5.3 Risk Metrics

| KPI | Formula | Threshold |
|-----|---------|-----------|
| Price Exposure | Unhedged Volume × Price Volatility | Monitor |
| Weather VaR | P10 Yield Loss × Area × Price | < 10% GM |
| FX Exposure | USD Revenue × FX Volatility | Monitor |

---

## 6. RESPONSE TEMPLATES

### 6.1 Descriptive Response Template
```
**[Metric] for [Period]: [Value]**

Compared to [benchmark/prior period]:
- [Direction] by [amount/percentage]
- Key contributors: [top items]

Breakdown by [dimension]:
| [Category] | [Value] | [% of Total] |
```

### 6.2 Diagnostic Response Template
```
**Variance Analysis: [Metric] [Period]**

Total Variance: [Actual] vs [Budget] = [Δ Amount] ([Δ%])

**Driver Decomposition:**
1. [Driver 1]: [±Amount] ([explanation])
2. [Driver 2]: [±Amount] ([explanation])
3. [Driver 3]: [±Amount] ([explanation])

**Root Causes:**
- [Primary cause with data reference]
- [Secondary cause with data reference]
```

### 6.3 Predictive Response Template
```
**[Metric] Forecast: [Period]**

Base Case: [Value] (Confidence: [P10]-[P90])

**Sensitivity Analysis:**
| Driver | Change | Impact on [Metric] |
|--------|--------|-------------------|

**Key Risks:**
1. [Risk 1]: Probability [%], Impact [amount]
2. [Risk 2]: Probability [%], Impact [amount]

**Key Opportunities:**
1. [Opportunity 1]: Probability [%], Upside [amount]
```

### 6.4 Prescriptive Response Template
```
**Recommendation: [Action Summary]**

Expected Benefit: [+Amount] vs current plan

**Proposed Actions:**
1. [Action 1]: [Specific recommendation]
   - Expected impact: [+/- Amount]
   - Implementation: [timeline/steps]

2. [Action 2]: [Specific recommendation]
   - Expected impact: [+/- Amount]
   - Implementation: [timeline/steps]

**Risk Profile:**
- Current Plan: P10 = [value], Expected = [value]
- Recommended: P10 = [value], Expected = [value]

**Constraints Considered:**
- [Constraint 1]
- [Constraint 2]
```

---

## 7. GLOSSARY

| Term | Definition |
|------|------------|
| **GM** | Gross Margin = Revenue - Cost of Production |
| **EBITDA** | Earnings Before Interest, Taxes, Depreciation, Amortization |
| **OSR** | Oil Seed Rape (Canola) |
| **t/ha** | Tons per hectare (yield measure) |
| **YTD** | Year to Date |
| **5+7** | 5 months actual + 7 months forecast |
| **COGS** | Cost of Goods Sold |
| **FX** | Foreign Exchange |
| **P10/P50/P90** | 10th/50th/90th percentile outcomes |
| **CVaR** | Conditional Value at Risk |

---

*Last Updated: December 2025*
*Data Source: CFG Ukraine Performance Report, Financial Performance May 2025*
