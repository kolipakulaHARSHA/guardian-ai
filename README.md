# Guardian AI - Backend Final

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5--Pro-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Guardian AI** is an intelligent compliance and code analysis system that combines legal document analysis, code auditing, and repository Q&A capabilities using Google's Gemini AI.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/kolipakulaHARSHA/guardian-ai.git
cd guardian-ai

# 2. Set up virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set API key
$env:GOOGLE_API_KEY="your-api-key-here"  # Windows
# export GOOGLE_API_KEY="your-api-key-here"  # Linux/Mac

# 5. Run interactive mode
python guardian_agent_simple.py --interactive
```

---

## 📚 Documentation

### **01. Getting Started**
- **[START_HERE.md](documentation/01-getting-started/START_HERE.md)** - Begin your journey with Guardian AI
- **[README.md](documentation/01-getting-started/README.md)** - Original project documentation

### **02. QA Feature** 
Ask questions about any GitHub repository using RAG:
- **[QA_FEATURE_GUIDE.md](documentation/02-qa-feature/QA_FEATURE_GUIDE.md)** - Complete guide to the QA feature
- **[QA_AGENT_WORKFLOW.md](documentation/02-qa-feature/QA_AGENT_WORKFLOW.md)** - How the QA agent works
- **[QA_FLOW_VISUAL_GUIDE.md](documentation/02-qa-feature/QA_FLOW_VISUAL_GUIDE.md)** - Visual flowcharts
- **[INTERACTIVE_MODE_QUICKREF.md](documentation/02-qa-feature/INTERACTIVE_MODE_QUICKREF.md)** - Quick reference
- **[FIX_QA_SESSION_CONTEXT.md](documentation/02-qa-feature/FIX_QA_SESSION_CONTEXT.md)** - Session context fix details
- **[CHANGELOG_QA_FIXES.md](documentation/02-qa-feature/CHANGELOG_QA_FIXES.md)** - QA fixes changelog

### **03. Code Scanner**
Scan GitHub repositories for compliance violations:
- **[README.md](documentation/03-code-scanner/README.md)** - Code scanner overview
- **[QUICKSTART.md](documentation/03-code-scanner/QUICKSTART.md)** - Quick start guide
- **[QUICK_REFERENCE.md](documentation/03-code-scanner/QUICK_REFERENCE.md)** - Command reference
- **[CODE_TOOL_README.md](documentation/03-code-scanner/CODE_TOOL_README.md)** - Tool documentation
- **[AUDIT_MODE_GUIDE.md](documentation/03-code-scanner/AUDIT_MODE_GUIDE.md)** - Audit vs Compliance modes
- **[PROJECT_SUMMARY.md](documentation/03-code-scanner/PROJECT_SUMMARY.md)** - Project summary

### **04. Legal Analyzer**
Analyze PDF regulatory documents:
- **[README.md](documentation/04-legal-analyzer/README.md)** - Legal analyzer overview
- **[ORCHESTRATOR_GUIDE.md](documentation/04-legal-analyzer/ORCHESTRATOR_GUIDE.md)** - Integration guide
- **[QUICK_REFERENCE.md](documentation/04-legal-analyzer/QUICK_REFERENCE.md)** - Quick reference

### **05. Agent System**
Orchestrated multi-tool AI agent:
- **[AGENT_INTEGRATION_COMPLETE.md](documentation/05-agent-system/AGENT_INTEGRATION_COMPLETE.md)** - Integration status
- **[AGENT_MODES_EXPLAINED.md](documentation/05-agent-system/AGENT_MODES_EXPLAINED.md)** - Agent modes
- **[AGENT_ORCHESTRATION_EXPLAINED.md](documentation/05-agent-system/AGENT_ORCHESTRATION_EXPLAINED.md)** - How orchestration works
- **[DATA_FLOW_EXPLANATION.md](documentation/05-agent-system/DATA_FLOW_EXPLANATION.md)** - Data flow diagrams

### **06. Development**
Developer resources and setup:
- **[PROGRESS.md](documentation/06-development/PROGRESS.md)** - Development progress
- **[TROUBLESHOOTING.md](documentation/06-development/TROUBLESHOOTING.md)** - Common issues and solutions
- **[SETUP_COMPLETE.md](documentation/06-development/SETUP_COMPLETE.md)** - Setup verification
- **[GEMINI_MIGRATION.md](documentation/06-development/GEMINI_MIGRATION.md)** - Gemini API migration
- **[GEMINI_READY.md](documentation/06-development/GEMINI_READY.md)** - Gemini readiness status

### **07. Technical Details**
Advanced technical information:
- **[ARCHITECTURAL_ANALYSIS.md](documentation/07-technical-details/ARCHITECTURAL_ANALYSIS.md)** - Architecture overview
- **[INTEGRATION_PROPOSAL.md](documentation/07-technical-details/INTEGRATION_PROPOSAL.md)** - Integration proposals
- **[JSON_EXPORT_FEATURE.md](documentation/07-technical-details/JSON_EXPORT_FEATURE.md)** - JSON export feature
- **[JSON_DETAILED_VIOLATIONS.md](documentation/07-technical-details/JSON_DETAILED_VIOLATIONS.md)** - Violations format
- **[MODE_UPDATE_SUMMARY.md](documentation/07-technical-details/MODE_UPDATE_SUMMARY.md)** - Mode updates
- **[COMPLIANCE_TEST_RESULTS.md](documentation/07-technical-details/COMPLIANCE_TEST_RESULTS.md)** - Test results

---

## 🎯 Features

### **1. Legal Document Analysis**
- Extract compliance requirements from PDF regulations
- Create technical briefs for developers
- Support for GDPR, ISO 27001, and custom regulations

### **2. Code Auditing**
- **Audit Mode**: Line-by-line violation scanning
- **Compliance Mode**: RAG-based semantic compliance checking
- Detailed violation reports with line numbers and explanations

### **3. Repository Q&A**
- Ask questions about any GitHub repository
- RAG-powered semantic search
- Session management for fast multi-question workflows
- Source citations for transparency

### **4. Intelligent Agent Orchestration**
- Automatic tool selection based on query
- Multi-step workflows (e.g., analyze regulation → audit code)
- Smart query routing and context awareness

---

## 📖 Usage Examples

### **Interactive Mode (Recommended)**

```bash
python guardian_agent_simple.py --interactive

You: set repo https://github.com/user/repo
✅ QA session ready! Indexed 150 documents.

You: what does this repo do?
🤖 Guardian AI: [Answer with sources...]

You: check https://github.com/user/repo against sample_regulation.pdf
🤖 Guardian AI: [Compliance report...]

You: exit
```

### **Single Query Mode**

```bash
# Ask a question
python guardian_agent_simple.py "What is https://github.com/user/repo about?"

# Analyze a regulation
python guardian_agent_simple.py "Analyze sample_regulation.pdf"

# Audit code
python guardian_agent_simple.py "Check https://github.com/user/repo against sample.pdf"

# Save results to JSON
python guardian_agent_simple.py "Audit repo" --output report.json
```

### **Direct Tool Usage**

```bash
# QA Tool
python Github_scanner/qa_tool.py https://github.com/user/repo --interactive

# Code Auditor
python Github_scanner/code_tool.py https://github.com/user/repo --brief "compliance.txt"

# Legal Analyzer
python Guardian-Legal-analyzer-main/legal_tool.py sample.pdf
```

---

## 🏗️ Project Structure

```
guardian-ai/
├── guardian_agent_simple.py    # Main agent (orchestrator)
├── guardian_agent.py           # Alternative agent implementation
│
├── Github_scanner/             # Code scanning module
│   ├── code_tool.py           # Code auditor (audit + compliance modes)
│   ├── qa_tool.py             # Repository Q&A tool
│   └── README.md              # Scanner documentation
│
├── Guardian-Legal-analyzer-main/  # Legal analysis module
│   ├── legal_tool.py          # PDF regulation analyzer
│   └── README.md              # Legal analyzer docs
│
├── documentation/              # Organized documentation
│   ├── 01-getting-started/    # Quick start guides
│   ├── 02-qa-feature/         # QA feature docs
│   ├── 03-code-scanner/       # Code scanner docs
│   ├── 04-legal-analyzer/     # Legal analyzer docs
│   ├── 05-agent-system/       # Agent orchestration docs
│   ├── 06-development/        # Developer resources
│   └── 07-technical-details/  # Technical specifications
│
└── requirements.txt            # Python dependencies
```

---

## 🛠️ Technology Stack

- **Python 3.8+**
- **Google Gemini AI** (2.5 Pro, 2.5 Flash)
- **LangChain** - Agent framework and RAG
- **FAISS** - Vector similarity search
- **ChromaDB** - Vector database (legal analyzer)
- **GitPython** - Repository cloning

---

## 🔧 Configuration

### **Environment Variables**

```bash
# Required
GOOGLE_API_KEY=your-gemini-api-key

# Optional
GUARDIAN_MODEL=gemini-2.5-pro-preview-03-25  # Default model
GUARDIAN_VERBOSE=true                         # Verbose logging
```

### **Model Options**

- `gemini-2.5-pro-preview-03-25` - Most capable (default for agent)
- `gemini-2.5-flash` - Faster, good for code scanning
- `gemini-1.5-pro` - Stable alternative

---

## 📊 Performance

### **QA Feature**
- **Setup:** 25-45 seconds (one-time per repository)
- **First question:** ~27 seconds
- **Subsequent questions:** ~2 seconds (95% faster!)

### **Code Auditing**
- **Audit mode:** ~2-5 minutes (exhaustive scanning)
- **Compliance mode:** ~30-60 seconds (semantic checking)

### **Legal Analysis**
- **PDF indexing:** ~10-20 seconds (one-time)
- **Query response:** ~5-10 seconds

---

## 🤝 Contributing

Contributions are welcome! Please see [PROGRESS.md](documentation/06-development/PROGRESS.md) for current development status.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Google Gemini AI team for the powerful language models
- LangChain community for the excellent framework
- All contributors and testers

---

## 📞 Support

- **Documentation:** See `documentation/` directory
- **Issues:** GitHub Issues
- **Troubleshooting:** [TROUBLESHOOTING.md](documentation/06-development/TROUBLESHOOTING.md)

---

## 🚦 Status

✅ **Backend_Final** - Fully functional with QA session management, code auditing, and legal analysis.

**Current Branch:** `Backend_Final`

**Last Updated:** October 26, 2025

---

**Made with ❤️ using Google Gemini AI**
