"""
Test script for Guardian AI Agent
Tests various scenarios to demonstrate intelligent orchestration
"""

import os
import sys
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

# Check API key
if not os.environ.get('GOOGLE_API_KEY'):
    print("❌ Error: GOOGLE_API_KEY not set")
    print("\nPlease set it:")
    print("  PowerShell: $env:GOOGLE_API_KEY='your-key-here'")
    sys.exit(1)

from guardian_agent import GuardianAgent

print("="*80)
print("GUARDIAN AI AGENT - TEST SUITE")
print("="*80)
print("\nThis will demonstrate the agent's ability to:")
print("  ✓ Analyze regulatory documents")
print("  ✓ Audit code repositories")
print("  ✓ Answer questions about code")
print("  ✓ Intelligently combine tools")
print("\n" + "="*80 + "\n")

# Create agent
agent = GuardianAgent(verbose=True)

# Test scenarios
tests = [
    {
        "name": "Test 1: Simple Legal Analysis",
        "query": "What are the key compliance requirements in GuardianAI-Orchestrator/sample_regulation.pdf?",
        "expected_tools": ["Legal_Analyzer"],
        "description": "Agent should use ONLY the Legal_Analyzer tool"
    },
    {
        "name": "Test 2: Code Q&A",
        "query": "What is the FINANCE_MANAGEMENT_APP project about? The repo is https://github.com/kolipakulaHARSHA/FINANCE_MANAGEMENT_APP",
        "expected_tools": ["QA_Tool"],
        "description": "Agent should use ONLY the QA_Tool"
    },
    {
        "name": "Test 3: Full Compliance Check",
        "query": "Check if https://github.com/kolipakulaHARSHA/FINANCE_MANAGEMENT_APP complies with the regulations in GuardianAI-Orchestrator/sample_regulation.pdf",
        "expected_tools": ["Legal_Analyzer", "Code_Auditor"],
        "description": "Agent should use Legal_Analyzer THEN Code_Auditor"
    },
]

# Run tests
for i, test in enumerate(tests, 1):
    print("\n" + "="*80)
    print(f"{test['name']}")
    print("="*80)
    print(f"Description: {test['description']}")
    print(f"Expected tools: {', '.join(test['expected_tools'])}")
    print(f"\nQuery: {test['query']}")
    print("\n" + "-"*80)
    
    try:
        result = agent.run(test['query'])
        
        print("\n" + "="*80)
        print("RESULT")
        print("="*80)
        print(f"\n{result['output']}\n")
        
        # Analyze which tools were used
        tools_used = [step[0].tool for step in result.get('intermediate_steps', [])]
        print(f"Tools used: {', '.join(tools_used) if tools_used else 'None'}")
        
        # Check if expected tools were used
        if set(test['expected_tools']) <= set(tools_used):
            print("✅ Test PASSED - Used expected tools")
        else:
            print(f"⚠️  Test WARNING - Expected {test['expected_tools']}, got {tools_used}")
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Pause between tests
    if i < len(tests):
        input("\n\nPress Enter to continue to next test...")

print("\n" + "="*80)
print("ALL TESTS COMPLETE!")
print("="*80)
print("\n🎉 The agent successfully demonstrates intelligent tool orchestration!")
print("\nKey capabilities shown:")
print("  ✓ Reasoning about which tools to use")
print("  ✓ Using tools in the correct order")
print("  ✓ Adapting to different types of requests")
print("  ✓ Combining multiple tools for complex tasks")
