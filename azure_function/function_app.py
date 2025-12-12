"""
Azure Function - CFG Ukraine Financial Analytics Agent
HTTP Trigger for chat endpoint
"""
import azure.functions as func
import json
import logging
import os
import uuid

# Import agent components
from shared.query_classifier import QueryClassifier
from shared.sql_generator import SQLGenerator
from shared.fabric_connector import get_connector
from shared.response_generator import ResponseGenerator
from shared.conversation_memory import InMemoryStore

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Initialize components (lazy loading)
classifier = None
sql_generator = None
response_generator = None
connector = None
memory = InMemoryStore()


def get_components():
    """Lazy initialization of agent components."""
    global classifier, sql_generator, response_generator, connector
    
    if classifier is None:
        classifier = QueryClassifier()
        sql_generator = SQLGenerator()
        response_generator = ResponseGenerator()
        connector = get_connector(use_mock=False)
    
    return classifier, sql_generator, response_generator, connector


@app.route(route="chat", methods=["POST"])
def chat(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main chat endpoint for the financial analytics agent.
    
    Request body:
    {
        "message": "What were G&A expenses in 2024?",
        "session_id": "optional-session-id"
    }
    """
    logging.info('Chat function triggered')
    
    try:
        # Parse request
        req_body = req.get_json()
        message = req_body.get('message', '')
        session_id = req_body.get('session_id', str(uuid.uuid4()))
        
        if not message:
            return func.HttpResponse(
                json.dumps({"error": "Message is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get components
        classifier, sql_generator, response_generator, connector = get_components()
        
        # Process the query
        result = {
            "session_id": session_id,
            "question": message,
            "classification": None,
            "sql": None,
            "data": None,
            "response": None,
            "suggestions": [],
            "error": None
        }
        
        # Step 1: Classify
        classification = classifier.classify(message)
        result["classification"] = classification
        logging.info(f"Query classified as: {classification}")
        
        # Step 2: Get context
        context = memory.get_context(session_id, num_turns=3)
        
        # Step 3: Generate SQL
        sql = sql_generator.generate_sql(message, context)
        result["sql"] = sql
        
        # Step 4: Execute query
        data = connector.execute_query(sql)
        result["data"] = data
        logging.info(f"Retrieved {data['row_count']} rows")
        
        # Step 5: Generate response
        if classification == "DESCRIPTIVE":
            response = response_generator.generate_descriptive_response(message, data, sql)
        elif classification == "DIAGNOSTIC":
            response = response_generator.generate_diagnostic_response(message, data, sql)
        elif classification == "PREDICTIVE":
            response = response_generator.generate_predictive_response(message, data, sql)
        elif classification == "PRESCRIPTIVE":
            response = response_generator.generate_prescriptive_response(message, data, sql)
        else:
            response = response_generator.generate_descriptive_response(message, data, sql)
        
        result["response"] = response
        
        # Step 6: Generate suggestions
        suggestions = response_generator.generate_followup_suggestions(message, classification, data)
        result["suggestions"] = suggestions
        
        # Step 7: Store in memory
        memory.add_turn(
            session_id=session_id,
            user_query=message,
            classification=classification,
            sql=sql,
            response=response,
            data_summary={"row_count": data["row_count"], "columns": data["columns"]}
        )
        
        return func.HttpResponse(
            json.dumps(result, default=str),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "CFG Ukraine Financial Analytics Agent",
            "version": "1.0.0"
        }),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="capabilities", methods=["GET"])
def capabilities(req: func.HttpRequest) -> func.HttpResponse:
    """Return agent capabilities for Copilot Studio."""
    return func.HttpResponse(
        json.dumps({
            "query_types": ["DESCRIPTIVE", "DIAGNOSTIC", "PREDICTIVE", "PRESCRIPTIVE"],
            "description": "Financial analytics agent for CFG Ukraine",
            "examples": [
                "What were the G&A expenses in 2024?",
                "Why did expenses increase in Q4?",
                "Forecast expenses for next quarter",
                "How can we reduce administrative costs?"
            ]
        }),
        status_code=200,
        mimetype="application/json"
    )
