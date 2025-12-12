"""
Conversation Memory Module
Maintains conversation history for context-aware responses

For production, replace InMemoryStore with CosmosDBStore
"""
from datetime import datetime
from typing import List, Dict, Optional
import json


class ConversationMemory:
    """
    Base class for conversation memory.
    Stores conversation turns and enables context-aware follow-up questions.
    """
    
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
    
    def add_turn(
        self,
        session_id: str,
        user_query: str,
        classification: str,
        sql: str,
        response: str,
        data_summary: dict = None
    ):
        raise NotImplementedError
    
    def get_context(self, session_id: str, num_turns: int = 5) -> List[Dict]:
        raise NotImplementedError
    
    def clear_session(self, session_id: str):
        raise NotImplementedError


class InMemoryStore(ConversationMemory):
    """
    Simple in-memory conversation store.
    Good for demos and testing. Data is lost when the application restarts.
    """
    
    def __init__(self, max_turns: int = 10):
        super().__init__(max_turns)
        self.sessions: Dict[str, List[Dict]] = {}
    
    def add_turn(
        self,
        session_id: str,
        user_query: str,
        classification: str,
        sql: str,
        response: str,
        data_summary: dict = None
    ):
        """Add a conversation turn to the session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        turn = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_query": user_query,
            "classification": classification,
            "sql": sql,
            "response": response[:500],  # Truncate for memory efficiency
            "data_summary": data_summary or {}
        }
        
        self.sessions[session_id].append(turn)
        
        # Keep only the last max_turns
        if len(self.sessions[session_id]) > self.max_turns:
            self.sessions[session_id] = self.sessions[session_id][-self.max_turns:]
    
    def get_context(self, session_id: str, num_turns: int = 5) -> List[Dict]:
        """Get the last num_turns from the session."""
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id][-num_turns:]
    
    def get_last_turn(self, session_id: str) -> Optional[Dict]:
        """Get the most recent turn from the session."""
        if session_id not in self.sessions or len(self.sessions[session_id]) == 0:
            return None
        return self.sessions[session_id][-1]
    
    def clear_session(self, session_id: str):
        """Clear all turns for a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_session_summary(self, session_id: str) -> str:
        """Get a text summary of the conversation for context."""
        turns = self.get_context(session_id)
        if not turns:
            return "No previous conversation."
        
        summary_parts = []
        for i, turn in enumerate(turns, 1):
            summary_parts.append(
                f"Turn {i}: User asked about {turn['classification'].lower()} analytics: "
                f"'{turn['user_query'][:100]}...'"
            )
        
        return "\n".join(summary_parts)


class CosmosDBStore(ConversationMemory):
    """
    Azure Cosmos DB conversation store.
    For production use - persistent storage across application restarts.
    
    Prerequisites:
    - pip install azure-cosmos
    - Cosmos DB account with a database and container created
    """
    
    def __init__(
        self,
        endpoint: str,
        key: str,
        database_name: str = "agent_memory",
        container_name: str = "conversations",
        max_turns: int = 10
    ):
        super().__init__(max_turns)
        
        try:
            from azure.cosmos import CosmosClient, PartitionKey
            
            self.client = CosmosClient(endpoint, key)
            self.database = self.client.create_database_if_not_exists(database_name)
            self.container = self.database.create_container_if_not_exists(
                id=container_name,
                partition_key=PartitionKey(path="/session_id"),
                offer_throughput=400
            )
        except ImportError:
            raise ImportError("azure-cosmos package required. Install with: pip install azure-cosmos")
    
    def add_turn(
        self,
        session_id: str,
        user_query: str,
        classification: str,
        sql: str,
        response: str,
        data_summary: dict = None
    ):
        """Add a conversation turn to Cosmos DB."""
        import uuid
        
        turn = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_query": user_query,
            "classification": classification,
            "sql": sql,
            "response": response[:500],
            "data_summary": data_summary or {}
        }
        
        self.container.create_item(turn)
        
        # Clean up old turns if exceeding max
        self._cleanup_old_turns(session_id)
    
    def get_context(self, session_id: str, num_turns: int = 5) -> List[Dict]:
        """Get recent turns from Cosmos DB."""
        query = f"""
            SELECT * FROM c 
            WHERE c.session_id = '{session_id}'
            ORDER BY c.timestamp DESC
            OFFSET 0 LIMIT {num_turns}
        """
        
        items = list(self.container.query_items(query, enable_cross_partition_query=True))
        return list(reversed(items))  # Return in chronological order
    
    def clear_session(self, session_id: str):
        """Delete all turns for a session."""
        query = f"SELECT c.id FROM c WHERE c.session_id = '{session_id}'"
        items = list(self.container.query_items(query, enable_cross_partition_query=True))
        
        for item in items:
            self.container.delete_item(item['id'], partition_key=session_id)
    
    def _cleanup_old_turns(self, session_id: str):
        """Remove old turns exceeding max_turns."""
        query = f"""
            SELECT c.id, c.timestamp FROM c 
            WHERE c.session_id = '{session_id}'
            ORDER BY c.timestamp DESC
        """
        
        items = list(self.container.query_items(query, enable_cross_partition_query=True))
        
        if len(items) > self.max_turns:
            # Delete oldest turns
            for item in items[self.max_turns:]:
                self.container.delete_item(item['id'], partition_key=session_id)


def get_memory_store(use_cosmos: bool = False, **cosmos_config) -> ConversationMemory:
    """
    Factory function to get the appropriate memory store.
    
    Args:
        use_cosmos: If True, use Cosmos DB. Otherwise, use in-memory store.
        **cosmos_config: Cosmos DB configuration (endpoint, key, database_name, container_name)
    """
    if use_cosmos:
        return CosmosDBStore(**cosmos_config)
    return InMemoryStore()


# Test the memory store
if __name__ == "__main__":
    # Test in-memory store
    memory = InMemoryStore()
    
    session_id = "test-session-123"
    
    # Add some turns
    memory.add_turn(
        session_id=session_id,
        user_query="What were G&A expenses in Q4?",
        classification="DESCRIPTIVE",
        sql="SELECT ... FROM ...",
        response="The G&A expenses for Q4 2024 were $27,584.64...",
        data_summary={"total": 27584.64, "period": "Q4 2024"}
    )
    
    memory.add_turn(
        session_id=session_id,
        user_query="Why did they decrease?",
        classification="DIAGNOSTIC",
        sql="SELECT ... FROM ...",
        response="The decrease was primarily due to...",
        data_summary={"variance": -5000, "main_driver": "payroll"}
    )
    
    # Retrieve context
    context = memory.get_context(session_id)
    print(f"Session has {len(context)} turns")
    
    for turn in context:
        print(f"- {turn['classification']}: {turn['user_query']}")
    
    print("\nSession Summary:")
    print(memory.get_session_summary(session_id))
