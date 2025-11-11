# ⚡ Guardian AI - Quick Reference

## 🚀 Start Commands

### Backend
```bash
cd Backend
python api.py
```
→ Runs on `http://localhost:8000`

### Frontend  
```bash
cd Frontend
npm install    # First time only
npm run dev
```
→ Runs on `http://localhost:5173`

---

## 📡 API Endpoints

| Endpoint | What It Does |
|----------|--------------|
| `POST /api/audit/code` | Audit repository for violations |
| `POST /api/qa/init` | Start Q&A session |
| `POST /api/qa/ask` | Ask repository question |
| `POST /api/upload/pdf` | Upload compliance PDF |
| `GET /health` | Check API status |

Full docs: `http://localhost:8000/docs`

---

## 🎯 Pages

| URL | Page | Purpose |
|-----|------|---------|
| `/` | Dashboard | Landing page, navigation |
| `/audit` | Code Audit | Scan repositories for violations |
| `/qa` | Q&A Chat | Ask questions about codebases |

---

## 🎨 Key Features

✅ Dark/Light theme (auto-saves preference)  
✅ Real-time progress indicators  
✅ Code syntax highlighting  
✅ Export results to JSON  
✅ Interactive chat interface  
✅ Violation grouping by rule  
✅ Responsive design  
✅ Smooth animations  

---

## 🔑 Required Environment Variable

**Backend `.env` file:**
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get your key: https://makersuite.google.com/app/apikey

---

## 📦 Tech Stack

**Backend:**
- FastAPI + Uvicorn
- LangChain
- Google Gemini AI
- ChromaDB + FAISS

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- React Router

---

## 🐛 Quick Fixes

**Backend won't start:**
```bash
pip install -r requirements.txt
# Check .env file exists with GOOGLE_API_KEY
```

**Frontend errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Port conflicts:**
- Backend: Edit port in `api.py` line with `uvicorn.run()`
- Frontend: Vite auto-selects next available port

---

## 📂 File Structure (Simplified)

```
Backend/
  api.py              ← FastAPI server
  requirements.txt    ← Python dependencies
  .env               ← API key (create this!)
  
Frontend/
  src/
    pages/           ← Dashboard, CodeAudit, QAChat
    components/      ← Navbar, ViolationResults
    services/api.ts  ← API calls
  package.json       ← Node dependencies
```

---

## 💡 Common Tasks

**Build for production:**
```bash
cd Frontend
npm run build
# Output: dist/ folder
```

**Run tests:**
```bash
# Backend
cd Backend
pytest

# Frontend
cd Frontend
npm run lint
```

**Update dependencies:**
```bash
# Backend
pip install -r requirements.txt --upgrade

# Frontend
npm update
```

---

## 📊 Default Ports

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Frontend | 5173 | http://localhost:5173 |

---

## 🎬 Typical Workflow

1. Start backend: `cd Backend ; python api.py`
2. Start frontend: `cd Frontend ; npm run dev`
3. Open browser: `http://localhost:5173`
4. Choose analysis type
5. Input repository URL
6. Get results!

---

## 📝 Notes

- First frontend run requires `npm install`
- Backend must run before frontend
- Theme persists in localStorage
- Sessions cleared on backend restart
- TypeScript errors normal until deps installed

---

**Need help?** Check `SETUP_GUIDE.md` or `PROJECT_COMPLETE.md`
