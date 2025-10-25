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
        # Persistent QA tool for interactive mode
        self.qa_tool_instance = None
        self.qa_repo_url = None
        self.qa_temp_dir = None
    
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
        
        # Add context about active QA session
        qa_context = ""
        if self.qa_repo_url:
            qa_context = f"""

IMPORTANT CONTEXT: A QA session is currently active for repository: {self.qa_repo_url}
If the user's query is asking about "the repo", "this repository", "the project", or similar references WITHOUT specifying a URL,
they are referring to the active QA session repository.
In this case, set repo_url to: {self.qa_repo_url}
"""
        
        planning_prompt = f"""You are Guardian AI, a compliance and code analysis assistant. Analyze this user query and create an execution plan.

Available tools:
1. Legal_Analyzer: Analyzes PDF regulatory documents to extract compliance requirements
2. Code_Auditor: Scans code repositories for violations
   - AUDIT mode (default): Exhaustive line-by-line scanning to find specific violations
   - COMPLIANCE mode: RAG-based semantic search to check overall compliance with guidelines
3. QA_Tool: Answers questions about code repositories using RAG
{qa_context}
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
    "repo_url": "https://github.com/..." (if Code_Auditor or QA_Tool is needed, extract from query OR use active session repo),
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
        
        # Check for repository mentions or active QA session
        if 'github.com' in query_lower or 'repo' in query_lower or self.qa_repo_url:
            url_match = re.search(r'https?://github\.com/[\w-]+/[\w-]+', query)
            if url_match:
                plan["repo_url"] = url_match.group(0)
            elif self.qa_repo_url:
                # Use active QA session repository
                plan["repo_url"] = self.qa_repo_url
            
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
                "Create a concise, bullet-pointed technical brief for a developer. "
                "List the key compliance requirements from this document that can "
                "be checked in a codebase."
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
        """Run QA tool - uses existing session if available for the same repo"""
        if not repo_url:
            return "Error: No repository URL provided"
        
        # Check if we have an active QA session for this repo
        if self.qa_tool_instance and self.qa_repo_url == repo_url:
            self._log(f"Using existing QA session for {repo_url}")
            try:
                result = self.qa_tool_instance.ask_question(question)
                
                if result['status'] == 'success':
                    answer = result['answer']
                    sources = result.get('sources', [])
                    if sources:
                        answer += f"\n\nSources: {', '.join(sources[:3])}"
                    return answer
                else:
                    return f"Error: {result.get('error', 'Unknown error')}"
            except Exception as e:
                return f"Error in Q&A: {e}"
        
        # No existing session or different repo - create a new one-time session
        try:
            import tempfile
            import shutil
            import git
            from pathlib import Path
            
            QATool = get_qa_tool()
            qa = QATool(model_name=self.model_name)
            
            # Clone repository to temporary directory
            temp_dir = tempfile.mkdtemp(prefix='guardian_qa_')
            try:
                self._log(f"Cloning repository: {repo_url}")
                git.Repo.clone_from(repo_url, temp_dir)
                self._log(f"✓ Repository cloned")
                
                # Index repository
                self._log("Indexing repository...")
                repo_path = Path(temp_dir)
                index_result = qa.index_repository(repo_path)
                
                if index_result['status'] == 'error':
                    return f"Error indexing repository: {index_result.get('message', 'Unknown error')}"
                
                self._log(f"✓ Indexed {index_result['documents_count']} documents")
                
                # Ask question
                self._log(f"Answering question: {question}")
                result = qa.ask_question(question)
                
                if result['status'] == 'success':
                    answer = result['answer']
                    sources = result.get('sources', [])
                    if sources:
                        answer += f"\n\nSources: {', '.join(sources[:3])}"
                    return answer
                else:
                    return f"Error: {result.get('error', 'Unknown error')}"
                    
            finally:
                # Cleanup temporary directory
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir, onerror=lambda func, path, exc: (os.chmod(path, 0o777), func(path)))
                    except Exception as cleanup_error:
                        self._log(f"Warning: Cleanup failed: {cleanup_error}")
                        
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
    
    def setup_qa_session(self, repo_url: str) -> Dict[str, Any]:
        """
        Set up a persistent QA session for a repository.
        This allows asking multiple questions without re-indexing.
        """
        import tempfile
        import shutil
        import git
        from pathlib import Path
        
        # Clean up any existing session
        self.cleanup_qa_session()
        
        try:
            QATool = get_qa_tool()
            self.qa_tool_instance = QATool(model_name=self.model_name)
            self.qa_repo_url = repo_url
            
            # Clone repository
            self.qa_temp_dir = tempfile.mkdtemp(prefix='guardian_qa_')
            print(f"📥 Cloning repository: {repo_url}")
            git.Repo.clone_from(repo_url, self.qa_temp_dir)
            print(f"✓ Repository cloned\n")
            
            # Index repository
            print("📚 Indexing repository (this may take a moment)...")
            repo_path = Path(self.qa_temp_dir)
            index_result = self.qa_tool_instance.index_repository(repo_path)
            
            if index_result['status'] == 'error':
                self.cleanup_qa_session()
                return {
                    'status': 'error',
                    'message': f"Error indexing repository: {index_result.get('message', 'Unknown error')}"
                }
            
            print(f"✅ QA session ready! Indexed {index_result['documents_count']} documents.\n")
            print("💡 You can now ask questions about this repository without providing the URL.\n")
            
            return {
                'status': 'success',
                'repo_url': repo_url,
                'documents_count': index_result['documents_count'],
                'chunks_count': index_result['chunks_count']
            }
            
        except Exception as e:
            self.cleanup_qa_session()
            return {
                'status': 'error',
                'message': f"Error setting up QA session: {e}"
            }
    
    def ask_qa(self, question: str) -> str:
        """Ask a question in the current QA session"""
        if not self.qa_tool_instance:
            return "❌ No QA session active. Use 'set repo <url>' to start a session."
        
        try:
            result = self.qa_tool_instance.ask_question(question)
            
            if result['status'] == 'success':
                answer = result['answer']
                sources = result.get('sources', [])
                if sources:
                    answer += f"\n\n📎 Sources: {', '.join(sources[:3])}"
                return answer
            else:
                return f"❌ Error: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"❌ Error in Q&A: {e}"
    
    def cleanup_qa_session(self):
        """Clean up the QA session and temporary files"""
        if self.qa_temp_dir and os.path.exists(self.qa_temp_dir):
            try:
                import shutil
                shutil.rmtree(self.qa_temp_dir, onerror=lambda func, path, exc: (os.chmod(path, 0o777), func(path)))
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  Warning: Cleanup failed: {e}")
        
        self.qa_tool_instance = None
        self.qa_repo_url = None
        self.qa_temp_dir = None


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
        print("="*70)
        print("INTERACTIVE MODE")
        print("="*70)
        print("\n📖 Commands:")
        print("  • 'set repo <url>'  - Set up QA session for a repository")
        print("  • 'show repo'       - Show current QA repository")
        print("  • 'clear repo'      - Clear QA session")
        print("  • 'help'            - Show this help")
        print("  • 'exit' or 'quit'  - Exit interactive mode")
        print("\n💡 Tips:")
        print("  • After setting a repo, ask questions directly without the URL")
        print("  • For other tasks (legal analysis, code audit), include full details")
        print("\n" + "="*70 + "\n")
        
        while True:
            try:
                query = input("You: ").strip()
                
                if not query:
                    continue
                
                # Handle special commands
                if query.lower() in ['exit', 'quit', 'q']:
                    if agent.qa_tool_instance:
                        print("\n🧹 Cleaning up QA session...")
                        agent.cleanup_qa_session()
                    print("👋 Goodbye!\n")
                    break
                
                elif query.lower() == 'help':
                    print("\n📖 Available Commands:")
                    print("  • set repo <url>   - Set up QA session for a GitHub repository")
                    print("  • show repo        - Display current QA repository URL")
                    print("  • clear repo       - Clear the current QA session")
                    print("  • help             - Show this help message")
                    print("  • exit/quit        - Exit interactive mode")
                    print("\n💬 Usage Examples:")
                    print("  You: set repo https://github.com/user/repo")
                    print("  You: What does this project do?")
                    print("  You: How do I install it?")
                    print("  You: clear repo")
                    print()
                    continue
                
                elif query.lower().startswith('set repo '):
                    repo_url = query[9:].strip()
                    if repo_url:
                        result = agent.setup_qa_session(repo_url)
                        if result['status'] == 'error':
                            print(f"\n❌ {result['message']}\n")
                        # Success message already printed by setup_qa_session
                    else:
                        print("\n❌ Please provide a repository URL.\n")
                        print("   Example: set repo https://github.com/user/repo\n")
                    continue
                
                elif query.lower() == 'show repo':
                    if agent.qa_repo_url:
                        print(f"\n📦 Current repository: {agent.qa_repo_url}")
                        print("   Status: ✅ Active QA session\n")
                    else:
                        print("\n📦 No repository set.")
                        print("   Use 'set repo <url>' to start a QA session.\n")
                    continue
                
                elif query.lower() in ['clear repo', 'reset repo']:
                    if agent.qa_tool_instance:
                        print("\n🧹 Clearing QA session...")
                        agent.cleanup_qa_session()
                        print("✅ QA session cleared.\n")
                    else:
                        print("\n💡 No active QA session to clear.\n")
                    continue
                
                # Handle regular queries
                # If QA session is active and query doesn't mention repo/pdf, use QA mode
                if agent.qa_tool_instance and not any(word in query.lower() for word in ['github.com', 'repository', 'repo', '.pdf', 'regulation']):
                    answer = agent.ask_qa(query)
                    print(f"\n🤖 Guardian AI: {answer}\n")
                else:
                    # Use full agent for complex queries
                    answer = agent.ask(query)
                    print(f"\n🤖 Guardian AI: {answer}\n")
                    
            except KeyboardInterrupt:
                print("\n")
                if agent.qa_tool_instance:
                    print("🧹 Cleaning up QA session...")
                    agent.cleanup_qa_session()
                print("👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                import traceback
                if not args.quiet:
                    traceback.print_exc()
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
