# QA Agent Workflow - Complete Guide

## Overview

The QA (Question-Answering) Agent uses **RAG (Retrieval Augmented Generation)** to answer questions about GitHub repositories. It combines semantic search with LLM reasoning to provide accurate, source-backed answers.

---

## 🔄 Complete Workflow

### **Phase 1: Initialization**

```
User Action: python guardian_agent_simple.py --interactive
                              │
                              ▼
┌──────────────────────────────────────────────────────┐
│  GuardianAgentSimple.__init__()                      │
│  ───────────────────────────────────                 │
│  • Initialize Gemini LLM                             │
│  • Set model: gemini-2.5-pro-preview-03-25           │
│  • Initialize QA session variables:                  │
│    - qa_tool_instance = None                         │
│    - qa_repo_url = None                              │
│    - qa_temp_dir = None                              │
└──────────────────────────────────────────────────────┘
                              │
                              ▼
                    ✅ Agent Ready!
```

---

### **Phase 2: Setting Up QA Session**

```
User Command: set repo https://github.com/user/repo
                              │
                              ▼
┌──────────────────────────────────────────────────────┐
│  setup_qa_session(repo_url)                          │
└──────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 1: Import Dependencies        │
        │  • tempfile (for temp directory)    │
        │  • git (for cloning)                │
        │  • RepoQATool (the QA engine)       │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2: Cleanup Old Session        │
        │  • cleanup_qa_session()             │
        │  • Remove any existing temp files   │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 3: Initialize QA Tool         │
        │  • qa_tool = RepoQATool()           │
        │  • Store in qa_tool_instance        │
        │  • Store repo_url in qa_repo_url    │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 4: Clone Repository           │
        │  📥 Cloning repository...           │
        │  • Create temp directory            │
        │  • git.Repo.clone_from(url, dir)    │
        │  ✓ Repository cloned                │
        └─────────────────────────────────────┘
                Time: ~5-10 seconds
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 5: Index Repository           │
        │  📚 Indexing repository...          │
        │  (See detailed indexing flow below) │
        │  ✓ Indexed 150 documents            │
        └─────────────────────────────────────┘
                Time: ~20-40 seconds
                              │
                              ▼
┌──────────────────────────────────────────────────────┐
│  Result: Session Active                              │
│  ───────────────────────                             │
│  • qa_tool_instance = <QA Tool Object>               │
│  • qa_repo_url = "https://github.com/user/repo"      │
│  • qa_temp_dir = "/tmp/guardian_qa_xxxxx"            │
│                                                       │
│  ✅ QA session ready! Indexed 150 documents.         │
│  💡 You can now ask questions without the URL.       │
└──────────────────────────────────────────────────────┘
```

---

### **Phase 3: Repository Indexing (Detailed)**

```
┌──────────────────────────────────────────────────────┐
│  qa_tool.index_repository(repo_path)                 │
└──────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 1: Scan for Files             │
        │  • Supported extensions:            │
        │    - Code: .py, .js, .ts, .java     │
        │    - Docs: .md, .txt, .rst          │
        │    - Config: .json, .yaml, .yml     │
        │    - Web: .html, .css               │
        │  • Ignore:                          │
        │    - node_modules/, venv/, .git/    │
        │    - __pycache__/, build/, dist/    │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2: Load Documents             │
        │  For each file:                     │
        │  • Read content (UTF-8)             │
        │  • Create Document object:          │
        │    - page_content = file contents   │
        │    - metadata = {                   │
        │        source: "path/to/file.py"    │
        │        file_name: "file.py"         │
        │        extension: ".py"             │
        │      }                              │
        │  ✓ Loaded 150 documents             │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 3: Split into Chunks          │
        │  • RecursiveCharacterTextSplitter   │
        │  • chunk_size = 1000 chars          │
        │  • chunk_overlap = 200 chars        │
        │  • Preserves code structure         │
        │  ✓ Created 500 chunks               │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 4: Create Embeddings          │
        │  For each chunk:                    │
        │  • GoogleGenerativeAIEmbeddings     │
        │  • model: "models/embedding-001"    │
        │  • Convert text → 768D vector       │
        │  • Capture semantic meaning         │
        └─────────────────────────────────────┘
                Time: ~20-30 seconds
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 5: Build Vector Store         │
        │  • FAISS.from_documents()           │
        │  • Store all embeddings             │
        │  • Enable fast similarity search    │
        │  • Create retriever (k=5)           │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 6: Create QA Chain            │
        │  • Prompt template with context     │
        │  • Chain: retriever → prompt → LLM │
        │  • Output parser for clean answers  │
        └─────────────────────────────────────┘
                              │
                              ▼
                    ✅ Indexing Complete!
```

---

### **Phase 4: Asking Questions (Fast Path)**

```
User: what does this repo do?
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Interactive Mode Router            │
        │  • Check: QA session active? ✓      │
        │  • Check: Question has URL? ✗       │
        │  • Check: Question has PDF? ✗       │
        │  → Route to: ask_qa() (FAST!)       │
        └─────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────┐
│  ask_qa(question)                                    │
└──────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 1: Validate Session           │
        │  • Check qa_tool_instance exists    │
        │  • If not: return error message     │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2: Call QA Tool               │
        │  result = qa_tool.ask_question(q)   │
        └─────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────┐
│  qa_tool.ask_question(question) - CORE LOGIC         │
└──────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2a: Semantic Retrieval        │
        │  • Convert question → embedding     │
        │  • Search FAISS vector store        │
        │  • Find top 5 similar chunks        │
        │  • Return relevant code/docs        │
        └─────────────────────────────────────┘
                Time: ~500ms
                              │
                Example Results:
                ├─ README.md (lines 1-50)
                ├─ main.py (lines 120-180)
                ├─ auth.py (lines 45-90)
                ├─ docs/overview.md (lines 10-60)
                └─ config.py (lines 5-25)
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2b: Build Context             │
        │  Combine retrieved chunks:          │
        │  "Context from README.md:           │
        │   This is a web application...      │
        │                                     │
        │   Context from main.py:             │
        │   def main():                       │
        │       app = create_app()...         │
        │                                     │
        │   Context from auth.py:             │
        │   def authenticate(user):..."       │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2c: Generate Answer           │
        │  Prompt:                            │
        │  "Answer based on this context:     │
        │   [retrieved chunks]                │
        │                                     │
        │   Question: what does this do?      │
        │                                     │
        │   Provide detailed answer with      │
        │   specific examples from code."     │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2d: LLM Processing            │
        │  • Gemini reads context             │
        │  • Analyzes code snippets           │
        │  • Synthesizes answer               │
        │  • Cites specific files             │
        └─────────────────────────────────────┘
                Time: ~1-2 seconds
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 3: Format Response            │
        │  • Extract answer text              │
        │  • Get source file names            │
        │  • Add source citations             │
        └─────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────┐
│  Response                                            │
│  ────────                                            │
│  Answer: "This repository is a web application       │
│  that provides user authentication and data          │
│  management. The main entry point is in main.py      │
│  which creates the Flask app. Authentication is      │
│  handled via JWT tokens in auth.py..."              │
│                                                       │
│  📎 Sources: README.md, main.py, auth.py            │
└──────────────────────────────────────────────────────┘
                              │
                              ▼
                Total Time: ~2 seconds ⚡
```

---

### **Phase 5: Asking Questions (Full Agent Path)**

```
User: how does authentication work in the repo?
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Interactive Mode Router            │
        │  • Contains "repo" keyword          │
        │  → Route to: ask() (Full Agent)     │
        └─────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────┐
│  ask(query) → run(query)                             │
└──────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  STEP 1: PLANNING                   │
        │  _create_plan(query)                │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 1a: Check Active Session      │
        │  • qa_repo_url exists? ✓            │
        │  • Add context to prompt:           │
        │    "IMPORTANT: Active session:      │
        │     https://github.com/user/repo"   │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 1b: LLM Planning              │
        │  Prompt:                            │
        │  "Available tools:                  │
        │   1. Legal_Analyzer                 │
        │   2. Code_Auditor                   │
        │   3. QA_Tool                        │
        │                                     │
        │   Active session: <url>             │
        │   Query: how does auth work?        │
        │                                     │
        │   Which tools needed?"              │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 1c: Parse Plan                │
        │  {                                  │
        │    "tools_needed": ["QA_Tool"],     │
        │    "execution_order": ["QA_Tool"],  │
        │    "repo_url": "<active session>",  │
        │    "question": "how does auth..."   │
        │  }                                  │
        └─────────────────────────────────────┘
                Time: ~2-3 seconds
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  STEP 2: EXECUTION                  │
        │  _execute_plan(plan)                │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2a: Execute QA_Tool           │
        │  _run_qa_tool(repo_url, question)   │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2b: Check for Existing Session│
        │  • repo_url == qa_repo_url? ✓       │
        │  • qa_tool_instance exists? ✓       │
        │  → Use cached session! (No clone)   │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 2c: Ask Question              │
        │  • qa_tool.ask_question(q)          │
        │  • Same retrieval process as before │
        │  • Return answer with sources       │
        └─────────────────────────────────────┘
                Time: ~2 seconds
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  STEP 3: SYNTHESIS                  │
        │  _synthesize_answer(query, results) │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 3a: Build Synthesis Prompt    │
        │  "You executed these tools:         │
        │   QA_Tool: [answer about auth...]   │
        │                                     │
        │   User query: how does auth work?   │
        │                                     │
        │   Provide comprehensive answer."    │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Step 3b: Generate Final Answer     │
        │  • LLM formats the response         │
        │  • Adds structure and clarity       │
        │  • Returns polished answer          │
        └─────────────────────────────────────┘
                Time: ~1-2 seconds
                              │
                              ▼
                Total Time: ~5-7 seconds
```

---

## 🔍 Technical Deep Dive

### **1. Vector Embeddings**

```
Text Chunk: "def authenticate(user, password):"
                              │
                              ▼
        Google Embedding API (embedding-001)
                              │
                              ▼
Vector: [0.123, -0.456, 0.789, ..., 0.234]  (768 dimensions)
                              │
                              ▼
        Stored in FAISS index
```

**Purpose:** Convert text to numbers that capture semantic meaning.  
**Benefit:** "how to login" finds "authenticate" even without exact words.

### **2. Similarity Search**

```
Question: "how does authentication work?"
                              │
                              ▼
Question Embedding: [0.111, -0.333, 0.555, ...]
                              │
                              ▼
        Compare with ALL chunk embeddings
                              │
        Using cosine similarity:
        similarity = (query · chunk) / (||query|| * ||chunk||)
                              │
                              ▼
Top 5 Most Similar Chunks:
1. auth.py lines 45-90      (similarity: 0.89)
2. README.md lines 120-160  (similarity: 0.84)
3. middleware.py lines 20-50 (similarity: 0.78)
4. config.py lines 10-30    (similarity: 0.72)
5. docs/auth.md lines 5-40  (similarity: 0.69)
```

### **3. RAG Chain**

```
┌────────────────────────────────────────────┐
│  Question: "how does auth work?"           │
└────────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Retriever            │
        │  (FAISS search)       │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Context + Question   │
        │  (Prompt Template)    │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  LLM                  │
        │  (Gemini)             │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  String Parser        │
        │  (Clean output)       │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Answer               │
        └───────────────────────┘
```

---

## 📊 Performance Metrics

### **Setup Times**

| Operation | Time | Notes |
|-----------|------|-------|
| Clone repo | 5-10s | Depends on repo size |
| Load documents | 2-5s | ~150 files |
| Create chunks | 1-2s | ~500 chunks |
| Generate embeddings | 15-25s | API calls |
| Build FAISS index | 1-3s | In-memory |
| **Total Setup** | **25-45s** | One-time cost |

### **Query Times**

| Operation | Time | Notes |
|-----------|------|-------|
| Vector search | 0.5s | FAISS is fast |
| LLM inference | 1-2s | Gemini API |
| **Total Query** | **2-3s** | Per question |

### **Session Reuse Benefit**

```
Scenario: 5 questions about a repository

WITHOUT session reuse:
Question 1: 25s setup + 2s query = 27s
Question 2: 25s setup + 2s query = 27s
Question 3: 25s setup + 2s query = 27s
Question 4: 25s setup + 2s query = 27s
Question 5: 25s setup + 2s query = 27s
Total: 135 seconds

WITH session reuse:
Question 1: 25s setup + 2s query = 27s
Question 2: 0s setup  + 2s query = 2s   ⚡
Question 3: 0s setup  + 2s query = 2s   ⚡
Question 4: 0s setup  + 2s query = 2s   ⚡
Question 5: 0s setup  + 2s query = 2s   ⚡
Total: 35 seconds

Speedup: 3.86x faster! 🚀
```

---

## 🎯 Key Components

### **1. RepoQATool Class**

```python
class RepoQATool:
    def __init__(self, model_name):
        # Initialize embeddings and LLM
        self.embeddings = GoogleGenerativeAIEmbeddings(...)
        self.llm = ChatGoogleGenerativeAI(...)
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
    
    def index_repository(self, repo_path):
        # Load, split, embed, and index files
        # Returns: {'status': 'success', 'documents_count': 150}
    
    def ask_question(self, question):
        # Retrieve context and generate answer
        # Returns: {'status': 'success', 'answer': '...', 'sources': [...]}
```

### **2. GuardianAgentSimple Integration**

```python
class GuardianAgentSimple:
    def __init__(self):
        self.qa_tool_instance = None  # Cached QA tool
        self.qa_repo_url = None       # Active repo URL
        self.qa_temp_dir = None       # Temp directory
    
    def setup_qa_session(self, repo_url):
        # Clone, index, and cache QA tool
    
    def ask_qa(self, question):
        # Direct question to cached QA tool
    
    def _run_qa_tool(self, repo_url, question):
        # Check for existing session, reuse if possible
```

---

## 💡 Smart Features

### **1. Session Awareness**

The planner knows about active sessions:

```python
if self.qa_repo_url:
    qa_context = f"""
    IMPORTANT: Active QA session for {self.qa_repo_url}
    User questions about "the repo" refer to this URL.
    """
```

### **2. Automatic Session Reuse**

```python
if self.qa_tool_instance and self.qa_repo_url == repo_url:
    # Use existing session - no cloning!
    return self.qa_tool_instance.ask_question(question)
```

### **3. Intelligent Routing**

```python
# Fast path: Direct to QA if simple question
if qa_session_active and not has_url_or_pdf(query):
    return ask_qa(query)

# Full path: Use agent for complex tasks
else:
    return ask(query)
```

---

## 🎉 Summary

The QA Agent workflow combines:

1. **✅ Git Cloning** - Get the repository code
2. **✅ Document Loading** - Read all relevant files
3. **✅ Text Chunking** - Split into manageable pieces
4. **✅ Vector Embedding** - Convert to semantic vectors
5. **✅ FAISS Indexing** - Fast similarity search
6. **✅ Semantic Retrieval** - Find relevant context
7. **✅ LLM Generation** - Synthesize answers
8. **✅ Session Caching** - Reuse for speed

**Result:** Fast, accurate answers about any codebase with source citations! 🚀
