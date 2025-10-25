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
from langchain_google_genai import ChatGoogleGenerativeAI


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
            if violations and isinstance(violations, list):
                for violation in violations:
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
            total_files = 0
            analyzed_files = 0
            
            print("\nScanning files...")
            for file_path in repo_path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    
                    if self._should_analyze_file(file_path):
                        analyzed_files += 1
                        print(f"Analyzing: {file_path.relative_to(repo_path)}")
                        
                        violations_in_file = self._analyze_file(
                            file_path, 
                            repo_path, 
                            technical_brief
                        )
                        
                        if violations_in_file > 0:
                            print(f"  ⚠ Found {violations_in_file} violation(s)")
            
            # Compile results
            result = {
                'status': 'success',
                'repository': repo_url,
                'total_files': total_files,
                'analyzed_files': analyzed_files,
                'total_violations': len(self.violations),
                'violations': self.violations
            }
            
            print(f"\n✓ Scan complete:")
            print(f"  - Total files: {total_files}")
            print(f"  - Analyzed files: {analyzed_files}")
            print(f"  - Violations found: {len(self.violations)}")
            
            return result
        
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


# Testing function
if __name__ == "__main__":
    import os
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
    
    # Example usage
    print("="*70)
    print("CODE AUDITOR AGENT - Person C Implementation")
    print("="*70)
    
    # Test with a small repository
    repo_url = "https://github.com/pallets/click"
    
    technical_brief = """
    Code Quality Requirements:
    1. All functions must have docstrings explaining their purpose
    2. No print statements should be used in production code (use logging instead)
    3. Functions should not exceed 50 lines of code
    4. All public functions must have type hints
    """
    
    print(f"\nRepository: {repo_url}")
    print(f"\nTechnical Brief:")
    print(technical_brief)
    print("\n" + "="*70)
    
    # Run the audit
    result_json = code_auditor_agent(repo_url, technical_brief)
    
    # Display results
    violations = json.loads(result_json)
    print(f"\n\nRESULTS: Found {len(violations)} violations")
    print("="*70)
    
    if violations:
        for i, violation in enumerate(violations[:5], 1):  # Show first 5
            print(f"\nViolation {i}:")
            print(f"  File: {violation.get('file_path', 'N/A')}")
            print(f"  Line: {violation.get('line_number', 'N/A')}")
            print(f"  Rule: {violation.get('rule_violated', 'N/A')}")
            print(f"  Explanation: {violation.get('explanation', 'N/A')}")
            print(f"  Code: {violation.get('violating_code', 'N/A')[:100]}...")
        
        if len(violations) > 5:
            print(f"\n... and {len(violations) - 5} more violations")
    else:
        print("\n✓ No violations found!")
