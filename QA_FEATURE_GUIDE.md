# Guardian AI - QA Feature Guide

## Overview
The QA (Question-Answering) feature allows you to ask questions about any GitHub repository using RAG (Retrieval Augmented Generation). It indexes the repository code and documentation, then answers your questions with relevant context.

## 🚀 Quick Start

### Option 1: Interactive Mode (Recommended)
```bash
python guardian_agent_simple.py --interactive
```

### Option 2: Direct QA Tool
```bash
python Github_scanner\qa_tool.py <repo_url> --interactive
```

### Option 3: Single Query
```bash
python guardian_agent_simple.py "What does https://github.com/user/repo do?"
```

## 📖 Interactive Mode Commands

### Set Up a QA Session
```
You: set repo https://github.com/user/repo
```
This will:
- Clone the repository
- Index all code files and documentation
- Keep the session active for multiple questions

### Ask Questions (After Setting Repo)
```
You: What does this project do?
You: How do I install it?
You: What are the main features?
You: How does authentication work?
```

### Check Current Repository
```
You: show repo
```

### Clear QA Session
```
You: clear repo
```

### Get Help
```
You: help
```

### Exit
```
You: exit
```

## 💡 Key Features

### ✅ Persistent Sessions
- Set a repository once
- Ask unlimited questions
- No need to repeat the URL
- Automatic cleanup on exit

### ✅ Smart Query Routing
- Questions about the active repo → Fast QA mode
- Complex queries with PDFs/audits → Full agent mode
- Automatic detection and routing

### ✅ Source Citations
- Shows which files were used to answer
- Top 3-5 relevant source files
- Transparent and traceable

## 📝 Example Session

```
🤖 Initializing Guardian AI...
✅ Ready!

======================================================================
INTERACTIVE MODE
======================================================================

📖 Commands:
  • 'set repo <url>'  - Set up QA session for a repository
  • 'show repo'       - Show current QA repository
  • 'clear repo'      - Clear QA session
  • 'help'            - Show this help
  • 'exit' or 'quit'  - Exit interactive mode

💡 Tips:
  • After setting a repo, ask questions directly without the URL
  • For other tasks (legal analysis, code audit), include full details

======================================================================

You: set repo https://github.com/langchain-ai/langchain

📥 Cloning repository: https://github.com/langchain-ai/langchain
✓ Repository cloned

📚 Indexing repository (this may take a moment)...
✓ Loaded 1250 documents
✓ Created 5000 chunks
✅ QA session ready! Indexed 1250 documents.

💡 You can now ask questions about this repository without providing the URL.

You: What is LangChain?

🤖 Guardian AI: LangChain is a framework for developing applications 
powered by language models. It provides tools and abstractions for 
working with LLMs, including prompt templates, chains, agents, and 
memory systems...

📎 Sources: README.md, docs/introduction.md, langchain/llms/base.py

You: How do I create a simple chain?

🤖 Guardian AI: To create a simple chain in LangChain, you can use 
the LLMChain class. Here's an example:

```python
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI

template = "What is a good name for {product}?"
prompt = PromptTemplate(template=template, input_variables=["product"])
chain = LLMChain(llm=OpenAI(), prompt=prompt)
```

📎 Sources: examples/chains/simple_chain.py, docs/chains.md

You: exit

🧹 Cleaning up QA session...
👋 Goodbye!
```

## 🔧 Advanced Usage

### Using the QA Tool Directly

For dedicated Q&A sessions without the full agent:

```bash
# Interactive session
python Github_scanner\qa_tool.py https://github.com/user/repo --interactive

# Single question
python Github_scanner\qa_tool.py https://github.com/user/repo \
  --question "What does this project do?"

# Multiple questions
python Github_scanner\qa_tool.py https://github.com/user/repo \
  -q "What is the main purpose?" \
  -q "How do I install it?" \
  -q "What are the dependencies?"

# Save answers to JSON
python Github_scanner\qa_tool.py https://github.com/user/repo \
  -q "Summarize this project" \
  --output summary.json

# Use different model
python Github_scanner\qa_tool.py https://github.com/user/repo \
  --interactive \
  --model gemini-1.5-pro
```

## 🎯 Use Cases

### 1. Understanding New Codebases
```
You: set repo https://github.com/unfamiliar/project
You: What is the overall architecture?
You: What are the main components?
You: Where is the authentication logic?
```

### 2. Finding Specific Information
```
You: How does error handling work?
You: What database is used?
You: Are there any security features?
```

### 3. Learning APIs
```
You: What are the available API endpoints?
You: How do I authenticate with the API?
You: What's an example of using the main class?
```

### 4. Documentation Exploration
```
You: How do I get started?
You: What are the configuration options?
You: Are there any examples?
```

## 🔍 What Gets Indexed

The QA tool indexes:
- **Code files**: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.cs`, etc.
- **Documentation**: `.md`, `.txt`, `.rst`
- **Config files**: `.json`, `.yaml`, `.yml`, `.toml`, `.xml`
- **Web files**: `.html`, `.css`

Automatically excludes:
- `node_modules/`, `venv/`, `env/`
- `.git/`, `__pycache__/`
- `build/`, `dist/`, `target/`

## ⚙️ How It Works

1. **Clone**: Downloads the repository to a temporary directory
2. **Load**: Reads all relevant files
3. **Split**: Breaks content into ~1000 character chunks
4. **Embed**: Creates vector embeddings using Google's model
5. **Index**: Stores in FAISS vector database
6. **Query**: Retrieves relevant chunks for each question
7. **Generate**: Uses Gemini to synthesize an answer
8. **Cleanup**: Removes temporary files on exit

## 🐛 Troubleshooting

### "No QA session active"
- Solution: Use `set repo <url>` first

### "Repository not found"
- Check the URL is correct and accessible
- Ensure you have internet connection

### Slow indexing
- Normal for large repos (1000+ files)
- Progress is shown during indexing
- Only happens once per session

### Out of memory
- Use a smaller repository
- Or use the direct QA tool with targeted questions

## 🔐 API Key Setup

The QA feature requires a Google API key:

```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your-key-here"

# Linux/Mac
export GOOGLE_API_KEY="your-key-here"

# Or create .env file
GOOGLE_API_KEY=your-key-here
```

## 📊 Performance Tips

1. **Set repo once**: Reuse the session for multiple questions
2. **Be specific**: Detailed questions get better answers
3. **Check sources**: Verify the context used
4. **Clear when done**: Frees up memory and disk space

## 🆚 QA Mode vs Full Agent Mode

| Feature | QA Mode | Full Agent Mode |
|---------|---------|-----------------|
| Speed | ⚡ Fast | 🐢 Slower |
| Scope | Single repo | Multi-tool |
| Use Case | Code questions | Complex tasks |
| Trigger | Simple questions | Mentions PDF/audit |
| Persistence | ✅ Yes | ❌ No |

## 📚 Examples by Repository Type

### Python Projects
```
You: What's the project structure?
You: How are dependencies managed?
You: Where are the tests?
You: What's the main entry point?
```

### JavaScript/Node Projects
```
You: What framework is used?
You: How is state managed?
You: What are the API routes?
You: How do I run the development server?
```

### Documentation Sites
```
You: What topics are covered?
You: How do I get started?
You: Are there code examples?
You: What's the installation process?
```

## 🚀 Pro Tips

1. **Start broad, then narrow**: "What does this do?" → "How does auth work?"
2. **Ask follow-ups**: The context is maintained within the session
3. **Reference files**: "What does main.py do?"
4. **Compare**: "What's the difference between X and Y?"
5. **Explore**: "What are all the components?" → "Tell me more about component X"

---

## Need Help?

- Type `help` in interactive mode
- Check error messages for specific guidance
- Ensure your API key is set correctly
- Try with a smaller repository first
