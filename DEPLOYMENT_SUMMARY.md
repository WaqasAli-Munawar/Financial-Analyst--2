# CFG Ukraine Financial Analytics Agent
## Deployment Package Summary

---

## PACKAGE CONTENTS

| File | Purpose | Use In |
|------|---------|--------|
| `CFG_Ukraine_Knowledge_Base.md` | Comprehensive reference data | Agent context/instructions |
| `Agent_Instructions.md` | Agent behavior & response templates | Azure AI Foundry instructions |
| `Independent_Variables_Reference.md` | 86 variables with analytics mapping | Reference document |
| `SQL_Query_Templates.md` | Query patterns for Fabric Data Agent | Tool configuration |

---

## DEPLOYMENT OPTIONS

### Option 1: Azure AI Foundry Portal Agent (Recommended)

**Setup Steps:**
1. Navigate to Azure AI Foundry → Agent playground
2. Create new agent with GPT-4o model
3. Copy `Agent_Instructions.md` content to Instructions field
4. Add Fabric Data Agent as tool (native integration)
5. Configure Fabric connection to SALIC_Finance_Warehouse
6. Test with sample queries

**Advantages:**
- 100% Microsoft-native solution
- No code deployment required
- Native Fabric integration
- IT-friendly architecture

### Option 2: Azure AI Agent Service with SDK

**Setup Steps:**
1. Deploy via Azure AI Foundry SDK
2. Use existing Python connection code
3. Deploy to Azure App Service (requires Contributor role)

**Advantages:**
- More customization options
- Programmatic control
- Can integrate additional tools

---

## CONFIGURATION FOR FABRIC DATA AGENT

### Connection Details
```
Workspace: SALIC_Analytics
Lakehouse: SALIC_Finance_Warehouse
Authentication: Service Principal
Tenant ID: [from IT]
Client ID: [from IT]
Client Secret: [from IT]
```

### Tables Available
- vw_Fact_Actuals_SALIC_Ukraine
- vw_Dim_Entity
- vw_Dim_Account
- vw_Dim_Time
- Additional views as created

---

## ANALYTICS CAPABILITIES MATRIX

| Query Type | Capability | Example |
|------------|------------|---------|
| **Descriptive** | Report metrics, show totals | "What was May revenue?" |
| **Diagnostic** | Variance decomposition | "Why did GM beat budget?" |
| **Predictive** | Scenario analysis | "What if prices drop 10%?" |
| **Prescriptive** | Recommendations | "How to optimize crop mix?" |

---

## TESTING CHECKLIST

### Descriptive Queries
- [ ] "What is CFG Ukraine's revenue for 2025?"
- [ ] "Show me EBITDA by quarter"
- [ ] "What are the crop areas?"

### Diagnostic Queries
- [ ] "Why did net income exceed budget?"
- [ ] "What drove the yield variance?"
- [ ] "Explain the cost increase"

### Predictive Queries
- [ ] "Forecast FY2025 gross margin"
- [ ] "What if wheat prices rise 15%?"
- [ ] "Show sensitivity analysis"

### Prescriptive Queries
- [ ] "How should we allocate crops?"
- [ ] "What hedging strategy is optimal?"
- [ ] "Where can we reduce costs?"

---

## VALUE-DRIVER TREE REFERENCE

```
                    ┌─────────────────────────────────┐
                    │        GROSS MARGIN             │
                    │   Revenue - Cost of Production  │
                    └─────────────┬───────────────────┘
                                  │
              ┌───────────────────┴───────────────────┐
              │                                       │
    ┌─────────┴─────────┐               ┌─────────────┴─────────────┐
    │      REVENUE      │               │   COST OF PRODUCTION      │
    │  Volume × Price   │               │  Volume × Cost per ton    │
    └────────┬──────────┘               └─────────────┬─────────────┘
             │                                        │
    ┌────────┴────────┐                    ┌──────────┴──────────┐
    │                 │                    │                     │
┌───┴───┐       ┌─────┴─────┐        ┌─────┴─────┐        ┌──────┴──────┐
│VOLUME │       │NET SALES  │        │DIRECT     │        │YIELD (t/ha) │
│ (t)   │       │PRICE($/t) │        │COSTS ($/ha│        │             │
└───┬───┘       └─────┬─────┘        └─────┬─────┘        └──────┬──────┘
    │                 │                    │                     │
┌───┴────┐    ┌───────┴───────┐    ┌───────┴───────┐    ┌────────┴────────┐
│Area×   │    │Commodity      │    │Input Prices   │    │Agronomy        │
│Yield   │    │Prices + FX    │    │+ Application  │    │Soil + Weather  │
└────────┘    └───────────────┘    │Rates          │    └─────────────────┘
                                   └───────────────┘

INDEPENDENT VARIABLES (External/Decision):
├── Crop Area (ha) - Decision
├── Agronomy practices - Decision
├── Commodity prices - External
├── FX rates - External
├── Input prices - External
├── Weather/soil - External
└── Hedging strategy - Decision
```

---

## PENDING ITEMS

### From IT Team
- [ ] Enable cross-geo Azure OpenAI policy in Fabric Admin Portal
- [ ] Verify Service Principal has read access to all required views
- [ ] Optional: Increase GPT-4o TPM quota

### From User (Optional)
- [ ] Upload Tech Cards for detailed agronomic parameters
- [ ] Upload Management Report March 2025 for additional context
- [ ] Upload Ukraine Power BI Report for dashboard integration

### Future Enhancements
- [ ] Add web search integration for commodity prices
- [ ] Create automated variance alerts
- [ ] Build scenario comparison dashboard
- [ ] Integrate with Power BI for visualization

---

## SUPPORT & DOCUMENTATION

**Created:** December 2025
**Project:** SALIC CFG Ukraine Financial Analytics
**Owner:** Data Analytics Team

**Key Contacts:**
- IT Support: For Azure/Fabric permissions
- Finance: For data validation
- Management: For requirements/priorities

---

*Package Version: 1.0*
*Ready for Azure AI Foundry deployment*
