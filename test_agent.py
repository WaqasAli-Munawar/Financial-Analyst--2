"""
Test Script for CFG Ukraine Financial Analytics Agent
Run this to verify all components are working correctly.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_classifier():
    """Test the query classifier."""
    print("\n" + "=" * 50)
    print("Testing Query Classifier")
    print("=" * 50)
    
    from query_classifier import QueryClassifier
    classifier = QueryClassifier()
    
    test_cases = [
        ("Show me G&A expenses for Q4 2024", "DESCRIPTIVE"),
        ("Why did expenses increase in September?", "DIAGNOSTIC"),
        ("Forecast expenses for next quarter", "PREDICTIVE"),
        ("How can we reduce administrative costs?", "PRESCRIPTIVE")
    ]
    
    passed = 0
    for question, expected in test_cases:
        result = classifier.classify(question)
        status = "✓" if result == expected else "✗"
        if result == expected:
            passed += 1
        print(f"{status} '{question[:40]}...' -> {result} (expected: {expected})")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_sql_generator():
    """Test the SQL generator."""
    print("\n" + "=" * 50)
    print("Testing SQL Generator")
    print("=" * 50)
    
    from sql_generator import SQLGenerator
    generator = SQLGenerator()
    
    question = "Show me G&A expenses by month for 2024"
    print(f"Question: {question}")
    
    sql = generator.generate_sql(question)
    print(f"\nGenerated SQL:\n{sql}")
    
    validation = generator.validate_sql(sql)
    print(f"\nValidation: {validation}")
    
    return validation["valid"]


def test_mock_connector():
    """Test the mock Fabric connector."""
    print("\n" + "=" * 50)
    print("Testing Mock Fabric Connector")
    print("=" * 50)
    
    from fabric_connector import get_connector
    connector = get_connector(use_mock=True)
    connector.connect_interactive()
    
    result = connector.execute_query("SELECT * FROM General and administrative expenses")
    
    print(f"Columns: {result['columns']}")
    print(f"Row count: {result['row_count']}")
    print(f"Sample row: {result['rows'][0] if result['rows'] else 'No data'}")
    
    connector.close()
    return result['row_count'] > 0


def test_memory():
    """Test the conversation memory."""
    print("\n" + "=" * 50)
    print("Testing Conversation Memory")
    print("=" * 50)
    
    from conversation_memory import InMemoryStore
    memory = InMemoryStore()
    
    session_id = "test-123"
    
    # Add turns
    memory.add_turn(
        session_id=session_id,
        user_query="What were G&A expenses?",
        classification="DESCRIPTIVE",
        sql="SELECT ...",
        response="The expenses were..."
    )
    
    memory.add_turn(
        session_id=session_id,
        user_query="Why did they increase?",
        classification="DIAGNOSTIC",
        sql="SELECT ...",
        response="They increased because..."
    )
    
    # Retrieve
    context = memory.get_context(session_id)
    print(f"Stored {len(context)} turns")
    
    for turn in context:
        print(f"  - [{turn['classification']}] {turn['user_query']}")
    
    return len(context) == 2


def test_full_agent():
    """Test the full agent pipeline."""
    print("\n" + "=" * 50)
    print("Testing Full Agent Pipeline")
    print("=" * 50)
    
    from agent import CFGUkraineAgent
    
    agent = CFGUkraineAgent(use_mock_data=True)
    
    # Test all 4 query types
    questions = [
        "What were the G&A expenses in 2024?",
        "Why did expenses spike in September?",
        "What will expenses be next quarter?",
        "How can we reduce costs?"
    ]
    
    session_id = "test-full-agent"
    all_passed = True
    
    for question in questions:
        print(f"\n🔹 Question: {question}")
        result = agent.chat(question, session_id)
        
        if result.get("error"):
            print(f"  ❌ Error: {result['error']}")
            all_passed = False
        else:
            print(f"  ✓ Classification: {result['classification']}")
            print(f"  ✓ Response length: {len(result['response'])} chars")
            print(f"  ✓ Suggestions: {len(result.get('suggestions', []))}")
    
    agent.close()
    return all_passed


def main():
    """Run all tests."""
    print("\n" + "🧪" * 25)
    print("  CFG Ukraine Agent - Test Suite")
    print("🧪" * 25)
    
    results = {}
    
    # Test each component
    try:
        results["Classifier"] = test_classifier()
    except Exception as e:
        print(f"❌ Classifier test failed: {e}")
        results["Classifier"] = False
    
    try:
        results["SQL Generator"] = test_sql_generator()
    except Exception as e:
        print(f"❌ SQL Generator test failed: {e}")
        results["SQL Generator"] = False
    
    try:
        results["Mock Connector"] = test_mock_connector()
    except Exception as e:
        print(f"❌ Mock Connector test failed: {e}")
        results["Mock Connector"] = False
    
    try:
        results["Memory"] = test_memory()
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        results["Memory"] = False
    
    try:
        results["Full Agent"] = test_full_agent()
    except Exception as e:
        print(f"❌ Full Agent test failed: {e}")
        results["Full Agent"] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
