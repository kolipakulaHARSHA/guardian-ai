# Guardian AI - Data Flow Architecture

## 📋 Overview

Guardian AI is a **three-module AI compliance system** that checks code repositories against regulatory documents. The system follows an **orchestration pattern** where a central coordinator (Member A) delegates specialized tasks to two expert modules (Members B and C).

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                 │
│   "Check this GitHub repo against this PDF regulation"              │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  MODULE A: GuardianAI-Orchestrator (Chief Conductor)                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Files: main.py, contracts.py                                       │
│  Role: Coordinates the entire workflow                              │
└─────────┬───────────────────────────────────────┬───────────────────┘
          │                                       │
          │ STEP 1: Request Technical Brief      │ STEP 2: Send Brief + Repo URL
          │                                       │
          ▼                                       ▼
┌──────────────────────────────┐    ┌──────────────────────────────────┐
│ MODULE B: Legal Analyzer     │    │ MODULE C: Code Scanner           │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━ │    │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Guardian-Legal-analyzer-main │    │ Github_scanner                   │
│ Files: legal_tool.py         │    │ Files: code_tool.py, qa_tool.py  │
│ Role: Regulatory Expert      │    │ Role: Code Analysis Expert       │
└──────────────────────────────┘    └──────────────────────────────────┘
          │                                       │
          │ Returns: Plain-English Brief         │ Returns: JSON Violations List
          │                                       │
          ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FINAL COMPLIANCE REPORT                           │
│  {                                                                   │
│    "violations": [                                                   │
│      {                                                               │
│        "file": "auth.py",                                           │
│        "line": 45,                                                  │
│        "violating_code": "password = request.form['password']",     │
│        "explanation": "No password strength validation",            │
│        "rule_violated": "Password fields must be validated"         │
│      }                                                               │
│    ]                                                                 │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Detailed Data Flow

### Phase 1: Initialization

```
User provides:
├─ regulation_pdf: "path/to/gdpr_compliance.pdf"
└─ repository_url: "https://github.com/user/project"
```

---

### Phase 2: Legal Analysis (Module B)

**INPUT to Module B:**
- `pdf_file_path`: Path to regulatory PDF
- `question`: "Create a technical brief listing compliance requirements"

**PROCESS in Module B:**

```python
1. Load PDF
   └─ PyPDFLoader reads: "gdpr_compliance.pdf"
   
2. Split into Chunks
   └─ RecursiveCharacterTextSplitter
      ├─ Chunk size: 1000 characters
      ├─ Overlap: 200 characters
      └─ Creates ~50 chunks from document
   
3. Create Embeddings
   └─ GoogleGenerativeAIEmbeddings
      └─ Converts each chunk → vector representation
   
4. Store in Vector Database
   └─ ChromaDB (./chroma_db/)
      ├─ Persistent storage
      ├─ Deduplication (hash-based IDs)
      └─ Can accumulate multiple PDFs
   
5. RAG Query
   └─ ChatGoogleGenerativeAI (Gemini Pro)
      ├─ Retrieves: Top 5 relevant chunks
      ├─ Context window: Regulatory excerpts
      └─ Generates: Plain-English technical brief
```

**OUTPUT from Module B:**

```
Technical Brief (String):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- All image elements must have valid alt attributes
- User data must be encrypted during transmission  
- Password fields must implement minimum strength requirements
- CSRF tokens must be present in all forms
- API endpoints must implement rate limiting
- User consent must be obtained before data collection
- Personal data must be deletable upon request
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Phase 3: Code Auditing (Module C)

**INPUT to Module C:**
- `repo_url`: "https://github.com/user/project"
- `technical_brief`: The plain-English rules from Module B

**PROCESS in Module C:**

```python
1. Clone Repository
   └─ GitPython
      ├─ Creates temp directory: /tmp/guardian_audit_xyz/
      ├─ Clones: https://github.com/user/project
      └─ Downloads entire codebase locally
   
2. File Iteration & Filtering
   └─ os.walk() through all files
      ├─ INCLUDE: .py, .js, .html, .java, .ts, .tsx, etc.
      ├─ EXCLUDE: .jpg, .png, .zip, .exe, etc.
      └─ SKIP DIRS: node_modules, venv, .git, __pycache__
   
3. Chunk-by-Chunk Analysis
   For each relevant file:
   ├─ Read file content
   ├─ Split into chunks (20-40 lines each)
   └─ For each chunk:
      │
      ├─ Build Analysis Prompt:
      │  ┌──────────────────────────────────────────┐
      │  │ You are an expert code auditor.          │
      │  │                                          │
      │  │ TECHNICAL BRIEF:                         │
      │  │ [Paste full brief from Module B]        │
      │  │                                          │
      │  │ CODE SNIPPET (file.js, lines 20-50):   │
      │  │ ```javascript                            │
      │  │ const password = req.body.password;      │
      │  │ user.save();                             │
      │  │ ```                                      │
      │  │                                          │
      │  │ Find violations. Return JSON:            │
      │  │ [{"violating_code": "...",              │
      │  │   "explanation": "...",                  │
      │  │   "rule_violated": "..."}]               │
      │  └──────────────────────────────────────────┘
      │
      ├─ Send to LLM (Gemini Flash)
      ├─ Parse JSON response
      └─ If violations found → Add to master list
   
4. Compile Results
   └─ Aggregate all violations from all files
   
5. Cleanup
   └─ Delete temporary directory
```

**OUTPUT from Module C:**

```json
[
  {
    "file": "backend/auth.py",
    "line": 45,
    "violating_code": "password = request.form['password']",
    "explanation": "No password strength validation implemented before saving",
    "rule_violated": "Password fields must implement minimum strength requirements"
  },
  {
    "file": "frontend/components/ImageGallery.js",
    "line": 15,
    "violating_code": "<img src='/logo.png' />",
    "explanation": "Image element missing alt attribute for accessibility",
    "rule_violated": "All image elements must have valid alt attributes"
  },
  {
    "file": "backend/api/routes.py",
    "line": 23,
    "violating_code": "@app.route('/api/user', methods=['POST'])",
    "explanation": "No rate limiting detected on this API endpoint",
    "rule_violated": "API endpoints must implement rate limiting"
  }
]
```

---

### Phase 4: Report Assembly (Module A)

**PROCESS in Module A:**

```python
1. Receive violations JSON from Module C
2. Parse JSON string → Python dict
3. Format as final report
4. Return to user
```

**FINAL OUTPUT:**

```json
{
  "status": "success",
  "repository": "https://github.com/user/project",
  "regulation": "gdpr_compliance.pdf",
  "total_violations": 3,
  "violations": [
    {
      "file": "backend/auth.py",
      "line": 45,
      "violating_code": "password = request.form['password']",
      "explanation": "No password strength validation implemented",
      "rule_violated": "Password fields must implement minimum strength requirements"
    },
    {
      "file": "frontend/components/ImageGallery.js",
      "line": 15,
      "violating_code": "<img src='/logo.png' />",
      "explanation": "Image element missing alt attribute",
      "rule_violated": "All image elements must have valid alt attributes"
    },
    {
      "file": "backend/api/routes.py",
      "line": 23,
      "violating_code": "@app.route('/api/user', methods=['POST'])",
      "explanation": "No rate limiting detected",
      "rule_violated": "API endpoints must implement rate limiting"
    }
  ]
}
```

---

## 📊 Data Types & Contracts

### The Contract Interface (`contracts.py`)

```python
# Module B Contract
def legal_analyst_tool(pdf_file_path: str, question: str) -> str:
    """
    INPUT:
      - pdf_file_path: Path to regulatory PDF
      - question: Query about compliance requirements
    
    OUTPUT:
      - Plain-English technical brief (string)
    """
    pass

# Module C Contract
def code_auditor_agent(repo_url: str, technical_brief: str) -> str:
    """
    INPUT:
      - repo_url: GitHub repository URL
      - technical_brief: Plain-English rules from Module B
    
    OUTPUT:
      - JSON string containing list of violations
    """
    pass
```

---

## 🔍 Key Data Transformations

### Transformation 1: PDF → Technical Brief (Module B)

```
INPUT:  Complex 50-page PDF with legal jargon
        ↓
PROCESS: RAG extracts relevant passages + LLM summarizes
        ↓
OUTPUT: 7 bullet points in plain English
```

**Example:**

```
PDF (Legal Text):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"Article 32(1)(a) of the GDPR mandates that controllers and processors 
implement appropriate technical and organizational measures to ensure a 
level of security appropriate to the risk, including inter alia as 
appropriate: the pseudonymisation and encryption of personal data..."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        ↓ RAG + LLM ↓

Technical Brief (Developer-Friendly):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- User data must be encrypted during transmission
- Personal data must be encrypted at rest
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Transformation 2: Code + Brief → Violations (Module C)

```
INPUT:  Code chunk + Technical brief
        ↓
PROCESS: LLM analyzes code against each rule
        ↓
OUTPUT: Structured JSON with violations
```

**Example:**

```python
Code Chunk:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')  # Line 45
    user = User.objects.get(username=username)
    user.password = password
    user.save()
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

+

Technical Brief:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Password fields must implement minimum strength requirements
- User data must be encrypted during transmission
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        ↓ LLM Analysis ↓

Violation JSON:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{
  "file": "backend/auth.py",
  "line": 45,
  "violating_code": "password = request.POST.get('password')",
  "explanation": "Password is stored without strength validation",
  "rule_violated": "Password fields must implement minimum strength requirements"
}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🛠️ Technology Stack per Module

### Module A: Orchestrator
```
├─ langchain (agent framework)
├─ langchain_google_genai (LLM interface)
└─ contracts.py (module interface definitions)
```

### Module B: Legal Analyzer
```
├─ PyPDFLoader (PDF parsing)
├─ RecursiveCharacterTextSplitter (text chunking)
├─ GoogleGenerativeAIEmbeddings (vector embeddings)
├─ ChromaDB (vector database - persistent)
├─ ChatGoogleGenerativeAI (Gemini Pro - RAG queries)
└─ hashlib (content deduplication)
```

### Module C: Code Scanner
```
├─ GitPython (repository cloning)
├─ ChatGoogleGenerativeAI (Gemini Flash - code analysis)
├─ tempfile (temporary storage)
├─ os, pathlib (file system navigation)
└─ json (violation formatting)
```

---

## 🔐 Current Implementation State

### ✅ Fully Implemented (Optimized Branch)

**Module C (Github_scanner):**
- ✅ `code_tool.py` - Dual-mode tool (audit + compliance)
  - Audit mode: Line-by-line violation detection
  - Compliance mode: RAG-based compliance checking
  - Model: `gemini-2.5-pro-preview-03-25` for compliance
  - Model: `gemini-2.5-flash` for audit
- ✅ `qa_tool.py` - Repository Q&A tool
  - Interactive mode
  - Multi-question support
  - Model: `gemini-2.5-pro-preview-03-25`

**Module B (Guardian-Legal-analyzer-main):**
- ✅ `legal_tool.py` - RAG-based PDF analyzer
  - ChromaDB integration
  - Multi-PDF support
  - Deduplication
  - Model: `gemini-pro`

**Module A (GuardianAI-Orchestrator):**
- ✅ `main.py` - Simple orchestration
- ✅ `contracts.py` - Interface definitions
- ⚠️ Uses mock implementations (for testing)

---

## 📈 Execution Flow Timeline

```
Time    Module    Action                              Data Passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
T+0s    A         Receives user request              PDF path + Repo URL
T+1s    A→B       Calls legal_analyst_tool()         PDF path + Question
T+2s    B         Loads PDF into ChromaDB            PDF chunks → Vectors
T+10s   B         RAG query for technical brief      Query → Relevant chunks
T+15s   B→A       Returns technical brief            Plain-English string
T+16s   A→C       Calls code_auditor_agent()         Repo URL + Brief
T+17s   C         Clones repository                  GitHub → Local temp
T+20s   C         Iterates through files             File paths
T+25s   C         Analyzes code chunks               Code + Brief → LLM
T+45s   C         Compiles violations                Individual violations
T+46s   C→A       Returns violations JSON            JSON string
T+47s   A         Formats final report               Parsed JSON dict
T+48s   User      Receives compliance report         Complete report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔄 Sequence Diagram

```
┌──────┐          ┌────────────┐          ┌───────────┐          ┌──────────┐
│ User │          │  Module A  │          │  Module B │          │ Module C │
│      │          │Orchestrator│          │  Legal    │          │   Code   │
└──┬───┘          └─────┬──────┘          └─────┬─────┘          └────┬─────┘
   │                    │                       │                     │
   │ Request Audit      │                       │                     │
   │─────────────────>│                       │                     │
   │                    │                       │                     │
   │                    │ Get Technical Brief   │                     │
   │                    │──────────────────────>│                     │
   │                    │                       │                     │
   │                    │                       │ Load PDF            │
   │                    │                       │──┐                  │
   │                    │                       │  │ Split chunks     │
   │                    │                       │  │ Create embeddings│
   │                    │                       │  │ Store in ChromaDB│
   │                    │                       │  │ RAG query        │
   │                    │                       │<─┘                  │
   │                    │                       │                     │
   │                    │   Technical Brief     │                     │
   │                    │<──────────────────────│                     │
   │                    │                       │                     │
   │                    │ Audit Code            │                     │
   │                    │─────────────────────────────────────────────>│
   │                    │                       │                     │
   │                    │                       │                     │ Clone repo
   │                    │                       │                     │──┐
   │                    │                       │                     │  │ Filter files
   │                    │                       │                     │  │ Read code
   │                    │                       │                     │  │ Analyze chunks
   │                    │                       │                     │  │ with LLM
   │                    │                       │                     │  │ Collect violations
   │                    │                       │                     │<─┘
   │                    │                       │                     │
   │                    │   Violations JSON     │                     │
   │                    │<─────────────────────────────────────────────│
   │                    │                       │                     │
   │                    │ Format Report         │                     │
   │                    │──┐                    │                     │
   │                    │  │                    │                     │
   │                    │<─┘                    │                     │
   │                    │                       │                     │
   │  Compliance Report │                       │                     │
   │<───────────────────│                       │                     │
   │                    │                       │                     │
```

---

## 💡 Key Design Patterns

### 1. **Separation of Concerns**
- Each module has a single, well-defined responsibility
- Module B: Legal expertise (understands regulations)
- Module C: Technical expertise (understands code)
- Module A: Coordination (manages workflow)

### 2. **Contract-Based Integration**
- `contracts.py` defines clear interfaces
- Modules communicate through function contracts
- Enables independent development and testing

### 3. **RAG (Retrieval Augmented Generation)**
- Module B uses RAG to ground answers in actual PDF content
- Prevents hallucinations about regulations
- Enables multi-document knowledge base

### 4. **Agent-Based Code Analysis**
- Module C uses LLM as "intelligent agent"
- Goes beyond regex pattern matching
- Understands context and intent of code

### 5. **Temporary Storage Pattern**
- Module C clones repos to temp directories
- Ensures cleanup (try/finally blocks)
- Prevents disk space issues

---

## 🎯 Current Status Summary

| Module | Status | Model Used | Primary Function |
|--------|--------|-----------|------------------|
| **A: Orchestrator** | ✅ Mock | gemini-pro | Workflow coordination |
| **B: Legal Analyzer** | ✅ Production | gemini-pro | PDF → Technical Brief |
| **C: Code Scanner** | ✅ Production | gemini-2.5-pro-preview-03-25 (compliance)<br>gemini-2.5-flash (audit) | Code → Violations |

---

## 🚀 How to Use the System

### Standalone Module C (Current Best Practice)

```bash
# Compliance mode (uses Module C directly)
python code_tool.py compliance https://github.com/user/repo \
  --guideline "Must have LICENSE file" \
  --guideline "Must encrypt user data"

# Audit mode (uses Module C directly)
python code_tool.py audit https://github.com/user/repo \
  --brief "All functions need docstrings"

# Q&A mode (uses qa_tool.py)
python qa_tool.py https://github.com/user/repo --interactive
```

### Full System (A → B → C)

```python
# Using Module A orchestrator (with real B & C)
from main import run_compliance_audit

report = run_compliance_audit(
    regulation_pdf="path/to/gdpr.pdf",
    repository_url="https://github.com/user/repo"
)
```

---

## 📝 Conclusion

The Guardian AI system implements a **three-tier architecture** where:

1. **Module A** acts as the **brain** (orchestration)
2. **Module B** acts as the **legal counsel** (regulation interpretation)
3. **Module C** acts as the **code auditor** (violation detection)

Data flows sequentially from PDF regulations → Technical brief → Code analysis → Violations report, with each module transforming the data into the format needed by the next stage.

The system is currently **production-ready** for standalone use (Modules B and C work independently), with Module A providing optional orchestration capabilities.
