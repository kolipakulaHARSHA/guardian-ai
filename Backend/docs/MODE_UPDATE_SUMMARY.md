# ✅ Guardian AI Agent - Mode Awareness Update

## What Was Updated

I've updated the Guardian AI agent to be **fully aware** of all tool modes! 🎉

---

## 🛠️ **The Three Tools & Their Modes**

### 1. **Legal Analyzer** 📄
- **Mode**: Single mode (PDF analysis)
- **Purpose**: Extract compliance requirements from regulatory PDFs

### 2. **Code Auditor** 🔍 
**NOW SUPPORTS TWO MODES:**

#### **AUDIT Mode** (Line-by-Line Scanning)
- **When**: Agent wants to find specific violations
- **Method**: Exhaustive scanning of every code line
- **Output**: Violations with exact file paths and line numbers
- **Model**: `gemini-2.5-flash` (fast)
- **Example**: "Find all hardcoded credentials"

#### **COMPLIANCE Mode** (RAG-Based Semantic Search) ✨ NEW!
- **When**: Agent wants to check overall compliance
- **Method**: Semantic search using vector database
- **Output**: Assessment with evidence snippets
- **Model**: `gemini-2.5-pro-preview-03-25` (intelligent)
- **Example**: "Does this repo follow OWASP guidelines?"

### 3. **QA Tool** 💬
- **Mode**: Single mode (Question-Answering)
- **Purpose**: Answer questions about code using RAG

---

## 🧠 **How the Agent Chooses**

The agent's AI brain now automatically decides:
1. **Which tool to use** (Legal, Code, QA)
2. **Which mode to use** (for Code Auditor: AUDIT vs COMPLIANCE)
3. **What order to execute**

### Example Queries & Automatic Mode Selection

| Your Query | Agent Chooses | Why |
|------------|---------------|-----|
| "Find violations in repo X" | Code Auditor → **AUDIT** | Looking for specific violations |
| "Does repo X comply with GDPR?" | Code Auditor → **COMPLIANCE** | Checking overall compliance |
| "Check repo X against sample.pdf" | Legal → Code (**AUDIT**) | Get rules, then find violations |
| "What does repo X do?" | **QA Tool** | Asking a question |

---

## 📝 **What Changed in the Code**

### 1. **Updated `_run_code_auditor()` Method**
```python
def _run_code_auditor(self, repo_url: str, brief: str, mode: str = "audit"):
    """
    Now supports TWO modes:
    - mode="audit": Exhaustive line-by-line scanning
    - mode="compliance": RAG-based semantic checking
    """
```

**AUDIT Mode** (default):
- Uses `CodeAuditorAgent.scan_repository()`
- Returns specific violations with line numbers

**COMPLIANCE Mode** (new):
- Uses `ComplianceChecker.check_compliance()`
- Returns overall compliance assessment

### 2. **Updated Planning Prompt**
Now tells the AI brain about both modes:
```
Available tools:
1. Legal_Analyzer: Analyzes PDF documents
2. Code_Auditor: Scans code repositories
   - AUDIT mode: Exhaustive line-by-line scanning
   - COMPLIANCE mode: RAG-based semantic search
3. QA_Tool: Answers questions about code
```

### 3. **Updated Execution Logic**
```python
mode = plan.get("audit_mode", "audit")  # Get mode from plan
result = self._run_code_auditor(repo_url, brief, mode)
```

---

## 🎯 **Usage Examples**

### Example 1: Find Specific Violations (AUDIT Mode)
```bash
python guardian_agent_simple.py "Find security violations in https://github.com/Aadisheshudupa/3DTinKer against GuardianAI-Orchestrator/sample_regulation.pdf"
```

**Agent Decision**:
- Tools: Legal_Analyzer → Code_Auditor
- Mode: **AUDIT** (because looking for violations)
- Result: Specific violations with line numbers

---

### Example 2: Check Overall Compliance (COMPLIANCE Mode)
```bash
python guardian_agent_simple.py "Does https://github.com/Aadisheshudupa/3DTinKer comply with data protection guidelines?"
```

**Agent Decision**:
- Tools: Code_Auditor only
- Mode: **COMPLIANCE** (because checking compliance status)
- Result: Overall assessment with evidence

---

### Example 3: Answer Questions (QA Mode)
```bash
python guardian_agent_simple.py "What does https://github.com/Aadisheshudupa/3DTinKer do?"
```

**Agent Decision**:
- Tools: QA_Tool
- Result: Description of repository functionality

---

## 🔍 **How to Tell Which Mode Was Used**

Look at the output:

**AUDIT Mode Output**:
```
Audit Results (Line-by-line):
- Repository: https://github.com/...
- Violations found: 12

Top violations:
1. src/App.jsx (line 45)
   Missing alt attribute on <img> element
```

**COMPLIANCE Mode Output**:
```
Compliance Check Results (RAG-based):
- Repository: https://github.com/...
- Guidelines checked: 5

Guideline: Data must be encrypted in transit
Assessment: Yes, TLS 1.2 is configured in config/ssl.js...
```

---

## 🎬 **Demo for Hackathon**

Show the judges the **intelligent mode selection**:

```bash
# 1. AUDIT mode (specific violations)
python guardian_agent_simple.py "Find all violations in https://github.com/Aadisheshudupa/3DTinKer against sample_regulation.pdf"

# 2. COMPLIANCE mode (overall assessment)
python guardian_agent_simple.py "Is https://github.com/Aadisheshudupa/3DTinKer compliant with accessibility standards?"

# 3. QA mode (understanding)
python guardian_agent_simple.py "What does https://github.com/Aadisheshudupa/3DTinKer do?"
```

**Talking Point**: 
> "Notice how Guardian AI automatically chose different analysis modes based on my question? 
> AUDIT mode for finding violations, COMPLIANCE mode for checking guidelines, 
> and QA mode for understanding the code. It's not pre-programmed - the AI decides!"

---

## ✅ **Summary**

| Feature | Before | After |
|---------|--------|-------|
| **Code Auditor Modes** | 1 (AUDIT only) | 2 (AUDIT + COMPLIANCE) |
| **Agent Awareness** | Not aware of modes | Fully aware, chooses automatically |
| **Planning** | Basic | Intelligent mode selection |
| **Output** | Generic | Mode-specific formatting |

---

## 📚 **Documentation Created**

1. **AGENT_MODES_EXPLAINED.md** - Complete guide to all modes
2. **This file** - Summary of changes

---

## 🎯 **Answer to Your Question**

> "Is the agent aware of those modes and what about QA mode?"

**YES!** ✅ The agent is now **fully aware** of:
1. ✅ **AUDIT mode** (exhaustive scanning)
2. ✅ **COMPLIANCE mode** (semantic checking) 
3. ✅ **QA mode** (question answering)

The agent's AI brain automatically picks the right mode based on your query!

---

## 🚀 **Next Steps**

Try these queries to see the agent choose different modes:

```bash
# Will use AUDIT mode
python guardian_agent_simple.py "Scan https://github.com/Aadisheshudupa/3DTinKer for violations"

# Will use COMPLIANCE mode
python guardian_agent_simple.py "Does https://github.com/Aadisheshudupa/3DTinKer comply with security best practices?"

# Will use QA mode
python guardian_agent_simple.py "How does https://github.com/Aadisheshudupa/3DTinKer work?"
```

---

**All modes are now integrated and the agent intelligently chooses! 🎉**
