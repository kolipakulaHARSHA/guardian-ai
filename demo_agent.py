"""
Simple Demo of Guardian AI Agent
Quick demonstration of intelligent orchestration
"""

import os
import sys
from pathlib import Path

# Set working directory
os.chdir(Path(__file__).parent)

# Load .env if it exists
from dotenv import load_dotenv
load_dotenv()

# Check API key
if not os.environ.get('GOOGLE_API_KEY'):
    # Try to load from Github_scanner/.env
    env_file = Path('Github_scanner/.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

if not os.environ.get('GOOGLE_API_KEY'):
    print("❌ Error: GOOGLE_API_KEY not set")
    sys.exit(1)

print("🤖 Initializing Guardian AI Agent...\n")

from guardian_agent_simple import GuardianAgent

# Create agent with verbose output
agent = GuardianAgent(verbose=True)

print("✅ Agent ready!\n")
print("="*70)
print("DEMO: Ask the agent to analyze a regulation")
print("="*70)

# Simple query that should only use Legal_Analyzer
query = "Summarize the key requirements from GuardianAI-Orchestrator/sample_regulation.pdf"

print(f"\nQuery: {query}\n")
print("-"*70)

try:
    result = agent.run(query)
    
    print("\n" + "="*70)
    print("FINAL ANSWER")
    print("="*70)
    print(f"\n{result['output']}\n")
    
    print("="*70)
    print("SUCCESS! Agent completed the task.")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
