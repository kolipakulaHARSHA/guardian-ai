import os
import json
from typing import Dict, Any
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import GoogleGenerativeAI
from contracts import legal_analyst_tool, code_auditor_agent

# Initialize the LLM with API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)

# Simple orchestration function (replaces complex agent framework)
def orchestrate_compliance_check(regulation_pdf: str, repository_url: str) -> str:
    """
    Orchestrates the two-step compliance checking process.
    Step 1: Get technical brief from legal analyst
    Step 2: Use brief to audit code
    """
    print("\n=== STEP 1: Analyzing Regulatory Document ===")
    question = "Create a concise, bullet-pointed technical brief for a developer. This brief should list the key compliance requirements from this document that can be checked in a codebase."
    technical_brief = legal_analyst_tool(regulation_pdf, question)
    print(f"Technical Brief:\n{technical_brief}\n")
    
    print("\n=== STEP 2: Auditing Code Repository ===")
    violations = code_auditor_agent(repository_url, technical_brief)
    print(f"Violations Found:\n{violations}\n")
    
    return violations

def run_compliance_audit(regulation_pdf: str, repository_url: str) -> Dict[str, Any]:
    """
    Main function to run a compliance audit.
    
    Args:
        regulation_pdf: Path to the regulatory PDF document
        repository_url: URL of the GitHub repository to audit
    
    Returns:
        Dict[str, Any]: Parsed JSON report containing compliance violations
    """
    
    try:
        # Use the orchestration function instead of agent
        violations_json = orchestrate_compliance_check(regulation_pdf, repository_url)
        
        # Parse the JSON string to return as dict
        try:
            return json.loads(violations_json)
        except json.JSONDecodeError:
            return {"raw_output": violations_json}
        
    except ValueError as ve:
        raise ValueError(f"Configuration error: {str(ve)}") from ve
    except Exception as e:
        raise RuntimeError(f"Error during compliance audit: {str(e)}") from e

if __name__ == "__main__":
    # Set the path to your PDF file and the repository URL you want to audit
    regulation_pdf = r"C:\Users\Karthik Sagar P\OneDrive\Desktop\GuardianAI\sample_regulation.pdf"  # Replace with your PDF filename
    repository_url = "https://github.com/your-repo/to-audit"  # Replace with the repository you want to audit

    try:
        report = run_compliance_audit(regulation_pdf, repository_url)
        print("\nFinal Compliance Report:")
        print(json.dumps(report, indent=2))
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        exit(1)