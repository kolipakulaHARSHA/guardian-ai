# 🎛️ Guardian AI Agent - Tool Modes Explained

## Overview

The Guardian AI agent integrates **three specialized tools**, and some tools have **multiple modes** for different use cases. The agent's AI brain automatically decides which tool and mode to use based on your query.

---

## 🛠️ Available Tools

### 1. **Legal Analyzer** 📄
- **Purpose**: Extract compliance requirements from PDF documents
- **Input**: PDF regulatory documents (GDPR, HIPAA, internal policies)
- **Output**: Technical brief with compliance rules
- **Technology**: ChromaDB vector database + RAG

---

### 2. **Code Auditor** 🔍
This tool has **TWO MODES**:

#### **Mode A: AUDIT (Line-by-Line Scanning)**
- **Use When**: You want to find specific violations in code
- **How it Works**: 
  - Clones repository
  - Reads every code file line-by-line
  - Splits into chunks (20-40 lines)
  - Uses LLM to analyze each chunk against technical brief
  - Returns exact line numbers where violations occur
- **Best For**: 
  - Finding hardcoded credentials
  - Detecting missing alt attributes in HTML
  - Identifying unencrypted HTTP connections
  - Precise, actionable violations
- **Model**: `gemini-2.5-flash` (fast, cost-efficient)
- **Output**: List of violations with file paths and line numbers

**Example Query**:
```
"Find all security violations in https://github.com/user/repo"
"Check if https://github.com/user/repo violates the rules in sample_regulation.pdf"
```

---

#### **Mode B: COMPLIANCE (RAG-Based Semantic Search)**
- **Use When**: You want to check overall compliance with guidelines
- **How it Works**:
  - Clones repository
  - Indexes all code and documentation into FAISS vector store
  - Uses RAG to semantically search for evidence of compliance/non-compliance
  - Provides assessment with code snippets as evidence
- **Best For**:
  - High-level compliance questions
  - "Does this repo have a LICENSE file?"
  - "Does the code follow REST API best practices?"
  - Understanding if a guideline is met
- **Model**: `gemini-2.5-pro-preview-03-25` (more intelligent)
- **Output**: Assessment for each guideline with evidence

**Example Query**:
```
"Does https://github.com/user/repo comply with data protection guidelines?"
"Check if the repository follows our coding standards"
```

---

### 3. **QA Tool** 💬
- **Purpose**: Answer questions about code repositories
- **How it Works**:
  - Indexes repository using FAISS
  - Uses RAG to retrieve relevant code
  - Answers questions with context
- **Best For**:
  - "What does this repository do?"
  - "How is authentication implemented?"
  - "Where is the API endpoint defined?"
- **Model**: `gemini-2.5-pro-preview-03-25`

**Example Query**:
```
"What is https://github.com/user/repo about?"
"How does https://github.com/user/repo handle user authentication?"
```

---

## 🤖 How the Agent Chooses

The agent's **AI brain** analyzes your query and automatically decides:

1. **Which tools to use**
2. **What order to execute them**
3. **Which mode to use** (for Code Auditor)

### Decision Logic Examples

| Query | Tools Used | Mode | Reasoning |
|-------|------------|------|-----------|
| "Summarize sample.pdf" | Legal_Analyzer | N/A | Only needs to analyze PDF |
| "Find violations in repo X" | Code_Auditor | **AUDIT** | Looking for specific violations |
| "Does repo X comply with GDPR?" | Code_Auditor | **COMPLIANCE** | Checking overall compliance |
| "Check repo X against sample.pdf" | Legal_Analyzer → Code_Auditor | **AUDIT** | Get rules first, then find violations |
| "What does repo X do?" | QA_Tool | N/A | Asking a question about code |

---

## 📊 Mode Comparison

### Code Auditor: AUDIT vs COMPLIANCE

| Feature | AUDIT Mode | COMPLIANCE Mode |
|---------|-----------|-----------------|
| **Approach** | Line-by-line exhaustive scan | Semantic RAG search |
| **Speed** | Slower (analyzes every line) | Faster (semantic retrieval) |
| **Precision** | Very high (exact line numbers) | Medium (general assessment) |
| **Output** | Specific violations with locations | Overall compliance status |
| **Best For** | Finding violations | Checking if guidelines are met |
| **Cost** | Higher (more LLM calls) | Lower (fewer LLM calls) |
| **Model** | gemini-2.5-flash | gemini-2.5-pro |

---

## 💡 Usage Examples

### Example 1: Full Compliance Check (AUDIT Mode)
```bash
python guardian_agent_simple.py "Check if https://github.com/Aadisheshudupa/3DTinKer complies with GuardianAI-Orchestrator/sample_regulation.pdf"
```

**What happens**:
1. ✅ Legal_Analyzer extracts requirements from PDF
2. ✅ Code_Auditor (AUDIT mode) scans code line-by-line
3. ✅ Returns violations like:
   ```
   src/App.jsx (line 45): Missing alt attribute on <img> element
   src/utils.js (line 12): Hardcoded API key detected
   ```

---

### Example 2: High-Level Compliance (COMPLIANCE Mode)
```bash
python guardian_agent_simple.py "Does https://github.com/user/repo comply with data protection guidelines?"
```

**What happens**:
1. ✅ Code_Auditor (COMPLIANCE mode) indexes repository
2. ✅ Checks for evidence of data protection
3. ✅ Returns assessment:
   ```
   Guideline: Data must be encrypted in transit
   Assessment: Yes, the code uses HTTPS and TLS 1.2. Evidence found in config/ssl.js
   ```

---

### Example 3: Code Q&A (QA Mode)
```bash
python guardian_agent_simple.py "What authentication method does https://github.com/user/repo use?"
```

**What happens**:
1. ✅ QA_Tool indexes repository
2. ✅ Searches for authentication-related code
3. ✅ Returns answer:
   ```
   The repository uses JWT-based authentication. Tokens are generated in auth/jwt.js
   and validated in middleware/auth.js using the jsonwebtoken library.
   ```

---

## 🎯 When to Use Each Mode

### Use **AUDIT Mode** when:
- ✅ You need to find specific violations
- ✅ You want exact line numbers
- ✅ You have a technical brief with specific rules
- ✅ You need actionable, fix-able issues
- ✅ Example: "Find all hardcoded passwords"

### Use **COMPLIANCE Mode** when:
- ✅ You want a high-level compliance assessment
- ✅ You're checking if a guideline is met (yes/no)
- ✅ You don't need exact locations
- ✅ You want faster results
- ✅ Example: "Does this repo follow OWASP guidelines?"

### Use **QA Tool** when:
- ✅ You're asking "what" or "how" questions
- ✅ You want to understand the codebase
- ✅ You're not looking for violations
- ✅ Example: "What does this repo do?"

---

## 🔧 Manual Mode Selection (Advanced)

The agent automatically chooses the best mode, but you can influence it with your wording:

**To force AUDIT mode**:
- Use words: "find violations", "scan", "audit", "check against"
- Example: "Audit this repo for violations"

**To force COMPLIANCE mode**:
- Use words: "comply", "compliance", "does it follow", "is it compliant"
- Example: "Is this repo compliant with GDPR?"

**To use QA mode**:
- Ask questions: "what", "how", "where", "why"
- Example: "How does this repo work?"

---

## 🎬 Demo for Hackathon

Show the judges the **intelligent mode selection**:

```bash
# Query 1: AUDIT mode (finds specific violations)
python guardian_agent_simple.py "Find security violations in https://github.com/Aadisheshudupa/3DTinKer"

# Query 2: COMPLIANCE mode (high-level assessment)
python guardian_agent_simple.py "Is https://github.com/Aadisheshudupa/3DTinKer compliant with accessibility guidelines?"

# Query 3: QA mode (understanding code)
python guardian_agent_simple.py "What does https://github.com/Aadisheshudupa/3DTinKer do?"
```

Point out: **"Notice how the AI chose different modes automatically based on what I asked!"**

---

## 🏆 Why This Is Impressive

1. **Multi-Modal Intelligence**: Not just one tool, but multiple modes optimized for different tasks
2. **Automatic Decision Making**: AI chooses the best approach
3. **Complementary Strengths**: AUDIT for precision, COMPLIANCE for speed, QA for understanding
4. **Real-World Applicability**: Different compliance scenarios need different approaches

---

## 📝 Summary

| Tool | Modes | When to Use |
|------|-------|-------------|
| **Legal Analyzer** | 1 mode | Extract compliance requirements from PDFs |
| **Code Auditor** | 2 modes: AUDIT & COMPLIANCE | Find violations (AUDIT) or check compliance (COMPLIANCE) |
| **QA Tool** | 1 mode | Answer questions about code |

**The agent's AI brain picks the right tool and mode for you!** 🧠✨

---

**Updated**: Agent now supports all modes and chooses intelligently based on your query!
