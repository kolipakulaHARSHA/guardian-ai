# Guardian AI - GitHub Repository Compliance Checker

An intelligent AI-powered tool that scans GitHub repositories and checks them for compliance with coding standards, documentation requirements, and organizational guidelines using Google Gemini AI and LangChain.

## 🌟 Features

- **Repository Scanner** - Clone and analyze GitHub repositories
- **AI-Powered Q&A** - Ask natural language questions about any repository
- **Compliance Checking** - Automatically verify repos against custom guidelines
- **Intelligent Analysis** - Uses RAG (Retrieval Augmented Generation) for accurate results
- **Vector Search** - FAISS-powered semantic search through codebases

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/guardian-ai.git
cd guardian-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
cd Github_scanner
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Usage

#### 1. Scan a Repository
```bash
python cli.py scan https://github.com/username/repo
```

#### 2. Ask Questions
```bash
python cli.py ask https://github.com/username/repo -q "What does this project do?"
```

#### 3. Check Compliance
```bash
python cli.py compliance https://github.com/username/repo -g "Must have README" "Must have tests"
```

## 📚 Documentation

- [Quick Start Guide](Github_scanner/QUICKSTART.md)
- [Gemini Setup](Github_scanner/GEMINI_READY.md)
- [Quick Reference](Github_scanner/QUICK_REFERENCE.md)
- [Project Summary](Github_scanner/PROJECT_SUMMARY.md)

## 🛠️ Tech Stack

- **Python 3.12**
- **LangChain** - Agentic AI framework
- **Google Gemini AI** - Large Language Model (gemini-2.5-flash)
- **FAISS** - Vector database for semantic search
- **GitPython** - Repository cloning and management

## 📦 Project Structure

```
Guardian/
├── Github_scanner/           # Main project directory
│   ├── cli.py               # Command-line interface
│   ├── repo_qa_agent.py     # AI Q&A agent
│   ├── github_repo_tool.py  # Repository scanner
│   ├── examples.py          # Usage examples
│   ├── requirements.txt     # Dependencies
│   └── *.md                 # Documentation
├── venv/                    # Virtual environment (not tracked)
└── README.md               # This file
```

## 🎯 Use Cases

- **Code Review Automation** - Verify coding standards across repos
- **Documentation Compliance** - Ensure all projects have proper docs
- **Security Audits** - Check for security best practices
- **License Verification** - Confirm license files exist
- **Onboarding** - Help new developers understand codebases

## 🔑 Environment Variables

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Built for the Hackathon project to demonstrate Agentic AI capabilities with LangChain and Google Gemini.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made with ❤️ using AI**
