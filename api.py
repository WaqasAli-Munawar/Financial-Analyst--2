"""
FastAPI Web Service for CFG Ukraine Financial Analytics Agent
Deploy this as an Azure App Service or Azure Container App
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env", override=True)

# Import the agent
from agent import CFGUkraineAgent, format_response

# Initialize FastAPI app
app = FastAPI(
    title="CFG Ukraine Financial Analytics Agent",
    description="Agentic AI for Descriptive, Diagnostic, Predictive, and Prescriptive financial analytics",
    version="1.0.0"
)

# Add CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent (use mock data by default, configure via env vars)
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
agent = CFGUkraineAgent(use_mock_data=USE_MOCK_DATA)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    question: str
    classification: str
    response: str
    sql: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    mock_mode: bool


# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        mock_mode=USE_MOCK_DATA
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Azure."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        mock_mode=USE_MOCK_DATA
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for the financial analytics agent.
    
    Send a natural language question and receive an AI-powered response.
    The agent automatically classifies queries into:
    - DESCRIPTIVE: What happened?
    - DIAGNOSTIC: Why did it happen?
    - PREDICTIVE: What will happen?
    - PRESCRIPTIVE: What should we do?
    """
    try:
        result = agent.chat(
            message=request.message,
            session_id=request.session_id
        )
        
        return ChatResponse(
            session_id=result["session_id"],
            question=result["question"],
            classification=result["classification"],
            response=result["response"],
            sql=result.get("sql"),
            data=result.get("data"),
            suggestions=result.get("suggestions", []),
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get conversation history for a session."""
    try:
        history = agent.get_conversation_history(session_id)
        return {
            "session_id": session_id,
            "turns": history,
            "turn_count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history for a session."""
    try:
        agent.clear_conversation(session_id)
        return {"status": "cleared", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/capabilities")
async def get_capabilities():
    """Get information about agent capabilities."""
    return {
        "query_types": {
            "DESCRIPTIVE": {
                "description": "What happened? - Historical data, trends, summaries",
                "examples": [
                    "Show G&A expenses for 2024",
                    "What was the cash position last quarter?",
                    "List monthly expenses by category"
                ]
            },
            "DIAGNOSTIC": {
                "description": "Why did it happen? - Root cause analysis, variance explanations",
                "examples": [
                    "Why did expenses increase in Q4?",
                    "What caused the cash decrease?",
                    "Explain the variance in G&A"
                ]
            },
            "PREDICTIVE": {
                "description": "What will happen? - Forecasts, projections",
                "examples": [
                    "Forecast expenses for next quarter",
                    "What will cash position be in 6 months?",
                    "Project 2025 G&A costs"
                ]
            },
            "PRESCRIPTIVE": {
                "description": "What should we do? - Recommendations, actions",
                "examples": [
                    "How can we reduce G&A expenses?",
                    "What should we do to improve cash flow?",
                    "Recommend cost optimization strategies"
                ]
            }
        },
        "available_data": {
            "entity": "CFG Ukraine (E250)",
            "time_range": "2024 (Q3-Q4)",
            "scenarios": ["Actual"],
            "account_categories": [
                "General and administrative expenses",
                "Cash and cash_equivalents",
                "Trade and other payables",
                "Finance charge",
                "Exchange loss",
                "Intangible assets, net",
                "FX Reserve",
                "FCCS equity items"
            ]
        }
    }


# Run with: uvicorn api:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
