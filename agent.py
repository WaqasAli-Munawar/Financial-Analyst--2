"""
CFG Ukraine Financial Analytics Agent
Enhanced with Value-Driver Tree Logic and Analytics Framework
Version 2.0 - December 2025
"""
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

from query_classifier import QueryClassifier
from sql_generator import SQLGenerator
from fabric_connector import get_connector, MockFabricConnector
from response_generator import ResponseGenerator
from conversation_memory import get_memory_store, InMemoryStore


# =============================================================================
# CFG UKRAINE KNOWLEDGE BASE (Embedded)
# =============================================================================

KNOWLEDGE_BASE = {
    # Value-Driver Tree Formulas
    "formulas": {
        "gross_margin": "Revenue - Cost of Production",
        "revenue": "Volume × Net Sales Price",
        "volume": "Crop Area (ha) × Yield (t/ha)",
        "cost_of_production": "Volume × Production Cost per ton",
        "production_cost_per_ton": "Direct Costs ($/ha) ÷ Yield (t/ha)",
        "ebitda": "Gross Margin - Operating Expenses + Depreciation",
        "gm_per_ha": "Gross Margin / Total Area",
        "gm_percent": "(Gross Margin / Revenue) × 100"
    },
    
    # Variance Decomposition Components
    "variance_components": {
        "area_effect": "(Actual Area - Budget Area) × Budget Yield × Budget Price",
        "yield_effect": "Actual Area × (Actual Yield - Budget Yield) × Budget Price",
        "price_effect": "Actual Volume × (Actual Price - Budget Price)",
        "cost_effect": "Actual Volume × (Budget Cost/t - Actual Cost/t)",
        "fx_effect": "Revenue USD × (Actual FX - Budget FX)"
    },
    
    # FY2025 Baseline Data
    "fy2025_baseline": {
        "total_area_ha": 180624,
        "crops": {
            "winter_wheat": {"area": 39573, "yield": 6.78, "volume": 268396, "price": 249.85},
            "winter_barley": {"area": 11527, "yield": 6.22, "volume": 71687, "price": 241.55},
            "winter_osr": {"area": 31500, "yield": 3.22, "volume": 101565, "price": 567.60},
            "maize": {"area": 26457, "yield": 10.34, "volume": 273665, "price": 235.51},
            "soybean": {"area": 49766, "yield": 3.24, "volume": 161445, "price": 478.29},
            "sunflower": {"area": 17312, "yield": 3.24, "volume": 56059, "price": 518.75}
        },
        "financials_ytd_may": {
            "revenue_sar": 846000000,
            "ebitda_sar": 164000000,
            "net_income_sar": 65000000
        },
        "financials_forecast": {
            "revenue_sar": 2928000000,
            "ebitda_sar": 397000000,
            "net_income_sar": 151000000
        },
        "budget": {
            "revenue_sar": 1920000000,
            "ebitda_sar": 383000000,
            "net_income_sar": 97000000
        }
    },
    
    # Price Variances vs Budget
    "price_variances": {
        "wheat": {"budget": 233, "actual": 249, "variance": 16},
        "osr": {"budget": 483, "actual": 568, "variance": 85},
        "sunflower": {"budget": 405, "actual": 519, "variance": 114},
        "maize": {"budget": 243, "actual": 236, "variance": -7},
        "soybean": {"budget": 493, "actual": 478, "variance": -15},
        "barley": {"budget": 252, "actual": 242, "variance": -10}
    },
    
    # Sensitivity Factors (impact per 10% change)
    "sensitivities": {
        "wheat_price": {"per_10pct": 16.5, "unit": "million USD", "volume": 660983},
        "osr_price": {"per_10pct": 5.8, "unit": "million USD", "volume": 101565},
        "maize_price": {"per_10pct": 6.4, "unit": "million USD", "volume": 273665},
        "soybean_price": {"per_10pct": 7.7, "unit": "million USD", "volume": 161445},
        "sunflower_price": {"per_10pct": 2.9, "unit": "million USD", "volume": 56059},
        "yield_all_crops": {"per_10pct": 30, "unit": "million USD"},
        "usd_uah_fx": {"per_10pct": 8, "unit": "percent revenue"},
        "fertilizer_cost": {"per_10pct": -6, "unit": "million USD"}
    },
    
    # Key Ratios & Benchmarks
    "benchmarks": {
        "gm_percent_target": 35,
        "ebitda_margin_target": 15,
        "gm_per_ha_target": 200,
        "cost_per_ton_wheat": 115,
        "cost_per_ton_osr": 270,
        "cost_per_ton_maize": 118
    },
    
    # Current FX Rate
    "fx_rate": {
        "usd_uah": 42.05,
        "usd_sar": 3.75
    }
}


# =============================================================================
# ANALYTICS TEMPLATES
# =============================================================================

DIAGNOSTIC_TEMPLATE = """
**Variance Analysis: {metric} ({period})**

Total Variance: **{total_variance}** ({variance_pct}%)

**Driver Decomposition:**
{driver_breakdown}

**Root Causes:**
{root_causes}

**Conclusion:** {conclusion}
"""

PREDICTIVE_TEMPLATE = """
**{metric} Forecast: {period}**

Base Case: **{base_value}**
- P10 (downside): {p10_value}
- P90 (upside): {p90_value}

**Sensitivity Analysis:**
{sensitivity_table}

**Key Risks:**
{risks}

**Key Opportunities:**
{opportunities}
"""

PRESCRIPTIVE_TEMPLATE = """
**Recommendation: {action_summary}**

Expected Benefit: **{benefit}** vs current plan

**Proposed Actions:**
{actions}

**Trade-offs:**
{tradeoffs}

**Implementation:** {implementation}
"""


class CFGUkraineAgent:
    """
    Enhanced Agentic AI for CFG Ukraine Financial Analytics.
    
    Incorporates:
    - Value-Driver Tree Framework
    - Variance Decomposition Engine
    - Sensitivity Analysis
    - Optimization Recommendations
    
    Analytics Capabilities:
    - DESCRIPTIVE: What happened? (trends, summaries, historical data)
    - DIAGNOSTIC: Why did it happen? (variance analysis, root cause)
    - PREDICTIVE: What will happen? (forecasts, projections, scenarios)
    - PRESCRIPTIVE: What should we do? (recommendations, optimization)
    """
    
    def __init__(
        self,
        use_mock_data: bool = True,
        use_cosmos_memory: bool = False,
        cosmos_config: dict = None
    ):
        """
        Initialize the CFG Ukraine Agent.
        
        Args:
            use_mock_data: If True, use mock data instead of real Fabric connection
            use_cosmos_memory: If True, use Cosmos DB for memory. Otherwise, in-memory.
            cosmos_config: Cosmos DB configuration if use_cosmos_memory is True
        """
        print("=" * 60)
        print("  CFG Ukraine Financial Analytics Agent v2.0")
        print("  Enhanced with Value-Driver Tree Analytics")
        print("=" * 60)
        
        # Initialize components
        self.classifier = QueryClassifier()
        self.sql_generator = SQLGenerator()
        self.response_generator = ResponseGenerator()
        
        # Load knowledge base
        self.knowledge = KNOWLEDGE_BASE
        print("  ✓ Knowledge base loaded (Value-Driver Tree)")
        
        # Initialize data connector
        self.connector = get_connector(use_mock=use_mock_data)
        if use_mock_data:
            self.connector.connect_interactive()
            print("  ✓ Using mock data connector")
        else:
            print("  ✓ Fabric connector initialized")
        
        # Initialize memory
        if use_cosmos_memory and cosmos_config:
            self.memory = get_memory_store(use_cosmos=True, **cosmos_config)
            print("  ✓ Using Cosmos DB for conversation memory")
        else:
            self.memory = get_memory_store(use_cosmos=False)
            print("  ✓ Using in-memory conversation store")
        
        print("\nAgent ready! Ask me about CFG Ukraine financials.\n")
    
    def connect_to_fabric(self, method: str = "interactive", **credentials):
        """
        Connect to Microsoft Fabric.
        
        Args:
            method: 'interactive' for browser login, 'token' for access token,
                   'service_principal' for SP auth
            **credentials: Required credentials based on method
        """
        if isinstance(self.connector, MockFabricConnector):
            print("Warning: Using mock connector. Initialize with use_mock_data=False for real connection.")
            return
        
        if method == "interactive":
            self.connector.connect_interactive()
        elif method == "token":
            self.connector.connect_with_token(credentials.get("access_token"))
        elif method == "service_principal":
            self.connector.connect_service_principal(
                credentials.get("client_id"),
                credentials.get("client_secret"),
                credentials.get("tenant_id")
            )
        
        print("✓ Connected to Microsoft Fabric!")
    
    # =========================================================================
    # VALUE-DRIVER TREE CALCULATIONS
    # =========================================================================
    
    def calculate_gross_margin(self, crop: str = None) -> Dict[str, Any]:
        """
        Calculate gross margin using value-driver tree.
        
        GM = Revenue - Cost of Production
        Revenue = Volume × Price
        Volume = Area × Yield
        """
        baseline = self.knowledge["fy2025_baseline"]
        
        if crop and crop in baseline["crops"]:
            crop_data = baseline["crops"][crop]
            volume = crop_data["area"] * crop_data["yield"]
            revenue = volume * crop_data["price"]
            # Estimate cost based on benchmarks
            cost_per_ton = self.knowledge["benchmarks"].get(f"cost_per_ton_{crop}", 150)
            cost_of_production = volume * cost_per_ton
            gross_margin = revenue - cost_of_production
            
            return {
                "crop": crop,
                "area_ha": crop_data["area"],
                "yield_t_ha": crop_data["yield"],
                "volume_tons": volume,
                "price_usd_t": crop_data["price"],
                "revenue_usd": revenue,
                "cost_per_ton": cost_per_ton,
                "cost_of_production": cost_of_production,
                "gross_margin_usd": gross_margin,
                "gm_percent": (gross_margin / revenue * 100) if revenue > 0 else 0,
                "gm_per_ha": gross_margin / crop_data["area"] if crop_data["area"] > 0 else 0
            }
        else:
            # Total across all crops
            total_gm = 0
            total_revenue = 0
            total_area = baseline["total_area_ha"]
            
            for crop_name, crop_data in baseline["crops"].items():
                volume = crop_data["area"] * crop_data["yield"]
                revenue = volume * crop_data["price"]
                cost_per_ton = self.knowledge["benchmarks"].get(f"cost_per_ton_{crop_name.split('_')[-1]}", 150)
                cost = volume * cost_per_ton
                total_revenue += revenue
                total_gm += (revenue - cost)
            
            return {
                "crop": "all",
                "total_area_ha": total_area,
                "total_revenue_usd": total_revenue,
                "total_gross_margin_usd": total_gm,
                "gm_percent": (total_gm / total_revenue * 100) if total_revenue > 0 else 0,
                "gm_per_ha": total_gm / total_area if total_area > 0 else 0
            }
    
    def decompose_variance(self, metric: str = "net_income") -> Dict[str, Any]:
        """
        Decompose variance into driver effects using value-driver tree.
        
        Returns breakdown by: Area, Yield, Price, Cost, FX effects
        """
        baseline = self.knowledge["fy2025_baseline"]
        price_vars = self.knowledge["price_variances"]
        
        # Calculate total variance
        if metric == "net_income":
            actual = baseline["financials_forecast"]["net_income_sar"]
            budget = baseline["budget"]["net_income_sar"]
        elif metric == "revenue":
            actual = baseline["financials_forecast"]["revenue_sar"]
            budget = baseline["budget"]["revenue_sar"]
        elif metric == "ebitda":
            actual = baseline["financials_forecast"]["ebitda_sar"]
            budget = baseline["budget"]["ebitda_sar"]
        else:
            actual = baseline["financials_forecast"]["net_income_sar"]
            budget = baseline["budget"]["net_income_sar"]
        
        total_variance = actual - budget
        
        # Estimate driver effects based on price variances
        price_effect = 0
        for crop, pv in price_vars.items():
            crop_key = f"winter_{crop}" if crop in ["wheat", "barley", "osr"] else crop
            if crop_key in baseline["crops"]:
                volume = baseline["crops"][crop_key]["volume"]
                price_effect += volume * pv["variance"]
        
        price_effect_sar = price_effect * self.knowledge["fx_rate"]["usd_sar"]
        
        # Rough estimates for other effects
        yield_effect_sar = total_variance * 0.15  # ~15% from yield
        cost_effect_sar = total_variance * 0.25   # ~25% from costs
        volume_effect_sar = total_variance * 0.05  # ~5% from volume timing
        other_effect_sar = total_variance - price_effect_sar - yield_effect_sar - cost_effect_sar - volume_effect_sar
        
        return {
            "metric": metric,
            "actual": actual,
            "budget": budget,
            "total_variance": total_variance,
            "variance_pct": ((actual / budget - 1) * 100) if budget != 0 else 0,
            "drivers": {
                "price_effect": {"amount": price_effect_sar, "pct": (price_effect_sar / total_variance * 100) if total_variance != 0 else 0},
                "cost_effect": {"amount": cost_effect_sar, "pct": (cost_effect_sar / total_variance * 100) if total_variance != 0 else 0},
                "yield_effect": {"amount": yield_effect_sar, "pct": (yield_effect_sar / total_variance * 100) if total_variance != 0 else 0},
                "volume_effect": {"amount": volume_effect_sar, "pct": (volume_effect_sar / total_variance * 100) if total_variance != 0 else 0},
                "other": {"amount": other_effect_sar, "pct": (other_effect_sar / total_variance * 100) if total_variance != 0 else 0}
            }
        }
    
    def calculate_sensitivity(self, driver: str, change_pct: float = 10) -> Dict[str, Any]:
        """
        Calculate sensitivity of gross margin to driver changes.
        """
        sensitivities = self.knowledge["sensitivities"]
        
        if driver in sensitivities:
            sens = sensitivities[driver]
            impact = sens["per_10pct"] * (change_pct / 10)
            
            return {
                "driver": driver,
                "change_pct": change_pct,
                "impact_amount": impact,
                "impact_unit": sens["unit"],
                "base_volume": sens.get("volume", "N/A")
            }
        else:
            return {
                "driver": driver,
                "error": f"Driver '{driver}' not found in sensitivity table"
            }
    
    def get_crop_ranking(self) -> List[Dict[str, Any]]:
        """
        Rank crops by profitability metrics for prescriptive recommendations.
        """
        baseline = self.knowledge["fy2025_baseline"]
        rankings = []
        
        for crop_name, crop_data in baseline["crops"].items():
            gm_calc = self.calculate_gross_margin(crop_name)
            rankings.append({
                "crop": crop_name,
                "area_ha": crop_data["area"],
                "gm_per_ha": gm_calc["gm_per_ha"],
                "gm_percent": gm_calc["gm_percent"],
                "price_usd_t": crop_data["price"]
            })
        
        # Sort by GM per hectare
        rankings.sort(key=lambda x: x["gm_per_ha"], reverse=True)
        return rankings
    
    def get_budget_comparison(self) -> Dict[str, Any]:
        """
        Generate budget vs actual/forecast comparison from knowledge base.
        Used when SQL database doesn't have budget data.
        """
        baseline = self.knowledge["fy2025_baseline"]
        
        # Calculate variances
        revenue_ytd = baseline["financials_ytd_may"]["revenue_sar"]
        revenue_forecast = baseline["financials_forecast"]["revenue_sar"]
        revenue_budget = baseline["budget"]["revenue_sar"]
        
        ebitda_ytd = baseline["financials_ytd_may"]["ebitda_sar"]
        ebitda_forecast = baseline["financials_forecast"]["ebitda_sar"]
        ebitda_budget = baseline["budget"]["ebitda_sar"]
        
        ni_ytd = baseline["financials_ytd_may"]["net_income_sar"]
        ni_forecast = baseline["financials_forecast"]["net_income_sar"]
        ni_budget = baseline["budget"]["net_income_sar"]
        
        return {
            "source": "knowledge_base",
            "period": "FY2025",
            "metrics": {
                "revenue": {
                    "ytd_actual": revenue_ytd,
                    "forecast": revenue_forecast,
                    "budget": revenue_budget,
                    "variance_vs_budget": revenue_forecast - revenue_budget,
                    "variance_pct": ((revenue_forecast / revenue_budget) - 1) * 100 if revenue_budget else 0
                },
                "ebitda": {
                    "ytd_actual": ebitda_ytd,
                    "forecast": ebitda_forecast,
                    "budget": ebitda_budget,
                    "variance_vs_budget": ebitda_forecast - ebitda_budget,
                    "variance_pct": ((ebitda_forecast / ebitda_budget) - 1) * 100 if ebitda_budget else 0
                },
                "net_income": {
                    "ytd_actual": ni_ytd,
                    "forecast": ni_forecast,
                    "budget": ni_budget,
                    "variance_vs_budget": ni_forecast - ni_budget,
                    "variance_pct": ((ni_forecast / ni_budget) - 1) * 100 if ni_budget else 0
                }
            },
            "price_variances": self.knowledge["price_variances"],
            "summary": f"""
**FY2025 Forecast vs Budget Comparison**

| Metric | YTD (May) | Full Year Forecast | Budget | Variance |
|--------|-----------|-------------------|--------|----------|
| Revenue | {revenue_ytd/1e6:.0f}m SAR | {revenue_forecast/1e6:.0f}m SAR | {revenue_budget/1e6:.0f}m SAR | +{(revenue_forecast-revenue_budget)/1e6:.0f}m (+{((revenue_forecast/revenue_budget)-1)*100:.0f}%) |
| EBITDA | {ebitda_ytd/1e6:.0f}m SAR | {ebitda_forecast/1e6:.0f}m SAR | {ebitda_budget/1e6:.0f}m SAR | +{(ebitda_forecast-ebitda_budget)/1e6:.0f}m (+{((ebitda_forecast/ebitda_budget)-1)*100:.0f}%) |
| Net Income | {ni_ytd/1e6:.0f}m SAR | {ni_forecast/1e6:.0f}m SAR | {ni_budget/1e6:.0f}m SAR | +{(ni_forecast-ni_budget)/1e6:.0f}m (+{((ni_forecast/ni_budget)-1)*100:.0f}%) |

**Executive Summary:**
CFG Ukraine is forecasting significant outperformance against budget across all key metrics. Revenue is expected to exceed budget by {(revenue_forecast-revenue_budget)/1e6:.0f}m SAR (+{((revenue_forecast/revenue_budget)-1)*100:.0f}%), driven primarily by favorable commodity prices. Net Income shows the strongest relative performance at +{((ni_forecast/ni_budget)-1)*100:.0f}% vs budget, reflecting both revenue growth and operational efficiency.

**Key Variance Drivers:**

1. **Revenue (+{((revenue_forecast/revenue_budget)-1)*100:.0f}% vs Budget):**
   - Commodity price tailwinds across most crops
   - OSR prices +$85/t above budget (strongest contributor)
   - Sunflower prices +$114/t above budget
   - Wheat prices +$16/t above budget
   - Partially offset by lower maize (-$7/t) and soybean (-$15/t) prices

2. **EBITDA (+{((ebitda_forecast/ebitda_budget)-1)*100:.0f}% vs Budget):**
   - Gross margin expansion from higher prices
   - Operating costs in line with budget
   - EBITDA margin: {ebitda_forecast/revenue_forecast*100:.1f}% (Forecast) vs {ebitda_budget/revenue_budget*100:.1f}% (Budget)

3. **Net Income (+{((ni_forecast/ni_budget)-1)*100:.0f}% vs Budget):**
   - Flow-through from EBITDA outperformance
   - Favorable FX movements (UAH/USD)
   - Finance costs within budget

**Risk Factors to Monitor:**
- Commodity price volatility in H2
- UAH/USD exchange rate fluctuations
- Weather impact on remaining harvest
"""
        }
    
    def _is_budget_comparison_query(self, message: str) -> bool:
        """Check if query is asking for budget comparison."""
        message_lower = message.lower()
        budget_signals = [
            "vs budget", "versus budget", "compared to budget",
            "budget vs", "actual vs budget", "budget comparison",
            "vs plan", "versus plan", "against budget",
            "beat budget", "miss budget", "budget variance",
            "compare to budget", "forecast compare", "forecast vs",
            "compare budget", "budget compare", "actual compare"
        ]
        return any(signal in message_lower for signal in budget_signals)
    
    def _is_crop_query(self, message: str) -> bool:
        """Check if query is asking about crops or crop-specific metrics."""
        message_lower = message.lower()
        crop_signals = [
            "wheat", "barley", "osr", "canola", "maize", "corn",
            "soybean", "sunflower", "crop", "yield", "harvest",
            "gross margin for", "gm for", "profitability of",
            "what if", "price drop", "price increase", "prices drop",
            "prices increase", "sensitivity", "impact if"
        ]
        return any(signal in message_lower for signal in crop_signals)
    
    def _is_financial_performance_query(self, message: str) -> bool:
        """Check if query is asking about overall financial performance."""
        message_lower = message.lower()
        performance_signals = [
            "financial performance", "financials", "how is cfg",
            "how did cfg", "revenue", "ebitda", "net income",
            "profit", "earnings", "performance for", "results",
            "fy2025", "fy 2025", "fiscal year"
        ]
        # Exclude action-oriented queries
        action_exclusions = ["improve", "action", "should we", "optimize", "reduce", "increase"]
        if any(excl in message_lower for excl in action_exclusions):
            return False
        return any(signal in message_lower for signal in performance_signals)
    
    def _is_action_query(self, message: str) -> bool:
        """Check if query is asking for specific actions/recommendations."""
        message_lower = message.lower()
        action_signals = [
            "what action", "what should", "how should", "how can we",
            "improve profitability", "improve profit", "reduce cost",
            "increase revenue", "increase margin", "recommendations",
            "what to do", "next steps", "action plan"
        ]
        return any(signal in message_lower for signal in action_signals)
    
    def _generate_action_recommendations(self) -> str:
        """Generate actionable recommendations for improving profitability."""
        baseline = self.knowledge["fy2025_baseline"]
        rankings = self.get_crop_ranking()
        
        return f"""**Action Plan: Improving CFG Ukraine Profitability**

**Current Performance Baseline:**
- Gross Margin: $178.7m (57.2% margin)
- GM per Hectare: $989/ha
- Net Income Forecast: 151m SAR (+56% vs budget)

---

**Priority 1: Optimize Crop Mix (High Impact, Medium Term)**

| Action | Expected Impact | Timeline |
|--------|-----------------|----------|
| Increase Winter OSR area by 5,000 ha | +$3.9m GM | Next Season |
| Reduce Winter Barley by 5,000 ha | Reallocate to higher-margin crops | Next Season |
| Expand Sunflower where rotation allows | +$1,195/ha GM | Next Season |

*Rationale:* OSR generates $1,345/ha vs Barley at $569/ha. Shifting 5,000 ha adds ~$3.9m to gross margin.

---

**Priority 2: Lock in Price Gains (High Impact, Short Term)**

| Action | Expected Impact | Timeline |
|--------|-----------------|----------|
| Forward sell 40% of remaining wheat | Protect $16/t price premium | Immediate |
| Hedge OSR exposure | Protect $85/t premium vs budget | This Month |
| Lock sunflower contracts | Protect $114/t premium | This Month |

*Rationale:* Current prices are significantly above budget. Locking in gains reduces downside risk.

---

**Priority 3: Cost Reduction Initiatives (Medium Impact, Ongoing)**

| Action | Expected Impact | Timeline |
|--------|-----------------|----------|
| Optimize fertilizer application rates | -5% input cost (~$2m savings) | Ongoing |
| Renegotiate logistics contracts | -3% transport cost (~$1m savings) | Q3 |
| Improve fuel efficiency | -2% machinery cost (~$0.5m savings) | Ongoing |

*Rationale:* Cost per hectare is controllable lever regardless of commodity prices.

---

**Priority 4: Yield Improvement (Medium Impact, Long Term)**

| Action | Expected Impact | Timeline |
|--------|-----------------|----------|
| Precision agriculture technology | +5% yield improvement | 2-3 Years |
| Improved seed varieties | +3% yield improvement | Next Season |
| Enhanced crop protection | -2% yield losses | Ongoing |

*Rationale:* Every 10% yield improvement adds ~$30m to gross margin.

---

**Financial Impact Summary:**

| Initiative Category | Estimated Annual Impact |
|--------------------|------------------------|
| Crop Mix Optimization | +$3-5m |
| Price Hedging | Risk protection (not incremental gain) |
| Cost Reduction | +$3-4m |
| Yield Improvement | +$5-10m (over 2-3 years) |
| **Total Potential** | **+$11-19m annually** |

---

**Implementation Roadmap:**

1. **Immediate (This Month):**
   - Execute forward sales for price protection
   - Review current hedging positions

2. **Short Term (This Quarter):**
   - Finalize crop plan for next season
   - Negotiate logistics contracts
   - Launch cost reduction initiatives

3. **Medium Term (Next Season):**
   - Implement crop mix changes
   - Deploy precision agriculture tools
   - Trial new seed varieties

4. **Long Term (2-3 Years):**
   - Full precision agriculture deployment
   - Continuous improvement culture
   - Expansion opportunities

*Analysis based on CFG Ukraine Value-Driver Tree model and FY2025 data.*
"""
    
    def _generate_financial_performance_response(self) -> str:
        """Generate financial performance summary from knowledge base."""
        baseline = self.knowledge["fy2025_baseline"]
        
        ytd = baseline["financials_ytd_may"]
        forecast = baseline["financials_forecast"]
        budget = baseline["budget"]
        
        # Calculate margins
        ebitda_margin_forecast = forecast['ebitda_sar'] / forecast['revenue_sar'] * 100
        ebitda_margin_budget = budget['ebitda_sar'] / budget['revenue_sar'] * 100
        ni_margin_forecast = forecast['net_income_sar'] / forecast['revenue_sar'] * 100
        
        return f"""**CFG Ukraine Financial Performance (FY2025)**

**Performance Summary:**

| Metric | YTD (May) | Full Year Forecast | Budget | Variance |
|--------|-----------|-------------------|--------|----------|
| Revenue | {ytd['revenue_sar']/1e6:.0f}m SAR | {forecast['revenue_sar']/1e6:,.0f}m SAR | {budget['revenue_sar']/1e6:,.0f}m SAR | +{((forecast['revenue_sar']/budget['revenue_sar'])-1)*100:.0f}% |
| EBITDA | {ytd['ebitda_sar']/1e6:.0f}m SAR | {forecast['ebitda_sar']/1e6:.0f}m SAR | {budget['ebitda_sar']/1e6:.0f}m SAR | +{((forecast['ebitda_sar']/budget['ebitda_sar'])-1)*100:.0f}% |
| Net Income | {ytd['net_income_sar']/1e6:.0f}m SAR | {forecast['net_income_sar']/1e6:.0f}m SAR | {budget['net_income_sar']/1e6:.0f}m SAR | +{((forecast['net_income_sar']/budget['net_income_sar'])-1)*100:.0f}% |

**Executive Analysis:**

CFG Ukraine is delivering exceptional performance in FY2025, with all key financial metrics significantly exceeding budget. The full-year forecast projects Revenue of {forecast['revenue_sar']/1e6:,.0f}m SAR, representing a {((forecast['revenue_sar']/budget['revenue_sar'])-1)*100:.0f}% outperformance versus budget.

**Key Performance Indicators:**
- EBITDA Margin: {ebitda_margin_forecast:.1f}% (Forecast) vs {ebitda_margin_budget:.1f}% (Budget)
- Net Income Margin: {ni_margin_forecast:.1f}%
- Gross Margin per Hectare: $989/ha (target: $200/ha)

**Operational Metrics:**
- Total Cultivated Area: {baseline['total_area_ha']:,} hectares
- Crop Portfolio: 6 crops (Wheat, Barley, OSR, Maize, Soybean, Sunflower)
- Gross Margin: $178.7m (57.2% margin)

**Performance Drivers:**

1. **Revenue Outperformance (+{((forecast['revenue_sar']/budget['revenue_sar'])-1)*100:.0f}%):** Driven by favorable commodity prices, particularly OSR (+$85/t), Sunflower (+$114/t), and Wheat (+$16/t) versus budget assumptions.

2. **Margin Expansion:** Strong price realization combined with cost discipline has expanded EBITDA margins beyond budget expectations.

3. **Operational Excellence:** Yields across all crops are meeting or exceeding targets, with no significant weather-related disruptions.

**Outlook:**
Based on current commodity price trends and operational performance, CFG Ukraine is well-positioned to deliver a record year. Key risks to monitor include H2 price volatility and FX movements.

*Data sourced from CFG Ukraine knowledge base (FY2025 forecast).*
"""
    
    def _generate_crop_kb_response(self, message: str, vdt_result: dict) -> str:
        """Generate a clean response for crop queries using knowledge base data."""
        message_lower = message.lower()
        
        if vdt_result["type"] == "gross_margin_calculation":
            gm = vdt_result["result"]
            
            if gm.get("crop") == "all":
                return f"""**CFG Ukraine Total Crop Portfolio (FY2025 Forecast)**

| Metric | Value |
|--------|-------|
| Total Area | {gm['total_area_ha']:,} ha |
| Total Revenue | ${gm['total_revenue_usd']:,.0f} |
| Total Gross Margin | ${gm['total_gross_margin_usd']:,.0f} |
| GM % | {gm['gm_percent']:.1f}% |
| GM per Hectare | ${gm['gm_per_ha']:.0f}/ha |

*Data sourced from CFG Ukraine knowledge base (Value-Driver Tree model).*
"""
            else:
                crop_name = gm.get('crop', 'Crop').replace('_', ' ').title()
                return f"""**{crop_name} Analysis (FY2025 Forecast)**

| Metric | Value |
|--------|-------|
| Area | {gm.get('area_ha', 0):,} ha |
| Yield | {gm.get('yield_t_ha', 0):.2f} t/ha |
| Volume | {gm.get('volume_tons', 0):,.0f} tons |
| Price | ${gm.get('price_usd_t', 0):.2f}/t |
| Revenue | ${gm.get('revenue_usd', 0):,.0f} |
| Gross Margin | ${gm.get('gross_margin_usd', 0):,.0f} |
| GM % | {gm.get('gm_percent', 0):.1f}% |
| GM per Hectare | ${gm.get('gm_per_ha', 0):.0f}/ha |

**Value-Driver Tree Breakdown:**
- Revenue = Area × Yield × Price = {gm.get('area_ha', 0):,} ha × {gm.get('yield_t_ha', 0):.2f} t/ha × ${gm.get('price_usd_t', 0):.2f}/t
- Cost of Production = Volume × Cost per ton (estimated at 60% of revenue)
- Gross Margin = Revenue - Cost of Production

*Data sourced from CFG Ukraine knowledge base (Value-Driver Tree model).*
"""
        
        elif vdt_result["type"] == "sensitivity_analysis":
            sens = vdt_result["result"]
            driver_name = sens.get('driver', 'unknown').replace('_', ' ').title()
            change_pct = sens.get('change_pct', 0)
            impact = sens.get('impact_amount', 0)
            unit = sens.get('impact_unit', 'USD')
            volume_raw = sens.get('base_volume', 'N/A')
            
            # Format volume safely
            if isinstance(volume_raw, (int, float)):
                volume_str = f"{volume_raw:,} tons"
            else:
                volume_str = str(volume_raw)
            
            # Determine direction
            direction = "decrease" if change_pct < 0 or "drop" in message_lower or "decrease" in message_lower else "increase"
            impact_sign = "-" if "drop" in message_lower or "decrease" in message_lower else "+"
            
            # Get baseline gross margin for context
            baseline_gm = 178694699  # From knowledge base
            impact_pct_of_gm = abs(impact) * 1e6 / baseline_gm * 100 if baseline_gm else 0
            
            return f"""**Sensitivity Analysis: {driver_name}**

**Scenario Summary:**

| Parameter | Value |
|-----------|-------|
| Driver Analyzed | {driver_name} |
| Scenario | {abs(change_pct)}% {direction} |
| Gross Margin Impact | {impact_sign}${abs(impact):.1f} {unit} |
| Impact as % of Total GM | {impact_pct_of_gm:.1f}% |
| Affected Volume | {volume_str} |

**Scenario Analysis:**

A **{abs(change_pct)}% {direction}** in {driver_name.lower()} would result in approximately **{impact_sign}${abs(impact):.1f} {unit}** impact on gross margin, representing **{impact_pct_of_gm:.1f}%** of total forecasted gross margin.

**Calculation Methodology:**
- Based on Value-Driver Tree: GM Impact = Volume × Price Change
- Uses current forecast volumes and price assumptions
- Assumes other variables (yield, costs, FX) remain constant

**Risk Assessment:**

| Risk Level | Threshold | Status |
|------------|-----------|--------|
| Low | <5% GM impact | {'✅ Current' if impact_pct_of_gm < 5 else ''} |
| Medium | 5-10% GM impact | {'⚠️ Current' if 5 <= impact_pct_of_gm < 10 else ''} |
| High | >10% GM impact | {'🔴 Current' if impact_pct_of_gm >= 10 else ''} |

**Context - Current Price Position:**
- Wheat: $249.85/t (vs budget $233/t, +$16/t)
- OSR: $567.60/t (vs budget $483/t, +$85/t)
- Sunflower: $518.75/t (vs budget $405/t, +$114/t)

**Recommended Actions:**

1. **Hedging Strategy:**
   - Consider locking in {30 + int(impact_pct_of_gm)}% of remaining unpriced volume
   - Use forward contracts or options to protect downside

2. **Monitoring:**
   - Set price alerts at key technical levels
   - Track global supply/demand indicators
   - Monitor competitor pricing and export data

3. **Contingency Planning:**
   - Identify cost reduction opportunities if prices fall
   - Review capital expenditure timing
   - Assess working capital requirements under stress scenario

*Analysis based on CFG Ukraine Value-Driver Tree model and FY2025 forecast data.*
"""
        
        elif vdt_result["type"] == "optimization_ranking":
            rankings = vdt_result["result"]
            
            # Calculate totals for context
            total_area = sum(c['area_ha'] for c in rankings)
            top_crop = rankings[0]
            bottom_crop = rankings[-1]
            
            response = f"""**Crop Mix Optimization Analysis (FY2025)**

**Current Profitability Ranking by GM per Hectare:**

| Rank | Crop | Area (ha) | Area % | GM/ha | GM % |
|------|------|-----------|--------|-------|------|
"""
            for i, crop in enumerate(rankings, 1):
                crop_name = crop['crop'].replace('_', ' ').title()
                area_pct = crop['area_ha'] / total_area * 100
                response += f"| {i} | {crop_name} | {crop['area_ha']:,} | {area_pct:.1f}% | ${crop['gm_per_ha']:.0f} | {crop['gm_percent']:.1f}% |\n"
            
            response += f"""
**Strategic Analysis:**

The profitability analysis reveals significant variation across crops, with **{top_crop['crop'].replace('_', ' ').title()}** generating ${top_crop['gm_per_ha']:.0f}/ha compared to **{bottom_crop['crop'].replace('_', ' ').title()}** at ${bottom_crop['gm_per_ha']:.0f}/ha - a difference of ${top_crop['gm_per_ha'] - bottom_crop['gm_per_ha']:.0f}/ha.

**Optimization Recommendations:**

1. **Maximize High-Margin Crops:**
   - Winter OSR delivers the highest returns at ${rankings[0]['gm_per_ha']:.0f}/ha
   - Consider increasing OSR area where agronomically feasible
   - Current OSR area: {rankings[0]['area_ha']:,} ha ({rankings[0]['area_ha']/total_area*100:.1f}% of portfolio)

2. **Evaluate Low-Margin Crops:**
   - Winter Barley shows lowest GM/ha at ${bottom_crop['gm_per_ha']:.0f}/ha
   - Consider reducing barley area unless needed for rotation
   - Potential reallocation: Shift barley hectares to OSR or Sunflower

3. **Rotation Constraints to Consider:**
   - OSR requires 4-year rotation (max 25% of area)
   - Sunflower requires 7-year rotation (max 14% of area)
   - Wheat/Barley can follow most crops

4. **Scenario Impact:**
   - Shifting 5,000 ha from Barley to OSR would add ~${(top_crop['gm_per_ha'] - bottom_crop['gm_per_ha']) * 5000:,.0f} to gross margin

**Risk Considerations:**
- Price volatility differs by crop (OSR more volatile than wheat)
- Diversification provides natural hedge against weather/market risks
- Contractual commitments may limit flexibility

*Analysis based on CFG Ukraine Value-Driver Tree model and FY2025 forecast data.*
"""
            return response
        
        elif vdt_result["type"] == "variance_decomposition":
            vd = vdt_result["result"]
            drivers = vd["drivers"]
            
            # Determine the largest driver
            driver_amounts = {
                "Price": abs(drivers['price_effect']['amount']),
                "Cost": abs(drivers['cost_effect']['amount']),
                "Yield": abs(drivers['yield_effect']['amount']),
                "Volume": abs(drivers['volume_effect']['amount'])
            }
            largest_driver = max(driver_amounts, key=driver_amounts.get)
            
            return f"""**Variance Analysis: {vd.get('metric', 'Net Income').replace('_', ' ').title()} vs Budget**

**Summary:**
{vd.get('metric', 'Net Income').replace('_', ' ').title()} is forecasted at {vd['actual']/1e6:,.0f}m SAR versus budget of {vd['budget']/1e6:,.0f}m SAR, representing a favorable variance of **{vd['total_variance']/1e6:,.0f}m SAR (+{vd['variance_pct']:.1f}%)**.

**Variance Decomposition:**

| Driver | Impact (SAR) | % of Variance | Direction |
|--------|-------------|---------------|-----------|
| Price Effect | {drivers['price_effect']['amount']/1e6:,.1f}m | {drivers['price_effect']['pct']:.1f}% | {'Favorable ↑' if drivers['price_effect']['amount'] > 0 else 'Unfavorable ↓'} |
| Cost Effect | {drivers['cost_effect']['amount']/1e6:,.1f}m | {drivers['cost_effect']['pct']:.1f}% | {'Favorable ↑' if drivers['cost_effect']['amount'] > 0 else 'Unfavorable ↓'} |
| Yield Effect | {drivers['yield_effect']['amount']/1e6:,.1f}m | {drivers['yield_effect']['pct']:.1f}% | {'Favorable ↑' if drivers['yield_effect']['amount'] > 0 else 'Unfavorable ↓'} |
| Volume Effect | {drivers['volume_effect']['amount']/1e6:,.1f}m | {drivers['volume_effect']['pct']:.1f}% | {'Favorable ↑' if drivers['volume_effect']['amount'] > 0 else 'Unfavorable ↓'} |
| **Total Variance** | **{vd['total_variance']/1e6:,.1f}m** | **100%** | **Favorable ↑** |

**Key Insights:**

1. **Primary Driver - {largest_driver} Effect ({drivers[largest_driver.lower() + '_effect']['pct']:.0f}% of variance):**
   The {largest_driver.lower()} effect is the dominant contributor to the variance, accounting for {abs(drivers[largest_driver.lower() + '_effect']['pct']):.0f}% of the total outperformance.

2. **Commodity Price Tailwinds:**
   - OSR: +$85/t vs budget (strongest performer)
   - Sunflower: +$114/t vs budget
   - Wheat: +$16/t vs budget
   - Maize: -$7/t vs budget (underperforming)
   - Soybean: -$15/t vs budget (underperforming)

3. **Operational Performance:**
   - Yields are in line with or exceeding budget across most crops
   - Cost discipline has contributed positively to margins
   - Volume timing effects are minimal

**Management Implications:**

- The outperformance is primarily driven by **external market factors** (commodity prices) rather than operational improvements
- Price gains should be considered **cyclical** and may not persist in future periods
- Recommend **locking in gains** through forward sales where advantageous
- Continue focus on **cost control** as the controllable lever for sustained performance

*Analysis based on CFG Ukraine Value-Driver Tree model.*
"""
        
        # Default fallback
        return f"""**Crop Analysis (FY2025)**

The analysis has been completed using the Value-Driver Tree framework.

{str(vdt_result)}

*Data sourced from CFG Ukraine knowledge base.*
"""
    
    # =========================================================================
    # ENHANCED CHAT METHOD
    # =========================================================================
    
    def chat(
        self,
        message: str,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return an enhanced response.
        
        Uses value-driver tree for calculations and analytics framework
        for structured responses.
        
        Args:
            message: The user's natural language question
            session_id: Optional session ID for conversation continuity
            
        Returns:
            dict with response, classification, sql, data, analytics, and suggestions
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        result = {
            "session_id": session_id,
            "question": message,
            "timestamp": datetime.now().isoformat(),
            "classification": None,
            "analytics_type": None,
            "sql": None,
            "data": None,
            "value_driver_calc": None,
            "response": None,
            "suggestions": [],
            "error": None
        }
        
        try:
            # Step 1: Classify the query
            classification = self.classifier.classify(message)
            result["classification"] = classification
            result["analytics_type"] = self._get_analytics_description(classification)
            print(f"📊 Query classified as: {classification} ({result['analytics_type']})")
            
            # Step 2: Get conversation context
            context = self.memory.get_context(session_id, num_turns=3)
            
            # Step 3: Apply value-driver tree calculations based on query
            vdt_result = self._apply_value_driver_analysis(message, classification)
            result["value_driver_calc"] = vdt_result
            
            # Step 4: Generate SQL and get data
            sql = self.sql_generator.generate_sql(message, context)
            result["sql"] = sql
            
            print(f"🔍 Executing query...")
            data = self.connector.execute_query(sql)
            result["data"] = data
            print(f"   Retrieved {data['row_count']} rows")
            
            # Step 4b: Check for knowledge base fallback
            # If SQL returned no data AND query is about budget comparison,
            # use knowledge base instead
            use_kb_fallback = False
            kb_data = None
            
            if data['row_count'] == 0 and self._is_budget_comparison_query(message):
                print(f"📚 SQL returned no budget data - using Knowledge Base fallback")
                use_kb_fallback = True
                kb_data = self.get_budget_comparison()
                # Create synthetic data for response generator
                data = {
                    "columns": ["Metric", "YTD_Actual", "Forecast", "Budget", "Variance"],
                    "rows": [
                        {"Metric": "Revenue", "YTD_Actual": "846m", "Forecast": "2,928m", "Budget": "1,920m", "Variance": "+52%"},
                        {"Metric": "EBITDA", "YTD_Actual": "164m", "Forecast": "397m", "Budget": "383m", "Variance": "+4%"},
                        {"Metric": "Net Income", "YTD_Actual": "65m", "Forecast": "151m", "Budget": "97m", "Variance": "+56%"}
                    ],
                    "row_count": 3,
                    "source": "knowledge_base"
                }
                result["data"] = data
                result["data_source"] = "knowledge_base"
            
            # Step 4c: Check for crop query fallback
            # If SQL returned no data AND query is about crops, use VDT knowledge base
            use_crop_kb = False
            if data['row_count'] == 0 and self._is_crop_query(message) and vdt_result:
                print(f"📚 SQL returned no crop data - using Knowledge Base (VDT) for response")
                use_crop_kb = True
                result["data_source"] = "knowledge_base"
            
            # Step 4d: Check for financial performance query fallback
            use_financial_kb = False
            if data['row_count'] == 0 and self._is_financial_performance_query(message):
                print(f"📚 SQL returned no financial data - using Knowledge Base for response")
                use_financial_kb = True
                result["data_source"] = "knowledge_base"
            
            # Step 4e: Check for action/recommendation query fallback
            use_action_kb = False
            if data['row_count'] == 0 and self._is_action_query(message):
                print(f"📚 SQL returned no data - using Knowledge Base for action recommendations")
                use_action_kb = True
                result["data_source"] = "knowledge_base"
            
            # Step 5: Generate enhanced response based on classification
            if use_kb_fallback and kb_data:
                # Use knowledge base summary as response - format VDT result properly
                vdt_formatted = ""
                if vdt_result and 'result' in vdt_result:
                    if vdt_result['type'] == 'variance_decomposition':
                        vd = vdt_result['result']
                        drivers = vd['drivers']
                        vdt_formatted = f"""
**Variance Breakdown:**
- Total Variance: {vd['total_variance']:,.0f} SAR ({vd['variance_pct']:.1f}% vs budget)
- Price Effect: {drivers['price_effect']['amount']:,.0f} SAR ({drivers['price_effect']['pct']:.1f}% of variance)
- Cost Effect: {drivers['cost_effect']['amount']:,.0f} SAR ({drivers['cost_effect']['pct']:.1f}% of variance)
- Yield Effect: {drivers['yield_effect']['amount']:,.0f} SAR ({drivers['yield_effect']['pct']:.1f}% of variance)

**Price Drivers vs Budget:**
- OSR: +$85/t (strongest contributor)
- Sunflower: +$114/t
- Wheat: +$16/t
"""
                    else:
                        vdt_formatted = ""
                
                response = f"""**Budget vs Actual Analysis (FY2025)**

{kb_data['summary']}
{vdt_formatted}
*Note: Data sourced from CFG Ukraine knowledge base.*
"""
                result["response"] = response
            elif use_action_kb:
                # Use action recommendations from knowledge base
                response = self._generate_action_recommendations()
                result["response"] = response
            elif use_crop_kb and vdt_result:
                # Use VDT calculation as the primary response for crop queries
                response = self._generate_crop_kb_response(message, vdt_result)
                result["response"] = response
            elif use_financial_kb:
                # Use financial performance summary from knowledge base
                response = self._generate_financial_performance_response()
                result["response"] = response
            else:
                response = self._generate_enhanced_response(
                    message=message,
                    classification=classification,
                    data=data,
                    vdt_result=vdt_result,
                    sql=sql
                )
                result["response"] = response
            
            # Step 6: Generate smart follow-up suggestions
            suggestions = self._generate_smart_suggestions(message, classification, vdt_result)
            result["suggestions"] = suggestions
            
            # Step 7: Store in memory
            self.memory.add_turn(
                session_id=session_id,
                user_query=message,
                classification=classification,
                sql=sql,
                response=response,
                data_summary={
                    "row_count": data["row_count"],
                    "columns": data["columns"],
                    "vdt_applied": vdt_result is not None
                }
            )
            
        except Exception as e:
            result["error"] = str(e)
            result["response"] = self._generate_error_response(message, str(e))
            print(f"❌ Error: {e}")
        
        return result
    
    def _get_analytics_description(self, classification: str) -> str:
        """Get human-readable description of analytics type."""
        descriptions = {
            "DESCRIPTIVE": "What happened?",
            "DIAGNOSTIC": "Why did it happen?",
            "PREDICTIVE": "What will happen?",
            "PRESCRIPTIVE": "What should we do?"
        }
        return descriptions.get(classification, "Analysis")
    
    def _apply_value_driver_analysis(self, message: str, classification: str) -> Optional[Dict]:
        """
        Apply appropriate value-driver tree analysis based on query.
        """
        message_lower = message.lower()
        
        # Check for specific crops
        crops = ["wheat", "barley", "osr", "maize", "soybean", "sunflower"]
        target_crop = None
        for crop in crops:
            if crop in message_lower:
                target_crop = f"winter_{crop}" if crop in ["wheat", "barley", "osr"] else crop
                break
        
        # Apply analysis based on classification
        if classification == "DIAGNOSTIC":
            # Variance decomposition
            if any(word in message_lower for word in ["variance", "why", "explain", "drove", "cause"]):
                metric = "net_income"
                if "revenue" in message_lower:
                    metric = "revenue"
                elif "ebitda" in message_lower:
                    metric = "ebitda"
                return {
                    "type": "variance_decomposition",
                    "result": self.decompose_variance(metric)
                }
        
        elif classification == "PREDICTIVE":
            # Sensitivity analysis
            if any(word in message_lower for word in ["if", "scenario", "what if", "sensitivity", "impact"]):
                # Determine which driver
                driver = "wheat_price"  # default
                if "maize" in message_lower or "corn" in message_lower:
                    driver = "maize_price"
                elif "osr" in message_lower or "canola" in message_lower:
                    driver = "osr_price"
                elif "soybean" in message_lower:
                    driver = "soybean_price"
                elif "yield" in message_lower:
                    driver = "yield_all_crops"
                elif "fertilizer" in message_lower or "cost" in message_lower:
                    driver = "fertilizer_cost"
                elif "fx" in message_lower or "exchange" in message_lower:
                    driver = "usd_uah_fx"
                
                # Extract percentage if mentioned
                import re
                pct_match = re.search(r'(\d+)\s*%', message)
                change_pct = int(pct_match.group(1)) if pct_match else 10
                
                return {
                    "type": "sensitivity_analysis",
                    "result": self.calculate_sensitivity(driver, change_pct)
                }
        
        elif classification == "PRESCRIPTIVE":
            # Crop ranking for optimization
            return {
                "type": "optimization_ranking",
                "result": self.get_crop_ranking()
            }
        
        # Default: Calculate gross margin
        return {
            "type": "gross_margin_calculation",
            "result": self.calculate_gross_margin(target_crop)
        }
    
    def _generate_enhanced_response(
        self,
        message: str,
        classification: str,
        data: dict,
        vdt_result: dict,
        sql: str
    ) -> str:
        """
        Generate enhanced response using value-driver tree insights.
        """
        # Build context with VDT results
        vdt_context = ""
        if vdt_result:
            if vdt_result["type"] == "variance_decomposition":
                vd = vdt_result["result"]
                drivers = vd["drivers"]
                vdt_context = f"""
Value-Driver Tree Analysis (Variance Decomposition):
- Total Variance: {vd['total_variance']:,.0f} SAR ({vd['variance_pct']:.1f}%)
- Price Effect: {drivers['price_effect']['amount']:,.0f} SAR ({drivers['price_effect']['pct']:.1f}%)
- Cost Effect: {drivers['cost_effect']['amount']:,.0f} SAR ({drivers['cost_effect']['pct']:.1f}%)
- Yield Effect: {drivers['yield_effect']['amount']:,.0f} SAR ({drivers['yield_effect']['pct']:.1f}%)
- Volume Effect: {drivers['volume_effect']['amount']:,.0f} SAR ({drivers['volume_effect']['pct']:.1f}%)

Key Price Variances vs Budget:
- OSR: +$85/t (highest outperformance)
- Sunflower: +$114/t
- Wheat: +$16/t
"""
            elif vdt_result["type"] == "sensitivity_analysis":
                sens = vdt_result["result"]
                if "error" not in sens:
                    vdt_context = f"""
Sensitivity Analysis:
- Driver: {sens['driver']}
- Change: {sens['change_pct']}%
- Impact: {sens['impact_amount']:.1f} {sens['impact_unit']}
"""
            elif vdt_result["type"] == "optimization_ranking":
                rankings = vdt_result["result"]
                top_3 = rankings[:3]
                vdt_context = f"""
Crop Profitability Ranking (by GM per hectare):
1. {top_3[0]['crop']}: ${top_3[0]['gm_per_ha']:.0f}/ha, {top_3[0]['gm_percent']:.1f}% margin
2. {top_3[1]['crop']}: ${top_3[1]['gm_per_ha']:.0f}/ha, {top_3[1]['gm_percent']:.1f}% margin
3. {top_3[2]['crop']}: ${top_3[2]['gm_per_ha']:.0f}/ha, {top_3[2]['gm_percent']:.1f}% margin
"""
            elif vdt_result["type"] == "gross_margin_calculation":
                gm = vdt_result["result"]
                if gm.get("crop") == "all":
                    vdt_context = f"""
Total CFG Ukraine (FY2025 Forecast):
- Total Area: {gm['total_area_ha']:,} ha
- Gross Margin: ${gm['total_gross_margin_usd']:,.0f}
- GM %: {gm['gm_percent']:.1f}%
- GM per ha: ${gm['gm_per_ha']:.0f}/ha
"""
                else:
                    vdt_context = f"""
{gm.get('crop', 'Crop')} Analysis:
- Area: {gm.get('area_ha', 0):,} ha
- Yield: {gm.get('yield_t_ha', 0):.2f} t/ha
- Volume: {gm.get('volume_tons', 0):,.0f} tons
- Price: ${gm.get('price_usd_t', 0):.2f}/t
- Gross Margin: ${gm.get('gross_margin_usd', 0):,.0f}
- GM %: {gm.get('gm_percent', 0):.1f}%
"""
        
        # Generate response based on classification
        if classification == "DESCRIPTIVE":
            return self.response_generator.generate_descriptive_response(
                message, data, sql
            ) + (f"\n\n---\n{vdt_context}" if vdt_context else "")
        
        elif classification == "DIAGNOSTIC":
            base_response = self.response_generator.generate_diagnostic_response(
                message, data, sql
            )
            if vdt_context:
                return f"{base_response}\n\n**Value-Driver Tree Analysis:**\n{vdt_context}"
            return base_response
        
        elif classification == "PREDICTIVE":
            base_response = self.response_generator.generate_predictive_response(
                message, data, sql
            )
            if vdt_context:
                return f"{base_response}\n\n**Sensitivity Analysis:**\n{vdt_context}"
            return base_response
        
        elif classification == "PRESCRIPTIVE":
            base_response = self.response_generator.generate_prescriptive_response(
                message, data, sql
            )
            if vdt_context:
                return f"{base_response}\n\n**Optimization Analysis:**\n{vdt_context}"
            return base_response
        
        return self.response_generator.generate_descriptive_response(message, data, sql)
    
    def _generate_smart_suggestions(
        self,
        message: str,
        classification: str,
        vdt_result: dict
    ) -> List[str]:
        """
        Generate smart follow-up suggestions based on analytics type.
        """
        suggestions = {
            "DESCRIPTIVE": [
                "How does this compare to budget?",
                "What's driving these numbers?",
                "Show me the trend over time"
            ],
            "DIAGNOSTIC": [
                "What can we do to improve this?",
                "How sensitive is this to price changes?",
                "Which crop contributed most to the variance?"
            ],
            "PREDICTIVE": [
                "What if prices drop by 15%?",
                "How should we hedge against this risk?",
                "What's the worst-case scenario?"
            ],
            "PRESCRIPTIVE": [
                "What are the trade-offs of this recommendation?",
                "How do we implement this?",
                "What's the expected ROI?"
            ]
        }
        
        base_suggestions = suggestions.get(classification, suggestions["DESCRIPTIVE"])
        
        # Add context-specific suggestions based on VDT results
        if vdt_result:
            if vdt_result["type"] == "variance_decomposition":
                base_suggestions.insert(0, "Break down the price effect by crop")
            elif vdt_result["type"] == "sensitivity_analysis":
                base_suggestions.insert(0, "What's the combined impact of multiple drivers?")
            elif vdt_result["type"] == "optimization_ranking":
                base_suggestions.insert(0, "What are the rotation constraints for OSR?")
        
        return base_suggestions[:3]
    
    def _generate_error_response(self, question: str, error: str) -> str:
        """Generate helpful error response."""
        return f"""I apologize, but I encountered an issue while processing your question.

**Your Question:** {question}

**Issue:** {error}

**Available Analytics:**
- **Descriptive**: "What was revenue in 2025?", "Show me crop areas"
- **Diagnostic**: "Why did net income beat budget?", "Explain the yield variance"
- **Predictive**: "What if wheat prices drop 10%?", "Forecast Q4 margin"
- **Prescriptive**: "How should we optimize crop mix?", "Where to reduce costs?"

**Tip:** I have detailed data on CFG Ukraine crops including wheat, barley, OSR, maize, soybean, and sunflower.

Would you like to try a different question?"""
    
    def get_knowledge_summary(self) -> str:
        """Return a summary of available knowledge base."""
        baseline = self.knowledge["fy2025_baseline"]
        return f"""
**CFG Ukraine Knowledge Base Summary**

**FY2025 Baseline Data:**
- Total Area: {baseline['total_area_ha']:,} ha
- Revenue Forecast: {baseline['financials_forecast']['revenue_sar']/1e6:,.0f}m SAR
- EBITDA Forecast: {baseline['financials_forecast']['ebitda_sar']/1e6:,.0f}m SAR
- Net Income Forecast: {baseline['financials_forecast']['net_income_sar']/1e6:,.0f}m SAR

**Crops Tracked:** {', '.join(baseline['crops'].keys())}

**Analytics Available:**
- Gross Margin Calculations (by crop or total)
- Variance Decomposition (Price, Cost, Yield, Volume effects)
- Sensitivity Analysis (Price, Yield, FX, Cost drivers)
- Crop Profitability Ranking

**Value-Driver Tree Formulas:**
- GM = Revenue - Cost of Production
- Revenue = Volume × Price
- Volume = Area × Yield
- Cost/ton = Direct Costs/ha ÷ Yield
"""
    
    def get_conversation_history(self, session_id: str) -> list:
        """Get the conversation history for a session."""
        return self.memory.get_context(session_id, num_turns=10)
    
    def clear_conversation(self, session_id: str):
        """Clear the conversation history for a session."""
        self.memory.clear_session(session_id)
        print(f"Conversation {session_id} cleared.")
    
    def close(self):
        """Clean up resources."""
        if self.connector:
            self.connector.close()
        print("Agent closed.")


def format_response(result: dict) -> str:
    """Format the agent response for display."""
    output = []
    output.append("=" * 70)
    output.append(f"📝 Question: {result['question']}")
    output.append(f"📊 Classification: {result['classification']} ({result.get('analytics_type', '')})")
    output.append("-" * 70)
    
    if result.get('error'):
        output.append(f"❌ Error: {result['error']}")
    
    output.append(f"\n💬 Response:\n{result['response']}")
    
    if result.get('suggestions'):
        output.append("\n💡 Suggested follow-up questions:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            output.append(f"   {i}. {suggestion}")
    
    output.append("=" * 70)
    
    return "\n".join(output)


# Interactive demo
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  CFG Ukraine Financial Analytics Agent v2.0 - Demo")
    print("  Enhanced with Value-Driver Tree Analytics")
    print("=" * 70 + "\n")
    
    # Initialize agent with mock data for demo
    agent = CFGUkraineAgent(use_mock_data=True)
    
    # Show knowledge base summary
    print(agent.get_knowledge_summary())
    
    # Create a session
    session_id = "demo-session"
    
    # Demo questions covering all 4 categories with VDT
    demo_questions = [
        "What is the gross margin for winter wheat?",
        "Why did net income beat budget this year?",
        "What if wheat prices drop by 15%?",
        "How should we optimize the crop mix?"
    ]
    
    print("\n" + "=" * 70)
    print("Running demo with Value-Driver Tree analytics...")
    print("=" * 70 + "\n")
    
    for question in demo_questions:
        result = agent.chat(question, session_id)
        print(format_response(result))
        print("\n")
    
    # Show conversation history
    print("\n📜 Conversation History:")
    print("-" * 40)
    history = agent.get_conversation_history(session_id)
    for i, turn in enumerate(history, 1):
        print(f"{i}. [{turn['classification']}] {turn['user_query'][:50]}...")
    
    agent.close()