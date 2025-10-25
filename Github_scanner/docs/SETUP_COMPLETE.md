# Guardian AI - GitHub Scanner Tool
## Setup Complete! 🎉

## What I Built For You

I've created a complete **GitHub Repository Scanner and Compliance Checker** tool for your Guardian AI project. This tool uses **Agentic AI** to scan GitHub repositories, understand their contents, and verify compliance with your guidelines.

## 📦 What's Included

### Core Files:
1. **github_repo_tool.py** - Clone and analyze GitHub repos (290+ lines)
2. **repo_qa_agent.py** - AI-powered Q&A using LangChain (330+ lines)
3. **cli.py** - Command-line interface with 3 commands (300+ lines)
4. **examples.py** - 5 complete usage examples (250+ lines)

### Documentation:
5. **README.md** - Complete documentation with all features
6. **QUICKSTART.md** - 5-minute getting started guide
7. **PROJECT_SUMMARY.md** - High-level overview and architecture
8. **compliance_guidelines.txt** - Sample compliance rules

### Support Files:
9. **requirements.txt** - All Python dependencies
10. **.env.example** - Configuration template
11. **test_basic.py** - Automated testing
12. **__init__.py** - Package initialization

## ✅ Status: READY TO USE

✓ All dependencies installed
✓ Windows file permissions handled
✓ Basic functionality tested
✓ LangChain integration complete
✓ CLI interface working

## 🚀 How to Use

### 1. Basic Repository Scanning (No API Key Needed)

```powershell
cd Github_scanner

# Scan any GitHub repository
python cli.py scan https://github.com/pallets/flask

# Save results to JSON
python cli.py scan https://github.com/microsoft/vscode -o vscode_summary.json
```

### 2. AI-Powered Question Answering (Requires OpenAI API Key)

```powershell
# Set your API key first
$env:OPENAI_API_KEY = "sk-your-api-key-here"

# Ask a specific question
python cli.py ask https://github.com/pallets/flask -q "What is Flask used for?"

# Interactive mode - ask multiple questions
python cli.py ask https://github.com/django/django --interactive

# Focus on specific file types
python cli.py ask https://github.com/facebook/react --extensions ".js,.jsx,.md" -q "How does the rendering work?"
```

### 3. Compliance Checking (For Guardian AI's Main Purpose)

```powershell
# Check with default compliance rules
python cli.py compliance https://github.com/your-org/your-project

# Use custom guidelines
python cli.py compliance https://github.com/your-org/your-project --guidelines-file compliance_guidelines.txt

# Save compliance report
python cli.py compliance https://github.com/your-org/your-project -o compliance_report.json

# Specify guidelines directly
python cli.py compliance https://github.com/your-org/app -g "Must have tests" "Must have security docs"
```

## 💻 Programmatic Usage

```python
from github_repo_tool import GitHubRepoTool
from repo_qa_agent import RepoQAAgent

# Basic usage - no API key needed
tool = GitHubRepoTool()
tool.clone_repository("https://github.com/pallets/flask")
summary = tool.get_repository_summary()
python_files = tool.search_files("*.py")
readme = tool.read_file("README.md")
tool.cleanup()

# AI-powered usage - requires API key
agent = RepoQAAgent(model_name="gpt-4")
agent.clone_and_index_repository(
    "https://github.com/pallets/flask",
    file_extensions=['.py', '.md']
)

# Ask questions
answer = agent.ask_question("How does routing work in Flask?")
print(answer['answer'])

# Check compliance
guidelines = [
    "Must have LICENSE file",
    "Must have security documentation",
    "Must have tests"
]
compliance = agent.check_compliance(guidelines)

# Get insights
insights = agent.get_repository_insights()
agent.cleanup()
```

## 🎯 Guardian AI Integration

For your compliance checking use case:

```python
# 1. User uploads compliance guidelines
guidelines = load_user_guidelines()  # Your existing code

# 2. User provides GitHub repository URL
repo_url = "https://github.com/user/project"

# 3. Use Guardian AI Scanner
from repo_qa_agent import RepoQAAgent

agent = RepoQAAgent(model_name="gpt-4")
agent.clone_and_index_repository(repo_url)

# 4. Check compliance
compliance_report = agent.check_compliance(guidelines)

# 5. Present results to user
# compliance_report contains detailed assessment of each guideline
# with evidence from the code and documentation

agent.cleanup()
```

## 📊 Features Breakdown

### Without API Key:
- ✅ Clone any public GitHub repository
- ✅ Get file structure and statistics
- ✅ Search for specific files
- ✅ Read file contents
- ✅ Generate JSON reports
- ✅ Detect important files (LICENSE, README, etc.)

### With OpenAI API Key:
- 🤖 Ask natural language questions about code
- 🤖 Check compliance against custom guidelines
- 🤖 Get automated repository insights
- 🤖 Semantic code search
- 🤖 Source citations for all answers

## 🔧 Configuration

### Set OpenAI API Key:
```powershell
# Temporary (current session)
$env:OPENAI_API_KEY = "sk-your-key-here"

# Permanent (create .env file)
# Copy .env.example to .env and edit
```

### Choose AI Model:
```bash
# Fast and cheap
python cli.py ask <repo> -m gpt-3.5-turbo -q "question"

# Better quality
python cli.py ask <repo> -m gpt-4 -q "question"
```

## 📁 Project Structure

```
Github_scanner/
├── Core Tool
│   ├── github_repo_tool.py       # Repository operations
│   ├── repo_qa_agent.py          # AI Q&A & compliance
│   └── __init__.py               # Package init
├── Interface
│   ├── cli.py                    # Command-line interface
│   └── examples.py               # Code examples
├── Documentation
│   ├── README.md                 # Full documentation
│   ├── QUICKSTART.md             # Quick start guide
│   ├── PROJECT_SUMMARY.md        # Architecture overview
│   └── SETUP_COMPLETE.md         # This file
├── Configuration
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Config template
│   └── compliance_guidelines.txt # Sample guidelines
└── Testing
    └── test_basic.py             # Basic tests
```

## 🧪 Test It Now

Run the basic test:
```powershell
cd Github_scanner
python test_basic.py
```

Expected output:
```
✓ Clone successful!
✓ Structure analysis successful!
✓ Summary generation successful!
✓ Search successful!
✓ File read successful!
✓ Cleanup successful!
✓ ALL TESTS PASSED!
```

## 🎓 Next Steps

1. **Try the basic scan** (no API key needed):
   ```bash
   python cli.py scan https://github.com/pallets/flask
   ```

2. **Set up OpenAI API key** for AI features:
   - Get key from https://platform.openai.com/api-keys
   - Set: `$env:OPENAI_API_KEY = "sk-..."`

3. **Test AI features**:
   ```bash
   python cli.py ask https://github.com/pallets/click -q "What is this project?"
   ```

4. **Customize for Guardian AI**:
   - Edit `compliance_guidelines.txt` with your rules
   - Integrate with your existing Guardian AI workflow
   - Add custom compliance checks as needed

5. **Run examples**:
   ```bash
   python examples.py
   ```

## 🆘 Troubleshooting

### "git: command not found"
Install Git from https://git-scm.com/download/win

### Import errors
```bash
pip install -r requirements.txt
```

### API key errors
```bash
# Check if set
echo $env:OPENAI_API_KEY

# Set it
$env:OPENAI_API_KEY = "sk-your-key"
```

### Out of memory with large repos
```bash
# Limit file types
python cli.py ask <repo> --extensions ".py,.md"
```

## 💡 Pro Tips

1. **Save time**: Use `--keep` flag to reuse cloned repos
2. **Better results**: Use GPT-4 for compliance checking
3. **Faster**: Limit to relevant file extensions only
4. **Batch mode**: Write a script to check multiple repos

## 📚 Resources

- **README.md**: Detailed documentation with all features
- **QUICKSTART.md**: 5-minute tutorial
- **PROJECT_SUMMARY.md**: Architecture and technical details
- **examples.py**: Working code examples
- **compliance_guidelines.txt**: Sample compliance rules

## 🎉 You're All Set!

Your Guardian AI GitHub Scanner is fully operational. You can now:

✅ Clone and analyze any GitHub repository
✅ Ask questions about code using AI
✅ Check compliance against custom guidelines
✅ Generate detailed reports
✅ Integrate with your Guardian AI project

**Start with**: `python cli.py scan https://github.com/pallets/flask`

---

**Need help?** Check the documentation files or run:
```bash
python cli.py --help
python cli.py scan --help
python cli.py ask --help
python cli.py compliance --help
```

**Good luck with your Guardian AI project!** 🚀
