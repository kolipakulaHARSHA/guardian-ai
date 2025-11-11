# Guardian AI - Complete Setup Guide

This guide will help you set up and run the Guardian AI project on your local machine.

## 📋 Prerequisites

Before you begin, make sure you have the following installed:

### Required Software:
1. **Python 3.12+** - [Download here](https://www.python.org/downloads/)
2. **Node.js 20+ and npm** - [Download here](https://nodejs.org/)
3. **Git** - [Download here](https://git-scm.com/downloads)
4. **Google API Key** for Gemini - [Get it here](https://makersuite.google.com/app/apikey)

---

## 🚀 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/KarthikSagarP/GuardianAI.git
cd GuardianAI
git checkout Frontend
```

### 2. Backend Setup (Python)

#### Step 2.1: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 2.2: Install Python Dependencies

```bash
pip install -r Backend/requirements.txt
```

**If requirements.txt doesn't exist, install these packages:**
```bash
pip install fastapi==0.120.0
pip install uvicorn==0.38.0
pip install python-multipart==0.0.20
pip install langchain==1.0.2
pip install langchain-google-genai==3.0.0
pip install langgraph==1.0.0
pip install chromadb==1.2.1
pip install faiss-cpu==1.12.0
pip install gitpython==3.1.43
pip install pypdf==6.1.3
pip install python-dotenv==1.0.0
pip install sse-starlette==3.0.2
```

#### Step 2.3: Configure Environment Variables

Create a `.env` file in the `Backend` directory:

**Backend/.env:**
```env
GOOGLE_API_KEY=your_actual_google_api_key_here
```

⚠️ **Important:** Replace `your_actual_google_api_key_here` with your actual Google Gemini API key!

---

### 3. Frontend Setup (Node.js)

#### Step 3.1: Navigate to Frontend Directory

```bash
cd Frontend
```

#### Step 3.2: Install Node Dependencies

```bash
npm install
```

This will install all dependencies listed in `package.json`:
- React 18.2.0
- TypeScript 5.2.2
- Vite 5.0.8
- Tailwind CSS 3.3.6
- Framer Motion 10.16.16
- React Router DOM 6.20.0
- Axios 1.6.2
- Lucide React 0.294.0
- React Syntax Highlighter 15.5.0

---

## 🎮 Running the Application

You need to run **both** the backend and frontend servers simultaneously.

### Terminal 1 - Start Backend Server

**Windows (PowerShell):**
```powershell
# From project root (version-3 directory)
.\venv\Scripts\python.exe Backend\api.py
```

**macOS/Linux:**
```bash
# From project root
python Backend/api.py
```

✅ Backend will be running at: **http://localhost:8000**  
📚 API docs available at: **http://localhost:8000/docs**

---

### Terminal 2 - Start Frontend Server

```bash
# From project root
cd Frontend
npm run dev
```

✅ Frontend will be running at: **http://localhost:5173**

---

## 🌐 Accessing the Application

Once both servers are running, open your browser and go to:

**http://localhost:5173**

You should see the Guardian AI dashboard with three main features:
1. 📝 **Code Audit** - Scan repositories for compliance violations
2. 💬 **Q&A Chat** - Ask questions about your codebase
3. 🤖 **AI Agent** - Intelligent routing to the right tool

---

## 📦 Project Structure

```
version-3/
├── Backend/
│   ├── api.py                          # FastAPI server
│   ├── guardian_agent.py               # AI orchestrator
│   ├── code_tool.py                    # Code compliance scanner
│   ├── qa_tool.py                      # Q&A chat tool
│   ├── legal_tool.py                   # Legal document analyzer
│   ├── requirements.txt                # Python dependencies
│   └── .env                            # Environment variables (create this!)
├── Frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx           # Landing page
│   │   │   ├── CodeAudit.tsx           # Code audit interface
│   │   │   └── QAChat.tsx              # Q&A chat interface
│   │   ├── components/
│   │   │   ├── Navbar.tsx              # Navigation bar
│   │   │   ├── FormattedMessage.tsx    # Formatted chat messages
│   │   │   └── ViolationResults.tsx    # Violation display
│   │   ├── services/
│   │   │   └── api.ts                  # API client
│   │   └── types/
│   │       └── index.ts                # TypeScript types
│   ├── package.json                    # Node dependencies
│   ├── vite.config.ts                  # Vite configuration
│   └── tailwind.config.js              # Tailwind CSS config
└── venv/                                # Python virtual environment (create this!)
```

---

## 🔧 Troubleshooting

### Backend Issues

**Issue:** `ModuleNotFoundError: No module named 'fastapi'`  
**Solution:** Make sure virtual environment is activated and dependencies are installed:
```bash
.\venv\Scripts\Activate.ps1  # Windows
pip install -r Backend/requirements.txt
```

**Issue:** `GOOGLE_API_KEY not found`  
**Solution:** Create `Backend/.env` file with your API key:
```env
GOOGLE_API_KEY=your_actual_api_key_here
```

**Issue:** `Port 8000 already in use`  
**Solution:** Kill the process using port 8000 or change the port in `api.py`

---

### Frontend Issues

**Issue:** `npm: command not found`  
**Solution:** Install Node.js from https://nodejs.org/

**Issue:** `Port 5173 already in use`  
**Solution:** The app will automatically try port 5174. Check terminal output for the actual port.

**Issue:** Frontend can't connect to backend  
**Solution:** Make sure backend is running on http://localhost:8000

---

## ✨ Features

### 1. Code Audit
- Upload compliance PDF documents
- Scan GitHub repositories
- Real-time progress tracking
- Line-by-line violation detection
- Export results

### 2. Q&A Chat
- Repository indexing with vector search
- Interactive chat interface
- Formatted responses (code blocks, lists, bold/italic)
- Session management

### 3. AI Agent
- Intelligent tool routing
- Multi-step reasoning
- Context-aware responses

---

## 🎨 UI Features

- 🌓 **Dark/Light Mode** - Toggle with moon/sun icon
- ⚡ **Real-time Updates** - See progress as files are analyzed
- 📱 **Responsive Design** - Works on all screen sizes
- 🎭 **Animations** - Smooth transitions with Framer Motion
- 🎯 **Modern UI** - Futuristic design with Tailwind CSS

---

## 📝 Additional Notes

### Timeout Configuration
The application has a 24-hour timeout for long-running operations. If you need to change this, edit:
- **Backend:** `Backend/api.py` - Uvicorn timeout settings
- **Frontend:** `Frontend/src/services/api.ts` - Axios timeout (currently 86400000ms)

### Database Files
- ChromaDB stores vector embeddings in `Backend/chroma_db/`
- These files are excluded from git (in `.gitignore`)
- They will be created automatically on first use

### Development Mode
Both servers run in development mode with:
- **Backend:** Auto-reload on file changes (Uvicorn)
- **Frontend:** Hot module replacement (Vite)

---

## 🤝 Need Help?

If you encounter any issues:

1. Check that both servers are running
2. Verify your `.env` file has a valid API key
3. Make sure you're using the correct Python and Node versions
4. Check the terminal output for error messages

For more information, see:
- `PROJECT_COMPLETE.md` - Full project documentation
- `QUICK_START.md` - Quick reference guide
- `BACKEND_FIXED.md` - LangChain/LangGraph migration notes

---

## 🚀 Quick Start Summary

```bash
# 1. Clone and checkout
git clone https://github.com/KarthikSagarP/GuardianAI.git
cd GuardianAI
git checkout Frontend

# 2. Setup backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux
pip install -r Backend/requirements.txt

# 3. Create .env file
echo "GOOGLE_API_KEY=your_key_here" > Backend/.env

# 4. Setup frontend
cd Frontend
npm install
cd ..

# 5. Run backend (Terminal 1)
.\venv\Scripts\python.exe Backend\api.py  # Windows
python Backend/api.py                      # macOS/Linux

# 6. Run frontend (Terminal 2)
cd Frontend
npm run dev

# 7. Open browser
# http://localhost:5173
```

Happy coding! 🎉
