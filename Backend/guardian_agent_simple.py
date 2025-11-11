"""
Guardian AI - Simplified Agent Implementation
Manual orchestration with LLM reasoning (more reliable than LangChain agents)
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add module paths
GUARDIAN_ROOT = Path(__file__).parent
sys.path.insert(0, str(GUARDIAN_ROOT / 'Guardian-Legal-analyzer-main'))
sys.path.insert(0, str(GUARDIAN_ROOT / 'Github_scanner'))

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Verify API key
if not os.environ.get('GOOGLE_API_KEY'):
    raise ValueError("GOOGLE_API_KEY not found. Please set it in .env file")


# Tool imports (lazy loaded)
_legal_tool = None
_code_tool = None
_qa_tool = None


def get_legal_tool():
    """Lazy import legal tool"""
    global _legal_tool
    if _legal_tool is None:
        from legal_tool import legal_analyst_tool
        _legal_tool = legal_analyst_tool
    return _legal_tool


def get_code_tool():
    """Lazy import code tool"""
    global _code_tool
    if _code_tool is None:
        from code_tool import CodeAuditorAgent
        _code_tool = CodeAuditorAgent
    return _code_tool


def get_qa_tool():
    """Lazy import QA tool"""
    global _qa_tool
    if _qa_tool is None:
        from qa_tool import RepoQATool
        _qa_tool = RepoQATool
    return _qa_tool


class GuardianAgentSimple:
    """Simplified Guardian AI Agent with manual tool orchestration"""
    
    def __init__(self, model_name: str = "gemini-2.5-pro-preview-03-25", verbose: bool = True):
        self.model_name = model_name
        self.verbose = verbose
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.3,
            google_api_key=os.environ['GOOGLE_API_KEY']
        )
        self.conversation_history = []
    
    def _log(self, message: str):
        """Print if verbose"""
        if self.verbose:
            print(message)
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Run the agent with a query.
        
        The agent will:
        1. Analyze the query to determine what tools are needed
        2. Execute tools in the appropriate order
        3. Synthesize the results
        """
        self._log(f"\n{'='*70}")
        self._log(f"GUARDIAN AI - PROCESSING QUERY")
        self._log(f"{'='*70}")
        self._log(f"\nQuery: {query}\n")
        
        # Step 1: Plan which tools to use
        self._log(f"{'='*70}")
        self._log("STEP 1: PLANNING")
        self._log(f"{'='*70}\n")
        
        plan = self._create_plan(query)
        self._log(f"\nPlan: {plan}\n")
        
        # Step 2: Execute the plan
        self._log(f"\n{'='*70}")
        self._log("STEP 2: EXECUTION")
        self._log(f"{'='*70}\n")
        
        results = self._execute_plan(plan, query)
        
        # Step 3: Synthesize final answer
        self._log(f"\n{'='*70}")
        self._log("STEP 3: SYNTHESIS")
        self._log(f"{'='*70}\n")
        
        final_answer = self._synthesize_answer(query, results)
        
        return {
            'output': final_answer,
            'plan': plan,
            'tool_results': results
        }
    
    def _create_plan(self, query: str) -> Dict[str, Any]:
        """Use LLM to create an execution plan"""
        
        planning_prompt = f"""You are Guardian AI, a compliance and code analysis assistant. Analyze this user query and create an execution plan.

Available tools:
1. Legal_Analyzer: Analyzes PDF regulatory documents to extract compliance requirements
2. Code_Auditor: Scans code repositories for violations
   - AUDIT mode (default): Exhaustive line-by-line scanning to find specific violations
   - COMPLIANCE mode: RAG-based semantic search to check overall compliance with guidelines
3. QA_Tool: Answers questions about code repositories using RAG

User Query: "{query}"

Determine:
1. Which tools are needed?
2. In what order should they be used?
3. What information should be passed between tools?
4. For Code_Auditor: Should it use "audit" mode (find violations) or "compliance" mode (check guidelines)?

Respond ONLY with a JSON object like this:
{{
    "tools_needed": ["Legal_Analyzer", "Code_Auditor"],
    "execution_order": ["Legal_Analyzer", "Code_Auditor"],
    "reasoning": "Need to first understand regulations, then audit code for violations",
    "pdf_path": "path/to/pdf" (if Legal_Analyzer is needed, extract from query),
    "repo_url": "https://github.com/..." (if Code_Auditor or QA_Tool is needed, extract from query),
    "audit_mode": "audit" (use "audit" for finding violations, "compliance" for checking guidelines),
    "question": "specific question" (if QA_Tool is needed)
}}

JSON:"""

        response = self.llm.invoke([HumanMessage(content=planning_prompt)])
        response_text = response.content.strip()
        
        # Extract JSON from response
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        try:
            plan = json.loads(response_text)
            return plan
        except json.JSONDecodeError:
            # Fallback: try to extract info manually
            self._log(f"⚠️  Could not parse plan JSON, using fallback...")
            return self._fallback_plan(query)
    
    def _fallback_plan(self, query: str) -> Dict[str, Any]:
        """Fallback planning if JSON parsing fails"""
        query_lower = query.lower()
        
        plan = {
            "tools_needed": [],
            "execution_order": [],
            "reasoning": "Fallback planning",
            "pdf_path": None,
            "repo_url": None,
            "question": None
        }
        
        # Check for PDF/regulation mentions
        if any(word in query_lower for word in ['pdf', 'regulation', 'compliance', 'gdpr', 'law']):
            if 'audit' in query_lower or 'check' in query_lower or 'scan' in query_lower:
                plan["tools_needed"] = ["Legal_Analyzer", "Code_Auditor"]
                plan["execution_order"] = ["Legal_Analyzer", "Code_Auditor"]
            else:
                plan["tools_needed"] = ["Legal_Analyzer"]
                plan["execution_order"] = ["Legal_Analyzer"]
            
            # Extract PDF path
            pdf_match = re.search(r'(\S+\.pdf)', query)
            if pdf_match:
                plan["pdf_path"] = pdf_match.group(1)
        
        # Check for repository mentions
        if 'github.com' in query_lower or 'repo' in query_lower:
            url_match = re.search(r'https?://github\.com/[\w-]+/[\w-]+', query)
            if url_match:
                plan["repo_url"] = url_match.group(0)
            
            if 'what' in query_lower or 'how' in query_lower or '?' in query:
                if "QA_Tool" not in plan["tools_needed"]:
                    plan["tools_needed"].append("QA_Tool")
                    plan["execution_order"].append("QA_Tool")
                plan["question"] = query
        
        return plan
    
    def _execute_plan(self, plan: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Execute the planned tools"""
        results = {}
        
        for tool_name in plan.get("execution_order", []):
            self._log(f"\n--- Executing: {tool_name} ---\n")
            
            if tool_name == "Legal_Analyzer":
                result = self._run_legal_analyzer(plan.get("pdf_path"))
                results["legal_brief"] = result
                self._log(f"✓ Legal analysis complete\n")
                
            elif tool_name == "Code_Auditor":
                brief = results.get("legal_brief", "Check for code quality and security issues")
                mode = plan.get("audit_mode", "audit")  # "audit" or "compliance"
                result = self._run_code_auditor(plan.get("repo_url"), brief, mode)
                # Store both summary and detailed data
                if isinstance(result, dict):
                    results["audit_results"] = result.get("summary", str(result))
                    results["audit_details"] = result.get("details", {})
                else:
                    results["audit_results"] = result
                self._log(f"✓ Code {mode} complete\n")
                
            elif tool_name == "QA_Tool":
                result = self._run_qa_tool(plan.get("repo_url"), plan.get("question", query))
                results["qa_answer"] = result
                self._log(f"✓ Q&A complete\n")
        
        return results
    
    def _run_legal_analyzer(self, pdf_path: str) -> str:
        """Run legal analyzer tool"""
        if not pdf_path:
            return "Error: No PDF path provided"
        
        # Make path absolute
        if not os.path.isabs(pdf_path):
            possible_paths = [
                Path(pdf_path),
                GUARDIAN_ROOT / pdf_path,
                GUARDIAN_ROOT / 'GuardianAI-Orchestrator' / pdf_path,
            ]
            for p in possible_paths:
                if p.exists():
                    pdf_path = str(p)
                    break
        
        if not os.path.exists(pdf_path):
            return f"Error: PDF not found at {pdf_path}"
        
        try:
            legal_tool = get_legal_tool()
            question = (
                "Extract ALL specific technical security requirements, controls, and best practices "
                "from this ISO 27001 implementation guide that apply to software development and code security. "
                "Focus on:\n"
                "- Access control requirements\n"
                "- Data protection and encryption requirements\n"
                "- Input validation and security controls\n"
                "- Authentication and authorization requirements\n"
                "- Logging and monitoring requirements\n"
                "- Error handling and information disclosure\n"
                "- Secure coding practices\n"
                "- Configuration management\n"
                "- API security requirements\n"
                "\nProvide a comprehensive list of concrete, testable requirements that can be checked in source code. "
                "Include specific examples where applicable."
            )
            result = legal_tool(pdf_path, question, use_existing_db=True, filter_by_current_pdf=True)
            return result
        except Exception as e:
            return f"Error in legal analysis: {e}"
    
    def _run_code_auditor(self, repo_url: str, brief: str, mode: str = "audit"):
        """
        Run code auditor tool in either AUDIT or COMPLIANCE mode
        
        Args:
            repo_url: GitHub repository URL
            brief: Technical brief or compliance guidelines
            mode: "audit" (exhaustive line-by-line) or "compliance" (RAG-based semantic)
            
        Returns:
            dict with 'summary' (string) and 'details' (raw data)
        """
        if not repo_url:
            return {"summary": "Error: No repository URL provided", "details": {}}
        
        try:
            if mode == "compliance":
                # COMPLIANCE MODE - RAG-based semantic checking
                from Github_scanner.code_tool import ComplianceChecker
                checker = ComplianceChecker(model_name="gemini-2.5-pro-preview-03-25")
                
                # Parse brief into guidelines
                guidelines = [line.strip() for line in brief.split('\n') if line.strip() and not line.strip().startswith('#')]
                
                result = checker.check_compliance(repo_url, guidelines)
                
                # Format summary
                summary = f"Compliance Check Results (RAG-based):\n"
                summary += f"- Repository: {repo_url}\n"
                summary += f"- Guidelines checked: {len(result.get('compliance_checks', []))}\n\n"
                
                for check in result.get('compliance_checks', [])[:5]:
                    summary += f"Guideline: {check.get('guideline')}\n"
                    summary += f"Assessment: {check.get('assessment', 'N/A')[:200]}...\n\n"
                
                return {
                    "summary": summary,
                    "details": {
                        "mode": "compliance",
                        "repository": repo_url,
                        "guidelines_checked": len(result.get('compliance_checks', [])),
                        "compliance_checks": result.get('compliance_checks', []),
                        "raw_result": result
                    }
                }
            
            else:
                # AUDIT MODE - Exhaustive line-by-line scanning (default)
                CodeAuditor = get_code_tool()
                auditor = CodeAuditor(model_name="gemini-2.5-flash")
                result = auditor.scan_repository(repo_url, brief)
                
                # Format summary
                violations = result.get('violations', [])
                summary = f"Audit Results (Line-by-line):\n"
                summary += f"- Repository: {repo_url}\n"
                summary += f"- Violations found: {len(violations)}\n\n"
                
                if violations:
                    summary += "Top violations:\n"
                    for i, v in enumerate(violations[:10], 1):
                        summary += f"{i}. {v.get('file')} (line {v.get('line')})\n"
                        summary += f"   {v.get('explanation')}\n\n"
                else:
                    summary += "✅ No violations found!\n"
                
                return {
                    "summary": summary,
                    "details": {
                        "mode": "audit",
                        "repository": repo_url,
                        "total_violations": len(violations),
                        "violations": violations,
                        "files_scanned": result.get('files_scanned', 0),
                        "scan_statistics": result.get('statistics', {})
                    }
                }
                
        except Exception as e:
            return {
                "summary": f"Error in code {mode}: {str(e)}",
                "details": {"error": str(e), "mode": mode}
            }
    
    def _run_qa_tool(self, repo_url: str, question: str) -> str:
        """Run QA tool"""
        if not repo_url:
            return "Error: No repository URL provided"
        
        try:
            QATool = get_qa_tool()
            qa = QATool(model_name=self.model_name)
            answer = qa.ask_question(repo_url, question)
            return answer
        except Exception as e:
            return f"Error in Q&A: {e}"
    
    def _synthesize_answer(self, query: str, results: Dict[str, str]) -> str:
        """Synthesize final answer from tool results"""
        
        synthesis_prompt = f"""You are Guardian AI. You have executed tools to answer a user's query.

User Query: "{query}"

Tool Results:
{json.dumps(results, indent=2)}

Based on these results, provide a comprehensive, well-formatted answer to the user's query.
Be clear, professional, and helpful. Structure your answer with headings and bullet points where appropriate.

Answer:"""

        response = self.llm.invoke([HumanMessage(content=synthesis_prompt)])
        return response.content.strip()
    
    def ask(self, query: str) -> str:
        """Simple interface - just returns the answer"""
        result = self.run(query)
        return result['output']


# Make it easy to import
GuardianAgent = GuardianAgentSimple


# CLI interface
def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Guardian AI - Intelligent Compliance Agent',
        epilog="""
Examples:
  # Simple query
  python guardian_agent_simple.py "Analyze sample_regulation.pdf"
  
  # Full compliance check
  python guardian_agent_simple.py "Check https://github.com/user/repo against gdpr.pdf"
  
  # Save results to JSON
  python guardian_agent_simple.py "Check repo compliance" --output report.json
  
  # Output as JSON to console
  python guardian_agent_simple.py "Analyze PDF" --json
  
  # Interactive mode
  python guardian_agent_simple.py --interactive
        """
    )
    
    parser.add_argument('query', nargs='?', help='Your query')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--model', default='gemini-2.5-pro-preview-03-25', help='Model to use')
    parser.add_argument('--quiet', '-q', action='store_true', help='Less verbose output')
    parser.add_argument('--output', '-o', help='Save results to JSON file (e.g., report.json)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON to console')
    
    args = parser.parse_args()
    
    print("🤖 Initializing Guardian AI...")
    agent = GuardianAgent(model_name=args.model, verbose=not args.quiet)
    print("✅ Ready!\n")
    
    if args.interactive:
        print("Interactive mode. Type 'exit' to quit.\n")
        while True:
            try:
                query = input("You: ").strip()
                if query.lower() in ['exit', 'quit']:
                    break
                if query:
                    answer = agent.ask(query)
                    print(f"\nGuardian AI: {answer}\n")
            except KeyboardInterrupt:
                break
    elif args.query:
        result = agent.run(args.query)
        
        # Save to JSON file if requested
        if args.output:
            import json
            from datetime import datetime
            
            # Prepare JSON output
            json_output = {
                'timestamp': datetime.now().isoformat(),
                'query': args.query,
                'model': args.model,
                'plan': result.get('plan', {}),
                'tool_results': result.get('tool_results', {}),
                'final_answer': result.get('output', ''),
                'metadata': {
                    'guardian_version': '1.0',
                    'mode': 'agent_orchestration'
                }
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Results saved to: {args.output}")
        
        # Output as JSON to console if requested
        if args.json:
            import json
            from datetime import datetime
            
            json_output = {
                'timestamp': datetime.now().isoformat(),
                'query': args.query,
                'model': args.model,
                'plan': result.get('plan', {}),
                'tool_results': result.get('tool_results', {}),
                'final_answer': result.get('output', ''),
            }
            print(json.dumps(json_output, indent=2, ensure_ascii=False))
        else:
            # Regular console output
            print(f"\n{'='*70}")
            print("FINAL ANSWER")
            print(f"{'='*70}\n")
            print(result['output'])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
