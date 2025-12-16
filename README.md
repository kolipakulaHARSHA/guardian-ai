# 🛡️ Guardian AI

> **AI-Powered Code Compliance & Repository Analysis Platform**

Guardian AI is an intelligent, autonomous system that uses advanced AI agents to automatically audit code repositories for compliance violations and answer questions about any codebase. Built with LangChain's ReAct pattern and Google's Gemini models, it provides real-time, comprehensive code analysis through an intuitive web interface.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 Key Features

### 🤖 Intelligent AI Agent Orchestration
- **Autonomous Decision Making** - AI agent automatically selects and combines tools based on user requests
- **LangGraph ReAct Pattern** - Advanced reasoning and action loop for intelligent task execution
- **Multi-Tool Integration** - Seamlessly orchestrates legal analysis, code auditing, and Q&A capabilities

### 📄 Legal Document Analysis (RAG)
- **PDF Processing** - Extract compliance rules from regulatory documents (ISO-27001, GDPR, PCI-DSS, etc.)
- **ChromaDB Vector Store** - Persistent knowledge base with semantic search
- **Technical Brief Generation** - Convert legal documents into developer-friendly compliance checklists

### 🔍 Code Compliance Auditing
- **Line-by-Line Scanning** - Exhaustive analysis of entire repositories (20-40 line chunks)
- **Multi-Language Support** - Python, JavaScript, Java, C++, Go, and 10+ more languages
- **Structured Violation Reports** - Detailed JSON output with file paths, line numbers, and recommendations
- **Real-Time Progress** - Server-Sent Events (SSE) for live scanning updates

### 💬 Repository Q&A System
- **Interactive Chat** - Ask questions about any GitHub repository in natural language
- **RAG-Powered** - FAISS vector store for fast semantic search across codebases
- **Streaming Responses** - Real-time answer generation with progress indicators
- **Multi-Query Support** - Answer multiple questions in a single session

### 🎨 Modern Web Interface
- **React + TypeScript** - Type-safe, component-based architecture
- **Dark/Light Mode** - Automatic theme switching with system preference support
- **Responsive Design** - Seamless experience across desktop, tablet, and mobile
- **Smooth Animations** - Framer Motion powered transitions and interactions
- **Persistent State** - Work saved across sessions and page navigation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GUARDIAN AI SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐         ┌──────────────────────────┐    │
│  │   Frontend     │         │      Backend API         │    │
│  │  (React + TS)  │◄───────►│      (FastAPI)           │    │
│  │                │   REST  │                          │    │
│  │  - Dashboard   │   +SSE  │  ┌────────────────────┐  │    │
│  │  - Code Audit  │         │  │  Guardian Agent    │  │    │
│  │  - Q&A Chat    │         │  │ (LangGraph ReAct)  │  │    │
│  └────────────────┘         │  └─────────┬──────────┘  │    │
│                             │            │              │    │
│                             │  ┌─────────▼──────────┐  │    │
│                             │  │     AI Tools       │  │    │
│                             │  ├────────────────────┤  │    │
│                             │  │ • Legal Analyzer   │  │    │
│                             │  │ • Code Auditor     │  │    │
│                             │  │ • Q&A Tool         │  │    │
│                             │  └────────────────────┘  │    │
│                             └──────────────────────────┘    │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           External Services & Storage                  │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • Google Gemini API (gemini-2.5-flash/pro)           │ │
│  │  • ChromaDB (Legal document vectors)                  │ │
│  │  • FAISS (Code repository vectors)                    │ │
│  │  • GitHub Repositories (Code sources)                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Google API Key** - [Get one here](https://makersuite.google.com/app/apikey)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd guardian-ai
```

### 2. Backend Setup

```bash
# Navigate to backend
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Start the backend server
python api.py
```

Backend runs on: `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd Frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: `http://localhost:5173`

### 4. Access the Application

Open your browser to `http://localhost:5173` and start using Guardian AI!

---

## 📦 Technology Stack

### Backend
- **FastAPI** - Modern, high-performance web framework
- **LangChain** - LLM application framework with ReAct agent pattern
- **LangGraph** - Agent orchestration and workflow management
- **Google Gemini AI** - Advanced language models (gemini-2.5-flash, gemini-2.5-pro)
- **ChromaDB** - Vector database for legal document storage
- **FAISS** - Facebook AI Similarity Search for code vectors
- **PyPDF** - PDF document parsing
- **GitPython** - Repository cloning and management
- **Uvicorn** - ASGI server for FastAPI
- **SSE-Starlette** - Server-Sent Events for real-time updates

### Frontend
- **React 18** - Modern UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **React Syntax Highlighter** - Code highlighting

---

## 📚 Documentation

### Core Documentation
- **[Installation Guide](INSTALLATION_GUIDE.md)** - Detailed setup instructions
- **[Quick Start Guide](QUICK_START.md)** - Fast track to get running
- **[Project Documentation](PROJECT_DOCUMENTATION.md)** - Complete system overview
- **[Setup Status](SETUP_STATUS.md)** - Current configuration status

### Component Documentation
- **[Backend README](Backend/README.md)** - Backend API details
- **[Frontend README](Frontend/README.md)** - Frontend architecture
- **[Code Tool README](Backend/Github_scanner/CODE_TOOL_README.md)** - Code auditor details
- **[Q&A Tool README](Backend/Github_scanner/docs/QA_TOOL_README.md)** - Repository Q&A system
- **[Legal Tool README](Backend/Guardian-Legal-analyzer-main/README.md)** - Legal analyzer guide

### Guides
- **[Agent Orchestration Explained](Backend/docs/AGENT_ORCHESTRATION_EXPLAINED.md)** - How the AI agent works
- **[Agent Modes Explained](Backend/docs/AGENT_MODES_EXPLAINED.md)** - Different operational modes
- **[Data Flow Explanation](Backend/docs/DATA_FLOW_EXPLANATION.md)** - System data flow
- **[Troubleshooting](Backend/docs/TROUBLESHOOTING.md)** - Common issues and solutions

---

## 🎯 Usage

### 1. Code Compliance Audit

**Via Web Interface:**
1. Navigate to **Code Audit** page
2. Enter a GitHub repository URL (e.g., `https://github.com/user/repo`)
3. Upload a compliance PDF document (ISO-27001, GDPR, etc.)
4. Click **Start Audit**
5. Watch real-time progress as files are scanned
6. Review violations with file paths, line numbers, and recommendations
7. Export results to JSON

**Via Command Line:**
```bash
cd Backend/Github_scanner

# Audit mode - detect violations against a technical brief
python code_tool.py audit https://github.com/user/repo "path/to/compliance_brief.txt"

# Compliance mode - scan using PDF document
python code_tool.py compliance https://github.com/user/repo "path/to/regulation.pdf"
```

### 2. Repository Q&A

**Via Web Interface:**
1. Navigate to **Q&A Chat** page
2. Enter a GitHub repository URL
3. Wait for repository indexing (progress shown)
4. Ask questions in natural language
5. Receive streaming AI responses with code references

**Via Command Line:**
```bash
cd Backend/Github_scanner

# Interactive mode
python qa_tool.py https://github.com/user/repo

# Single question
python qa_tool.py https://github.com/user/repo --question "How does authentication work?"

# Multiple questions
python qa_tool.py https://github.com/user/repo --questions questions.txt
```

### 3. AI Agent Orchestration

The Guardian Agent can intelligently combine tools based on your request:

```python
from guardian_agent import GuardianAgent

agent = GuardianAgent()

# Agent automatically selects appropriate tools
result = agent.process_query(
    "Analyze regulation.pdf and audit https://github.com/user/repo for compliance"
)

print(result['response'])
```

---

## 📡 API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Health Check
```http
GET /health
```

#### Code Audit
```http
POST /api/audit/code
Content-Type: multipart/form-data

{
  "repo_url": "https://github.com/user/repo",
  "pdf_file": <file>,
  "mode": "compliance",
  "model_name": "gemini-2.5-flash"
}
```

#### Q&A Initialization
```http
POST /api/qa/init
Content-Type: application/json

{
  "repo_url": "https://github.com/user/repo",
  "model_name": "gemini-2.5-pro"
}
```

#### Ask Question
```http
POST /api/qa/ask
Content-Type: application/json

{
  "session_id": "abc123",
  "question": "How does the authentication system work?"
}
```

#### Upload PDF
```http
POST /api/upload/pdf
Content-Type: multipart/form-data

{
  "file": <pdf-file>
}
```

**Full API Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `Backend` directory:

```env
# Required: Google Gemini API Key
GOOGLE_API_KEY=your_api_key_here

# Optional: Model Configuration
DEFAULT_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=models/embedding-001

# Optional: Vector Store Configuration
CHROMA_DB_DIR=./chroma_db
FAISS_INDEX_DIR=./faiss_index

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Available Models

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `gemini-2.5-flash` | ⚡ Fast | ⭐⭐⭐ Good | Code auditing, quick scans |
| `gemini-2.5-pro` | 🐢 Slower | ⭐⭐⭐⭐⭐ Excellent | Complex Q&A, deep analysis |
| `gemini-2.5-pro-preview-03-25` | 🐢 Slower | ⭐⭐⭐⭐⭐ Excellent | Latest features, best quality |

---

## 📊 Project Structure

```
guardian-ai/
├── Backend/
│   ├── api.py                      # FastAPI server
│   ├── guardian_agent.py           # Main AI agent orchestrator
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (create this)
│   │
│   ├── Github_scanner/             # Code analysis tools
│   │   ├── code_tool.py           # Code auditor (line-by-line scanning)
│   │   ├── qa_tool.py             # Repository Q&A tool
│   │   ├── github_repo_tool.py    # Git operations
│   │   └── docs/                  # Tool documentation
│   │
│   ├── Guardian-Legal-analyzer-main/  # Legal document analysis
│   │   ├── legal_tool.py          # RAG-based PDF analyzer
│   │   └── README.md              # Legal tool guide
│   │
│   └── docs/                      # Backend documentation
│       ├── AGENT_ORCHESTRATION_EXPLAINED.md
│       ├── DATA_FLOW_EXPLANATION.md
│       └── TROUBLESHOOTING.md
│
├── Frontend/
│   ├── src/
│   │   ├── pages/                 # Main application pages
│   │   │   ├── Dashboard.tsx     # Landing page
│   │   │   ├── CodeAudit.tsx     # Code audit interface
│   │   │   └── QAChat.tsx        # Q&A chat interface
│   │   │
│   │   ├── components/            # Reusable UI components
│   │   │   ├── Navbar.tsx
│   │   │   ├── ViolationResults.tsx
│   │   │   └── FormattedMessage.tsx
│   │   │
│   │   ├── contexts/              # React context providers
│   │   │   ├── ThemeContext.tsx  # Dark/light mode
│   │   │   └── AppStateContext.tsx  # Global state
│   │   │
│   │   ├── services/              # API integration
│   │   │   └── api.ts
│   │   │
│   │   ├── types/                 # TypeScript definitions
│   │   │   └── index.ts
│   │   │
│   │   ├── App.tsx                # Main app component
│   │   └── main.tsx               # Entry point
│   │
│   ├── package.json               # Node dependencies
│   ├── vite.config.ts             # Vite configuration
│   ├── tailwind.config.js         # Tailwind configuration
│   └── tsconfig.json              # TypeScript configuration
│
├── README.md                      # This file
├── PROJECT_DOCUMENTATION.md       # Detailed documentation
├── QUICK_START.md                 # Quick reference guide
└── INSTALLATION_GUIDE.md          # Setup instructions
```

---

## 🎨 Features in Detail

### Real-Time Progress Tracking
- Server-Sent Events (SSE) stream updates during code scanning
- Live file-by-file progress indicators
- Real-time violation detection and display
- Smooth animations for status updates

### Intelligent Code Chunking
- 20-40 line code chunks for optimal LLM processing
- Language-aware splitting
- Context preservation across chunks
- Line number tracking for precise violation reporting

### Persistent State Management
- React Context API for global state
- LocalStorage for theme and preferences
- Session management for Q&A conversations
- Navigation state preservation

### Compliance Rule Extraction
- RAG (Retrieval Augmented Generation) from PDF documents
- ChromaDB vector storage for fast semantic search
- Technical brief generation for developers
- Multi-document knowledge accumulation

### Multi-Language Code Support
Supports analysis of: Python, JavaScript, TypeScript, Java, C++, C, Go, Ruby, PHP, Swift, Kotlin, HTML, CSS, and more.

---

## 🧪 Testing

### Backend Tests
```bash
cd Backend

# Test the Guardian Agent
python test_agent.py

# Test code auditor
python -m pytest Github_scanner/test_basic.py

# Test legal analyzer
python Guardian-Legal-analyzer-main/test_legal_tool.py
```

### Frontend Tests
```bash
cd Frontend

# Run linter
npm run lint

# Build test
npm run build

# Preview production build
npm run preview
```

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.12+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify API key
echo $GOOGLE_API_KEY  # Should show your key
```

**Frontend errors:**
```bash
# Clear node modules
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 20+
```

**API connection issues:**
- Verify backend is running on port 8000
- Check CORS settings in `api.py`
- Ensure frontend is configured for correct backend URL

**Model errors:**
- Verify `GOOGLE_API_KEY` is valid
- Check API quota limits
- Try a different model (flash vs pro)

For more troubleshooting, see [TROUBLESHOOTING.md](Backend/docs/TROUBLESHOOTING.md)

---

## 🚀 Deployment

### Backend (Production)

```bash
# Install production dependencies
pip install -r Backend/requirements.txt

# Run with Gunicorn (Linux/Mac)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker Backend.api:app

# Or use Uvicorn directly
uvicorn Backend.api:app --host 0.0.0.0 --port 8000
```

### Frontend (Production)

```bash
cd Frontend

# Build for production
npm run build

# Serve with static server
npm install -g serve
serve -s dist -p 5173
```

### Docker (Optional)

```dockerfile
# Backend Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY Backend/requirements.txt .
RUN pip install -r requirements.txt
COPY Backend/ .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow existing code style (PEP 8 for Python, ESLint for TypeScript)
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini AI** - Advanced language models
- **LangChain** - LLM application framework
- **FastAPI** - Modern Python web framework
- **React Team** - UI library
- **Tailwind Labs** - CSS framework
- **ChromaDB** - Vector database
- **FAISS** - Similarity search

---

## 📧 Support

- **Documentation:** Check the [docs](Backend/docs/) folder
- **Issues:** Open an issue on GitHub
- **Questions:** Contact the development team

---

## 🎯 Use Cases

### 1. Security Audits
Scan repositories for security vulnerabilities against industry standards (OWASP, CWE)

### 2. Compliance Verification
Ensure code meets regulatory requirements (GDPR, HIPAA, PCI-DSS, ISO-27001)

### 3. Code Review Automation
Automate initial code review process before human review

### 4. Onboarding Developers
New team members can ask questions about codebase structure and patterns

### 5. Documentation Verification
Check if code implementation matches technical documentation

### 6. Legacy Code Analysis
Understand unfamiliar or legacy codebases quickly

---

## 🔮 Roadmap

- [ ] Support for more AI models (OpenAI, Anthropic)
- [ ] Custom compliance rule creation
- [ ] Multi-repository analysis
- [ ] CI/CD integration (GitHub Actions, GitLab CI)
- [ ] VS Code extension
- [ ] Slack/Discord bot integration
- [ ] Advanced visualization dashboard
- [ ] Team collaboration features
- [ ] Custom report templates
- [ ] API rate limiting and caching

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ by the Guardian AI Team**
