# CFG Ukraine Financial Analytics Agent

An Agentic AI system for natural-language financial analytics queries against Microsoft Fabric data.

## 🎯 Capabilities

The agent classifies and handles four types of analytics queries:

| Type | Question | Example |
|------|----------|---------|
| **Descriptive** | What happened? | "Show G&A expenses for 2024" |
| **Diagnostic** | Why did it happen? | "Why did expenses increase in Q4?" |
| **Predictive** | What will happen? | "Forecast expenses for next quarter" |
| **Prescriptive** | What should we do? | "How can we reduce admin costs?" |

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User Query    │────▶│  Query Classifier │────▶│  SQL Generator  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│    Response     │◀────│ Response Generator│◀────│ Fabric Connector│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │ Conversation     │
                        │ Memory           │
                        └──────────────────┘
```

## 📁 Project Structure

```
cfg-ukraine-agent/
├── config.py              # Configuration and schema definitions
├── query_classifier.py    # Classifies queries into 4 categories
├── sql_generator.py       # Converts natural language to SQL
├── fabric_connector.py    # Executes queries against Fabric
├── response_generator.py  # Generates natural language responses
├── conversation_memory.py # Maintains conversation context
├── agent.py              # Main orchestrator
├── api.py                # FastAPI web service
├── test_agent.py         # Test suite
├── requirements.txt      # Python dependencies
├── .env.template         # Environment variables template
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- Azure OpenAI with GPT-4o deployed
- Microsoft Fabric workspace with data access

### 2. Installation

```bash
# Clone or download the project
cd cfg-ukraine-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit .env with your values
# Required: AZURE_OPENAI_API_KEY
```

### 4. Test the Agent

```bash
# Run with mock data (no Fabric connection needed)
python test_agent.py
```

### 5. Run the API

```bash
# Start the FastAPI server
uvicorn api:app --reload --port 8000

# Test the endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What were G&A expenses in 2024?"}'
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Yes |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name (e.g., gpt-4o) | Yes |
| `FABRIC_SQL_ENDPOINT` | Fabric SQL endpoint | For production |
| `FABRIC_DATABASE` | Fabric database name | For production |
| `USE_MOCK_DATA` | Use mock data (true/false) | No (default: true) |

## 🌐 Deployment Options

### Option 1: Azure App Service

```bash
# Create App Service
az webapp up --name cfg-ukraine-agent --resource-group your-rg --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set --name cfg-ukraine-agent --resource-group your-rg \
  --settings AZURE_OPENAI_API_KEY=your-key USE_MOCK_DATA=false
```

### Option 2: Azure Functions

See `azure_function/` directory for Azure Functions deployment files.

### Option 3: Azure Container Apps

```bash
# Build container
docker build -t cfg-ukraine-agent .

# Deploy to Azure Container Apps
az containerapp up --name cfg-ukraine-agent --source .
```

## 📊 Connecting to Real Fabric Data

To connect to your actual Microsoft Fabric warehouse:

1. Set `USE_MOCK_DATA=false` in `.env`

2. Configure Fabric connection:
   ```python
   from agent import CFGUkraineAgent
   
   agent = CFGUkraineAgent(use_mock_data=False)
   agent.connect_to_fabric(method="interactive")  # Browser login
   ```

3. For production (Service Principal):
   ```python
   agent.connect_to_fabric(
       method="service_principal",
       client_id="your-client-id",
       client_secret="your-secret",
       tenant_id="your-tenant-id"
   )
   ```

## 🧪 Testing

```bash
# Run all tests
python test_agent.py

# Run specific component tests
python -c "from test_agent import test_classifier; test_classifier()"
```

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/chat` | POST | Send a message to the agent |
| `/history/{session_id}` | GET | Get conversation history |
| `/history/{session_id}` | DELETE | Clear conversation history |
| `/capabilities` | GET | List agent capabilities |

### Example API Request

```json
POST /chat
{
    "message": "What were the G&A expenses for CFG Ukraine in 2024?",
    "session_id": "user-123"
}
```

### Example Response

```json
{
    "session_id": "user-123",
    "question": "What were the G&A expenses for CFG Ukraine in 2024?",
    "classification": "DESCRIPTIVE",
    "response": "The G&A expenses for CFG Ukraine in 2024 totaled $236,512.48...",
    "sql": "SELECT ...",
    "suggestions": [
        "How does this compare to 2023?",
        "Break down expenses by month",
        "What's driving the costs?"
    ]
}
```

## 🔒 Security Notes

- Never commit `.env` files with real credentials
- Use Azure Key Vault for production secrets
- Enable Managed Identity for Azure deployments
- Configure CORS appropriately for production

## 📄 License

Internal use only - CFG Ukraine / SALIC

## 🤝 Support

For issues or questions, contact the Data Analytics team.
