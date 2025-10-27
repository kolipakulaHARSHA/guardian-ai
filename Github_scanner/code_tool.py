"""
Code Auditor Agent - Person C Implementation
Following PROGRESS.md specifications

This module implements a line-by-line code analysis agent that:
1. Clones GitHub repositories
2. Iterates through all relevant files
3. Splits code into chunks (20-40 lines)
4. Uses LLM to detect violations against a technical brief
5. Returns structured JSON with violations
"""

import os
import json
import tempfile
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path
import git
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class CodeAuditorAgent:
    """
    AI-powered code auditor that scans repositories for compliance violations.
    Implements the exhaustive line-by-line scanning approach from PROGRESS.md.
    """
    
    # File extensions to analyze (from PROGRESS.md)
    RELEVANT_EXTENSIONS = {'.py', '.js', '.java', '.html', '.css', '.jsx', '.tsx', '.ts', '.cpp', '.c', '.h', '.go', '.rb', '.php', '.swift', '.kt'}
    
    # Extensions to ignore
    IGNORE_EXTENSIONS = {'.jpg', '.png', '.gif', '.pdf', '.zip', '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite', '.ico', '.svg', '.woff', '.ttf', '.eot'}
    
    # Directories to skip
    IGNORE_DIRS = {'node_modules', 'venv', 'env', '.git', '__pycache__', 'build', 'dist', '.idea', '.vscode', 'target', 'bin', 'obj'}
    
    def __init__(self, model_name: str = "gemini-2.5-flash", chunk_size: int = 30):
        """
        Initialize the Code Auditor Agent.
        
        Args:
            model_name: Gemini model to use for analysis
            chunk_size: Number of lines per chunk (PROGRESS.md specifies 20-40)
        """
        # Verify API key is set
        if not os.environ.get("GOOGLE_API_KEY"):
            raise ValueError(
                "GOOGLE_API_KEY not found. Please set it as an environment variable."
            )
        
        api_key = os.environ.get("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.1,  # Low temperature for consistent analysis
            convert_system_message_to_human=True,
            google_api_key=api_key
        )
        self.chunk_size = chunk_size
        self.violations = []
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """
        Determine if a file should be analyzed based on extension and path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be analyzed, False otherwise
        """
        # Check if in ignored directory
        parts = file_path.parts
        if any(ignored_dir in parts for ignored_dir in self.IGNORE_DIRS):
            return False
        
        # Check extension
        suffix = file_path.suffix.lower()
        
        # Skip if in ignore list
        if suffix in self.IGNORE_EXTENSIONS:
            return False
        
        # Only analyze if in relevant extensions or if it's a text file without extension
        if suffix in self.RELEVANT_EXTENSIONS:
            return True
        
        # Skip files with unknown extensions
        return False
    
    def _get_language_from_extension(self, extension: str) -> str:
        """Get language identifier for syntax highlighting in prompts."""
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.html': 'html',
            '.css': 'css',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        return lang_map.get(extension, 'text')
    
    def _split_into_chunks(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Split file content into chunks of specified line count.
        
        Args:
            content: File content as string
            file_path: Path to the file (for context)
            
        Returns:
            List of dictionaries containing chunk info
        """
        lines = content.split('\n')
        chunks = []
        
        for i in range(0, len(lines), self.chunk_size):
            chunk_lines = lines[i:i + self.chunk_size]
            chunk_text = '\n'.join(chunk_lines)
            
            chunks.append({
                'content': chunk_text,
                'file_path': file_path,
                'start_line': i + 1,
                'end_line': min(i + self.chunk_size, len(lines)),
                'total_lines': len(lines)
            })
        
        return chunks
    
    def _analyze_chunk(self, chunk: Dict[str, Any], technical_brief: str, language: str) -> List[Dict[str, Any]]:
        """
        Analyze a single code chunk for violations using LLM.
        This implements the core AI logic from PROGRESS.md.
        
        Args:
            chunk: Dictionary with chunk information
            technical_brief: Plain-English compliance rules
            language: Programming language for syntax highlighting
            
        Returns:
            List of violations found in this chunk
        """
        prompt = f"""You are an expert code auditor. Your task is to determine if the following code snippet violates any of the rules in the provided technical brief.

**TECHNICAL BRIEF:**
{technical_brief}

**CODE SNIPPET (File: {chunk['file_path']}, Lines {chunk['start_line']}-{chunk['end_line']}):**
```{language}
{chunk['content']}
```

---
Analyze the code snippet against the brief. If you find one or more violations, respond with a JSON list. Each item in the list should be a dictionary with the keys: "violating_code", "explanation", and "rule_violated". 

If there are no violations in this snippet, respond with an empty list: []

Your response must be ONLY the JSON list, nothing else.
"""
        
        try:
            # Call LLM
            response = self.llm.invoke(prompt)
            response_text = response.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            # Parse JSON
            violations = json.loads(response_text)
            
            # Add file path and line number to each violation
            # Use both old format (for compatibility) and new format (file/line)
            if violations and isinstance(violations, list):
                for violation in violations:
                    violation['file'] = chunk['file_path']
                    violation['line'] = chunk['start_line']
                    # Keep old keys for compatibility
                    violation['file_path'] = chunk['file_path']
                    violation['line_number'] = chunk['start_line']
                
                return violations
            
            return []
        
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse LLM response as JSON for {chunk['file_path']} lines {chunk['start_line']}-{chunk['end_line']}: {e}")
            print(f"Response was: {response_text[:200]}")
            return []
        
        except Exception as e:
            print(f"Error analyzing chunk {chunk['file_path']} lines {chunk['start_line']}-{chunk['end_line']}: {e}")
            return []
    
    def _analyze_file(self, file_path: Path, repo_root: Path, technical_brief: str) -> int:
        """
        Analyze a single file for violations.
        
        Args:
            file_path: Path to the file
            repo_root: Root directory of the repository
            technical_brief: Compliance rules to check against
            
        Returns:
            Number of violations found in this file
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Get relative path for reporting
            relative_path = file_path.relative_to(repo_root)
            
            # Determine language
            language = self._get_language_from_extension(file_path.suffix)
            
            # Split into chunks
            chunks = self._split_into_chunks(content, str(relative_path))
            
            # Analyze each chunk
            violations_found = 0
            for chunk in chunks:
                chunk_violations = self._analyze_chunk(chunk, technical_brief, language)
                if chunk_violations:
                    self.violations.extend(chunk_violations)
                    violations_found += len(chunk_violations)
            
            return violations_found
        
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return 0
    
    def scan_files(self, file_paths: List[str], technical_brief: str, repo_root: Optional[Path] = None) -> Dict[str, Any]:
        """
        Scan a specific list of files for compliance violations.
        
        Args:
            file_paths: List of absolute paths to files to scan.
            technical_brief: Plain-English compliance rules.
            repo_root: The root of the repository for determining relative paths. If None, it's inferred.
            
        Returns:
            Dictionary with scan results.
        """
        if not file_paths:
            return {
                'status': 'success',
                'total_files': 0,
                'analyzed_files': 0,
                'total_violations': 0,
                'violations': []
            }

        # Infer repo_root from the common path of the files if not provided
        if not repo_root:
            common_path = os.path.commonpath(file_paths)
            # Check if common_path is a directory, if not, get its parent
            if os.path.isfile(common_path):
                repo_root = Path(os.path.dirname(common_path))
            else:
                repo_root = Path(common_path)

        self.violations = []
        analyzed_files = 0
        
        print("\nScanning specific files...")
        for file_str_path in file_paths:
            file_path = Path(file_str_path)
            if file_path.is_file() and self._should_analyze_file(file_path):
                analyzed_files += 1
                print(f"Analyzing: {file_path.relative_to(repo_root)}")
                
                violations_in_file = self._analyze_file(
                    file_path, 
                    repo_root, 
                    technical_brief
                )
                
                if violations_in_file > 0:
                    print(f"  ⚠ Found {violations_in_file} violation(s)")

        result = {
            'status': 'success',
            'total_files': len(file_paths),
            'analyzed_files': analyzed_files,
            'total_violations': len(self.violations),
            'violations': self.violations
        }
        
        print(f"\n✓ Scan complete:")
        print(f"  - Analyzed files: {analyzed_files}")
        print(f"  - Violations found: {len(self.violations)}")
        
        return result

    def scan_repository(self, repo_url: str, technical_brief: str) -> Dict[str, Any]:
        """
        Scan a GitHub repository for compliance violations.
        Implements the main workflow from PROGRESS.md.
        
        Args:
            repo_url: URL of the GitHub repository
            technical_brief: Plain-English compliance rules
            
        Returns:
            Dictionary with scan results
        """
        temp_dir = None
        
        try:
            # Step 1: Create temporary directory and clone repository
            temp_dir = tempfile.mkdtemp(prefix='guardian_audit_')
            print(f"Cloning repository to {temp_dir}...")
            
            repo = git.Repo.clone_from(repo_url, temp_dir)
            print(f"✓ Repository cloned successfully")
            
            # Reset violations list
            self.violations = []
            
            # Step 2: Iterate through all files
            repo_path = Path(temp_dir)
            all_files = [str(p) for p in repo_path.rglob('*') if p.is_file()]
            
            # Use the new scan_files method
            return self.scan_files(all_files, technical_brief, repo_root=repo_path)
            
        except Exception as e:
            return {
                'status': 'error',
                'repository': repo_url,
                'error': str(e),
                'violations': []
            }
        
        finally:
            # Step 3: Cleanup (ALWAYS runs, even on error)
            if temp_dir and os.path.exists(temp_dir):
                print(f"\nCleaning up temporary directory...")
                try:
                    shutil.rmtree(temp_dir, onerror=self._handle_remove_readonly)
                    print("✓ Cleanup complete")
                except Exception as e:
                    print(f"Warning: Cleanup failed: {e}")
    
    @staticmethod
    def _handle_remove_readonly(func, path, exc):
        """Handle removal of read-only files on Windows."""
        import stat
        os.chmod(path, stat.S_IWRITE)
        func(path)


# Contract-compliant function (as specified in PROGRESS.md)
def code_auditor_agent(repo_url: str, technical_brief: str) -> str:
    """
    Scans a public GitHub repository using an AI agent to find violations.
    
    This is the main contract function as specified in PROGRESS.md.
    
    Args:
        repo_url: GitHub repository URL to scan
        technical_brief: Plain-English technical brief describing compliance rules
    
    Returns:
        JSON string containing list of violations
    """
    auditor = CodeAuditorAgent()
    result = auditor.scan_repository(repo_url, technical_brief)
    
    # Return just the violations as JSON (as specified in contract)
    return json.dumps(result['violations'], indent=2)


class ComplianceChecker:
    """
    RAG-based compliance checker for repositories.
    Uses semantic search and LLM to check compliance against guidelines.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-pro-preview-03-25"):
        """
        Initialize the Compliance Checker.
        
        Args:
            model_name: Gemini model to use
        """
        if not os.environ.get("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found. Please set it as an environment variable.")
        
        api_key = os.environ.get("GOOGLE_API_KEY")
        
        # Initialize embeddings and LLM
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.3,
            google_api_key=api_key
        )
        
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        self.documents = []
        self.repo_path = None
        self.temp_dir = None

    def _clone_and_index(self, repo_url: str, prioritized_extensions: List[str] = None) -> Dict[str, Any]:
        """Clones and indexes a repository. This is called once per session."""
        if self.repo_path:
            return {'status': 'success', 'message': 'Repository already indexed.'}

        try:
            self.temp_dir = tempfile.mkdtemp(prefix='guardian_compliance_')
            print(f"Cloning repository to {self.temp_dir}...")
            git.Repo.clone_from(repo_url, self.temp_dir)
            print(f"✓ Repository cloned successfully\n")
            self.repo_path = Path(self.temp_dir)
            
            index_result = self.index_repository(self.repo_path, prioritized_extensions)
            
            if index_result['status'] != 'success':
                return {
                    'status': 'error',
                    'error': f"Indexing failed: {index_result.get('message', 'Unknown error')}"
                }
            
            print(f"✓ Indexed {index_result['documents_count']} documents "
                  f"({index_result['chunks_count']} chunks)\n")
            return {'status': 'success'}

        except Exception as e:
            self.cleanup() # Clean up on failure
            return {'status': 'error', 'error': str(e)}

    def cleanup(self):
        """Cleans up the temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            print(f"\nCleaning up temporary directory...")
            try:
                shutil.rmtree(self.temp_dir, onerror=self._handle_remove_readonly)
                print("✓ Cleanup complete")
            except Exception as e:
                print(f"Warning: Cleanup failed: {e}")
        self.repo_path = None
        self.temp_dir = None
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        self.documents = []
    
    def index_repository(self, repo_path: Path, prioritized_extensions: List[str] = None) -> Dict[str, Any]:
        """
        Index repository files for semantic search.
        
        Args:
            repo_path: Path to cloned repository
            prioritized_extensions: List of file extensions to boost during retrieval.
            
        Returns:
            Indexing statistics
        """
        # File extensions to index
        default_extensions = [
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.java', '.cpp', '.c', '.h', '.cs',
            '.md', '.txt', '.rst',
            '.json', '.yaml', '.yml', '.toml', '.html', '.css'
        ]
        
        extensions_to_index = set(default_extensions)
        if prioritized_extensions:
            extensions_to_index.update(prioritized_extensions)

        print("Loading documents from repository...")
        self.documents = []
        
        # Load all relevant files
        for ext in extensions_to_index:
            for file_path in repo_path.rglob(f'*{ext}'):
                if self._should_index_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Add a boost for prioritized file types
                        metadata = {
                            'source': str(file_path.relative_to(repo_path)),
                            'file_name': file_path.name,
                            'extension': file_path.suffix
                        }
                        if prioritized_extensions and file_path.suffix in prioritized_extensions:
                            metadata['priority_boost'] = "high"

                        doc = Document(
                            page_content=content,
                            metadata=metadata
                        )
                        self.documents.append(doc)
                    except Exception as e:
                        print(f"Warning: Could not read {file_path}: {e}")
        
        if not self.documents:
            return {
                'status': 'warning',
                'message': 'No documents found to index',
                'documents_count': 0,
                'chunks_count': 0
            }
        
        print(f"Loaded {len(self.documents)} documents")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        print("Splitting documents into chunks...")
        splits = text_splitter.split_documents(self.documents)
        print(f"Created {len(splits)} chunks")
        
        # Create vector store
        print("Creating vector store (this may take a moment)...")
        self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        
        # Create retriever with priority boosting if applicable
        search_kwargs = {"k": 5}
        if prioritized_extensions:
            # FAISS doesn't directly support metadata boosting in the same way as some other vector stores.
            # A common workaround is to retrieve more results and then re-rank them in memory.
            search_kwargs["k"] = 10 # Retrieve more to allow for re-ranking
            
        self.retriever = self.vectorstore.as_retriever(search_kwargs=search_kwargs)
        
        # Create QA chain
        template = """Answer the question based only on the following context. Prioritize context from files with 'priority_boost: high' if available.

{context}

Question: {question}

Provide a detailed answer with specific examples from the code."""

        prompt = ChatPromptTemplate.from_template(template)
        
        self.qa_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return {
            'status': 'success',
            'documents_count': len(self.documents),
            'chunks_count': len(splits)
        }
    
    def _should_index_file(self, file_path: Path) -> bool:
        """Check if file should be indexed."""
        ignore_dirs = {'node_modules', 'venv', 'env', '.git', '__pycache__', 
                      'build', 'dist', '.idea', '.vscode', 'target'}
        
        parts = file_path.parts
        if any(ignored_dir in parts for ignored_dir in ignore_dirs):
            return False
        
        return True
    
    def check_patterns(self, patterns: List[str]) -> Dict[str, Any]:
        """
        Checks a list of patterns against the already-indexed repository.
        """
        if not self.repo_path or not self.qa_chain:
            return {
                'status': 'error',
                'error': 'Repository not indexed. Call _clone_and_index first.',
                'compliance_checks': []
            }

        compliance_results = []
        print("Running compliance checks on indexed repo...")
        for i, pattern in enumerate(patterns, 1):
            print(f"  [{i}/{len(patterns)}] Checking: {pattern[:60]}...")
            
            try:
                docs = self.retriever.invoke(pattern)
                answer = self.qa_chain.invoke(pattern)
                
                evidence_details = []
                for doc in docs[:3]:
                    source_file = doc.metadata.get('source', 'unknown')
                    content = doc.page_content.strip()
                    code_snippet = content[:150] + "..." if len(content) > 150 else content
                    line_number = self._estimate_line_number(self.repo_path, source_file, content)
                    
                    evidence_details.append({
                        'file': source_file,
                        'line': line_number,
                        'code_snippet': code_snippet
                    })
                
                compliance_results.append({
                    'guideline': pattern, # The "guideline" is the pattern
                    'assessment': answer,
                    'evidence_sources': [doc.metadata.get('source', 'unknown') for doc in docs[:3]],
                    'evidence_details': evidence_details
                })
            except Exception as e:
                compliance_results.append({
                    'guideline': pattern,
                    'assessment': f'Error checking compliance: {str(e)}',
                    'evidence_sources': [],
                    'evidence_details': []
                })
        
        return {
            'status': 'success',
            'compliance_checks': compliance_results,
            'total_guidelines_checked': len(patterns)
        }

    def check_compliance(
        self,
        repo_url: str,
        guidelines: List[str]
    ) -> Dict[str, Any]:
        """
        Check repository compliance against guidelines.
        
        Args:
            repo_url: GitHub repository URL
            guidelines: List of compliance guidelines to check
            
        Returns:
            Compliance check results
        """
        temp_dir = None
        
        try:
            # This method now uses the single-clone-and-index pattern
            clone_result = self._clone_and_index(repo_url)
            if clone_result['status'] == 'error':
                return clone_result

            # Check each guideline using the indexed repo
            return self.check_patterns(guidelines)
        
        except Exception as e:
            return {
                'status': 'error',
                'repository': repo_url,
                'error': str(e),
                'compliance_checks': []
            }
        
        finally:
            # Cleanup is now handled by the caller of the class instance
            pass
    
    @staticmethod
    def _handle_remove_readonly(func, path, exc):
        """Handle removal of read-only files on Windows."""
        import stat
        os.chmod(path, stat.S_IWRITE)
        func(path)
    
    def _estimate_line_number(self, repo_path: Path, source_file: str, chunk_content: str) -> int:
        """
        Estimate the line number where a chunk appears in the original file.
        
        Args:
            repo_path: Path to the repository
            source_file: Relative path to the source file
            chunk_content: The content chunk to find
            
        Returns:
            Estimated line number (1-based)
        """
        try:
            file_path = repo_path / source_file
            if not file_path.exists():
                return 1
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_lines = f.readlines()
            
            # Get first non-empty line from chunk to search for
            chunk_lines = chunk_content.split('\n')
            search_line = None
            for line in chunk_lines:
                stripped = line.strip()
                if stripped and len(stripped) > 10:  # Must be meaningful
                    search_line = stripped
                    break
            
            if not search_line:
                return 1
            
            # Search for this line in the file
            for i, file_line in enumerate(file_lines, 1):
                if search_line in file_line.strip():
                    return i
            
            # If not found, return 1
            return 1
            
        except Exception as e:
            # If anything goes wrong, default to line 1
            return 1


# Independent execution - Run audit directly without other files
if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path
    
    # Try to load .env file if it exists
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    # Check for API key
    if not os.environ.get('GOOGLE_API_KEY'):
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Gemini API key before running.")
        print("\nOptions:")
        print("1. Set in PowerShell: $env:GOOGLE_API_KEY='your-key-here'")
        print("2. Create .env file with: GOOGLE_API_KEY=your-key-here")
        exit(1)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Guardian AI - Independent Code Analysis & Compliance Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  audit       Line-by-line code auditing (exhaustive scanning)
  compliance  RAG-based compliance checking

Examples:
  # AUDIT MODE - Find specific violations
  python code_tool.py audit https://github.com/user/repo
  python code_tool.py audit https://github.com/user/repo --brief "All functions need docstrings"
  python code_tool.py audit https://github.com/user/repo --brief-file rules.txt --output report.json

  # COMPLIANCE MODE - Check against guidelines
  python code_tool.py compliance https://github.com/user/repo
  python code_tool.py compliance https://github.com/user/repo --guideline "Must have LICENSE file"
  python code_tool.py compliance https://github.com/user/repo --guidelines-file guidelines.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # AUDIT mode parser
    audit_parser = subparsers.add_parser('audit', help='Line-by-line code audit')
    audit_parser.add_argument(
        'repo_url',
        nargs='?',
        help='GitHub repository URL to audit'
    )
    audit_parser.add_argument(
        '--brief', '-b',
        action='append',
        help='Technical brief rule (can be specified multiple times)'
    )
    audit_parser.add_argument(
        '--brief-file',
        help='File containing technical brief (one rule per line)'
    )
    audit_parser.add_argument(
        '--model',
        default='gemini-2.5-flash',
        help='Gemini model to use (default: gemini-2.5-flash)'
    )
    audit_parser.add_argument(
        '--chunk-size',
        type=int,
        default=30,
        help='Number of lines per chunk (default: 30, range: 20-40)'
    )
    audit_parser.add_argument(
        '--max-display',
        type=int,
        default=10,
        help='Maximum violations to display (default: 10)'
    )
    audit_parser.add_argument(
        '--output', '-o',
        help='Output JSON file path'
    )
    audit_parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed statistics'
    )
    
    # COMPLIANCE mode parser
    compliance_parser = subparsers.add_parser('compliance', help='RAG-based compliance checking')
    compliance_parser.add_argument(
        'repo_url',
        nargs='?',
        help='GitHub repository URL to check'
    )
    compliance_parser.add_argument(
        '--guideline', '-g',
        action='append',
        help='Compliance guideline (can be specified multiple times)'
    )
    compliance_parser.add_argument(
        '--guidelines-file',
        help='File containing guidelines (one per line)'
    )
    compliance_parser.add_argument(
        '--model',
        default='gemini-2.5-pro-preview-03-25',
        help='Gemini model to use (default: gemini-2.5-pro-preview-03-25)'
    )
    compliance_parser.add_argument(
        '--max-display',
        type=int,
        default=5,
        help='Maximum compliance checks to display (default: 5)'
    )
    compliance_parser.add_argument(
        '--output', '-o',
        help='Output JSON file path'
    )
    
    args = parser.parse_args()
    
    # If no mode specified, show help
    if not args.mode:
        parser.print_help()
        print("\n" + "="*70)
        print("Please specify a mode: 'audit' or 'compliance'")
        print("="*70)
        sys.exit(1)
    
    # Handle AUDIT mode
    if args.mode == 'audit':
        # If no repo URL provided, use example
        if not args.repo_url:
            print("No repository URL provided. Using example repository...\n")
            repo_url = "https://github.com/kolipakulaHARSHA/FINANCE_MANAGEMENT_APP"
        else:
            repo_url = args.repo_url
        
        # Build technical brief
        if args.brief_file:
            try:
                with open(args.brief_file, 'r') as f:
                    technical_brief = f.read()
            except FileNotFoundError:
                print(f"Error: Brief file not found: {args.brief_file}")
                sys.exit(1)
        elif args.brief:
            technical_brief = '\n'.join(args.brief)
        else:
            # Default technical brief
            technical_brief = """
        Code Quality Requirements:
        1. All image elements must have valid alt attributes
        2. User data must be encrypted during transmission
        3. Password fields must implement minimum strength requirements
        4. CSRF tokens must be present in all forms
        5. API endpoints must implement rate limiting
        """
        
        # Display header
        print("="*70)
        print("CODE AUDITOR AGENT - Line-by-Line Analysis")
        print("="*70)
        print(f"\nRepository: {repo_url}")
        print(f"Model: {args.model}")
        print(f"Chunk Size: {args.chunk_size} lines")
        print(f"\nTechnical Brief:")
        print(technical_brief)
        print("\n" + "="*70)
        
        # Run the audit
        if args.detailed:
            # Use class for detailed stats
            auditor = CodeAuditorAgent(
                model_name=args.model,
                chunk_size=args.chunk_size
            )
            result = auditor.scan_repository(repo_url, technical_brief)
            violations = result['violations']
            
            # Display detailed stats
            print(f"\n\n=== AUDIT RESULTS ===")
            print(f"Total files scanned: {result['total_files']}")
            print(f"Files analyzed: {result['analyzed_files']}")
            print(f"Violations found: {result['total_violations']}")
            print("="*70)
        else:
            # Use contract function
            result_json = code_auditor_agent(repo_url, technical_brief)
            violations = json.loads(result_json)
            
            print(f"\n\n=== AUDIT RESULTS ===")
            print(f"Violations found: {len(violations)}")
            print("="*70)
        
        # Display violations
        if violations:
            print(f"\nViolations Found:")
            display_count = min(len(violations), args.max_display)
            
            # Print as formatted list
            violations_display = []
            for violation in violations[:display_count]:
                violations_display.append({
                    "file": violation.get('file', violation.get('file_path', 'N/A')),
                    "line": violation.get('line', violation.get('line_number', 'N/A')),
                    "violating_code": violation.get('violating_code', 'N/A'),
                    "explanation": violation.get('explanation', 'N/A'),
                    "rule_violated": violation.get('rule_violated', 'N/A')
                })
            
            print(json.dumps(violations_display, indent=2))
            
            if len(violations) > args.max_display:
                print(f"\n... and {len(violations) - args.max_display} more violations")
                print(f"    (use --max-display {len(violations)} to see all)")
        else:
            print("\nViolations Found: []")
            print("\n✓ No violations found!")
        
        # Save to file if requested
        if args.output:
            # Format violations in the new structure
            formatted_violations = []
            for violation in violations:
                formatted_violations.append({
                    "file": violation.get('file', violation.get('file_path', 'N/A')),
                    "line": violation.get('line', violation.get('line_number', 'N/A')),
                    "violating_code": violation.get('violating_code', 'N/A'),
                    "explanation": violation.get('explanation', 'N/A'),
                    "rule_violated": violation.get('rule_violated', 'N/A')
                })
            
            output_data = {
                'repository': repo_url,
                'technical_brief': technical_brief,
                'model': args.model,
                'chunk_size': args.chunk_size,
                'violations': formatted_violations,
                'total_violations': len(violations)
            }
            
            if args.detailed and 'result' in locals():
                output_data['stats'] = {
                    'total_files': result['total_files'],
                    'analyzed_files': result['analyzed_files']
                }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"\n✓ Results saved to: {args.output}")
    
    # Handle COMPLIANCE mode
    elif args.mode == 'compliance':
        # If no repo URL provided, use example
        if not args.repo_url:
            print("No repository URL provided. Using example repository...\n")
            repo_url = "https://github.com/kolipakulaHARSHA/FINANCE_MANAGEMENT_APP"
        else:
            repo_url = args.repo_url
        
        # Build guidelines list
        if args.guidelines_file:
            try:
                with open(args.guidelines_file, 'r') as f:
                    guidelines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except FileNotFoundError:
                print(f"Error: Guidelines file not found: {args.guidelines_file}")
                sys.exit(1)
        elif args.guideline:
            guidelines = args.guideline
        else:
            # Default compliance guidelines
            guidelines = [
                "The project must have a LICENSE file",
                "The project must have a README with installation instructions",
                "The project must have proper documentation",
                "The code should follow security best practices",
                "The project should have a clear contribution guide"
            ]
        
        # Display header
        print("="*70)
        print("COMPLIANCE CHECKER - RAG-Based Analysis")
        print("="*70)
        print(f"\nRepository: {repo_url}")
        print(f"Model: {args.model}")
        print(f"\nGuidelines to check ({len(guidelines)}):")
        for i, g in enumerate(guidelines, 1):
            print(f"  {i}. {g}")
        print("\n" + "="*70)
        
        # Run compliance check
        checker = ComplianceChecker(model_name=args.model)
        result = checker.check_compliance(repo_url, guidelines)
        
        if result['status'] == 'error':
            print(f"\n✗ Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        
        # Display results
        print(f"\n\n=== COMPLIANCE RESULTS ===")
        print(f"Guidelines checked: {result['total_guidelines_checked']}")
        print("="*70)
        
        compliance_checks = result['compliance_checks']
        
        # Convert compliance checks to violation format
        violations = []
        for check in compliance_checks:
            # Determine if this is a violation (non-compliance)
            assessment_lower = check['assessment'].lower()
            is_violation = any(keyword in assessment_lower for keyword in [
                'no', 'not', 'does not', 'missing', 'absent', 'lacking', 
                'cannot find', 'no information', 'no evidence', 'not found'
            ])
            
            if is_violation:
                # Use evidence details if available (includes line numbers and code)
                evidence_details = check.get('evidence_details', [])
                
                if evidence_details:
                    # Use the first evidence detail (most relevant)
                    first_evidence = evidence_details[0]
                    file_name = first_evidence.get('file', 'Repository-wide')
                    line_number = first_evidence.get('line', 1)
                    code_snippet = first_evidence.get('code_snippet', 'N/A - Compliance issue')
                else:
                    # Fallback to old method
                    file_name = check['evidence_sources'][0] if check['evidence_sources'] else 'Repository-wide'
                    line_number = 1
                    code_snippet = 'N/A - Compliance issue'
                
                violations.append({
                    "file": file_name,
                    "line": line_number,
                    "violating_code": code_snippet,
                    "explanation": check['assessment'],
                    "rule_violated": check['guideline']
                })
        
        # Display violations
        if violations:
            print(f"\nViolations Found:")
            display_count = min(len(violations), args.max_display)
            print(json.dumps(violations[:display_count], indent=2))
            
            if len(violations) > args.max_display:
                print(f"\n... and {len(violations) - args.max_display} more violations")
                print(f"    (use --max-display {len(violations)} to see all)")
        else:
            print("\nViolations Found: []")
            print("\n✓ All compliance checks passed!")
        
        # Save to file if requested
        if args.output:
            output_data = {
                'repository': repo_url,
                'guidelines': guidelines,
                'model': args.model,
                'violations': violations,  # Use new violation format
                'total_violations': len(violations),
                'total_guidelines_checked': result['total_guidelines_checked'],
                # Keep raw compliance checks for reference
                'compliance_checks': compliance_checks
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"\n✓ Results saved to: {args.output}")
    
    print("\n" + "="*70)
    print(f"{args.mode.upper()} complete!")
    print("="*70)
