# Azure Functions Deployment Guide

## Prerequisites
1. Azure CLI installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. Azure Functions Core Tools: `npm install -g azure-functions-core-tools@4`
3. Python 3.10 or 3.11

## Step 1: Login to Azure
```bash
az login
```

## Step 2: Create Resource Group (if needed)
```bash
az group create --name cfg-ukraine-rg --location uksouth
```

## Step 3: Create Storage Account
```bash
az storage account create --name cfgukrainestorage --location uksouth --resource-group cfg-ukraine-rg --sku Standard_LRS
```

## Step 4: Create Function App
```bash
az functionapp create \
  --resource-group cfg-ukraine-rg \
  --consumption-plan-location uksouth \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name cfg-ukraine-agent-api \
  --storage-account cfgukrainestorage \
  --os-type Linux
```

## Step 5: Configure Application Settings
```bash
az functionapp config appsettings set --name cfg-ukraine-agent-api --resource-group cfg-ukraine-rg --settings \
  AZURE_OPENAI_API_KEY="your-api-key" \
  AZURE_OPENAI_ENDPOINT="https://salic-azure-aifoundry.cognitiveservices.azure.com/" \
  AZURE_OPENAI_DEPLOYMENT="gpt-4o" \
  AZURE_OPENAI_API_VERSION="2025-01-01-preview" \
  FABRIC_SQL_ENDPOINT="c62kdprxik4ebmbak76otk63im-qzbcr6tjdtcexclylqd6vaz3fe.datawarehouse.fabric.microsoft.com" \
  FABRIC_DATABASE="salic_finance_warehouse" \
  AZURE_TENANT_ID="your-tenant-id" \
  AZURE_CLIENT_ID="your-client-id" \
  AZURE_CLIENT_SECRET="your-client-secret" \
  USE_MOCK_DATA="false"
```

## Step 6: Deploy the Function
```bash
cd azure_function
func azure functionapp publish cfg-ukraine-agent-api
```

## Step 7: Get Function URL
After deployment, your function URL will be:
```
https://cfg-ukraine-agent-api.azurewebsites.net/api/chat
```

## Step 8: Get Function Key
```bash
az functionapp keys list --name cfg-ukraine-agent-api --resource-group cfg-ukraine-rg
```

## Testing the Deployed Function
```bash
curl -X POST "https://cfg-ukraine-agent-api.azurewebsites.net/api/chat?code=YOUR_FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "What were G&A expenses in 2024?", "session_id": "test-1"}'
```

## Notes
- The function uses FUNCTION level authentication. You'll need the function key for API calls.
- For Copilot Studio integration, you'll add this URL as a custom connector.
- ODBC Driver 18 is pre-installed on Azure Functions Linux runtime.
