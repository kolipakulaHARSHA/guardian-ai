# Guardian AI - GitHub Repository Scanner
## Complete Project Summary

## 📁 Project Structure

```
Guardian/
├── Github_scanner/
│   ├── github_repo_tool.py      # Core repository operations (cloning, scanning, file operations)
│   ├── repo_qa_agent.py         # AI-powered Q&A and compliance checking
│   ├── cli.py                   # Command-line interface
│   ├── examples.py              # Example usage scripts
│   ├── test_basic.py            # Basic functionality tests
│   ├── __init__.py              # Package initialization
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment configuration template
│   ├── README.md                # Full documentation
│   ├── QUICKSTART.md            # Quick start guide
│   └── PROJECT_SUMMARY.md       # This file
├── package.json                 # Node.js dependencies (LangChain MCP adapters)
└── venv/                        # Python virtual environment
```

## 🎯 What Does This Tool Do?

Guardian AI's GitHub Scanner is a comprehensive tool that:

1. **Clones GitHub Repositories** - Download any public GitHub repository locally
2. **Analyzes Repository Structure** - Get detailed file statistics, directory trees, and important file detection
3. **Answers Questions** - Use AI (LangChain + OpenAI) to answer questions about code and documentation
4. **Checks Compliance** - Verify if repositories follow specific guidelines and requirements
5. **Generates Reports** - Create JSON reports for integration with other tools

## 🔧 Core Components

### 1. GitHubRepoTool (`github_repo_tool.py`)

Basic repository operations without requiring AI:

- `clone_repository()` - Clone a GitHub repo
- `get_repository_structure()` - Get directory tree
- `get_repository_summary()` - Get file statistics and important files
- `read_file()` - Read specific files
- `search_files()` - Find files by pattern
- `get_file_list()` - List all files with filters
- `cleanup()` - Remove cloned repository

**Use Case**: Quick repository analysis, file extraction, structure inspection

### 2. RepoQAAgent (`repo_qa_agent.py`)

AI-powered analysis using LangChain:

- `clone_and_index_repository()` - Clone and create searchable vector index
- `ask_question()` - Ask natural language questions about the code
- `check_compliance()` - Verify compliance with guidelines
- `get_repository_insights()` - Get automated analysis
- `index_repository()` - Create searchable index from files

**Use Case**: Understanding codebases, compliance verification, intelligent search

### 3. CLI (`cli.py`)

Command-line interface with three main commands:

```bash
# Scan - Basic repository analysis (no API key needed)
python cli.py scan <repo_url> [options]

# Ask - Question answering (requires API key)
python cli.py ask <repo_url> [options]

# Compliance - Check guidelines (requires API key)
python cli.py compliance <repo_url> [options]
```

## 📋 Features

### Basic Features (No API Key Required)
- ✅ Clone any public GitHub repository
- ✅ Analyze repository structure and file distribution
- ✅ Search for files by pattern or extension
- ✅ Read and extract file contents
- ✅ Generate JSON reports
- ✅ Detect important files (README, LICENSE, etc.)

### AI-Powered Features (Requires OpenAI API Key)
- 🤖 Natural language question answering about code
- 🤖 Compliance checking against custom guidelines
- 🤖 Automated repository insights
- 🤖 Intelligent code search using embeddings
- 🤖 Source citation for all answers

## 🚀 Quick Start

### Installation
```powershell
cd Github_scanner
pip install -r requirements.txt
```

### Basic Usage (No API Key)
```powershell
# Scan a repository
python cli.py scan https://github.com/pallets/flask

# Save to JSON
python cli.py scan https://github.com/pallets/flask -o report.json
```

### AI Usage (Requires API Key)
```powershell
# Set API key
$env:OPENAI_API_KEY = "sk-your-key-here"

# Ask questions
python cli.py ask https://github.com/pallets/flask -q "What is Flask?"

# Interactive mode
python cli.py ask https://github.com/pallets/flask --interactive

# Check compliance
python cli.py compliance https://github.com/your-org/repo
```

## 💡 Use Cases for Guardian AI

### 1. Compliance Auditing
Check if repositories meet organizational standards:
```python
agent = RepoQAAgent()
agent.clone_and_index_repository("https://github.com/org/repo")

guidelines = [
    "Must have security documentation",
    "Must use approved dependencies",
    "Must have test coverage"
]

report = agent.check_compliance(guidelines)
```

### 2. Code Review Assistant
Understand new codebases quickly:
```bash
python cli.py ask https://github.com/new-project/code --interactive
# Then ask: "What are the main components?"
# "How is authentication implemented?"
# "What are the security considerations?"
```

### 3. Documentation Verification
Ensure documentation is complete:
```bash
python cli.py compliance https://github.com/org/api \
  -g "Must have API documentation" \
     "Must have examples" \
     "Must have installation guide"
```

### 4. Batch Repository Analysis
Analyze multiple repositories:
```python
repos = [
    "https://github.com/org/repo1",
    "https://github.com/org/repo2",
    "https://github.com/org/repo3"
]

for repo in repos:
    tool = GitHubRepoTool()
    result = tool.clone_repository(repo)
    summary = tool.get_repository_summary()
    # Save summary, check compliance, etc.
    tool.cleanup()
```

## 🔑 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your-key-here       # Required for AI features
DEFAULT_MODEL=gpt-3.5-turbo        # Optional: default LLM model
BASE_CLONE_DIR=./cloned_repos      # Optional: clone directory
```

### Customization Options
- **File Extensions**: Filter which files to index
- **LLM Model**: Choose between gpt-3.5-turbo, gpt-4, etc.
- **Clone Depth**: Use shallow clones for faster downloads
- **Custom Guidelines**: Create organization-specific compliance rules

## 📊 Output Formats

### Repository Summary (JSON)
```json
{
  "repo_metadata": {
    "repo_name": "flask",
    "repo_url": "https://github.com/pallets/flask",
    "local_path": "cloned_repos/flask"
  },
  "important_files": {
    "README.md": "README.md",
    "LICENSE": "LICENSE"
  },
  "file_statistics": {
    ".py": {"count": 150, "total_size": 500000},
    ".md": {"count": 20, "total_size": 50000}
  },
  "total_files": 200,
  "total_size": 1000000
}
```

### Compliance Report (JSON)
```json
{
  "status": "success",
  "compliance_checks": [
    {
      "guideline": "Must have LICENSE",
      "assessment": "Compliant. LICENSE file found...",
      "evidence_sources": ["LICENSE", "README.md"]
    }
  ]
}
```

## 🛠️ Integration

### Python Integration
```python
from github_repo_tool import GitHubRepoTool
from repo_qa_agent import RepoQAAgent

# Basic usage
tool = GitHubRepoTool()
tool.clone_repository(repo_url)
summary = tool.get_repository_summary()

# AI usage
agent = RepoQAAgent()
agent.clone_and_index_repository(repo_url)
answer = agent.ask_question("How does this work?")
```

### CI/CD Integration
```yaml
# Example GitHub Actions workflow
- name: Check Compliance
  run: |
    python cli.py compliance ${{ github.repository }} \
      --guidelines-file compliance.txt \
      -o compliance-report.json
```

## 🎓 Technical Details

### Technologies Used
- **Python 3.8+**: Core language
- **LangChain**: AI orchestration framework
- **OpenAI GPT**: Language models
- **FAISS**: Vector store for semantic search
- **Git**: Repository cloning

### AI Architecture
1. Clone repository
2. Load relevant files (filtered by extension)
3. Split into chunks (1000 chars with 200 overlap)
4. Create embeddings using OpenAI
5. Store in FAISS vector database
6. Use RAG (Retrieval Augmented Generation) for Q&A

### Performance Considerations
- Shallow clones reduce download time
- File filtering reduces indexing time
- Vector search enables fast retrieval
- Chunk-based processing handles large files

## 📝 Testing

Run basic functionality test:
```bash
python test_basic.py
```

Run examples:
```bash
python examples.py
```

## 🔒 Security Notes

- Never commit API keys
- Use `.env` files for configuration
- Be cautious with private repositories
- Review cloned code before execution
- Clean up repositories after use

## 📚 Documentation Files

- **README.md**: Complete documentation
- **QUICKSTART.md**: 5-minute getting started guide
- **PROJECT_SUMMARY.md**: This file (high-level overview)
- **examples.py**: Code examples

## 🤝 Contributing

To extend this tool:
1. Add new methods to `GitHubRepoTool` for basic operations
2. Add new methods to `RepoQAAgent` for AI features
3. Update CLI with new commands
4. Add examples to `examples.py`
5. Update documentation

## 📄 License

Part of the Guardian AI project.

---

**Created for**: Guardian AI Hackathon Project  
**Purpose**: Repository scanning and compliance checking using Agentic AI  
**Status**: ✅ Fully functional and tested
