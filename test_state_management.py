"""
Quick test script to verify state management implementation
"""

import sys
from pathlib import Path

# Add module paths
GUARDIAN_ROOT = Path(__file__).parent
sys.path.insert(0, str(GUARDIAN_ROOT))

from langchain_agent import LangChainGuardianAgent

def test_state_management():
    print("="*70)
    print("Testing State Management Implementation")
    print("="*70)
    
    agent = LangChainGuardianAgent()
    
    # Test 1: Check initial state
    print("\n1. Testing initial state...")
    assert agent.qa_repo_url is None, "Initial qa_repo_url should be None"
    assert agent.qa_tool_instance is None, "Initial qa_tool_instance should be None"
    assert len(agent.session_history) == 0, "Initial session history should be empty"
    print("   ✅ Initial state correct")
    
    # Test 2: Check session info
    print("\n2. Testing get_session_info()...")
    info = agent.get_session_info()
    assert "No active QA session" in info, "Should report no active session"
    print(f"   ✅ Session info: {info}")
    
    # Test 3: Check session history methods
    print("\n3. Testing session history...")
    history = agent.get_session_history()
    assert len(history) == 0, "History should be empty initially"
    
    # Manually add some history
    agent.session_history.append({'type': 'query', 'content': 'test query'})
    agent.session_history.append({'type': 'response', 'content': 'test response'})
    
    history = agent.get_session_history()
    assert len(history) == 2, "History should have 2 items"
    print(f"   ✅ Session history: {len(history)} items")
    
    # Test 4: Clear history
    print("\n4. Testing clear_session_history()...")
    result = agent.clear_session_history()
    assert len(agent.session_history) == 0, "History should be empty after clear"
    print(f"   ✅ {result}")
    
    # Test 5: Check stateful tools exist
    print("\n5. Testing stateful tools...")
    assert len(agent.tools) == 3, "Should have 3 tools"
    tool_names = [tool.name for tool in agent.tools]
    print(f"   Available tools: {tool_names}")
    assert 'legal_analyzer' in tool_names, "Should have legal_analyzer"
    assert 'stateful_code_auditor' in tool_names, "Should have stateful_code_auditor"
    assert 'stateful_repository_qa' in tool_names, "Should have stateful_repository_qa"
    print("   ✅ All stateful tools present")
    
    # Test 6: Check cleanup
    print("\n6. Testing _cleanup_qa_session()...")
    agent.qa_repo_url = "https://test.com/repo"
    agent.qa_tool_instance = "dummy"
    agent._cleanup_qa_session()
    assert agent.qa_repo_url is None, "qa_repo_url should be None after cleanup"
    assert agent.qa_tool_instance is None, "qa_tool_instance should be None after cleanup"
    print("   ✅ Cleanup works correctly")
    
    print("\n" + "="*70)
    print("✅ All tests passed!")
    print("="*70)
    print("\nState management is working correctly.")
    print("\nYou can now use:")
    print("  - Interactive mode: python langchain_agent.py -i")
    print("  - Single query: python langchain_agent.py \"your query\"")
    print("\nCommands in interactive mode:")
    print("  - start_qa <url>  : Start a QA session")
    print("  - end_qa          : End QA session")
    print("  - session         : Show session info")
    print("  - history         : Show conversation history")
    print("  - clear           : Clear history")
    print("  - exit            : Exit the program")

if __name__ == "__main__":
    test_state_management()
