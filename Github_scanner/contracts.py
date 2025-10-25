"""
Contract Definitions for Guardian AI
Following the PROGRESS.md specifications
"""

import json
from code_tool import CodeAuditorAgent


# Built by: Person C (Code Auditor)
# Called by: Person A (Orchestrator)
def code_auditor_agent(repo_url: str, technical_brief: str) -> str:
    """
    Scans a public GitHub repository using an AI agent to find violations.
    
    This function follows the PROGRESS.md specification:
    - Clones the repository to a temporary directory
    - Iterates through all relevant files
    - Splits code into 20-40 line chunks
    - For each chunk, asks the LLM if it violates the technical brief
    - Returns a JSON string list of all violations found
    
    Args:
        repo_url: URL of the GitHub repository to scan
        technical_brief: Plain-English description of compliance rules
                        (e.g., "Check all image tags for alt attributes.
                               Ensure user data is handled with encryption.")
    
    Returns:
        JSON string containing list of violations. Each violation includes:
        - violating_code: The exact code that violates
        - explanation: Why it violates the rule
        - rule_violated: Which rule from the brief was violated
        - file_path: Path to the file containing the violation
        - line_number: Starting line number of the violation
        
    Example:
        >>> brief = "All functions must have docstrings. No print statements in production code."
        >>> result = code_auditor_agent("https://github.com/user/repo", brief)
        >>> print(result)
        [
            {
                "violating_code": "def calculate(x, y):\\n    return x + y",
                "explanation": "Function 'calculate' is missing a docstring",
                "rule_violated": "All functions must have docstrings",
                "file_path": "src/utils.py",
                "line_number": 42
            }
        ]
    """
    # Initialize the auditor
    auditor = CodeAuditorAgent()
    
    # Scan the repository
    result = auditor.scan_repository(repo_url, technical_brief)
    
    # Return violations as JSON string (per PROGRESS.md specification)
    return json.dumps(result['violations'], indent=2)


# Built by: Person B (Legal Analyst)
# Called by: Person A (Orchestrator)
def legal_analyst_tool(pdf_file_path: str, question: str) -> str:
    """
    Analyzes a regulatory PDF document using RAG.
    
    Args:
        pdf_file_path: Path to the PDF file to analyze
        question: Question to ask about the document
                 (e.g., "Create a technical brief for a developer...")
    
    Returns:
        String containing a plain-English, human-readable technical brief
    """
    pass
