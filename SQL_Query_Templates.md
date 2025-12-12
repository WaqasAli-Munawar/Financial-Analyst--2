# CFG Ukraine SQL Query Templates
## For Microsoft Fabric Data Agent

---

## 1. DESCRIPTIVE QUERIES

### 1.1 Revenue by Crop (YTD)
```sql
-- What is the revenue by crop for current year?
SELECT 
    crop_type,
    SUM(CASE WHEN scenario = 'Actual' THEN amount_sar ELSE 0 END) AS actual_revenue,
    SUM(CASE WHEN scenario = 'Budget' THEN amount_sar ELSE 0 END) AS budget_revenue,
    SUM(CASE WHEN scenario = 'Actual' THEN amount_sar ELSE 0 END) - 
    SUM(CASE WHEN scenario = 'Budget' THEN amount_sar ELSE 0 END) AS variance
FROM vw_Fact_Actuals_SALIC_Ukraine
WHERE fiscal_year = 2025
  AND account_category = 'Revenue'
GROUP BY crop_type
ORDER BY actual_revenue DESC;
```

### 1.2 Volume Sold by Crop
```sql
-- What volume has been sold by crop?
SELECT 
    crop_type,
    SUM(volume_tons) AS total_volume,
    SUM(volume_tons * price_per_ton) AS revenue_usd
FROM vw_Sales_SALIC_Ukraine
WHERE fiscal_year = 2025
GROUP BY crop_type
ORDER BY total_volume DESC;
```

### 1.3 Cost Structure Summary
```sql
-- What is the cost breakdown?
SELECT 
    account_category,
    account_subcategory,
    SUM(amount_usd) AS total_cost,
    SUM(amount_usd) / SUM(SUM(amount_usd)) OVER () * 100 AS pct_of_total
FROM vw_Fact_Actuals_SALIC_Ukraine
WHERE fiscal_year = 2025
  AND account_type = 'Expense'
GROUP BY account_category, account_subcategory
ORDER BY total_cost DESC;
```

### 1.4 P&L Summary
```sql
-- Full P&L summary
SELECT 
    account_category,
    SUM(CASE WHEN scenario = 'Actual' THEN amount_sar ELSE 0 END) AS actual,
    SUM(CASE WHEN scenario = 'Budget' THEN amount_sar ELSE 0 END) AS budget,
    SUM(CASE WHEN scenario = 'Forecast' THEN amount_sar ELSE 0 END) AS forecast
FROM vw_Fact_Actuals_SALIC_Ukraine
WHERE fiscal_year = 2025
GROUP BY account_category
ORDER BY 
    CASE account_category 
        WHEN 'Revenue' THEN 1
        WHEN 'Cost of Sales' THEN 2
        WHEN 'Gross Margin' THEN 3
        WHEN 'Operating Expenses' THEN 4
        WHEN 'EBITDA' THEN 5
        ELSE 6
    END;
```

---

## 2. DIAGNOSTIC QUERIES

### 2.1 Revenue Variance Decomposition
```sql
-- Revenue variance by driver (price vs volume)
WITH baseline AS (
    SELECT 
        crop_type,
        SUM(budget_volume) AS budget_vol,
        AVG(budget_price) AS budget_price,
        SUM(actual_volume) AS actual_vol,
        AVG(actual_price) AS actual_price
    FROM vw_Revenue_Detail
    WHERE fiscal_year = 2025
    GROUP BY crop_type
)
SELECT 
    crop_type,
    (actual_vol - budget_vol) * budget_price AS volume_effect,
    actual_vol * (actual_price - budget_price) AS price_effect,
    (actual_vol * actual_price) - (budget_vol * budget_price) AS total_variance
FROM baseline
ORDER BY ABS(total_variance) DESC;
```

### 2.2 Yield Variance Analysis
```sql
-- Yield performance vs budget
SELECT 
    crop_type,
    region,
    AVG(actual_yield_tha) AS actual_yield,
    AVG(budget_yield_tha) AS budget_yield,
    AVG(actual_yield_tha) - AVG(budget_yield_tha) AS yield_variance,
    (AVG(actual_yield_tha) / NULLIF(AVG(budget_yield_tha), 0) - 1) * 100 AS yield_variance_pct
FROM vw_Crop_Performance
WHERE harvest_year = 2025
GROUP BY crop_type, region
ORDER BY ABS(yield_variance) DESC;
```

### 2.3 Cost per Ton Analysis
```sql
-- Cost per ton variance by crop
SELECT 
    crop_type,
    SUM(actual_cost_usd) / NULLIF(SUM(actual_volume), 0) AS actual_cost_per_ton,
    SUM(budget_cost_usd) / NULLIF(SUM(budget_volume), 0) AS budget_cost_per_ton,
    (SUM(actual_cost_usd) / NULLIF(SUM(actual_volume), 0)) - 
    (SUM(budget_cost_usd) / NULLIF(SUM(budget_volume), 0)) AS cost_variance_per_ton
FROM vw_Cost_Detail
WHERE fiscal_year = 2025
GROUP BY crop_type
ORDER BY ABS(cost_variance_per_ton) DESC;
```

### 2.4 Gross Margin Bridge
```sql
-- GM variance components
SELECT 
    'Total GM Variance' AS component,
    SUM(actual_gm) - SUM(budget_gm) AS amount
FROM vw_Margin_Summary WHERE fiscal_year = 2025
UNION ALL
SELECT 
    'Volume Effect',
    SUM((actual_volume - budget_volume) * budget_margin_per_ton)
FROM vw_Margin_Detail WHERE fiscal_year = 2025
UNION ALL
SELECT 
    'Price Effect',
    SUM(actual_volume * (actual_price - budget_price))
FROM vw_Margin_Detail WHERE fiscal_year = 2025
UNION ALL
SELECT 
    'Cost Effect',
    SUM(actual_volume * (budget_cost_per_ton - actual_cost_per_ton))
FROM vw_Margin_Detail WHERE fiscal_year = 2025;
```

---

## 3. PREDICTIVE QUERIES

### 3.1 Scenario Revenue Forecast
```sql
-- Revenue under different price scenarios
WITH base_forecast AS (
    SELECT 
        crop_type,
        forecast_volume,
        base_price
    FROM vw_Forecast_2025
)
SELECT 
    crop_type,
    forecast_volume,
    base_price,
    forecast_volume * base_price AS base_revenue,
    forecast_volume * base_price * 1.10 AS bull_revenue_price_plus_10,
    forecast_volume * base_price * 0.90 AS bear_revenue_price_minus_10,
    forecast_volume * 1.05 * base_price AS bull_revenue_vol_plus_5,
    forecast_volume * 0.95 * base_price AS bear_revenue_vol_minus_5
FROM base_forecast;
```

### 3.2 Yield Forecast Based on Historical
```sql
-- Historical yield distribution for forecasting
SELECT 
    crop_type,
    AVG(yield_tha) AS mean_yield,
    STDEV(yield_tha) AS std_dev,
    MIN(yield_tha) AS min_yield,
    MAX(yield_tha) AS max_yield,
    PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY yield_tha) AS p10_yield,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY yield_tha) AS p50_yield,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY yield_tha) AS p90_yield
FROM vw_Historical_Yields
WHERE harvest_year BETWEEN 2019 AND 2024
GROUP BY crop_type;
```

### 3.3 Sensitivity Matrix
```sql
-- Impact of price changes on GM
WITH current_forecast AS (
    SELECT 
        crop_type,
        forecast_volume,
        forecast_price,
        forecast_cost_per_ton,
        forecast_volume * (forecast_price - forecast_cost_per_ton) AS base_gm
    FROM vw_Forecast_2025
)
SELECT 
    crop_type,
    base_gm,
    forecast_volume * 10 AS gm_impact_per_10_dollar_price_change,
    forecast_volume * -5 AS gm_impact_per_5_dollar_cost_increase,
    forecast_volume * 0.05 * (forecast_price - forecast_cost_per_ton) AS gm_impact_5pct_volume_change
FROM current_forecast
ORDER BY base_gm DESC;
```

---

## 4. PRESCRIPTIVE QUERIES

### 4.1 Crop Profitability Ranking
```sql
-- Rank crops by profitability metrics for allocation decisions
SELECT 
    crop_type,
    SUM(gross_margin_usd) / SUM(area_ha) AS gm_per_ha,
    SUM(gross_margin_usd) / SUM(volume_tons) AS gm_per_ton,
    SUM(gross_margin_usd) / SUM(direct_cost_usd) AS return_on_cost,
    RANK() OVER (ORDER BY SUM(gross_margin_usd) / SUM(area_ha) DESC) AS rank_gm_per_ha,
    RANK() OVER (ORDER BY SUM(gross_margin_usd) / SUM(direct_cost_usd) DESC) AS rank_roi
FROM vw_Crop_Economics
WHERE fiscal_year = 2025
GROUP BY crop_type;
```

### 4.2 Optimal Crop Mix Analysis
```sql
-- Compare current vs optimal allocation
WITH crop_metrics AS (
    SELECT 
        crop_type,
        AVG(gm_per_ha) AS avg_gm_per_ha,
        SUM(area_ha) AS current_area,
        MAX_AREA.max_rotation_area -- from rotation constraints
    FROM vw_Crop_Economics c
    JOIN vw_Rotation_Limits MAX_AREA ON c.crop_type = MAX_AREA.crop_type
    WHERE fiscal_year = 2025
    GROUP BY crop_type, MAX_AREA.max_rotation_area
)
SELECT 
    crop_type,
    current_area,
    max_rotation_area,
    avg_gm_per_ha,
    CASE 
        WHEN avg_gm_per_ha > 300 AND current_area < max_rotation_area THEN 'INCREASE'
        WHEN avg_gm_per_ha < 150 THEN 'REDUCE'
        ELSE 'MAINTAIN'
    END AS recommendation,
    (max_rotation_area - current_area) * avg_gm_per_ha AS potential_gm_upside
FROM crop_metrics
ORDER BY avg_gm_per_ha DESC;
```

### 4.3 Cost Reduction Opportunities
```sql
-- Identify crops with above-average costs
WITH cost_benchmarks AS (
    SELECT 
        crop_type,
        AVG(cost_per_ton) AS avg_cost,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY cost_per_ton) AS best_quartile_cost
    FROM vw_Historical_Costs
    WHERE fiscal_year BETWEEN 2022 AND 2024
    GROUP BY crop_type
)
SELECT 
    c.crop_type,
    c.current_cost_per_ton,
    b.avg_cost AS historical_avg,
    b.best_quartile_cost AS best_practice_cost,
    (c.current_cost_per_ton - b.best_quartile_cost) AS cost_gap,
    (c.current_cost_per_ton - b.best_quartile_cost) * c.forecast_volume AS savings_potential
FROM vw_Current_Costs c
JOIN cost_benchmarks b ON c.crop_type = b.crop_type
WHERE c.current_cost_per_ton > b.avg_cost
ORDER BY savings_potential DESC;
```

---

## 5. SUPPORTING QUERIES

### 5.1 FX Impact Analysis
```sql
-- Revenue at different FX rates
SELECT 
    crop_type,
    SUM(revenue_usd) AS revenue_usd,
    SUM(revenue_usd) * 42.05 AS revenue_sar_current,
    SUM(revenue_usd) * 40.00 AS revenue_sar_strong_uah,
    SUM(revenue_usd) * 45.00 AS revenue_sar_weak_uah,
    (SUM(revenue_usd) * 45.00) - (SUM(revenue_usd) * 40.00) AS fx_exposure_range
FROM vw_Revenue_Detail
WHERE fiscal_year = 2025
GROUP BY crop_type;
```

### 5.2 Hedge Coverage
```sql
-- Unhedged volume exposure
SELECT 
    crop_type,
    total_forecast_volume,
    contracted_volume,
    hedged_volume,
    total_forecast_volume - contracted_volume - hedged_volume AS unhedged_volume,
    (total_forecast_volume - contracted_volume - hedged_volume) / 
        NULLIF(total_forecast_volume, 0) * 100 AS pct_unhedged
FROM vw_Sales_Coverage
WHERE fiscal_year = 2025
ORDER BY unhedged_volume DESC;
```

### 5.3 Period-over-Period Comparison
```sql
-- Year over year comparison
SELECT 
    account_category,
    SUM(CASE WHEN fiscal_year = 2025 THEN amount_sar ELSE 0 END) AS fy2025,
    SUM(CASE WHEN fiscal_year = 2024 THEN amount_sar ELSE 0 END) AS fy2024,
    SUM(CASE WHEN fiscal_year = 2025 THEN amount_sar ELSE 0 END) - 
    SUM(CASE WHEN fiscal_year = 2024 THEN amount_sar ELSE 0 END) AS yoy_change,
    (SUM(CASE WHEN fiscal_year = 2025 THEN amount_sar ELSE 0 END) / 
     NULLIF(SUM(CASE WHEN fiscal_year = 2024 THEN amount_sar ELSE 0 END), 0) - 1) * 100 AS yoy_pct
FROM vw_Fact_Actuals_SALIC_Ukraine
WHERE fiscal_year IN (2024, 2025)
GROUP BY account_category;
```

---

## NOTES FOR FABRIC DATA AGENT

### Table Naming Convention
- Views prefixed with `vw_` are preferred for querying
- Fact tables contain transactional data
- Dim tables contain reference data

### Key Joins
```sql
-- Standard join pattern
FROM vw_Fact_Actuals_SALIC_Ukraine f
JOIN vw_Dim_Entity e ON f.entity_key = e.entity_key
JOIN vw_Dim_Account a ON f.account_key = a.account_key
JOIN vw_Dim_Time t ON f.time_key = t.time_key
```

### Aggregation Levels
- Entity → SALIC Ukraine (single entity)
- Region → Farm clusters
- Crop → Individual crop types
- Period → Month/Quarter/Year

---

*Query Templates Version: 1.0*
*For Microsoft Fabric SALIC_Finance_Warehouse*
*December 2025*
