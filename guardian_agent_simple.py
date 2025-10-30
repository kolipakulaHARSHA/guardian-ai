"""
Guardian AI - Simplified Agent Implementation
Manual orchestration with LLM reasoning (more reliable than LangChain agents)
"""

import os
import sys
import json
import re
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Any

# ============================================================================
# CRITICAL: Suppress warnings for cleaner output
# ============================================================================
# Suppress LangChain deprecation warnings
warnings.filterwarnings("ignore", message=".*Convert_system_message_to_human.*")
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ============================================================================
# CRITICAL: Enable real-time output (disable buffering)
# ============================================================================
os.environ['PYTHONUNBUFFERED'] = '1'

# Fix Unicode encoding for Windows console with line buffering
if sys.platform == 'win32':
    import codecs
    # Reconfigure for line buffering (real-time output)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    else:
        # Fallback for older Python versions
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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
            google_api_key=os.environ['GOOGLE_API_KEY'],
            convert_system_message_to_human=True  # Suppress deprecation warning
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
2. Code_Auditor: Scans code repositories for violations. It has three modes:
   - AUDIT: Exhaustive line-by-line scan. High precision, but slow and expensive. Use for finding specific, known violations.
   - COMPLIANCE: Fast, RAG-based semantic search. Good for a quick overview but may miss details.
   - HYBRID: Recommended for most compliance checks. Uses RAG to find relevant files, then runs a line-by-line audit on just those files. This is the best balance of speed and accuracy.
3. QA_Tool: Answers questions about code repositories using RAG.
{qa_context}
User Query: "{query}"

Determine:
1. Which tools are needed?
2. In what order should they be used?
3. What information should be passed between tools?
4. For Code_Auditor: Which mode should it use? Default to "hybrid" for compliance-related queries. Use "audit" only when the user explicitly asks for a full, exhaustive scan.

Respond ONLY with a JSON object like this:
{{
    "tools_needed": ["Legal_Analyzer", "Code_Auditor"],
    "execution_order": ["Legal_Analyzer", "Code_Auditor"],
    "reasoning": "Need to first understand regulations, then audit code for violations using the most balanced approach.",
    "pdf_path": "path/to/pdf" (if Legal_Analyzer is needed, extract from query),
    "repo_url": "https://github.com/..." (if Code_Auditor or QA_Tool is needed, extract from query OR use active session repo),
    "audit_mode": "hybrid" (use "hybrid" for compliance, "audit" for exhaustive scans, "compliance" for quick checks),
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
                mode = plan.get("audit_mode", "audit")  # "audit", "compliance", or "hybrid"
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
        Run code auditor tool in AUDIT, COMPLIANCE or HYBRID mode
        
        Args:
            repo_url: GitHub repository URL
            brief: Technical brief or compliance guidelines
            mode: "audit" (exhaustive), "compliance" (RAG), or "hybrid" (RAG -> audit)
            
        Returns:
            dict with 'summary' (string) and 'details' (raw data)
        """
        if not repo_url:
            return {"summary": "Error: No repository URL provided", "details": {}}
        
        try:
            if mode == "hybrid":
                return self._run_hybrid_audit(repo_url, brief)

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

    def _run_hybrid_audit(self, repo_url: str, brief: str) -> Dict[str, Any]:
        """
        Run an enhanced intelligent hybrid audit:
        0.  Determine relevant file types to prioritize from the brief.
        1.  Use an LLM to translate abstract guidelines into concrete, searchable code patterns.
        2.  Use targeted RAG searches to find files matching each pattern, boosting prioritized file types.
        3.  Run a precise, line-by-line audit on the aggregated set of relevant files.
        4.  Analyze the initial violations to generate new, more specific search patterns.
        5.  Run a second RAG search with the refined patterns to find any remaining files.
        6.  Perform a final deep scan on the newly discovered files and aggregate all results.
        """
        self._log("--- Running Enhanced Intelligent Hybrid Audit ---")

        # Step 0: Determine relevant file types from the brief (Strategy 3)
        self._log("\nStep 0: Determining relevant file types from brief...")
        prioritized_extensions = []
        try:
            file_type_prompt = f"""
Analyze the following compliance brief and list the file extensions that are most likely to contain relevant code.
Focus on source code, configuration, and documentation files.

Brief:
---
{brief}
---

Respond ONLY with a JSON array of strings.
Example: [".js", ".jsx", ".py", ".json", ".html", ".css", ".sql"]
"""
            response = self.llm.invoke([HumanMessage(content=file_type_prompt)])
            response_content = response.content.strip()
            if '```json' in response_content:
                response_content = response_content.split('```json')[1].split('```')[0].strip()
            prioritized_extensions = json.loads(response_content)
            self._log(f"✓ Prioritizing file types: {', '.join(prioritized_extensions)}")
        except Exception as e:
            self._log(f"⚠️  Could not determine file types, proceeding without prioritization. Error: {e}")
            prioritized_extensions = []


        # Step 1: Generate searchable code patterns from the compliance brief
        self._log("\nStep 1: Translating guidelines into searchable code patterns...")
        try:
            pattern_generation_prompt = f"""
You are a senior software architect specializing in code compliance. Analyze the following compliance guidelines and for each one, generate a list of concrete, problematic code patterns that would indicate a potential violation. These patterns should be searchable within a codebase.

Guidelines:
---
{brief}
---

Respond ONLY with a JSON object where each key is a summary of the guideline and the value is a list of searchable code pattern descriptions.

Example format:
{{
  "Configurable UI/Data": [
    "Hardcoded string literals inside JSX tags (e.g., <div>Hello</div>, <button>Submit</button>)",
    "Hardcoded strings in 'placeholder', 'alt', or 'title' attributes",
    "File paths or URLs as static strings in the code"
  ],
  "Configurable Business Rules": [
    "Use of 'magic numbers' or hardcoded numerical constants in business logic (e.g., if (price > 100.00))",
    "Hardcoded API endpoint URLs in fetch, axios, or other HTTP client calls"
  ],
  "Stateless Design": [
    "Imports of client-side state management libraries like 'jotai', 'redux', 'zustand'",
    "Use of 'useState' or 'useReducer' hooks in React components"
  ]
}}
"""
            response = self.llm.invoke([HumanMessage(content=pattern_generation_prompt)])
            response_content = response.content.strip()
            self._log(f"DEBUG: Raw pattern generation response: '{response_content}'")

            if not response_content:
                raise ValueError("LLM returned an empty response for pattern generation.")

            # Clean the response to ensure it's valid JSON
            if '```json' in response_content:
                response_content = response_content.split('```json')[1].split('```')[0].strip()
            elif response_content.startswith('```') and response_content.endswith('```'):
                response_content = response_content[3:-3].strip()

            guideline_patterns = json.loads(response_content)
            self._log(f"✓ Generated {len(guideline_patterns)} pattern categories.")
        except Exception as e:
            self._log(f"⚠️  Could not generate code patterns: {e}. Falling back to simple audit.")
            # Fallback to a full audit if pattern generation fails
            return self._run_code_auditor(repo_url, brief, mode="audit")

        # Step 2: Find relevant files for each pattern using targeted RAG searches
        self._log("\nStep 2: Discovering relevant files (Pass 1)...")
        initial_relevant_files = set()
        from Github_scanner.code_tool import ComplianceChecker
        checker = ComplianceChecker(model_name="gemini-2.5-flash")
        try:
            clone_result = checker._clone_and_index(repo_url, prioritized_extensions=prioritized_extensions)
            if clone_result['status'] == 'error':
                self._log(f"⚠️  Failed to clone or index repository: {clone_result['error']}")
                return self._run_code_auditor(repo_url, brief, mode="audit")

            for guideline, patterns in guideline_patterns.items():
                self._log(f"  - Searching for patterns related to: '{guideline}'")
                compliance_result = checker.check_patterns(patterns)
                for check in compliance_result.get('compliance_checks', []):
                    for source in check.get('evidence_sources', []):
                        if isinstance(source, str):
                            initial_relevant_files.add(source)
        finally:
            # We keep the checker alive for the second pass, cleanup happens at the end
            pass
        
        if not initial_relevant_files:
            checker.cleanup() # Cleanup now if we're exiting early
            return {
                "summary": "Intelligent Hybrid Audit Complete: No files matching the initial code patterns were found.",
                "details": {"mode": "hybrid_intelligent_v2", "repository": repo_url}
            }

        self._log(f"\n✓ Pass 1 Discovery complete. Found {len(initial_relevant_files)} files.")

        # Step 3: Run a deep, line-by-line audit on the first set of files
        self._log("\nStep 3: Running deep scan (Pass 1)...")
        CodeAuditor = get_code_tool()
        auditor = CodeAuditor(model_name="gemini-2.5-flash")
        
        import tempfile
        import shutil
        import git
        from pathlib import Path

        temp_dir = checker.temp_dir # Use the same temp dir from the checker
        repo_path = Path(temp_dir)
        
        files_to_scan_abs_pass1 = [str(repo_path / file) for file in initial_relevant_files if (repo_path / file).exists()]
        
        initial_audit_result = {"violations": []}
        if files_to_scan_abs_pass1:
            initial_audit_result = auditor.scan_files(files_to_scan_abs_pass1, brief)
        
        initial_violations = initial_audit_result.get('violations', [])
        self._log(f"✓ Pass 1 Scan complete. Found {len(initial_violations)} violations.")

        # --- Strategy 2: Iterative Pattern Refinement ---
        all_violations = initial_violations
        newly_discovered_files = set()

        if initial_violations:
            # Step 4: Analyze initial violations to generate new patterns
            self._log("\nStep 4: Analyzing violations to refine search patterns (Strategy 2)...")
            try:
                refinement_prompt = f"""
You are a code compliance expert. Based on the following list of violations that were just found, generate a new, more specific set of searchable code patterns to find similar but potentially missed issues.

Found Violations:
---
{json.dumps(initial_violations[:15], indent=2)}
---

Respond ONLY with a JSON object containing a single key "refined_patterns" with a list of new, specific, and searchable pattern descriptions.

Example:
{{
  "refined_patterns": [
    "Hardcoded color hex codes (e.g., #FFFFFF, #000) in CSS or inline styles",
    "Use of `setTimeout` with a hardcoded numerical delay",
    "Hardcoded file download names like 'animation.webm'"
  ]
}}
"""
                response = self.llm.invoke([HumanMessage(content=refinement_prompt)])
                response_content = response.content.strip()
                if '```json' in response_content:
                    response_content = response_content.split('```json')[1].split('```')[0].strip()
                
                refined_patterns_data = json.loads(response_content)
                refined_patterns = refined_patterns_data.get("refined_patterns", [])
                self._log(f"✓ Generated {len(refined_patterns)} new patterns for second pass.")

                # Step 5: Run a second RAG search with the refined patterns
                if refined_patterns:
                    self._log("\nStep 5: Discovering relevant files with refined patterns (Pass 2)...")
                    compliance_result_pass2 = checker.check_patterns(refined_patterns)
                    
                    second_pass_files = set()
                    for check in compliance_result_pass2.get('compliance_checks', []):
                        for source in check.get('evidence_sources', []):
                            if isinstance(source, str):
                                second_pass_files.add(source)
                    
                    # Filter out files we've already scanned
                    newly_discovered_files = second_pass_files - initial_relevant_files
                    self._log(f"✓ Pass 2 Discovery complete. Found {len(newly_discovered_files)} new files.")

            except Exception as e:
                self._log(f"⚠️  Could not refine patterns for second pass. Error: {e}")

        # Step 6: Perform a final deep scan on newly discovered files
        if newly_discovered_files:
            self._log("\nStep 6: Running deep scan on newly discovered files (Pass 2)...")
            files_to_scan_abs_pass2 = [str(repo_path / file) for file in newly_discovered_files if (repo_path / file).exists()]
            
            if files_to_scan_abs_pass2:
                second_audit_result = auditor.scan_files(files_to_scan_abs_pass2, brief)
                second_violations = second_audit_result.get('violations', [])
                self._log(f"✓ Pass 2 Scan complete. Found {len(second_violations)} new violations.")
                all_violations.extend(second_violations)
        
        # Final cleanup
        checker.cleanup()

        # Step 7: Aggregate and return all results
        summary = f"Enhanced Hybrid Audit Results:\n"
        summary += f"- Repository: {repo_url}\n"
        summary += f"- Pass 1 (Pattern-based): Found {len(initial_relevant_files)} files, resulting in {len(initial_violations)} violations.\n"
        if newly_discovered_files:
            summary += f"- Pass 2 (Refinement-based): Found {len(newly_discovered_files)} new files, adding {len(all_violations) - len(initial_violations)} more violations.\n"
        summary += f"- Total violations found: {len(all_violations)}\n\n"

        if all_violations:
            summary += "Top violations found:\n"
            for i, v in enumerate(all_violations[:10], 1):
                relative_path = v.get('file', '').replace(str(repo_path), '').lstrip('/\\')
                summary += f"{i}. {relative_path} (line {v.get('line')})\n"
                summary += f"   {v.get('explanation')}\n\n"
        else:
            summary += "✅ No violations found in the detailed scan of the relevant files!\n"

        return {
            "summary": summary,
            "details": {
                "mode": "hybrid_intelligent_v2",
                "repository": repo_url,
                "total_violations": len(all_violations),
                "violations": all_violations,
                "files_scanned_in_detail": list(initial_relevant_files | newly_discovered_files),
                "scan_statistics": {
                    "pass1_files": len(initial_relevant_files),
                    "pass1_violations": len(initial_violations),
                    "pass2_new_files": len(newly_discovered_files),
                    "pass2_violations": len(all_violations) - len(initial_violations)
                }
            }
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
        
        # Default behavior: Save results to a generated JSON file
        import json
        from datetime import datetime
        import re

        # Generate a filename based on repo and timestamp
        output_filename = args.output  # Use custom filename if provided
        if not output_filename:
            repo_url = result.get('plan', {}).get('repo_url')
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            repo_name = "guardian_report" # Default

            if repo_url:
                match = re.search(r'github\.com/[\w-]+/([\w.-]+)', repo_url)
                if match:
                    repo_name = match.group(1).replace('.git', '')
            
            output_filename = f"{repo_name}_{timestamp}.json"

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
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to: {output_filename}")
        
        # Output as JSON to console if requested
        if args.json:
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
