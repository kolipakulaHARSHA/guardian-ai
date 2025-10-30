import os
import sys
from pathlib import Path
import warnings

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

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
try:
    # Try old import for LangChain < 1.0
    from langchain.agents import AgentExecutor, create_tool_calling_agent
except ImportError:
    # For LangChain >= 1.0, AgentExecutor moved to langgraph
    try:
        from langgraph.prebuilt import create_react_agent
        # We'll use create_react_agent instead of AgentExecutor + create_tool_calling_agent
        AgentExecutor = None  # Flag to use alternative approach
        create_tool_calling_agent = None
    except ImportError:
        # If langgraph is not available, we need a different approach
        raise ImportError(
            "LangChain 1.0+ requires 'langgraph' for agent functionality. "
            "Please install it with: pip install langgraph"
        )
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# Load environment variables
load_dotenv()
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
if langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    print("LangSmith tracing enabled.")
else:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    print("Warning: LANGCHAIN_API_KEY not found. LangSmith tracing is disabled.")

if not os.getenv('GOOGLE_API_KEY'):
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

os.environ["LANGCHAIN_PROJECT"] = "GuardianAI-LangChain"

# Add module paths
GUARDIAN_ROOT = Path(__file__).parent
sys.path.insert(0, str(GUARDIAN_ROOT / 'Guardian-Legal-analyzer-main'))
sys.path.insert(0, str(GUARDIAN_ROOT / 'Github_scanner'))

# Tool imports (lazy loaded)
_legal_tool_func = None
_code_tool_class = None
_qa_tool_class = None

# Global storage for violations (for JSON export)
_last_audit_results = None


def get_legal_tool_func():
    """Lazy import legal tool"""
    global _legal_tool_func
    if _legal_tool_func is None:
        from legal_tool import legal_analyst_tool
        _legal_tool_func = legal_analyst_tool
    return _legal_tool_func


def get_code_tool_class():
    """Lazy import code tool"""
    global _code_tool_class
    if _code_tool_class is None:
        from code_tool import CodeAuditorAgent
        _code_tool_class = CodeAuditorAgent
    return _code_tool_class


def get_qa_tool_class():
    """Lazy import QA tool"""
    global _qa_tool_class
    if _qa_tool_class is None:
        from qa_tool import RepoQATool
        _qa_tool_class = RepoQATool
    return _qa_tool_class

# --- LangChain Tool Definitions ---

@tool
def legal_analyzer(pdf_path: str, question: str = "Create a concise, bullet-pointed technical brief for a developer. List the key compliance requirements from this document that can be checked in a codebase.") -> str:
    """
    Analyzes a PDF document to extract compliance requirements.
    Use this tool when you need to understand the rules or guidelines from a PDF.
    """
    legal_tool_func = get_legal_tool_func()
    if not os.path.isabs(pdf_path):
        pdf_path = str(GUARDIAN_ROOT / pdf_path)
    if not os.path.exists(pdf_path):
        return f"Error: PDF not found at {pdf_path}"
    try:
        return legal_tool_func(pdf_path, question, use_existing_db=True, filter_by_current_pdf=True)
    except Exception as e:
        return f"Error in legal analysis: {e}"

@tool
def code_auditor(repo_url: str, brief: str, mode: str = "hybrid") -> str:
    """
    Scans a code repository for violations based on a provided brief.
    It has three modes:
    - 'audit': Exhaustive line-by-line scan. High precision, but slow and expensive.
    - 'compliance': Fast, RAG-based semantic search. Good for a quick overview.
    - 'hybrid': Recommended. Uses RAG to find relevant files, then audits them. Best balance of speed and accuracy.
    """
    global _last_audit_results
    
    if not repo_url:
        return "Error: No repository URL provided"

    # Use the correct, full hybrid audit logic if mode is 'hybrid'
    if mode == "hybrid":
        try:
            import json
            # Instantiate a new LLM for internal tool operations
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro-preview-03-25", 
                temperature=0.3,
                convert_system_message_to_human=True
            )
            
            print("--- Running Enhanced Intelligent Hybrid Audit ---")
            print(f"DEBUG: Brief length: {len(brief)} characters")
            print(f"DEBUG: Brief preview: {brief[:200]}...")

            # Step 0: Determine relevant file types
            print("\nStep 0: Determining relevant file types from brief...")
            prioritized_extensions = []
            try:
                file_type_prompt = f'Analyze the following compliance brief and list the file extensions that are most likely to contain relevant code. Respond ONLY with a JSON array of file extensions (e.g., [".js", ".jsx", ".py"]). Brief:\n---\n{brief}\n---'
                response = llm.invoke(file_type_prompt)
                response_content = response.content.strip().split('```json')[-1].split('```')[0].strip()
                raw_extensions = json.loads(response_content)
                
                # Sanitize extensions: remove glob patterns, ensure they start with '.'
                prioritized_extensions = []
                for ext in raw_extensions:
                    if isinstance(ext, str):
                        # Remove glob patterns like '**/', '*/', etc.
                        ext = ext.replace('**/', '').replace('*/', '').replace('*', '')
                        # Ensure it starts with '.'
                        if not ext.startswith('.'):
                            ext = '.' + ext
                        # Only add if it's a valid extension (e.g., '.js', '.py')
                        if len(ext) > 1 and '/' not in ext:
                            prioritized_extensions.append(ext)
                
                if prioritized_extensions:
                    print(f"✓ Prioritizing file types: {', '.join(prioritized_extensions)}")
                else:
                    print(f"⚠️  No valid file extensions extracted, proceeding without prioritization.")
            except Exception as e:
                print(f"⚠️  Could not determine file types, proceeding without prioritization. Error: {e}")

            # Step 1: Generate searchable code patterns
            print("\nStep 1: Translating guidelines into searchable code patterns...")
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
                response = llm.invoke(pattern_generation_prompt)
                response_content = response.content.strip()
                
                if not response_content:
                    raise ValueError("LLM returned an empty response for pattern generation.")

                # Clean the response to ensure it's valid JSON
                if '```json' in response_content:
                    response_content = response_content.split('```json')[1].split('```')[0].strip()
                elif response_content.startswith('```') and response_content.endswith('```'):
                    response_content = response_content[3:-3].strip()

                guideline_patterns = json.loads(response_content)
                print(f"✓ Generated {len(guideline_patterns)} pattern categories.")
                print(f"DEBUG: Pattern categories: {list(guideline_patterns.keys())}")
            except Exception as e:
                print(f"⚠️  Could not generate code patterns: {e}. Falling back to simple audit.")
                mode = "audit" # Fallback to full audit
            
            # If hybrid setup failed, fall back to audit. Otherwise, continue with hybrid logic.
            if mode == "hybrid":
                # Step 2 & 3: Find and audit relevant files (Pass 1)
                print("\nStep 2 & 3: Discovering and scanning files (Pass 1)...")
                from Github_scanner.code_tool import ComplianceChecker

                initial_relevant_files = set()
                checker = ComplianceChecker(model_name="gemini-2.5-flash")
                initial_violations = []
                try:
                    clone_result = checker._clone_and_index(repo_url, prioritized_extensions=prioritized_extensions)
                    if clone_result['status'] == 'error':
                        raise RuntimeError(f"Failed to clone or index repository: {clone_result['error']}")

                    for guideline, patterns in guideline_patterns.items():
                        print(f"  - Searching for patterns related to: '{guideline}'")
                        
                        # Pass patterns directly to check_patterns, just like guardian_agent_simple.py
                        # The check_patterns method will handle the iteration
                        try:
                            compliance_result = checker.check_patterns(patterns)
                            files_found = len(compliance_result.get('compliance_checks', []))
                            print(f"    DEBUG: Found {files_found} compliance check results")
                            for check in compliance_result.get('compliance_checks', []):
                                for source in check.get('evidence_sources', []):
                                    if isinstance(source, str):
                                        initial_relevant_files.add(source)
                        except Exception as e:
                            print(f"    WARNING: Error processing patterns for '{guideline}': {e}")
                            # If there's an error (e.g., patterns not in expected format), try to recover
                            if isinstance(patterns, list):
                                # Filter to only strings and retry
                                safe_patterns = [p for p in patterns if isinstance(p, str)]
                                if safe_patterns:
                                    compliance_result = checker.check_patterns(safe_patterns)
                                    for check in compliance_result.get('compliance_checks', []):
                                        for source in check.get('evidence_sources', []):
                                            if isinstance(source, str):
                                                initial_relevant_files.add(source)
                    
                    print(f"\nDEBUG: Total unique files collected: {len(initial_relevant_files)}")
                    
                    # Step 3: Always create auditor and repo_path (needed for Pass 2 even if Pass 1 finds nothing)
                    CodeAuditor = get_code_tool_class()
                    auditor = CodeAuditor(model_name="gemini-2.5-flash")
                    repo_path = Path(checker.temp_dir)
                    
                    # Run deep scan on Pass 1 files if any were found
                    files_to_scan_abs = []
                    skipped_files = []
                    for f in initial_relevant_files:
                        file_path = repo_path / f
                        if file_path.exists():
                            files_to_scan_abs.append(str(file_path))
                        else:
                            skipped_files.append(f)
                            print(f"    WARNING: File not found, skipping: {f}")
                    
                    if skipped_files:
                        print(f"\n⚠️  {len(skipped_files)} file(s) were skipped because they don't exist:")
                        for sf in skipped_files:
                            print(f"    - {sf}")
                    
                    print(f"\nDEBUG: Passing {len(files_to_scan_abs)} files to auditor:")
                    for i, f in enumerate(files_to_scan_abs, 1):
                        print(f"    {i}. {Path(f).name}")
                    
                    initial_audit_result = {"violations": []}
                    if files_to_scan_abs:
                        initial_audit_result = auditor.scan_files(files_to_scan_abs, brief)
                    
                    initial_violations = initial_audit_result.get('violations', [])
                    print(f"✓ Pass 1 complete. Found {len(initial_relevant_files)} files, {len(initial_violations)} violations.")

                except Exception as e:
                    print(f"Error during Pass 1: {e}")
                # Don't cleanup yet, we need the repo for pass 2

                # Step 4, 5, 6: Refine patterns and run Pass 2
                # IMPORTANT: Create a COPY of initial_violations, not a reference!
                all_violations = initial_violations.copy()  # Use .copy() to avoid reference issues
                pass1_violation_count = len(initial_violations)  # Store the count
                newly_discovered_files = set()
                if initial_violations:
                    print("\nStep 4, 5, 6: Refining patterns and running Pass 2...")
                    try:
                        refinement_prompt = f'Based on these violations, generate new, specific searchable code patterns. Respond with a JSON object with a "refined_patterns" list. Violations:\n---\n{json.dumps(initial_violations[:10], indent=2)}\n---'
                        response = llm.invoke(refinement_prompt)
                        response_content = response.content.strip().split('```json')[-1].split('```')[0].strip()
                        parsed_response = json.loads(response_content)
                        refined_patterns_raw = parsed_response.get("refined_patterns", [])
                        
                        # Ensure all patterns are strings
                        refined_patterns = []
                        for pattern in refined_patterns_raw:
                            if isinstance(pattern, str):
                                refined_patterns.append(pattern)
                            elif isinstance(pattern, dict):
                                # If it's a dict, try to get a string value
                                pattern_str = pattern.get('pattern') or pattern.get('description') or str(pattern)
                                refined_patterns.append(pattern_str)
                            else:
                                # Convert to string as fallback
                                refined_patterns.append(str(pattern))
                        
                        if refined_patterns:
                            print(f"Running compliance checks with {len(refined_patterns)} refined patterns...")
                            compliance_result_pass2 = checker.check_patterns(refined_patterns)
                            second_pass_files = {src for check in compliance_result_pass2.get('compliance_checks', []) for src in check.get('evidence_sources', []) if isinstance(src, str)}
                            newly_discovered_files = second_pass_files - initial_relevant_files
                            print(f"✓ Pass 2 Discovery complete. Found {len(newly_discovered_files)} new files.")

                            if newly_discovered_files:
                                print("\nStep 6: Running deep scan on newly discovered files (Pass 2)...")
                                files_to_scan_abs_pass2 = [str(repo_path / f) for f in newly_discovered_files if (repo_path / f).exists()]
                                if files_to_scan_abs_pass2:
                                    print(f"DEBUG: Scanning {len(files_to_scan_abs_pass2)} Pass 2 files...", flush=True)
                                    print(f"DEBUG: Current violation count before Pass 2: {len(all_violations)}", flush=True)
                                    
                                    second_audit_result = auditor.scan_files(files_to_scan_abs_pass2, brief)
                                    second_violations = second_audit_result.get('violations', [])
                                    
                                    print(f"DEBUG: Pass 2 returned {len(second_violations)} violations", flush=True)
                                    all_violations.extend(second_violations)
                                    print(f"DEBUG: Total violations after extending: {len(all_violations)}", flush=True)
                                    print(f"✓ Pass 2 Scan complete. Found {len(second_violations)} new violations.", flush=True)
                        else:
                            print("⚠️  No valid refined patterns generated for Pass 2")

                    except Exception as e:
                        import traceback
                        print(f"⚠️  Could not refine patterns for second pass. Error: {e}")
                        if os.getenv('DEBUG'):
                            traceback.print_exc()

                # Final cleanup
                checker.cleanup()

                # Step 7: Aggregate and return summary
                # Calculate Pass 2 violations correctly
                pass2_violation_count = len(all_violations) - pass1_violation_count
                
                # Store violations globally for JSON export
                _last_audit_results = {
                    'mode': mode,
                    'repo_url': repo_url,
                    'violations': all_violations,
                    'stats': {
                        'total_violations': len(all_violations),
                        'pass1_files': len(initial_relevant_files),
                        'pass1_violations': pass1_violation_count,
                        'pass2_files': len(newly_discovered_files),
                        'pass2_violations': pass2_violation_count
                    }
                }
                
                summary = f"Enhanced Hybrid Audit Results:\n"
                summary += f"- Repository: {repo_url}\n"
                summary += f"- Pass 1 (Pattern-based): Found {len(initial_relevant_files)} files, resulting in {pass1_violation_count} violations.\n"
                if newly_discovered_files:
                    summary += f"- Pass 2 (Refinement-based): Found {len(newly_discovered_files)} new files, adding {pass2_violation_count} more violations.\n"
                summary += f"- Total violations found: {len(all_violations)}\n\n"
                
                if all_violations:
                    summary += "Top violations found:\n"
                    for i, v in enumerate(all_violations[:10], 1):
                        summary += f"{i}. {v.get('file')} (line {v.get('line')})\n   {v.get('explanation')}\n\n"
                else:
                    summary += "✅ No violations found in the detailed scan of relevant files.\n"
                
                return summary

        except Exception as e:
            return f"Error in hybrid code audit: {e}"

    # Fallback for 'audit' or 'compliance' modes
    try:
        CodeAuditor = get_code_tool_class()
        auditor = CodeAuditor(model_name="gemini-2.5-flash")
        # For simplicity, both 'audit' and 'compliance' will run a full scan in this tool.
        # A real implementation would differentiate them.
        result = auditor.scan_repository(repo_url, brief)
        
        violations = result.get('violations', [])
        
        # Store violations globally for JSON export
        _last_audit_results = {
            'mode': mode,
            'repo_url': repo_url,
            'violations': violations,
            'stats': {
                'total_violations': len(violations)
            }
        }
        
        summary = f"Audit Results (Mode: {mode}):\n"
        summary += f"- Repository: {repo_url}\n"
        summary += f"- Violations found: {len(violations)}\n\n"
        
        if violations:
            summary += "Top violations:\n"
            for i, v in enumerate(violations[:5], 1):
                summary += f"{i}. {v.get('file')} (line {v.get('line')})\n"
                summary += f"   {v.get('explanation')}\n\n"
        else:
            summary += "✅ No violations found!\n"
        return summary
    except Exception as e:
        return f"Error in code audit (mode: {mode}): {e}"

@tool
def repository_qa(repo_url: str, question: str) -> str:
    """
    Answers questions about a code repository.
    Use this to understand what a repository does, how to use it, etc.
    """
    if not repo_url:
        return "Error: No repository URL provided"
    try:
        QATool = get_qa_tool_class()
        qa = QATool(model_name="gemini-2.5-pro-preview-03-25")
        
        # This is a simplified, stateless implementation
        import tempfile
        import shutil
        import git
        from pathlib import Path

        temp_dir = tempfile.mkdtemp(prefix='guardian_qa_')
        try:
            git.Repo.clone_from(repo_url, temp_dir)
            repo_path = Path(temp_dir)
            index_result = qa.index_repository(repo_path)
            if index_result['status'] == 'error':
                return f"Error indexing repository: {index_result.get('message', 'Unknown error')}"
            
            result = qa.ask_question(question)
            if result['status'] == 'success':
                return result['answer']
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    except Exception as e:
        return f"Error in Q&A: {e}"

class LangChainGuardianAgent:
    def __init__(self, model_name: str = "gemini-2.5-pro-preview-03-25"):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=0.3,
            convert_system_message_to_human=True  # Explicitly enable (suppresses warning)
        )
        
        # State management for QA sessions
        self.qa_tool_instance = None
        self.qa_repo_url = None
        self.qa_temp_dir = None
        self.session_history = []
        
        # Create stateful tool wrappers
        self.tools = [
            legal_analyzer, 
            self._create_stateful_code_auditor(),
            self._create_stateful_repository_qa()
        ]
        self.agent_executor = self._create_agent_executor()
    
    def _create_stateful_code_auditor(self):
        """Create a stateful wrapper for code_auditor that can access instance state"""
        @tool
        def stateful_code_auditor(repo_url: str, brief: str, mode: str = "hybrid") -> str:
            """
            Scan a code repository for violations using intelligent hybrid scanning.
            
            Args:
                repo_url: The GitHub repository URL to scan
                brief: Compliance guidelines to check against (use output from legal_analyzer)
                mode: Scanning mode. ALWAYS use 'hybrid' (default, recommended) unless user explicitly requests otherwise.
                      'hybrid' = intelligent 2-pass scan with AI pattern generation (optimal accuracy/speed)
                      'audit' = slow exhaustive line-by-line scan (only if specifically requested)
                      'compliance' = fast RAG-only scan (quick overview only)
            
            Returns:
                A summary of violations found
            
            IMPORTANT: Use mode="hybrid" for best results. Do NOT use mode="audit" unless explicitly requested.
            """
            # Call the original code_auditor but it can access self through closure
            return code_auditor.func(repo_url, brief, mode)
        
        return stateful_code_auditor
    
    def _create_stateful_repository_qa(self):
        """Create a stateful wrapper for repository_qa that reuses indexed repos"""
        @tool
        def stateful_repository_qa(repo_url: str, question: str) -> str:
            """
            Answer questions about a code repository using RAG.
            
            Args:
                repo_url: The GitHub repository URL to analyze
                question: The question to answer about the repository
            
            Returns:
                The answer to the question based on repository content
            """
            # Check if we have this repo already indexed
            if self.qa_tool_instance and self.qa_repo_url == repo_url:
                print(f"♻️  Reusing existing QA session for {repo_url}")
                try:
                    result = self.qa_tool_instance.ask_question(question)
                    if result['status'] == 'success':
                        return result['answer']
                    else:
                        return f"Error: {result.get('error', 'Unknown error')}"
                except Exception as e:
                    print(f"⚠️  Error reusing session, creating new one: {e}")
                    self._cleanup_qa_session()
            
            # Need to create a new session
            print(f"🔄 Creating new QA session for {repo_url}")
            return self._start_qa_session(repo_url, question)
        
        return stateful_repository_qa
    
    def _start_qa_session(self, repo_url: str, question: str) -> str:
        """Start a new QA session with a repository"""
        import tempfile
        import shutil
        import git
        from pathlib import Path
        
        try:
            QATool = get_qa_tool_class()
            self.qa_tool_instance = QATool(model_name="gemini-2.5-pro-preview-03-25")
            
            # Create temp directory for this session
            self.qa_temp_dir = tempfile.mkdtemp(prefix='guardian_qa_session_')
            
            # Clone and index the repository
            git.Repo.clone_from(repo_url, self.qa_temp_dir)
            repo_path = Path(self.qa_temp_dir)
            
            index_result = self.qa_tool_instance.index_repository(repo_path)
            if index_result['status'] == 'error':
                self._cleanup_qa_session()
                return f"Error indexing repository: {index_result.get('message', 'Unknown error')}"
            
            # Store the repo URL for reuse
            self.qa_repo_url = repo_url
            print(f"✅ QA session started for {repo_url}")
            
            # Answer the question
            result = self.qa_tool_instance.ask_question(question)
            if result['status'] == 'success':
                return result['answer']
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            self._cleanup_qa_session()
            return f"Error in Q&A: {e}"
    
    def _cleanup_qa_session(self):
        """Clean up the current QA session"""
        if self.qa_temp_dir and os.path.exists(self.qa_temp_dir):
            import shutil
            try:
                shutil.rmtree(self.qa_temp_dir)
            except Exception as e:
                print(f"⚠️  Warning: Could not remove temp directory {self.qa_temp_dir}: {e}")
        
        self.qa_tool_instance = None
        self.qa_repo_url = None
        self.qa_temp_dir = None
    
    def end_qa_session(self):
        """End the current QA session (public method)"""
        if self.qa_repo_url:
            print(f"🔚 Ending QA session for {self.qa_repo_url}")
            self._cleanup_qa_session()
            return "QA session ended successfully."
        else:
            return "No active QA session to end."
    
    def get_session_info(self) -> str:
        """Get information about the current session"""
        if self.qa_repo_url:
            return f"Active QA session for: {self.qa_repo_url}"
        else:
            return "No active QA session"

    def _create_agent_executor(self):
        # Build system message with QA session context if active
        system_message = """You are Guardian AI, a powerful compliance and code analysis assistant.

Your goal is to answer the user's query fully. You have tools to help you.

Here's how your tools work together:
- The `legal_analyzer` tool can read local PDF files to extract rules and guidelines. Its output is a technical brief.
- The `stateful_code_auditor` tool scans a code repository. It needs a `brief` to know what to look for. You should use the output from `legal_analyzer` as the input `brief` for `stateful_code_auditor`.
- The `stateful_repository_qa` tool answers questions about repositories. It maintains a session, so multiple questions about the same repo are efficient.

IMPORTANT - SCANNING MODE:
When using `stateful_code_auditor`, ALWAYS set mode="hybrid" (the default) for the intelligent hybrid scan.
The hybrid scan is optimized to find violations efficiently using AI-powered pattern generation.
NEVER use mode="audit" unless specifically requested by the user.

Think step-by-step. If a user asks for an audit based on a local PDF, you should:
1. Call `legal_analyzer` with the provided file path.
2. Call `stateful_code_auditor` using the text from the legal analysis as the `brief` and mode="hybrid".
"""
        
        # Add QA session context if active
        if self.qa_repo_url:
            system_message += f"""

IMPORTANT CONTEXT: A QA session is currently active for repository: {self.qa_repo_url}
If the user's query is asking about "the repo", "this repository", "the project", or similar references WITHOUT specifying a URL,
they are referring to the active QA session repository: {self.qa_repo_url}
"""
        
        # Handle both old and new LangChain versions
        if AgentExecutor is not None:
            # LangChain < 1.0
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_message),
                    ("human", "{input}"),
                    ("placeholder", "{agent_scratchpad}"),
                ]
            )
            agent = create_tool_calling_agent(self.llm, self.tools, prompt)
            return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        else:
            # LangChain >= 1.0 uses langgraph's create_react_agent
            # The parameter is 'prompt', not 'state_modifier'
            return create_react_agent(self.llm, self.tools, prompt=system_message)

    def run(self, query: str):
        """Run the agent with a given query."""
        # Store query in session history
        self.session_history.append({'type': 'query', 'content': query})
        
        # Recreate agent executor to update system message with current QA session state
        self.agent_executor = self._create_agent_executor()
        
        # Handle both old and new LangChain versions
        if AgentExecutor is not None:
            # LangChain < 1.0
            response = self.agent_executor.invoke({"input": query})
            result = response["output"]
        else:
            # LangChain >= 1.0 with langgraph
            # create_react_agent returns a graph, invoke it and get the final message
            response = self.agent_executor.invoke({"messages": [("user", query)]})
            # Extract the final AI message from the response
            result = response["messages"][-1].content
        
        # Store result in session history
        self.session_history.append({'type': 'response', 'content': result})
        
        return result
    
    def get_session_history(self) -> list:
        """Get the session history"""
        return self.session_history
    
    def clear_session_history(self):
        """Clear the session history"""
        self.session_history = []
        return "Session history cleared."

def main():
    """Command-line interface for the LangChain-based agent."""
    import argparse
    import json
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Guardian AI (LangChain) - Intelligent Compliance Agent')
    parser.add_argument('query', nargs='?', help='Your query (optional, omit for interactive mode)')
    parser.add_argument('--json', action='store_true', help='Output result as JSON')
    parser.add_argument('--output', '-o', help='Output filename for JSON results (default: detailed_violations_langchain.json)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Start in interactive mode')
    args = parser.parse_args()
    
    print("🤖 Initializing Guardian AI (LangChain version)...")
    agent = LangChainGuardianAgent()
    print("✅ Ready!\n")
    
    # Interactive mode
    if args.interactive or not args.query:
        print("="*70)
        print("INTERACTIVE MODE")
        print("="*70)
        print("\nCommands:")
        print("  exit/quit    - Exit the program")
        print("  help         - Show this help message")
        print("  start_qa <url> - Start a QA session with a repository")
        print("  end_qa       - End the current QA session")
        print("  session      - Show current session info")
        print("  history      - Show session history")
        print("  clear        - Clear session history")
        print("\nType your query or command:\n")
        
        while True:
            try:
                # Show prompt with session info
                if agent.qa_repo_url:
                    prompt = f"📦 [{agent.qa_repo_url.split('/')[-1]}] > "
                else:
                    prompt = "Guardian AI > "
                
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit']:
                    print("\n👋 Goodbye!")
                    agent._cleanup_qa_session()
                    break
                
                elif user_input.lower() == 'help':
                    print("\nCommands:")
                    print("  exit/quit    - Exit the program")
                    print("  help         - Show this help message")
                    print("  start_qa <url> - Start a QA session with a repository")
                    print("  end_qa       - End the current QA session")
                    print("  session      - Show current session info")
                    print("  history      - Show session history")
                    print("  clear        - Clear session history")
                    print()
                    continue
                
                elif user_input.lower().startswith('start_qa '):
                    repo_url = user_input[9:].strip()
                    if repo_url:
                        # Start a QA session
                        result = agent._start_qa_session(repo_url, "Repository indexed and ready for questions.")
                        print(f"\n{result}\n")
                    else:
                        print("\n⚠️  Please provide a repository URL\n")
                    continue
                
                elif user_input.lower() == 'end_qa':
                    result = agent.end_qa_session()
                    print(f"\n{result}\n")
                    continue
                
                elif user_input.lower() == 'session':
                    info = agent.get_session_info()
                    print(f"\n{info}\n")
                    continue
                
                elif user_input.lower() == 'history':
                    history = agent.get_session_history()
                    if history:
                        print("\n" + "="*70)
                        print("SESSION HISTORY")
                        print("="*70)
                        for i, item in enumerate(history, 1):
                            if item['type'] == 'query':
                                print(f"\n[{i}] Query: {item['content']}")
                            else:
                                print(f"    Response: {item['content'][:200]}...")
                        print()
                    else:
                        print("\n📭 No history yet\n")
                    continue
                
                elif user_input.lower() == 'clear':
                    result = agent.clear_session_history()
                    print(f"\n{result}\n")
                    continue
                
                # Regular query
                print()
                result = agent.run(user_input)
                print(f"\n{'='*70}")
                print("ANSWER")
                print(f"{'='*70}\n")
                print(result)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                agent._cleanup_qa_session()
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}\n")
        
        return
    
    # Single query mode
    if args.query:
        result = agent.run(args.query)
        
        # Generate output filename based on repo name and timestamp
        output_filename = args.output  # Use custom filename if provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            repo_name = "guardian_report"  # Default
            
            # Try to extract repo name from the audit results
            global _last_audit_results
            if _last_audit_results and _last_audit_results.get('repo_url'):
                repo_url = _last_audit_results['repo_url']
                import re
                match = re.search(r'github\.com/[\w-]+/([\w.-]+)', repo_url)
                if match:
                    repo_name = match.group(1).replace('.git', '')
            
            output_filename = f"{repo_name}_{timestamp}.json"
        
        # Prepare JSON output
        json_output = {
            'timestamp': datetime.now().isoformat(),
            'query': args.query,
            'violations': _last_audit_results.get('violations', []) if _last_audit_results else [],
            'stats': _last_audit_results.get('stats', {}) if _last_audit_results else {},
            'final_answer': result,
            'metadata': {
                'guardian_version': '1.0-langchain',
                'mode': _last_audit_results.get('mode', 'unknown') if _last_audit_results else 'unknown',
                'repo_url': _last_audit_results.get('repo_url', '') if _last_audit_results else ''
            }
        }
        
        # Save to JSON file
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
            print(result)
        
        # Cleanup QA session if any
        agent._cleanup_qa_session()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
