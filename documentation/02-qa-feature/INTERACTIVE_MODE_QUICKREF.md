# Quick Reference: Interactive Mode Commands

## 🚀 Starting Interactive Mode
```bash
python guardian_agent_simple.py --interactive
```

## 📖 Available Commands

### QA Session Management
```
set repo <url>     Set up QA session for a GitHub repository
show repo          Show current QA repository URL
clear repo         Clear the current QA session and free resources
```

### General Commands
```
help               Show help and available commands
exit               Exit interactive mode (also: quit, q)
```

## 💡 Usage Examples

### Example 1: Simple Q&A Session
```
You: set repo https://github.com/langchain-ai/langchain
You: What is LangChain?
You: How do I create a chain?
You: What are agents?
You: exit
```

### Example 2: Exploring Your Own Project
```
You: set repo https://github.com/kolipakulaHARSHA/guardian-ai
You: What does Guardian AI do?
You: What are the main components?
You: How does the legal analyzer work?
You: clear repo
```

### Example 3: Multiple Repositories
```
You: set repo https://github.com/user/repo1
You: What is this project?
You: clear repo
You: set repo https://github.com/user/repo2
You: What is this project?
You: exit
```

### Example 4: Mixed Mode (QA + Full Agent)
```
You: set repo https://github.com/user/repo
You: What does this do?                          # Uses QA mode (fast)
You: Check https://github.com/other/repo         # Uses full agent mode
     against sample.pdf
You: How does authentication work?               # Back to QA mode
You: exit
```

## 🎯 Tips

1. **Set repo once**: After `set repo`, you can ask unlimited questions
2. **No need to repeat URL**: Just ask your questions directly
3. **Clear when switching**: Use `clear repo` before setting a new repository
4. **Check status**: Use `show repo` to see which repository is active
5. **Exit cleanly**: Use `exit` to ensure proper cleanup

## 🔍 What You Can Ask

### Understanding the Project
- "What does this project do?"
- "What is the main purpose?"
- "What problem does it solve?"

### Architecture & Structure
- "What is the project structure?"
- "What are the main components?"
- "How is the code organized?"

### Technical Details
- "How does authentication work?"
- "What database is used?"
- "How is error handling implemented?"

### Getting Started
- "How do I install this?"
- "What are the dependencies?"
- "How do I run it?"
- "Are there any examples?"

### Code Exploration
- "What does main.py do?"
- "Where is the API defined?"
- "How do I use class X?"

## ⚡ Speed Comparison

| Mode | Clone | Index | First Question | Second Question |
|------|-------|-------|----------------|-----------------|
| **Without Session** | 5s | 30s | 10s | *Repeat all* |
| **With Session** | 5s | 30s | 10s | **2s** ⚡ |

**Total for 5 questions:**
- Without session: ~225 seconds (clone+index each time)
- With session: ~45 seconds (clone+index once) ✅

## 🎨 Output Format

### Successful Answer
```
🤖 Guardian AI: [Detailed answer to your question]

📎 Sources: file1.py, README.md, docs/guide.md
```

### Error Messages
```
❌ No QA session active. Use 'set repo <url>' to start a session.
❌ Error: Repository not found
❌ Please provide a repository URL.
```

### Status Messages
```
📥 Cloning repository: https://github.com/user/repo
✓ Repository cloned
📚 Indexing repository (this may take a moment)...
✅ QA session ready! Indexed 150 documents.
🧹 Cleaning up QA session...
👋 Goodbye!
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No QA session active" | Use `set repo <url>` first |
| Slow to start | Normal for large repos, wait for indexing |
| Wrong answers | Check sources, try rephrasing question |
| Want to switch repos | Use `clear repo` then `set repo <new_url>` |
| Stuck or frozen | Press Ctrl+C to exit safely |

## 🌟 Pro Tips

1. **Ask follow-up questions**: The context is maintained
2. **Be specific**: "How does user authentication work?" vs "How does it work?"
3. **Reference files**: "What does main.py do?" gets targeted results
4. **Check sources**: Verify which files were used for the answer
5. **Start broad, narrow down**: "What does this do?" → "Tell me more about X"

## 📊 Command Cheat Sheet

| Want to... | Command |
|------------|---------|
| Start QA session | `set repo <url>` |
| Ask a question | Just type your question |
| Check current repo | `show repo` |
| Switch repositories | `clear repo` → `set repo <new_url>` |
| Get help | `help` |
| Exit | `exit` or `quit` or `q` |

---

**Remember**: After `set repo`, you can ask as many questions as you want without repeating the URL! 🎉
