# 🛡️ Guardian AI - Complete Project Documentation

> **An Agentic AI System for Automated Code Compliance Auditing**

**Author:** Guardian AI Team  
**Version:** 1.0.0  
**Last Updated:** October 26, 2025  
**Branch:** Guardian-AI-V1

---

## 📋 Table of Contents

1. [Project Introduction](#-project-introduction)
2. [Architecture Overview](#-architecture-overview)
3. [How It Works](#-how-it-works)
4. [Technology Stack](#-technology-stack)
5. [Core Components](#-core-components)
6. [Agentic AI Implementation](#-agentic-ai-implementation)
7. [Frontend Features](#-frontend-features)
8. [Backend API](#-backend-api)
9. [Data Flow](#-data-flow)
10. [Use Cases](#-use-cases)
11. [Getting Started](#-getting-started)
12. [Advanced Features](#-advanced-features)

---

## 🎯 Project Introduction

**Guardian AI** is an intelligent compliance auditing system that uses **Agentic AI** to automatically analyze code repositories against regulatory documents (like ISO-27001, GDPR, PCI-DSS, etc.).

### **What Makes It Special?**

- 🤖 **Autonomous AI Agent** - Makes intelligent decisions about which tools to use
- 📄 **PDF Analysis** - Extracts compliance rules from regulatory documents using RAG
- 🔍 **Code Auditing** - Scans entire repositories line-by-line for violations
- 💬 **Conversational AI** - Ask questions about any codebase in natural language
- ⚡ **Real-time Updates** - See progress as files are being analyzed
- 💾 **Stateful UI** - Your work persists across page navigation and refreshes

### **Key Capabilities**

| Feature | Description |
|---------|-------------|
| **Compliance Scanning** | Automatically detect violations against regulatory standards |
| **Repository Q&A** | Ask questions about any GitHub repository |
| **Real-time Progress** | Live updates via Server-Sent Events (SSE) |
| **Multi-Model Support** | Works with Gemini 2.0 Flash, Pro, and other models |
| **Persistent State** | Work is saved across sessions and page refreshes |
| **Beautiful UI** | Modern, animated interface with dark/light mode |

---

## 🏗️ Architecture Overview

### **System Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                      GUARDIAN AI SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐         ┌──────────────────────────┐     │
│  │   Frontend    │         │       Backend API        │     │
│  │  (React App)  │◄───────►│     (FastAPI)            │     │
│  │               │   REST  │                          │     │
│  │  - Dashboard  │   API   │  ┌────────────────────┐  │     │
│  │  - Code Audit │         │  │  Guardian Agent    │  │     │
│  │  - Q&A Chat   │         │  │  (LangGraph ReAct) │  │     │
│  └───────────────┘         │  └─────────┬──────────┘  │     │
│                            │            │              │     │
│                            │  ┌─────────▼──────────┐  │     │
│                            │  │    AI Tools        │  │     │
│                            │  ├────────────────────┤  │     │
│                            │  │ 1. Legal Analyzer  │  │     │
│                            │  │ 2. Code Auditor    │  │     │
│                            │  │ 3. Q&A Tool        │  │     │
│                            │  └────────────────────┘  │     │
│                            └──────────────────────────┘     │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              External Services & Storage              │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │  - Google Gemini API (AI Models)                      │  │
│  │  - ChromaDB / FAISS (Vector Stores)                   │  │
│  │  - GitHub Repositories (Code Sources)                 │  │
│  │  - Local File System (PDF Storage)                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### **Technology Layers**

```
┌──────────────────────────────────────┐
│      Presentation Layer              │
│  React + TypeScript + Tailwind CSS   │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│      API Layer                       │
│  FastAPI + Uvicorn + SSE             │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│      AI Agent Layer                  │
│  LangGraph + LangChain               │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│      Tool Layer                      │
│  Legal Analyzer + Code Auditor + QA  │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│      Foundation Layer                │
│  Google Gemini + Vector Databases    │
└──────────────────────────────────────┘
```

---

## ⚙️ How It Works

### **High-Level Workflow**

```
1. USER UPLOADS PDF + ENTERS REPO URL
         ↓
2. GUARDIAN AGENT RECEIVES QUERY
         ↓
3. AGENT REASONS: "What tools do I need?"
         ↓
4. AGENT INVOKES TOOLS IN SEQUENCE:
   ├── Legal Analyzer → Extract compliance rules from PDF
   ├── Code Auditor   → Scan repository for violations
   └── Synthesize     → Combine results into report
         ↓
5. RETURN DETAILED VIOLATION REPORT TO USER
```

### **Detailed Example: ISO-27001 Compliance Audit**

**User Action:**
```
Upload: ISO-27001.pdf
Repo: https://github.com/company/banking-api
Click: "Start Audit"
```

**Step 1: Guardian Agent Activates**
```python
agent.run("Find ISO-27001 violations in banking-api repository")
```

**Step 2: Agent's Reasoning Process**
```
Agent Thinks:
  "I need to understand ISO-27001 requirements first,
   then analyze the code against those requirements."

Plan:
  1. Use Legal_Analyzer to extract compliance rules
  2. Use Code_Auditor to scan repository
  3. Match violations to specific ISO-27001 clauses
```

**Step 3: Legal Analyzer (RAG System)**
```python
# Indexes PDF into vector database
legal_tool.index_pdf("ISO-27001.pdf")

# Extracts technical requirements
rules = legal_tool.ask_question(
    "What are the security requirements for access control, 
     data encryption, and logging?"
)

# Returns structured compliance rules
{
  "access_control": "Multi-factor authentication required",
  "encryption": "AES-256 for data at rest, TLS 1.3 for transit",
  "logging": "All access attempts must be logged with timestamps"
}
```

**Step 4: Code Auditor (Line-by-Line Analysis)**
```python
# Clones repository
git.clone("https://github.com/company/banking-api")

# Analyzes each file
for file in repo.files:
    violations = code_auditor.analyze(file, compliance_rules)
    
# Example violation found:
{
  "file": "auth/login.py",
  "line": 45,
  "code": "if password == user.password:",
  "violation": "Plaintext password comparison detected",
  "rule": "ISO-27001 A.9.4.3 - Password Management System",
  "severity": "CRITICAL",
  "recommendation": "Use bcrypt.checkpw() for secure comparison"
}
```

**Step 5: Real-time Progress Updates (SSE)**
```javascript
// Frontend receives live updates via EventSource

Progress Update 1: "📄 Analyzing ISO-27001.pdf..."
Progress Update 2: "🔍 Cloning repository..."
Progress Update 3: "✓ auth/login.py - 2 violations found"
Progress Update 4: "✓ api/users.py - 0 violations"
Progress Update 5: "✓ config/settings.py - 1 violation found"
...
Progress Update N: "✅ Audit complete: 15 violations across 8 files"
```

**Step 6: Final Report**
```json
{
  "summary": {
    "total_violations": 15,
    "critical": 3,
    "high": 5,
    "medium": 7,
    "files_scanned": 42
  },
  "violations": [
    {
      "file": "auth/login.py",
      "line": 45,
      "code": "if password == user.password:",
      "explanation": "Plaintext password comparison violates ISO-27001 A.9.4.3",
      "severity": "CRITICAL",
      "fix": "Use bcrypt.hashpw()"
    }
  ]
}
```

---

## 🧰 Technology Stack

### **Frontend Technologies**

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.x | UI Framework - Component-based architecture |
| **TypeScript** | 5.x | Type safety and better developer experience |
| **Vite** | 5.x | Build tool - Fast HMR and optimized builds |
| **Tailwind CSS** | 3.x | Utility-first CSS framework |
| **Framer Motion** | 11.x | Smooth animations and transitions |
| **React Router** | 6.x | Client-side routing |
| **React Markdown** | 9.x | Render formatted AI responses |
| **React Syntax Highlighter** | 15.x | Beautiful code blocks |
| **Lucide React** | Latest | Modern icon library |

### **Backend Technologies**

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12+ | Programming language |
| **FastAPI** | 0.110+ | Modern async web framework |
| **Uvicorn** | 0.27+ | ASGI server for FastAPI |
| **LangChain** | 0.1+ | AI agent framework |
| **LangGraph** | 0.0.40+ | ReAct pattern implementation |
| **Google Gemini** | Latest | Large Language Model |
| **ChromaDB** | 0.4+ | Vector database for RAG |
| **FAISS** | 1.8+ | Fast similarity search |
| **GitPython** | 3.1+ | Git operations |
| **PyPDF2** | 3.0+ | PDF text extraction |
| **SSE-Starlette** | 2.0+ | Server-Sent Events |
| **python-dotenv** | 1.0+ | Environment variable management |

### **Development Tools**

- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Git** - Version control
- **VS Code** - IDE

---

## 🔧 Core Components

### **1. Guardian Agent (Orchestrator)**

**Location:** `Backend/guardian_agent.py`

**Purpose:** Central brain that coordinates all AI tools

**Key Features:**
- Uses **LangGraph's ReAct pattern** (Reasoning + Acting)
- Autonomously selects tools based on user query
- Maintains conversation context
- Chains multiple tools together

**Architecture:**
```python
class GuardianAgent:
    def __init__(self, model_name="gemini-2.0-flash-exp"):
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0
        )
        
        # Register AI tools
        self.tools = [
            legal_analyst_tool,    # PDF analysis
            code_auditor_tool,     # Code scanning
            qa_tool                # Repository Q&A
        ]
        
        # Create ReAct agent
        self.agent = create_react_agent(
            self.llm, 
            self.tools,
            state_modifier="You are Guardian AI, a compliance expert..."
        )
    
    def run(self, query: str):
        # Agent autonomously decides what to do
        response = self.agent.invoke({
            "messages": [HumanMessage(content=query)]
        })
        return response
```

**Agent Reasoning Example:**
```
User: "Check GDPR compliance in user-api repo"

🧠 Thought 1: "I need to verify GDPR compliance"
🔧 Action 1: Legal_Analyzer("gdpr-rules.pdf")
👁️ Observation: "User consent required, data deletion API needed"

🧠 Thought 2: "Now I'll check the code"
🔧 Action 2: Code_Auditor("user-api")
👁️ Observation: "Found 8 violations"

🧠 Thought 3: "I have all info needed"
✅ Final Answer: "Found 8 GDPR violations. Critical: No consent mechanism..."
```

---

### **2. Legal Analyzer Tool (RAG System)**

**Location:** `Backend/Guardian-Legal-analyzer-main/legal_tool.py`

**Purpose:** Extract compliance rules from regulatory PDFs using RAG (Retrieval-Augmented Generation)

**How It Works:**

**Step 1: PDF Ingestion & Indexing**
```python
def index_pdf(self, pdf_path: str):
    # 1. Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    # 2. Split into chunks (1000 chars, 200 overlap)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    # 3. Generate embeddings using Gemini
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001"
    )
    
    # 4. Store in ChromaDB vector database
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    print(f"✅ Indexed {len(chunks)} chunks from {pdf_path}")
```

**Step 2: Question Answering with Context**
```python
def ask_question(self, question: str):
    # 1. Find most relevant PDF chunks (semantic search)
    relevant_chunks = self.vectorstore.similarity_search(
        question, 
        k=5  # Get top 5 most relevant chunks
    )
    
    # 2. Build context from retrieved chunks
    context = "\n\n".join([
        chunk.page_content for chunk in relevant_chunks
    ])
    
    # 3. Ask LLM with retrieved context
    prompt = f"""
    Based on this regulatory document:
    
    {context}
    
    Answer: {question}
    
    Provide specific requirements with clause numbers.
    """
    
    answer = self.llm.invoke(prompt)
    return answer
```

**Example Usage:**
```python
# Index ISO-27001 PDF
legal_tool.index_pdf("ISO-27001.pdf")

# Ask specific question
answer = legal_tool.ask_question(
    "What are the password security requirements?"
)

# Returns detailed answer:
"""
ISO-27001 A.9.4.3 - Password Management System requires:

1. **Minimum Length:** 12 characters
2. **Complexity:** Mix of uppercase, lowercase, numbers, symbols
3. **History:** Prevent reuse of last 5 passwords
4. **Storage:** Encrypted using bcrypt or Argon2
5. **MFA:** Required for privileged accounts
"""
```

---

### **3. Code Auditor Tool (Compliance Scanner)**

**Location:** `Backend/Github_scanner/code_tool.py`

**Purpose:** Scan repositories line-by-line for compliance violations

**Architecture:**

**Step 1: Repository Cloning**
```python
def clone_repository(self, repo_url: str):
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    local_path = f"./repos/{repo_name}"
    
    # Clone using GitPython
    if os.path.exists(local_path):
        shutil.rmtree(local_path)
    
    git.Repo.clone_from(repo_url, local_path)
    return local_path
```

**Step 2: File Discovery**
```python
def _get_code_files(self, repo_path: str):
    code_extensions = {
        '.py', '.js', '.ts', '.java', '.cpp', '.c', 
        '.cs', '.go', '.rb', '.php', '.swift'
    }
    
    code_files = []
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden and vendor directories
        dirs[:] = [d for d in dirs if not d.startswith('.') 
                   and d not in ['node_modules', 'venv', 'vendor']]
        
        for file in files:
            if any(file.endswith(ext) for ext in code_extensions):
                code_files.append(os.path.join(root, file))
    
    return code_files
```

**Step 3: AI-Powered File Analysis**
```python
def _analyze_file(self, file_path: str, code: str, rules: str):
    prompt = f"""
    Analyze this code for compliance violations.
    
    📁 File: {file_path}
    
    📋 Code:
    ```
    {code}
    ```
    
    📜 Compliance Rules:
    {rules}
    
    For EACH violation found, provide:
    1. Exact line number
    2. Violating code snippet
    3. Which rule is violated
    4. Clear explanation
    5. Recommended fix
    
    Return as JSON array:
    [
      {{
        "line": 45,
        "code": "password == user.password",
        "rule_violated": "ISO-27001 A.9.4.3",
        "explanation": "...",
        "severity": "CRITICAL",
        "recommendation": "..."
      }}
    ]
    """
    
    response = self.llm.invoke(prompt)
    violations = json.loads(response)
    
    # Add file path to each violation
    for v in violations:
        v['file'] = file_path
        v['file_path'] = file_path
    
    return violations
```

**Step 4: Progressive Scanning with SSE**
```python
def scan_repository_with_progress(self, repo_url, rules, callback):
    # Clone repo
    callback({"stage": "clone", "message": "🔍 Cloning repository..."})
    repo_path = self.clone_repository(repo_url)
    
    # Get all code files
    code_files = self._get_code_files(repo_path)
    callback({
        "stage": "discovery",
        "message": f"📂 Found {len(code_files)} code files"
    })
    
    # Analyze each file
    all_violations = []
    for i, file_path in enumerate(code_files):
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        violations = self._analyze_file(file_path, code, rules)
        all_violations.extend(violations)
        
        # Send progress update
        callback({
            "stage": "file_analysis",
            "file": os.path.basename(file_path),
            "violations": len(violations),
            "progress": (i + 1) / len(code_files) * 100
        })
    
    return all_violations
```

**Example Output:**
```json
{
  "violations": [
    {
      "file": "api/authentication.py",
      "line": 67,
      "code": "secret_key = 'hardcoded_secret_123'",
      "rule_violated": "ISO-27001 A.9.4.1 - Information Access Restriction",
      "explanation": "Hardcoded secrets in source code can be extracted by anyone with repository access",
      "severity": "CRITICAL",
      "recommendation": "Store secrets in environment variables: secret_key = os.getenv('SECRET_KEY')"
    },
    {
      "file": "database/connection.py",
      "line": 23,
      "code": "conn = psycopg2.connect('postgresql://user:pass@localhost/db')",
      "rule_violated": "ISO-27001 A.9.4.3 - Password Management",
      "explanation": "Database credentials exposed in connection string",
      "severity": "HIGH",
      "recommendation": "Use environment variables for database credentials"
    }
  ]
}
```

---

### **4. Q&A Tool (Repository Assistant)**

**Location:** `Backend/Github_scanner/qa_tool.py`

**Purpose:** Answer questions about codebases using RAG

**Architecture:**

**Step 1: Repository Indexing**
```python
class RepoQATool:
    def __init__(self, model_name="gemini-2.0-flash-exp"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)
        self.embeddings = GoogleGenerativeAIEmbeddings()
        self.vectorstore = None
    
    def index_repository(self, repo_path: str):
        # 1. Read all code files
        code_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java')):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        code_files.append({
                            'path': file_path,
                            'content': f.read()
                        })
        
        # 2. Create documents with metadata
        documents = [
            Document(
                page_content=file['content'],
                metadata={
                    'file_path': file['path'],
                    'file_name': os.path.basename(file['path'])
                }
            )
            for file in code_files
        ]
        
        # 3. Create FAISS vector store
        self.vectorstore = FAISS.from_documents(
            documents,
            self.embeddings
        )
        
        print(f"✅ Indexed {len(documents)} files")
```

**Step 2: Conversational Q&A**
```python
    def ask_question(self, question: str):
        if not self.vectorstore:
            raise ValueError("Repository not indexed yet!")
        
        # 1. Retrieve relevant code snippets
        relevant_docs = self.vectorstore.similarity_search(
            question, 
            k=3  # Get top 3 most relevant files
        )
        
        # 2. Build context with file paths
        context = "\n\n".join([
            f"📁 File: {doc.metadata['file_path']}\n```\n{doc.page_content}\n```"
            for doc in relevant_docs
        ])
        
        # 3. Generate answer with LLM
        prompt = f"""
        You are a code assistant. Answer questions about this codebase.
        
        📚 Relevant Code:
        {context}
        
        ❓ Question: {question}
        
        Provide:
        - Clear explanation
        - Code examples from the codebase
        - File locations (line numbers if possible)
        - Recommendations if applicable
        """
        
        answer = self.llm.invoke(prompt)
        
        return {
            "answer": answer.content,
            "sources": [doc.metadata['file_path'] for doc in relevant_docs]
        }
```

**Example Interaction:**
```
User: "How does user authentication work in this project?"

AI Response:
"User authentication is implemented using JWT tokens:

🔑 **Login Flow** (auth/login.py, lines 23-45):
1. User sends credentials to /api/login
2. Password verified using bcrypt.checkpw()
3. JWT token generated with SECRET_KEY
4. Token expires in 24 hours

🛡️ **Protected Routes** (middleware/auth.py, lines 12-34):
- @require_auth decorator validates JWT
- Checks token expiration
- Extracts user_id from payload

📝 **Example Usage:**
```python
@app.post('/api/protected')
@require_auth
def protected_route(user_id: int):
    return f'User {user_id} accessed protected resource'
```

📂 **Key Files:**
- auth/login.py (authentication logic)
- middleware/auth.py (JWT verification)
- config/settings.py (SECRET_KEY configuration)
"
```

---

## 🤖 Agentic AI Implementation

### **What is Agentic AI?**

**Traditional AI Systems:**
```python
# Hardcoded workflow - no autonomy
if task == "audit":
    analyze_pdf()
    scan_code()
elif task == "qa":
    answer_question()
```

**Agentic AI:**
```python
# Agent decides autonomously
agent.run("User's natural language query")
# Agent figures out:
# - What tools to use
# - In what order
# - When to stop
```

### **The ReAct Pattern**

Guardian AI uses **LangGraph's ReAct** (Reasoning + Acting) pattern:

```
┌─────────────────────────────────────────┐
│         ReAct Loop (Iterative)          │
├─────────────────────────────────────────┤
│                                         │
│  1. 🧠 THOUGHT                          │
│     "What do I need to do?"             │
│           ↓                             │
│  2. 🔧 ACTION                           │
│     Pick a tool & execute               │
│           ↓                             │
│  3. 👁️ OBSERVATION                      │
│     Get tool's result                   │
│           ↓                             │
│  4. 🧠 THOUGHT                          │
│     "Do I have enough info?"            │
│     ├─ YES → ✅ Final Answer            │
│     └─ NO  → 🔄 Repeat (go to step 2)   │
│                                         │
└─────────────────────────────────────────┘
```

### **Real-World Example: PCI-DSS Audit**

**User Query:**
```
"Check if the FastAPI backend violates PCI-DSS payment security 
standards using pci-dss-v4.pdf"
```

**Agent's Autonomous Reasoning:**

```
═══════════════════════════════════════════
📍 ITERATION 1
═══════════════════════════════════════════

🧠 Thought:
   "I need to understand PCI-DSS requirements for payment systems.
    Let me analyze the PDF first."

🔧 Action: Legal_Analyzer
   Input: {
     "pdf_path": "pci-dss-v4.pdf",
     "question": "Security requirements for payment data handling?"
   }

👁️ Observation:
   "PCI-DSS Requirements:
    - Req 3: Protect stored cardholder data (encryption)
    - Req 4: Encrypt transmission of cardholder data
    - Req 8: Identify and authenticate access
    - Req 10: Log all access to payment data"

═══════════════════════════════════════════
📍 ITERATION 2
═══════════════════════════════════════════

🧠 Thought:
   "Now I have the PCI-DSS rules. Need to scan the backend
    to check compliance."

🔧 Action: Code_Auditor
   Input: {
     "repo_url": "https://github.com/user/fastapi-backend",
     "compliance_rules": "[Rules from Iteration 1]"
   }

👁️ Observation:
   "Scan Results:
    - 12 violations found across 6 files
    - CRITICAL: Plaintext credit card storage (models.py:45)
    - HIGH: No encryption on payment endpoints (api/payment.py:89)
    - MEDIUM: Missing access logs (middleware/auth.py:23)"

═══════════════════════════════════════════
📍 ITERATION 3 (Final)
═══════════════════════════════════════════

🧠 Thought:
   "I have all information needed for a comprehensive answer."

✅ Final Answer:
   "PCI-DSS Compliance Audit Results:
    
    ⚠️ 12 CRITICAL VIOLATIONS FOUND
    
    🔴 Critical Issues:
    1. Plaintext Card Storage (models.py:45)
       • Rule: PCI-DSS Requirement 3.4
       • Issue: Credit card numbers not encrypted
       • Fix: Use AES-256 encryption
    
    2. Unencrypted Payment API (api/payment.py:89)
       • Rule: PCI-DSS Requirement 4.1
       • Issue: Endpoints not using TLS 1.2+
       • Fix: Enforce HTTPS with TLS 1.3
    
    📊 Summary:
    • Files Scanned: 42
    • Violations: 12 (3 Critical, 5 High, 4 Medium)
    • Compliance Score: 68/100
    
    🔧 Recommended Actions:
    1. Encrypt all cardholder data at rest
    2. Enable TLS 1.3 on payment endpoints
    3. Implement audit logging
    4. Add MFA for admin access"
```

### **Why This is Powerful**

✅ **Flexibility** - Adapts to any query without hardcoded logic  
✅ **Intelligence** - Understands context and nuance  
✅ **Transparency** - You can see the agent's reasoning  
✅ **Accuracy** - Combines multiple tools for comprehensive answers  
✅ **Extensibility** - Easy to add new tools

---

## 🎨 Frontend Features

### **1. Stateful UI with React Context + localStorage**

**Problem:** User loses work when navigating between pages or refreshing

**Solution:** Global state management that persists

**Implementation:**

```typescript
// AppStateContext.tsx

interface AppState {
  codeAudit: {
    repoUrl: string;
    pdfFileName: string;
    results: AuditResults | null;
    progressUpdates: ProgressUpdate[];
  };
  qaChat: {
    repoUrl: string;
    sessionId: string;
    messages: ChatMessage[];
    isInitialized: boolean;
  };
}

export function AppStateProvider({ children }: { children: ReactNode }) {
  // Load from localStorage on mount
  const [state, setState] = useState<AppState>(() => {
    const saved = localStorage.getItem('guardian-ai-state');
    return saved ? JSON.parse(saved) : defaultState;
  });
  
  // Save to localStorage on every change
  useEffect(() => {
    localStorage.setItem('guardian-ai-state', JSON.stringify(state));
  }, [state]);
  
  return (
    <AppStateContext.Provider value={{ state, updateState }}>
      {children}
    </AppStateContext.Provider>
  );
}
```

**Result:**
- ✅ Data persists when navigating between pages
- ✅ Data persists after browser refresh
- ✅ Data persists when closing/reopening tabs

---

### **2. Real-Time Progress with Server-Sent Events**

**Backend (FastAPI):**
```python
@app.get("/api/audit/code/stream")
async def code_audit_stream(repo_url: str, pdf_path: str):
    async def event_generator():
        # Progress update 1
        yield {
            "event": "progress",
            "data": json.dumps({
                "message": "📄 Analyzing compliance document..."
            })
        }
        
        # Progress update 2
        yield {
            "event": "progress",
            "data": json.dumps({
                "message": "🔍 Cloning repository..."
            })
        }
        
        # File-by-file updates
        for file in code_files:
            violations = analyze(file)
            yield {
                "event": "progress",
                "data": json.dumps({
                    "file": file.name,
                    "violations": len(violations)
                })
            }
        
        # Final result
        yield {
            "event": "complete",
            "data": json.dumps(final_results)
        }
    
    return EventSourceResponse(event_generator())
```

**Frontend (React):**
```typescript
function CodeAudit() {
  const handleAudit = () => {
    const eventSource = new EventSource(
      `/api/audit/code/stream?repo_url=${repoUrl}&pdf_path=${pdfPath}`
    );
    
    eventSource.addEventListener('progress', (event) => {
      const data = JSON.parse(event.data);
      // Update UI in real-time!
      setProgress(prev => [...prev, data]);
    });
    
    eventSource.addEventListener('complete', (event) => {
      const results = JSON.parse(event.data);
      setResults(results);
      eventSource.close();
    });
  };
}
```

**User Sees:**
```
✓ Analyzing ISO-27001.pdf...
✓ Cloning repository...
✓ auth/login.py - 2 violations
✓ api/users.py - 0 violations
✓ database/models.py - 3 violations
✓ Audit complete: 15 violations found
```

---

### **3. Visual Enhancements**

**Animated Background:**
```typescript
<motion.div
  animate={{
    backgroundPosition: ['0% 0%', '100% 100%'],
  }}
  transition={{
    duration: 20,
    repeat: Infinity,
    repeatType: 'reverse',
  }}
  className="animated-gradient"
/>
```

**Floating Orbs:**
```typescript
<motion.div
  animate={{
    x: [0, 100, 0],
    y: [0, -100, 0],
    scale: [1, 1.2, 1],
  }}
  transition={{
    duration: 15,
    repeat: Infinity,
    ease: 'easeInOut',
  }}
  className="floating-orb"
  style={{
    background: 'radial-gradient(circle, rgba(102,126,234,0.4), transparent)',
    width: 400,
    height: 400,
    filter: 'blur(60px)',
  }}
/>
```

**Card Hover Effects:**
```typescript
<motion.div
  whileHover={{
    scale: 1.05,
    y: -8,
  }}
  className="feature-card"
>
  <motion.div whileHover={{ rotate: 360 }}>
    <Icon />
  </motion.div>
</motion.div>
```

---

### **4. Dark/Light Mode**

**Implementation:**
```typescript
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    // Check localStorage first, then system preference
    const saved = localStorage.getItem('theme');
    if (saved) return saved as 'light' | 'dark';
    
    return window.matchMedia('(prefers-color-scheme: dark)').matches 
      ? 'dark' 
      : 'light';
  });
  
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);
  
  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');
  
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

**Usage:**
```typescript
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  <h1 className="text-blue-600 dark:text-blue-400">Guardian AI</h1>
</div>
```

---

## 🔌 Backend API

### **API Endpoints**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API welcome message |
| `/health` | GET | Health check status |
| `/api/upload/pdf` | POST | Upload compliance PDF |
| `/api/audit/code` | POST | Run code audit (full response) |
| `/api/audit/code/stream` | GET | Run audit with SSE progress |
| `/api/qa/init` | POST | Initialize Q&A session |
| `/api/qa/ask` | POST | Ask question about repository |
| `/api/qa/history/{session_id}` | GET | Get chat history |
| `/api/qa/session/{session_id}` | DELETE | Delete Q&A session |
| `/api/agent/query` | POST | Query Guardian Agent directly |

### **Example: Code Audit Stream**

**Request:**
```http
GET /api/audit/code/stream?repo_url=https://github.com/user/repo&pdf_path=uploads/iso27001.pdf
Accept: text/event-stream
```

**Response (SSE Stream):**
```
event: progress
data: {"stage":"pdf_analysis","message":"📄 Analyzing ISO-27001.pdf..."}

event: progress
data: {"stage":"repo_clone","message":"🔍 Cloning repository..."}

event: progress
data: {"stage":"file_analysis","file":"auth/login.py","violations":2}

event: progress
data: {"stage":"file_analysis","file":"api/users.py","violations":0}

event: complete
data: {"total_violations":15,"violations":[...]}
```

### **Example: Q&A Session**

**Initialize:**
```http
POST /api/qa/init
Content-Type: application/json

{
  "repo_url": "https://github.com/langchain-ai/langchain"
}
```

**Response:**
```json
{
  "session_id": "qa_20251026_123456",
  "status": "initialized",
  "message": "Repository indexed. You can now ask questions."
}
```

**Ask Question:**
```http
POST /api/qa/ask
Content-Type: application/json

{
  "session_id": "qa_20251026_123456",
  "question": "How does chain-of-thought prompting work?"
}
```

**Response:**
```json
{
  "answer": "Chain-of-thought prompting works by...\n\n**Implementation:**\n```python\nclass Chain:\n  def invoke(self, input):\n    ...\n```",
  "sources": ["chains/base.py", "prompts/cot.py"]
}
```

---

## 📊 Data Flow

### **Complete Request-Response Cycle**

```
USER
  │
  │ 1. Upload PDF + Enter Repo URL
  │    Click "Start Audit"
  ▼
FRONTEND (React)
  │
  │ 2. Collect form data
  │ 3. Upload PDF: POST /api/upload
  │ 4. Start SSE: GET /api/audit/code/stream
  ▼
BACKEND (FastAPI)
  │
  │ 5. Receive request
  │ 6. Create event generator
  │ 7. Invoke Guardian Agent
  ▼
GUARDIAN AGENT
  │
  │ 8. Reason about query
  │ 9. Decide: Use Legal_Analyzer first
  ▼
LEGAL ANALYZER (Tool 1)
  │
  │ 10. Index PDF → ChromaDB
  │ 11. Extract compliance rules
  │ 12. Return technical brief
  ▼
GUARDIAN AGENT
  │
  │ 13. Receive rules
  │ 14. Decide: Use Code_Auditor next
  ▼
CODE AUDITOR (Tool 2)
  │
  │ 15. Clone repository
  │ 16. Discover code files
  │ 17. Analyze file-by-file
  │ 18. Emit SSE progress events
  │ 19. Return violations list
  ▼
GUARDIAN AGENT
  │
  │ 20. Synthesize final report
  │ 21. Return to API
  ▼
BACKEND (FastAPI)
  │
  │ 22. Format JSON response
  │ 23. Emit SSE 'complete' event
  ▼
FRONTEND (React)
  │
  │ 24. Receive final data
  │ 25. Update UI components
  │ 26. Save to AppStateContext
  │ 27. Persist to localStorage
  ▼
USER
  │
  │ 28. View detailed results
  │ 29. Export JSON report
  │ 30. Navigate to other pages (data persists!)
  ▼
DONE ✅
```

---

## 💼 Use Cases

### **1. Enterprise Security Compliance**

**Scenario:** Fintech company ensuring PCI-DSS compliance

**Workflow:**
1. Upload `pci-dss-v4.pdf`
2. Enter repo: `https://github.com/company/banking-api`
3. Receive report with violations:
   - 🔴 Plaintext credit card storage
   - 🔴 No encryption on payment endpoints
   - 🟡 Missing access logs
4. Export report for audit
5. Fix violations
6. Re-scan to verify

**Value:** Weeks of manual review → Minutes of automated analysis

---

### **2. Open Source PR Verification**

**Scenario:** Maintainer checking PR for security issues

**Workflow:**
1. Upload project security guidelines PDF
2. Enter PR branch URL
3. Identify violations:
   - SQL injection risks
   - Hardcoded API keys
   - Missing input validation
4. Comment on PR with findings
5. Contributor fixes issues
6. Re-scan shows ✅ All clear

**Value:** Automated quality gates for contributions

---

### **3. Developer Onboarding**

**Scenario:** New team member learning codebase

**Workflow:**
1. Use Q&A Chat feature
2. Ask questions:
   - "How does authentication work?"
   - "Where is the database schema?"
   - "How to add a new API endpoint?"
3. Get detailed answers with code examples and file locations

**Value:** Weeks → Days for onboarding

---

### **4. Continuous Compliance**

**Scenario:** Healthcare company maintaining HIPAA compliance

**Workflow:**
1. Schedule weekly automated scans
2. Track compliance score over time
3. Alert on new violations
4. Generate audit trail reports

**Value:** Continuous monitoring with audit history

---

## 🚀 Getting Started

### **Prerequisites**

- **Python 3.12+**
- **Node.js 20+**
- **Git**
- **Google Gemini API Key**

### **Backend Setup**

```bash
# Navigate to project root
cd version-3

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r Backend/requirements.txt

# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > Backend/.env

# Run backend
python Backend/api.py
```

Backend runs on: **http://localhost:8000**  
API Docs: **http://localhost:8000/docs**

### **Frontend Setup**

```bash
# Navigate to Frontend
cd Frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs on: **http://localhost:5173**

### **Verify Installation**

1. Open http://localhost:5173
2. Upload a PDF (any regulatory document)
3. Enter a GitHub repository URL
4. Click "Start Audit"
5. Watch real-time progress!

---

## 🚀 Advanced Features

### **1. Custom Compliance Rules**

Define rules without PDFs:

```yaml
# custom-rules.yaml
rules:
  - name: "No hardcoded secrets"
    pattern: "(api_key|password|secret)\\s*=\\s*['\"]"
    severity: CRITICAL
  
  - name: "SQL injection risk"
    pattern: "execute\\(.*\\+.*\\)"
    severity: HIGH
```

### **2. Batch Repository Scanning**

Scan multiple repos at once:

```python
@app.post("/api/batch-audit")
async def batch_audit(repos: List[str], pdf_path: str):
    results = []
    for repo in repos:
        result = await scan_repository(repo, pdf_path)
        results.append(result)
    return {"total_repos": len(repos), "results": results}
```

### **3. AI-Powered Fix Generation**

Generate code patches:

```python
def generate_fix(violation: dict):
    prompt = f"""
    Generate a fix for this violation:
    
    File: {violation['file']}
    Line: {violation['line']}
    Code: {violation['code']}
    Issue: {violation['explanation']}
    
    Provide:
    1. Fixed code
    2. Explanation
    3. Git diff format
    """
    return llm.invoke(prompt)
```

### **4. Compliance Score Tracking**

Track compliance over time with a database:

```sql
CREATE TABLE audit_history (
  id INTEGER PRIMARY KEY,
  repo_url TEXT,
  timestamp DATETIME,
  violations INTEGER,
  compliance_score FLOAT
);
```

### **5. CI/CD Integration**

GitHub Actions workflow:

```yaml
name: Guardian AI Check

on: pull_request

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Guardian AI
        run: |
          curl -X POST $GUARDIAN_API/audit \
            -d '{"repo_url": "${{ github.repository }}"}'
```

---

## 🎓 Key Takeaways

### **What Makes Guardian AI Unique**

1. **Truly Agentic** - Agent makes autonomous decisions, not following hardcoded paths
2. **Multi-Tool Orchestration** - Seamlessly combines Legal Analysis + Code Scanning + Q&A
3. **Real-time Feedback** - Users see progress as it happens via SSE
4. **Persistent State** - Work is never lost, even after browser refresh
5. **Beautiful UX** - Modern, animated interface with dark mode
6. **Extensible** - Easy to add new tools, compliance standards, or features

### **Technical Highlights**

- **LangGraph ReAct Pattern** - Autonomous agent reasoning
- **RAG (Retrieval-Augmented Generation)** - Context-aware PDF analysis
- **SSE (Server-Sent Events)** - Real-time progress streaming
- **React Context + localStorage** - Persistent global state
- **Framer Motion** - Smooth, professional animations
- **FastAPI** - High-performance async API
- **TypeScript** - Type-safe frontend development

### **Business Value**

- ⏱️ **Time Savings:** Weeks → Minutes for compliance audits
- 🎯 **Accuracy:** AI-powered detection of subtle violations
- 📈 **Scalability:** Scan unlimited repositories
- 🔄 **Continuous:** Integrate into CI/CD pipelines
- 📊 **Audit Trail:** Complete history of scans and findings

---

## 📞 Support & Resources

### **Documentation**
- **LangChain:** https://python.langchain.com/docs/
- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **FastAPI:** https://fastapi.tiangolo.com/
- **React:** https://react.dev/

### **Repository**
- **GitHub:** https://github.com/KarthikSagarP/GuardianAI
- **Branch:** Guardian-AI-V1

### **API Keys**
- **Google Gemini:** https://ai.google.dev/

---

## 📄 License

This project is part of Guardian AI - An AI-powered compliance auditing platform.

---

**Last Updated:** October 26, 2025  
**Version:** 1.0.0  
**Maintained by:** Guardian AI Team
