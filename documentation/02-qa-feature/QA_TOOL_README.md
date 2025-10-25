# qa_tool.py - Standalone Repository Q&A Tool

## Overview
`qa_tool.py` is a **fully independent, standalone tool** for asking questions about any GitHub repository using RAG (Retrieval Augmented Generation).

## Features

✅ **Interactive Q&A Mode** - Ask unlimited questions in a chat-like session  
✅ **Single Question Mode** - Get quick answers to specific questions  
✅ **Multiple Questions** - Ask several questions at once  
✅ **JSON Export** - Save answers to a file  
✅ **Model Selection** - Choose which Gemini model to use  
✅ **Smart Indexing** - Automatically indexes relevant code files  
✅ **Source Citations** - Shows which files were used to answer  

## Installation

Already installed! Uses the same dependencies as `code_tool.py`:
- LangChain
- Google Gemini API
- GitPython

## Usage

### 1. Interactive Mode (Recommended)

Ask unlimited questions in a chat session:

```powershell
python qa_tool.py https://github.com/user/repo --interactive
```

Example session:
```
Question: What does this project do?
Answer: This project is a finance management application...
Sources: README.md, src/main.py

Question: How do I install it?
Answer: Installation requires Python 3.8+. Run pip install -r requirements.txt...
Sources: README.md, docs/installation.md

Question: exit
```

### 2. Single Question

Ask one question and exit:

```powershell
python qa_tool.py https://github.com/user/repo --question "What is the main purpose of this project?"
```

### 3. Multiple Questions

Ask several questions at once:

```powershell
python qa_tool.py https://github.com/user/repo -q "What does this do?" -q "How do I install it?" -q "What are the main features?"
```

### 4. Save to JSON

Export answers to a file:

```powershell
python qa_tool.py https://github.com/user/repo -q "Summarize this project" --output summary.json
```

### 5. Use Different Model

Choose a specific Gemini model:

```powershell
# Fast model (default)
python qa_tool.py https://github.com/user/repo --interactive --model gemini-2.5-flash

# More powerful model
python qa_tool.py https://github.com/user/repo --interactive --model gemini-1.5-pro

# Experimental fastest model
python qa_tool.py https://github.com/user/repo --interactive --model gemini-2.0-flash-exp
```

## Command-Line Options

```
positional arguments:
  repo_url              GitHub repository URL

options:
  -h, --help            Show help message
  --question, -q        Question to ask (can be specified multiple times)
  --interactive, -i     Start interactive Q&A session
  --model MODEL         Gemini model to use (default: gemini-2.5-flash)
  --output, -o          Output JSON file path for answers
```

## Examples

### Example 1: Quick Project Summary
```powershell
python qa_tool.py https://github.com/microsoft/vscode -q "What is VS Code?"
```

### Example 2: Technical Deep Dive
```powershell
python qa_tool.py https://github.com/user/repo --interactive
```
Then ask:
- "What architecture patterns are used?"
- "How is authentication implemented?"
- "What are the main API endpoints?"

### Example 3: Documentation Questions
```powershell
python qa_tool.py https://github.com/user/repo \
  -q "How do I install this?" \
  -q "What are the dependencies?" \
  -q "How do I run tests?" \
  --output installation_guide.json
```

### Example 4: Code Understanding
```powershell
python qa_tool.py https://github.com/user/repo --interactive --model gemini-1.5-pro
```
Then ask:
- "Explain how the payment system works"
- "What security measures are in place?"
- "How does the caching mechanism work?"

## Output Format

### Console Output
```
Q: What does this project do?
A: This is a finance management application that helps users track expenses and income...

Sources: README.md, src/main.py, docs/overview.md
```

### JSON Output
```json
{
  "repository": "https://github.com/user/repo",
  "model": "gemini-2.5-flash",
  "total_questions": 2,
  "results": [
    {
      "status": "success",
      "question": "What does this project do?",
      "answer": "This is a finance management application...",
      "sources": ["README.md", "src/main.py"],
      "source_count": 5
    },
    {
      "status": "success",
      "question": "How do I install it?",
      "answer": "Installation requires Python 3.8+...",
      "sources": ["README.md", "docs/installation.md"],
      "source_count": 3
    }
  ]
}
```

## Comparison: qa_tool.py vs cli.py

| Feature | qa_tool.py | cli.py (old) |
|---------|------------|--------------|
| **Independence** | ✅ Fully standalone | ❌ Requires other files |
| **CLI Interface** | ✅ Complete argparse | ⚠️ Limited |
| **Interactive Mode** | ✅ Built-in | ✅ Yes |
| **Single Questions** | ✅ Yes | ❌ No |
| **Multiple Questions** | ✅ Yes | ❌ No |
| **JSON Export** | ✅ Yes | ❌ No |
| **Model Selection** | ✅ `--model` flag | ⚠️ Hardcoded |
| **Help Menu** | ✅ `--help` | ❌ No |
| **Source Citations** | ✅ Shows files | ✅ Shows files |

## Use Cases

### 1. Understanding New Codebases
```powershell
python qa_tool.py https://github.com/unfamiliar/project --interactive
```
Ask questions to quickly understand the architecture, setup, and key components.

### 2. Documentation Research
```powershell
python qa_tool.py https://github.com/user/repo -q "How do I configure this?" -o config_help.json
```
Extract specific documentation for team members.

### 3. Code Review Assistance
```powershell
python qa_tool.py https://github.com/team/repo --interactive --model gemini-1.5-pro
```
Ask detailed questions about implementation decisions during code review.

### 4. Onboarding New Developers
```powershell
python qa_tool.py https://github.com/company/project \
  -q "What is the project structure?" \
  -q "How do I set up the development environment?" \
  -q "What are the coding standards?" \
  --output onboarding_guide.json
```

### 5. API Documentation
```powershell
python qa_tool.py https://github.com/api/service --interactive
```
Ask about endpoints, parameters, and usage examples.

## Technical Details

### How It Works

1. **Clone Repository**: Downloads the GitHub repo to a temp directory
2. **Index Files**: Loads and chunks relevant files (.py, .js, .md, etc.)
3. **Create Embeddings**: Generates semantic embeddings using Gemini
4. **Build Vector Store**: Creates FAISS index for fast similarity search
5. **Answer Questions**: Uses RAG to retrieve relevant context and generate answers
6. **Cleanup**: Removes temporary directory

### Indexed File Types

- **Code**: .py, .js, .ts, .java, .cpp, .c, .h, .cs
- **Web**: .html, .css, .jsx, .tsx
- **Docs**: .md, .txt, .rst
- **Config**: .json, .yaml, .yml, .toml, .xml

### Performance

- **Indexing Time**: ~10-30 seconds for medium-sized repos
- **Question Time**: ~2-5 seconds per question
- **Memory**: ~500MB-2GB depending on repo size

## Tips & Best Practices

### ✅ Good Questions
- "What is the main purpose of this project?"
- "How does authentication work in this codebase?"
- "What are the key dependencies?"
- "How do I run the tests?"
- "Explain the database schema"

### ❌ Avoid
- Very generic questions without context
- Questions requiring knowledge outside the repository
- Questions about future plans (unless documented)

### 💡 Pro Tips
1. **Use interactive mode** for exploratory analysis
2. **Use specific questions** with `--output` for documentation
3. **Use powerful models** (gemini-1.5-pro) for complex technical questions
4. **Ask follow-up questions** to drill deeper into topics
5. **Check sources** to verify answers

## Troubleshooting

### "GOOGLE_API_KEY not found"
```powershell
# Set the API key
$env:GOOGLE_API_KEY='your-key-here'

# Or create .env file
echo "GOOGLE_API_KEY=your-key-here" > .env
```

### "No documents found to index"
The repository might not have supported file types. Check that it has code files (.py, .js, etc.).

### Slow performance
Try using a faster model:
```powershell
python qa_tool.py <repo> --interactive --model gemini-2.0-flash-exp
```

## Comparison with Other Tools

### vs code_tool.py
- **code_tool.py**: Finds violations and compliance issues
- **qa_tool.py**: Answers questions and explains code

### vs repo_qa_agent.py
- **repo_qa_agent.py**: Class for importing into other code
- **qa_tool.py**: Standalone CLI tool for direct use

### vs cli.py
- **cli.py**: Original multi-mode orchestrator
- **qa_tool.py**: Focused Q&A tool with better UX

## Future Enhancements

Potential improvements:
- [ ] Conversation history for context-aware follow-ups
- [ ] Code snippet highlighting in answers
- [ ] Multi-repository indexing
- [ ] Custom file type filtering
- [ ] Answer caching for repeated questions
- [ ] Export to Markdown/HTML formats

## Status

✅ **COMPLETE AND READY TO USE**

The tool is fully functional, standalone, and production-ready!

## Quick Start

```powershell
# 1. Set your API key
$env:GOOGLE_API_KEY='your-key-here'

# 2. Run interactive mode
python qa_tool.py https://github.com/kolipakulaHARSHA/FINANCE_MANAGEMENT_APP --interactive

# 3. Start asking questions!
```

Enjoy exploring codebases with AI! 🚀
