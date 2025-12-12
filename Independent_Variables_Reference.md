# CFG Ukraine Independent Variables Reference
## 86 Variables Mapped to Value-Driver Tree

---

## CATEGORY 1: CROP YIELDS (t/ha)

| Variable | Crops Applicable | Analytics Use |
|----------|------------------|---------------|
| Winter OSR yield | OSR | Yield prediction, variance analysis |
| Winter wheat yield | Wheat | Volume forecasting |
| Winter barley yield | Barley | Production planning |
| Maize yield | Maize | Harvest forecasting |
| Soybean yield | Soybean | GM per hectare analysis |
| Sunflower yield | Sunflower | Capacity utilization |
| Sugar beet yield | Sugar beet | Processing volume |
| Potato yield | Potatoes (processing, seed, table) | Storage planning |

**Data Source:** Internal Tech Reports, Historical Actuals
**Update Frequency:** Seasonal (post-harvest)

---

## CATEGORY 2: CROP CONDITION (% Good Area)

| Variable | Timing | Analytics Use |
|----------|--------|---------------|
| Winter OSR condition after winter | Spring assessment | Early yield indication |
| Winter wheat condition after winter | Spring assessment | Risk flagging |
| Winter barley condition after winter | Spring assessment | Intervention planning |

**Data Source:** Internal Field Reports
**Update Frequency:** Monthly during growing season

---

## CATEGORY 3: CROP STRUCTURE (ha)

| Variable | Range | Analytics Use |
|----------|-------|---------------|
| Spring crops share (%) | 0-100% | Rotation optimization |
| Winter crops share (%) | 0-100% | Risk diversification |
| Individual crop areas | By crop | Revenue forecasting |

**Historical Data:** 2019-2025 Actual, 2026-2030 Plan
**Data Source:** Internal BI Reports

### Current Crop Areas (FY2025)

| Crop | Hectares | % of Total |
|------|----------|------------|
| Soybean | 49,766 | 27.5% |
| Winter Wheat | 39,573 | 21.9% |
| Winter OSR | 31,500 | 17.4% |
| Maize | 26,457 | 14.6% |
| Sunflower | 17,312 | 9.6% |
| Winter Barley | 11,527 | 6.4% |
| Potatoes | 2,122 | 1.2% |
| Sugar Beet | 2,367 | 1.3% |
| **TOTAL** | **180,624** | **100%** |

---

## CATEGORY 4: ROTATION AREAS

| Variable | Description | Analytics Use |
|----------|-------------|---------------|
| Rotation 1-6 areas | 6 distinct rotation zones | Crop sequencing optimization |
| Sugar beet rotation | Dedicated beet area | Processing capacity alignment |
| Potato rotation | Dedicated potato area | Storage capacity planning |
| Transitional areas | Land in conversion | Future capacity planning |

**Data Source:** Internal Planning Documents

---

## CATEGORY 5: FINANCIAL METRICS PER CROP

| Metric | Unit | Formula | Analytics Use |
|--------|------|---------|---------------|
| Net income per ha | $/ha | (Revenue - All Costs) / Area | Profitability ranking |
| Total expenses per ha | $/ha | All Costs / Area | Cost benchmarking |
| EBITDA per ha | $/ha | EBITDA / Area | Operational efficiency |
| Production cost per ton | $/t | Direct Costs / Volume | Unit economics |
| Production cost per ha | $/ha | Direct Costs / Area | Input efficiency |
| Gross margin per ha | $/ha | (Revenue - COGS) / Area | Crop comparison |
| Gross margin % | % | GM / Revenue | Margin analysis |
| Cost profitability | % | GM / Costs | Return on input |
| Income profitability | % | Net Income / Revenue | Bottom-line efficiency |

**Data Source:** Financial Reports, Management Accounts
**Update Frequency:** Monthly

---

## CATEGORY 6: SOIL & WEATHER

| Variable | Unit | Analytics Use |
|----------|------|---------------|
| Soil moisture content (0-20 cm) | % | Planting decision support |
| Reserve productive moisture (0-60 cm) | mm | Irrigation planning |
| Temperature (daily/seasonal) | °C | Yield modeling |
| Precipitation | mm | Drought/flood risk |
| GDD (Growing Degree Days) | degree-days | Crop maturity prediction |

**Data Source:** Internal Tech Reports, Weather Services
**Update Frequency:** Daily/Weekly during season

---

## CATEGORY 7: FERTILIZATION PROGRESS

| Variable | Crops | Analytics Use |
|----------|-------|---------------|
| N application progress | All crops | Cost tracking |
| P application progress | All crops | Budget monitoring |
| K application progress | All crops | Yield optimization |
| Micronutrient application | All crops | Quality management |

**Data Source:** Internal Tech Reports
**Update Frequency:** Weekly during application season

---

## CATEGORY 8: EXTERNAL MARKET VARIABLES

### 8.1 Commodity Prices

| Variable | Unit | Source | API |
|----------|------|--------|-----|
| Wheat FOB price | $/t | Agricensus | Limited |
| Corn FOB price | $/t | Agricensus | Limited |
| Barley FOB price | $/t | Agricensus | Limited |
| OSR price | $/t | Agricensus | Limited |
| Sunflower price | $/t | Agricensus | Limited |
| Soybean price | $/t | Agricensus | Limited |
| Wheat futures | USd/bu | Trading Economics | Yes (sub) |
| Corn futures | USd/bu | Trading Economics | Yes (sub) |

### 8.2 Input Prices

| Variable | Unit | Source | API |
|----------|------|--------|-----|
| Fertilizer (N) price | $/t | Argus Media | Subscription |
| Fertilizer (P) price | $/t | Argus Media | Subscription |
| Seed cost index | Index | Internal | Internal |
| Fuel price | $/L | Trading Economics | Yes |

### 8.3 FX & Macro

| Variable | Current Value | Source | API |
|----------|---------------|--------|-----|
| USD/UAH rate | ~42.05 | Trading Economics | Yes |
| Ukraine GDP growth | 2% (2025 est) | IMF | Yes |
| Ukraine CPI | 12.6% (2025) | IMF/NBU | Yes |
| Policy interest rate | 15.5% | NBU | Yes |

---

## CATEGORY 9: SELF-PRODUCED INPUTS

| Variable | Description | Analytics Use |
|----------|-------------|---------------|
| UAN area | Hectares for UAN production | Input cost optimization |
| UAN quantity | Tons produced | Self-sufficiency ratio |
| Seed multiplication area | Hectares for seed | Quality control |

**Data Source:** Internal Operations

---

## ANALYTICS APPLICATION MATRIX

| Variable Category | Descriptive | Diagnostic | Predictive | Prescriptive |
|-------------------|:-----------:|:----------:|:----------:|:------------:|
| Yields | ✓ | ✓✓✓ | ✓✓✓ | ✓✓ |
| Crop Condition | ✓ | ✓✓ | ✓✓✓ | ✓ |
| Crop Areas | ✓✓✓ | ✓✓ | ✓✓ | ✓✓✓ |
| Financial/ha | ✓✓✓ | ✓✓✓ | ✓✓ | ✓✓✓ |
| Soil/Weather | ✓ | ✓✓ | ✓✓✓ | ✓ |
| Commodity Prices | ✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ |
| FX/Macro | ✓ | ✓✓✓ | ✓✓✓ | ✓ |

**Legend:** ✓ = Useful, ✓✓ = Important, ✓✓✓ = Critical

---

## VARIANCE ATTRIBUTION MAP

When decomposing financial variances, map variables to effects:

| Effect | Primary Variables |
|--------|-------------------|
| **Area Effect** | Crop areas (ha), rotation decisions |
| **Yield Effect** | Yields (t/ha), crop condition, soil, weather |
| **Price Effect** | Commodity prices, quality indicators |
| **Cost Effect** | Input prices, application rates, yields |
| **FX Effect** | USD/UAH rate, inflation |

---

## DATA QUALITY NOTES

| Category | Completeness | Reliability | Update Lag |
|----------|--------------|-------------|------------|
| Internal Operational | High | High | Weekly |
| Financial Actuals | High | High | Monthly |
| Commodity Prices | High | Medium | Daily |
| Weather Data | Medium | High | Daily |
| Macro Indicators | High | High | Monthly |
| Forecasts | Medium | Low | Quarterly |

---

*Reference Version: 1.0*
*Based on Independent_Variable.xlsx and Independent_Driver.xlsx*
*December 2025*
