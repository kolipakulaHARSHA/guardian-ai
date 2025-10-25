# Guardian AI - Quick Reference (Gemini Edition)

## 🔑 Setup (One Time)

```powershell
# Get API key from: https://makersuite.google.com/app/apikey
$env:GOOGLE_API_KEY = "your-google-api-key-here"
```

## 📋 Common Commands

### Basic Scan (No API Key)
```powershell
python cli.py scan https://github.com/user/repo
python cli.py scan https://github.com/user/repo -o report.json
```

### Ask Questions (Requires API Key)
```powershell
# Single question
python cli.py ask https://github.com/user/repo -q "question here"

# Interactive mode
python cli.py ask https://github.com/user/repo --interactive

# Use better model
python cli.py ask https://github.com/user/repo -m gemini-1.5-pro -q "question"

# Filter file types
python cli.py ask https://github.com/user/repo --extensions ".py,.md" -q "question"
```

### Compliance Check (Requires API Key)
```powershell
# Default compliance
python cli.py compliance https://github.com/user/repo

# Custom guidelines file
python cli.py compliance https://github.com/user/repo -f guidelines.txt

# Direct guidelines
python cli.py compliance https://github.com/user/repo -g "Must have tests" "Must have docs"

# Save report
python cli.py compliance https://github.com/user/repo -o report.json

# Use better model
python cli.py compliance https://github.com/user/repo -m gemini-1.5-pro
```

## 🎨 Model Options

| Model | Use `-m` flag | Speed | Quality | Cost |
|-------|---------------|-------|---------|------|
| Flash (default) | `gemini-1.5-flash` | ⚡⚡⚡ | ⭐⭐⭐ | FREE |
| Pro | `gemini-1.5-pro` | ⚡⚡ | ⭐⭐⭐⭐⭐ | Low |

## 💻 Python API

```python
from github_repo_tool import GitHubRepoTool
from repo_qa_agent import RepoQAAgent

# Basic operations
tool = GitHubRepoTool()
tool.clone_repository("https://github.com/user/repo")
summary = tool.get_repository_summary()
tool.cleanup()

# AI operations
agent = RepoQAAgent(model_name="gemini-1.5-flash")
agent.clone_and_index_repository("https://github.com/user/repo")
answer = agent.ask_question("How does this work?")
compliance = agent.check_compliance(["guideline 1", "guideline 2"])
agent.cleanup()
```

## 🔧 Options

```
-b, --branch BRANCH        Branch to clone (default: main)
-m, --model MODEL          LLM model (default: gemini-1.5-flash)
-q, --question TEXT        Question to ask
-i, --interactive          Interactive mode
-e, --extensions EXTS      File extensions (e.g., ".py,.md")
-f, --guidelines-file FILE Compliance guidelines file
-g, --guidelines TEXT...   Direct guidelines
-o, --output FILE          Save output to JSON
-k, --keep                 Keep cloned repo
```

## 📝 Guidelines File Format

Create `guidelines.txt`:
```
The project must have a LICENSE file
The project must have comprehensive documentation
Code must follow security best practices
All dependencies must be up to date
```

## 🆘 Troubleshooting

```powershell
# Check API key
echo $env:GOOGLE_API_KEY

# Set API key
$env:GOOGLE_API_KEY = "your-key"

# Verify installation
pip show langchain-google-genai

# Reinstall dependencies
pip install -r requirements.txt
```

## 🔗 Links

- Get API Key: https://makersuite.google.com/app/apikey
- Full Docs: See README.md
- Migration Guide: See GEMINI_MIGRATION.md
