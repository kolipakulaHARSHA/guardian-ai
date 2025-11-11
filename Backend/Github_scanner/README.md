# Guardian AI - GitHub Repository Scanner

A powerful tool for scanning GitHub repositories and checking compliance using Agentic AI. This tool can clone repositories, analyze their structure, and answer questions about the codebase using advanced language models.

## Features

- 🔍 **Repository Scanning**: Clone and analyze GitHub repositories
- 🤖 **AI-Powered Q&A**: Ask questions about repository contents using LangChain
- ✅ **Compliance Checking**: Verify if repositories follow specific guidelines
- 📊 **Repository Insights**: Get automated insights about project structure and content
- 🚀 **Easy CLI Interface**: Simple command-line interface for all operations

## Installation

1. **Navigate to the Github_scanner directory:**
   ```powershell
   cd Github_scanner
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Set up Google Gemini API key:**
   Create a `.env` file or set environment variable:
   ```powershell
   $env:GOOGLE_API_KEY = "your-google-api-key-here"
   ```
   
   Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Prerequisites

- Python 3.8+
- Git installed and available in PATH
- Google Gemini API key (for AI features) - Free tier available!

## Usage

### 1. Basic Repository Scanning

Scan a repository to get structure and statistics:

```powershell
python cli.py scan https://github.com/langchain-ai/langchain
```

Save results to a file:
```powershell
python cli.py scan https://github.com/langchain-ai/langchain -o summary.json
```

### 2. Ask Questions About a Repository

Interactive question mode:
```powershell
python cli.py ask https://github.com/microsoft/vscode --interactive
```

Ask a specific question:
```powershell
python cli.py ask https://github.com/microsoft/vscode -q "What is the main architecture of this project?"
```

Index only specific file types:
```powershell
python cli.py ask https://github.com/facebook/react --extensions ".js,.jsx,.md" -q "How does the rendering system work?"
```

### 3. Compliance Checking

Check against default compliance guidelines:
```powershell
python cli.py compliance https://github.com/user/repo
```

Use custom guidelines from a file:
```powershell
python cli.py compliance https://github.com/user/repo --guidelines-file my_guidelines.txt
```

Provide guidelines directly:
```powershell
python cli.py compliance https://github.com/user/repo -g "Must have tests" "Must have CI/CD"
```

## Python API Usage

### Basic Repository Operations

```python
from github_repo_tool import GitHubRepoTool

# Initialize tool
tool = GitHubRepoTool()

# Clone repository
result = tool.clone_repository("https://github.com/langchain-ai/langchain")
print(f"Cloned to: {result['local_path']}")

# Get repository structure
structure = tool.get_repository_structure(max_depth=2)

# Get summary
summary = tool.get_repository_summary()

# Search for files
python_files = tool.search_files("*.py")

# Read a specific file
content = tool.read_file("README.md")

# Cleanup
tool.cleanup()
```

### AI-Powered Question Answering

```python
from repo_qa_agent import RepoQAAgent

# Initialize agent
agent = RepoQAAgent(model_name="gpt-4")

# Clone and index repository
agent.clone_and_index_repository(
    "https://github.com/langchain-ai/langchain",
    file_extensions=['.py', '.md']
)

# Ask questions
answer = agent.ask_question("What are the main components of this project?")
print(answer['answer'])

# Check compliance
guidelines = [
    "The project must have a LICENSE file",
    "The project must have comprehensive documentation"
]
compliance = agent.check_compliance(guidelines)

# Get automated insights
insights = agent.get_repository_insights()

# Cleanup
agent.cleanup()
```

## Advanced Features

### Custom File Extensions

Index specific file types for faster processing:

```python
agent.clone_and_index_repository(
    repo_url,
    file_extensions=['.py', '.js', '.md', '.json']
)
```

### Compliance Guidelines File Format

Create a text file with one guideline per line:

```text
The project must have a LICENSE file
The project must include security documentation
All dependencies must be pinned to specific versions
The project must have automated tests
Code must follow security best practices
```

### Using Different LLM Models

```python
# Use Gemini 1.5 Flash (default) - fast and efficient
agent = RepoQAAgent(model_name="gemini-1.5-flash")

# Use Gemini 1.5 Pro - better quality and reasoning
agent = RepoQAAgent(model_name="gemini-1.5-pro")

# Use Gemini Pro - previous generation
agent = RepoQAAgent(model_name="gemini-pro")
```

## Command Reference

### `scan` Command

```
python cli.py scan <repo_url> [options]

Options:
  -b, --branch BRANCH    Branch to clone (default: main)
  -o, --output FILE      Save summary to JSON file
  -k, --keep            Keep cloned repository after scan
```

### `ask` Command

```
python cli.py ask <repo_url> [options]

Options:
  -b, --branch BRANCH      Branch to clone (default: main)
  -q, --question TEXT      Specific question to ask
  -i, --interactive        Interactive question mode
  -m, --model MODEL        LLM model to use (default: gpt-3.5-turbo)
  -e, --extensions EXTS    Comma-separated file extensions
  -k, --keep              Keep cloned repository
```

### `compliance` Command

```
python cli.py compliance <repo_url> [options]

Options:
  -b, --branch BRANCH        Branch to clone (default: main)
  -f, --guidelines-file FILE File with compliance guidelines
  -g, --guidelines TEXT...   Direct guideline statements
  -m, --model MODEL          LLM model to use
  -o, --output FILE          Save report to JSON file
  -k, --keep                Keep cloned repository
```

## Environment Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key (required for AI features)
  - Get it free at [Google AI Studio](https://makersuite.google.com/app/apikey)

## Project Structure

```
Github_scanner/
├── github_repo_tool.py    # Core repository operations
├── repo_qa_agent.py       # AI-powered Q&A agent
├── cli.py                 # Command-line interface
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Examples

### Example 1: Quick Repository Analysis

```powershell
python cli.py scan https://github.com/fastapi/fastapi -o fastapi_analysis.json
```

### Example 2: Security Compliance Check

```powershell
python cli.py compliance https://github.com/your-org/your-repo -g "Must have security policy" "Must use dependency scanning" "Must have authentication"
```

### Example 3: Interactive Code Exploration

```powershell
python cli.py ask https://github.com/django/django --interactive --extensions ".py,.md"
```

Then ask questions like:
- "How does the ORM work?"
- "What are the main security features?"
- "How is middleware implemented?"

## Troubleshooting

### Git Clone Fails

- Ensure Git is installed and in PATH
- Check if the repository URL is correct
- Verify you have access to the repository (public or with proper credentials)

### Import Errors

Make sure all dependencies are installed:
```powershell
pip install -r requirements.txt
```

### API Key Issues

Set your OpenAI API key:
```powershell
$env:OPENAI_API_KEY = "sk-..."
```

### Out of Memory

For large repositories:
- Limit file extensions: `-e ".py,.md"`
- Use smaller models: `-m gpt-3.5-turbo`
- Scan specific branches with fewer files

## License

This tool is part of the Guardian AI project.

## Contributing

Contributions are welcome! Please ensure:
- Code follows Python best practices
- New features include examples
- Documentation is updated

## Support

For issues or questions, please refer to the main Guardian AI project documentation.
