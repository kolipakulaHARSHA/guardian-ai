# Guardian AI Frontend

Modern, futuristic React application for AI-powered code compliance and analysis.

## 🎨 Features

- **Futuristic UI/UX** - Modern, sleek interface with smooth animations
- **Dark/Light Mode** - Automatic theme switching with system preference support
- **Code Audit** - Scan repositories for compliance violations
- **Q&A Chat** - Interactive chat interface for repository questions
- **Real-time Analysis** - Live progress indicators and streaming responses
- **Responsive Design** - Works seamlessly on all devices

## 🛠️ Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Beautiful icons
- **React Syntax Highlighter** - Code highlighting

## 📦 Installation

### Prerequisites

- Node.js 18+ and npm/yarn
- Guardian AI Backend running on `localhost:8000`

### Setup

1. **Install dependencies:**
```bash
cd Frontend
npm install
```

2. **Start development server:**
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 🚀 Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## 📁 Project Structure

```
Frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Navbar.tsx
│   │   └── ViolationResults.tsx
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx
│   │   ├── CodeAudit.tsx
│   │   └── QAChat.tsx
│   ├── contexts/         # React contexts
│   │   └── ThemeContext.tsx
│   ├── services/         # API services
│   │   └── api.ts
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration
├── tailwind.config.js   # Tailwind configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies
```

## 🎯 Usage Guide

### 1. Code Audit

1. Navigate to **Code Audit** from the dashboard
2. Enter a GitHub repository URL
3. Upload a compliance PDF document
4. Click **Start Audit**
5. View detailed violation reports with:
   - Violation count and statistics
   - Grouped violations by rule
   - Code snippets with syntax highlighting
   - File locations and line numbers
6. Export results as JSON

### 2. Q&A Chat

1. Navigate to **Q&A Chat** from the dashboard
2. Enter a GitHub repository URL
3. Click **Start Chat** to index the repository
4. Ask questions about the codebase
5. Get instant AI-powered answers
6. Continue the conversation with follow-up questions

## 🎨 Theme Customization

The app supports both light and dark modes. The theme is stored in localStorage and syncs with system preferences.

Toggle theme using the button in the navbar (Moon/Sun icon).

### Custom Colors

Edit `tailwind.config.js` to customize the color palette:

```js
colors: {
  primary: { ... },  // Main accent color
  accent: { ... },   // Secondary accent
  cyber: { ... },    // Futuristic green accent
}
```

## 🔌 API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`.

All API calls are handled through the `api.ts` service:

```typescript
import { api } from '@/services/api';

// Code audit
const result = await api.auditCode({
  repo_url: 'https://github.com/...',
  pdf_path: 'path/to/compliance.pdf',
});

// Q&A
const session = await api.initQASession({ repo_url: '...' });
const answer = await api.askQuestion(sessionId, { question: '...' });
```

## 🐛 Troubleshooting

### Port Already in Use

If port 5173 is in use, Vite will automatically try the next available port.

### API Connection Errors

Ensure the backend is running on `localhost:8000`:
```bash
cd ../Backend
python api.py
```

### Build Errors

Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

## 🚢 Production Deployment

### Build

```bash
npm run build
```

The optimized build will be in the `dist/` directory.

### Preview Build

```bash
npm run preview
```

### Deploy

Deploy the `dist/` folder to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront

**Note:** Update the API base URL in `src/services/api.ts` for production:

```typescript
const client = axios.create({
  baseURL: process.env.VITE_API_URL || 'http://localhost:8000',
});
```

## 📄 License

MIT License - see LICENSE file for details
