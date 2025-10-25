# Guardian AI - Project Structure

This document describes the organized structure of the Guardian AI project.

## Directory Layout

```
Github_scanner/
├── cli.py                      # Main CLI entry point
├── github_repo_tool.py         # Repository cloning and management
├── repo_qa_agent.py           # RAG-based Q&A agent (LangChain)
├── code_tool.py               # Line-by-line code auditor
├── contracts.py               # Contract definitions (PROGRESS.md specs)
├── __init__.py                # Package initialization
├── requirements.txt           # Python dependencies
├── .env                       # API keys (gitignored)
├── .env.example              # Template for environment variables
├── README.md                 # Main documentation
│
├── docs/                     # 📁 All documentation
│   ├── examples/             # 📁 Example files and templates
│   │   ├── compliance_guidelines.txt  # Sample compliance rules
│   │   └── examples.py                # Programmatic usage examples
│   ├── QUICKSTART.md
│   ├── QUICK_REFERENCE.md
│   ├── PROJECT_SUMMARY.md
│   ├── AUDIT_MODE_GUIDE.md
│   ├── GEMINI_READY.md
│   ├── GEMINI_MIGRATION.md
│   ├── SETUP_COMPLETE.md
│   └── PROJECT_STRUCTURE.md  # This file
│
├── tests/                    # 📁 Test files
│   └── test_basic.py        # Basic functionality tests
│
└── cloned_repos/            # 📁 Temporary (gitignored)
    └── [temporary clones]   # Auto-cleaned after use
```

## Core Files

### Production Code (7 files)
1. **cli.py** - Command-line interface with 4 commands
2. **github_repo_tool.py** - Git repository operations
3. **repo_qa_agent.py** - RAG mode (LangChain + FAISS)
4. **code_tool.py** - Audit mode (line-by-line analysis)
5. **contracts.py** - Contract function signatures
6. **__init__.py** - Package exports
7. **requirements.txt** - Dependencies

### Configuration (2 files)
1. **.env** - API keys (not in git)
2. **.env.example** - Template for setup

### Documentation (1 + 7 files)
1. **README.md** - Main documentation (root level)
2. **docs/** - All supporting documentation (7 MD files)

### Examples & Tests (2 files)
1. **docs/examples/examples.py** - Code examples
2. **tests/test_basic.py** - Basic tests

## Files Removed (Cleanup)

The following files were removed during project cleanup:

### Deleted Files
- ❌ `list_gemini_models.py` - One-time utility with hardcoded API key (security risk)
- ❌ `click_report.json` - Temporary test output
- ❌ `cloned_repos/click/` - Leftover test clone

### Reorganized Files
- 📁 `compliance_guidelines.txt` → `docs/examples/`
- 📁 `examples.py` → `docs/examples/`
- 📁 `test_basic.py` → `tests/`
- 📁 All *.md files (except README.md) → `docs/`

## File Count Summary

```
Production Code:    7 files
Configuration:      2 files
Documentation:      8 files (1 root + 7 in docs/)
Examples/Tests:     2 files
Templates:          1 file (docs/examples/compliance_guidelines.txt)
───────────────────────────
Total:             20 files
```

## Import Relationships

```
cli.py
├── imports: repo_qa_agent, github_repo_tool, code_tool
├── uses: .env (auto-loads)
└── calls: All 4 modes

repo_qa_agent.py
├── imports: github_repo_tool, langchain (8 components)
└── uses: Google Gemini API

code_tool.py
├── imports: git (GitPython), langchain (1 component)
└── uses: Google Gemini API, .env (auto-loads)

github_repo_tool.py
├── imports: git, shutil, subprocess
└── uses: No AI, pure Git operations

contracts.py
└── Documentation only (defines function signatures)
```

## Usage Paths

### For End Users
```
README.md → QUICKSTART.md → Run CLI commands
```

### For Developers
```
README.md → docs/examples/examples.py → Write custom code
```

### For Understanding Architecture
```
README.md → PROJECT_SUMMARY.md → AUDIT_MODE_GUIDE.md
```

## Best Practices

1. **Keep root clean** - Only README.md and core .py files
2. **All docs in docs/** - Easy to find and maintain
3. **Examples separated** - Clear distinction from production code
4. **Tests in tests/** - Standard Python project structure
5. **Temp files ignored** - cloned_repos/ in .gitignore

## Maintenance Notes

- **cloned_repos/**: Auto-managed, don't commit
- **.env**: Never commit, use .env.example
- **docs/**: Update when adding features
- **tests/**: Add tests as you add features
- **examples/**: Update with new usage patterns

---

Last Updated: October 25, 2025
Cleanup Performed: Removed 3 files, reorganized 10 files into proper directories
