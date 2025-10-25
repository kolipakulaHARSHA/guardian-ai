"""
GitHub Repository Scanner Tool for Guardian AI
This tool clones GitHub repositories and provides question-answering capabilities
using agentic AI for compliance checking.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
import json


class GitHubRepoTool:
    """
    A tool to clone GitHub repositories and analyze their contents
    for compliance checking and question answering.
    """
    
    def __init__(self, base_clone_dir: str = "./cloned_repos"):
        """
        Initialize the GitHub Repository Tool.
        
        Args:
            base_clone_dir: Directory where repositories will be cloned
        """
        self.base_clone_dir = Path(base_clone_dir)
        self.base_clone_dir.mkdir(parents=True, exist_ok=True)
        self.current_repo_path: Optional[Path] = None
        self.repo_metadata: Dict[str, Any] = {}
    
    def clone_repository(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """
        Clone a GitHub repository to local storage.
        
        Args:
            repo_url: GitHub repository URL (https or git format)
            branch: Branch to clone (default: main)
            
        Returns:
            Dictionary containing clone status and repository path
        """
        try:
            # Extract repo name from URL
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            repo_path = self.base_clone_dir / repo_name
            
            # Remove existing clone if it exists
            if repo_path.exists():
                print(f"Removing existing clone at {repo_path}")
                # Handle Windows file permission issues
                def handle_remove_readonly(func, path, exc):
                    import stat
                    if not os.access(path, os.W_OK):
                        os.chmod(path, stat.S_IWUSR)
                        func(path)
                    else:
                        raise
                shutil.rmtree(repo_path, onerror=handle_remove_readonly)
            
            # Clone the repository
            print(f"Cloning {repo_url}...")
            result = subprocess.run(
                ['git', 'clone', '--branch', branch, '--depth', '1', repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.current_repo_path = repo_path
            self.repo_metadata = {
                'repo_url': repo_url,
                'repo_name': repo_name,
                'branch': branch,
                'local_path': str(repo_path),
                'status': 'success'
            }
            
            print(f"Successfully cloned repository to {repo_path}")
            return self.repo_metadata
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to clone repository: {e.stderr}"
            print(error_msg)
            return {
                'status': 'error',
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return {
                'status': 'error',
                'error': error_msg
            }
    
    def get_repository_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get the directory structure of the cloned repository.
        
        Args:
            max_depth: Maximum depth to traverse
            
        Returns:
            Dictionary containing the repository structure
        """
        if not self.current_repo_path or not self.current_repo_path.exists():
            return {'error': 'No repository cloned'}
        
        def build_tree(path: Path, current_depth: int = 0) -> Dict:
            if current_depth >= max_depth:
                return {}
            
            tree = {}
            try:
                for item in sorted(path.iterdir()):
                    # Skip .git directory
                    if item.name == '.git':
                        continue
                    
                    if item.is_file():
                        tree[item.name] = {
                            'type': 'file',
                            'size': item.stat().st_size
                        }
                    elif item.is_dir():
                        tree[item.name] = {
                            'type': 'directory',
                            'children': build_tree(item, current_depth + 1)
                        }
            except PermissionError:
                pass
            
            return tree
        
        structure = {
            'repo_name': self.repo_metadata.get('repo_name', 'unknown'),
            'structure': build_tree(self.current_repo_path)
        }
        
        return structure
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a specific file from the cloned repository.
        
        Args:
            file_path: Relative path to the file within the repository
            
        Returns:
            Dictionary containing file content and metadata
        """
        if not self.current_repo_path or not self.current_repo_path.exists():
            return {'error': 'No repository cloned'}
        
        full_path = self.current_repo_path / file_path
        
        if not full_path.exists():
            return {'error': f'File not found: {file_path}'}
        
        if not full_path.is_file():
            return {'error': f'Path is not a file: {file_path}'}
        
        try:
            # Try to read as text
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'file_path': file_path,
                'content': content,
                'size': full_path.stat().st_size,
                'type': 'text'
            }
        except UnicodeDecodeError:
            # Binary file
            return {
                'file_path': file_path,
                'content': '[Binary file - cannot display]',
                'size': full_path.stat().st_size,
                'type': 'binary'
            }
        except Exception as e:
            return {'error': f'Error reading file: {str(e)}'}
    
    def search_files(self, pattern: str, file_extensions: Optional[List[str]] = None) -> List[str]:
        """
        Search for files matching a pattern in the repository.
        
        Args:
            pattern: Search pattern (glob format)
            file_extensions: Optional list of file extensions to filter (e.g., ['.py', '.js'])
            
        Returns:
            List of matching file paths (relative to repo root)
        """
        if not self.current_repo_path or not self.current_repo_path.exists():
            return []
        
        matches = []
        
        for file_path in self.current_repo_path.rglob(pattern):
            if file_path.is_file() and '.git' not in file_path.parts:
                if file_extensions is None or file_path.suffix in file_extensions:
                    relative_path = file_path.relative_to(self.current_repo_path)
                    matches.append(str(relative_path))
        
        return matches
    
    def get_file_list(self, extensions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get a list of all files in the repository.
        
        Args:
            extensions: Optional list of file extensions to filter
            
        Returns:
            List of file information dictionaries
        """
        if not self.current_repo_path or not self.current_repo_path.exists():
            return []
        
        files = []
        
        for file_path in self.current_repo_path.rglob('*'):
            if file_path.is_file() and '.git' not in file_path.parts:
                if extensions is None or file_path.suffix in extensions:
                    relative_path = file_path.relative_to(self.current_repo_path)
                    files.append({
                        'path': str(relative_path),
                        'name': file_path.name,
                        'extension': file_path.suffix,
                        'size': file_path.stat().st_size
                    })
        
        return files
    
    def get_repository_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the repository including key files and statistics.
        
        Returns:
            Dictionary containing repository summary
        """
        if not self.current_repo_path or not self.current_repo_path.exists():
            return {'error': 'No repository cloned'}
        
        # Common important files
        important_files = [
            'README.md', 'README.rst', 'README.txt',
            'LICENSE', 'LICENSE.md', 'LICENSE.txt',
            'package.json', 'requirements.txt', 'setup.py', 'pyproject.toml',
            'Dockerfile', 'docker-compose.yml',
            '.gitignore', '.env.example'
        ]
        
        found_files = {}
        for file_name in important_files:
            file_path = self.current_repo_path / file_name
            if file_path.exists():
                found_files[file_name] = str(file_path.relative_to(self.current_repo_path))
        
        # Get file statistics by extension
        file_stats = {}
        total_files = 0
        total_size = 0
        
        for file_path in self.current_repo_path.rglob('*'):
            if file_path.is_file() and '.git' not in file_path.parts:
                ext = file_path.suffix or 'no_extension'
                if ext not in file_stats:
                    file_stats[ext] = {'count': 0, 'total_size': 0}
                
                file_stats[ext]['count'] += 1
                file_stats[ext]['total_size'] += file_path.stat().st_size
                total_files += 1
                total_size += file_path.stat().st_size
        
        return {
            'repo_metadata': self.repo_metadata,
            'important_files': found_files,
            'file_statistics': file_stats,
            'total_files': total_files,
            'total_size': total_size
        }
    
    def cleanup(self):
        """Remove the cloned repository from local storage."""
        if self.current_repo_path and self.current_repo_path.exists():
            # Handle Windows file permission issues with git files
            def handle_remove_readonly(func, path, exc):
                """Error handler for Windows readonly files."""
                import stat
                if not os.access(path, os.W_OK):
                    os.chmod(path, stat.S_IWUSR)
                    func(path)
                else:
                    raise
            
            shutil.rmtree(self.current_repo_path, onerror=handle_remove_readonly)
            print(f"Cleaned up repository at {self.current_repo_path}")
            self.current_repo_path = None
            self.repo_metadata = {}


# Example usage
if __name__ == "__main__":
    # Initialize the tool
    tool = GitHubRepoTool()
    
    # Clone a repository
    result = tool.clone_repository("https://github.com/langchain-ai/langchain")
    print("Clone result:", json.dumps(result, indent=2))
    
    # Get repository structure
    structure = tool.get_repository_structure(max_depth=2)
    print("\nRepository structure:", json.dumps(structure, indent=2)[:500], "...")
    
    # Get repository summary
    summary = tool.get_repository_summary()
    print("\nRepository summary:", json.dumps(summary, indent=2))
    
    # Search for Python files
    python_files = tool.search_files("*.py")
    print(f"\nFound {len(python_files)} Python files")
    
    # Clean up
    # tool.cleanup()
