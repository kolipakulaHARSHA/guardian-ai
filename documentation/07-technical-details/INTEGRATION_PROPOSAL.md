# Guardian AI - Integration Proposal

## 🎯 Executive Summary

Currently, you have three independently developed modules that need to work together as a unified system. I propose a **modular integration approach** that maintains each module's independence while enabling seamless collaboration.

---

## 📊 Current State Analysis

### ✅ What's Working Well

1. **Module C (Github_scanner)** - Production Ready
   - Fully standalone with `code_tool.py` and `qa_tool.py`
   - No dependencies on other modules
   - Clean CLI interface
   - Uses latest Gemini models

2. **Module B (Guardian-Legal-analyzer-main)** - Production Ready
   - Functional RAG implementation
   - ChromaDB persistence
   - Can be imported as a library

3. **Module A (GuardianAI-Orchestrator)** - Basic Structure
   - Has orchestration logic
   - Uses mock implementations
   - Needs real integration

### ⚠️ Current Challenges

1. **Mismatch in Contracts**
   - Module C (`code_tool.py`) has evolved beyond the original contract
   - It now has dual modes (audit + compliance) not in original spec
   - Module A expects the old contract function

2. **Duplicate Functionality**
   - Module C's compliance mode overlaps with Module B's purpose
   - Both do regulatory analysis but differently

3. **No Unified Entry Point**
   - Each module runs independently
   - No single command to run full workflow

---

## 🏗️ Proposed Integration Architecture

### Option 1: **Lightweight Wrapper (Recommended for Hackathon)**

Create a thin integration layer that orchestrates existing tools without modifying them.

```
┌─────────────────────────────────────────────────────────────┐
│                     guardian_cli.py                         │
│                  (New Unified Interface)                    │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Command Router                                      │  │
│  │  - Full Pipeline: PDF + Repo → Complete Report      │  │
│  │  - Legal Only: PDF → Technical Brief                │  │
│  │  - Audit Only: Repo + Brief → Violations            │  │
│  │  - Q&A Only: Repo → Interactive Q&A                 │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────┐ ┌──────────────┐
│   Module B      │ │  Module C   │ │  Module C    │
│ legal_tool.py   │ │code_tool.py │ │ qa_tool.py   │
│                 │ │ (audit)     │ │              │
└─────────────────┘ └─────────────┘ └──────────────┘
```

**Pros:**
- ✅ Minimal changes to existing code
- ✅ Fast to implement (1-2 hours)
- ✅ Maintains module independence
- ✅ Easy to test and debug
- ✅ Perfect for hackathon demo

**Cons:**
- ⚠️ Not as "intelligent" as full agent orchestration
- ⚠️ Fixed workflow (less flexible)

---

### Option 2: **Full Agent Orchestration (Advanced)**

Upgrade Module A to use LangChain agents with real tool integration.

```
┌─────────────────────────────────────────────────────────────┐
│              LangChain Agent Orchestrator                   │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Agent Brain (Gemini Pro)                            │  │
│  │  - Analyzes user request                            │  │
│  │  - Decides which tools to use                       │  │
│  │  - Plans multi-step workflows                       │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                │
│         ┌─────────────────┼─────────────────┐             │
│         ▼                 ▼                 ▼             │
│  ┌──────────┐      ┌──────────┐     ┌──────────┐        │
│  │ Tool 1:  │      │ Tool 2:  │     │ Tool 3:  │        │
│  │ Legal    │      │ Audit    │     │ Q&A      │        │
│  │ Analyzer │      │ Agent    │     │ Tool     │        │
│  └──────────┘      └──────────┘     └──────────┘        │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Very flexible and intelligent
- ✅ Can handle complex queries
- ✅ Impressive demo (shows AI reasoning)
- ✅ Extensible for future tools

**Cons:**
- ⚠️ More complex to implement (4-6 hours)
- ⚠️ LangChain agent behavior can be unpredictable
- ⚠️ Higher API costs (more LLM calls)
- ⚠️ Harder to debug

---

### Option 3: **Hybrid Approach (Best of Both Worlds)**

Combine both approaches: Simple CLI for standard workflows + Agent for complex queries.

```
┌─────────────────────────────────────────────────────────────┐
│                   guardian_system.py                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Mode 1: Standard Pipeline (Fast & Reliable)               │
│  ┌───────────────────────────────────────────────┐        │
│  │ PDF → Legal Tool → Brief → Audit Tool → JSON │        │
│  └───────────────────────────────────────────────┘        │
│                                                             │
│  Mode 2: Agent Mode (Flexible & Intelligent)               │
│  ┌───────────────────────────────────────────────┐        │
│  │ User Query → Agent Plans → Calls Tools → Answer│        │
│  └───────────────────────────────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Flexibility for different use cases
- ✅ Reliable standard workflows
- ✅ Impressive agent capabilities when needed
- ✅ Best user experience

**Cons:**
- ⚠️ More code to maintain
- ⚠️ Need to decide when to use which mode

---

## 💻 Implementation Plan (Option 1 - Recommended)

### Step 1: Create Unified CLI (`guardian_cli.py`)

```python
"""
Guardian AI - Unified Command Line Interface
Integrates Legal Analyzer, Code Auditor, and Q&A tools
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add module paths
sys.path.append(str(Path(__file__).parent / 'Guardian-Legal-analyzer-main'))
sys.path.append(str(Path(__file__).parent / 'Github_scanner'))

# Import modules
from legal_tool import legal_analyst_tool
from code_tool import CodeAuditorAgent
from qa_tool import RepoQATool


class GuardianAI:
    """Unified Guardian AI System"""
    
    def __init__(self, model_name="gemini-2.5-pro-preview-03-25"):
        self.model_name = model_name
        self.verify_api_key()
    
    def verify_api_key(self):
        """Ensure API key is set"""
        if not os.environ.get('GOOGLE_API_KEY'):
            raise ValueError("GOOGLE_API_KEY not set")
    
    def full_pipeline(self, pdf_path: str, repo_url: str, output_file: str = None):
        """
        Complete workflow: PDF → Brief → Code Audit → Report
        
        This is the main integration point for all three modules.
        """
        print("="*70)
        print("GUARDIAN AI - FULL COMPLIANCE PIPELINE")
        print("="*70)
        
        # STEP 1: Legal Analysis (Module B)
        print("\n[STEP 1/3] Analyzing Regulatory Document...")
        print("-"*70)
        
        question = (
            "Create a concise, bullet-pointed technical brief for a developer. "
            "List the key compliance requirements from this document that can "
            "be checked in a codebase."
        )
        
        technical_brief = legal_analyst_tool(
            pdf_file_path=pdf_path,
            question=question,
            use_existing_db=True,  # Keep accumulated knowledge
            filter_by_current_pdf=True  # Focus on current PDF
        )
        
        print("\n✅ Technical Brief Generated:")
        print(technical_brief)
        
        # STEP 2: Code Audit (Module C)
        print("\n[STEP 2/3] Auditing Code Repository...")
        print("-"*70)
        
        auditor = CodeAuditorAgent(model_name=self.model_name)
        result = auditor.scan_repository(repo_url, technical_brief)
        
        violations = result.get('violations', [])
        
        print(f"\n✅ Audit Complete: {len(violations)} violations found")
        
        # STEP 3: Format Report
        print("\n[STEP 3/3] Generating Final Report...")
        print("-"*70)
        
        report = {
            "status": "success",
            "regulation_source": pdf_path,
            "repository": repo_url,
            "model_used": self.model_name,
            "technical_brief": technical_brief,
            "total_violations": len(violations),
            "violations": violations,
            "summary": {
                "total_files_scanned": result.get('total_files', 0),
                "files_analyzed": result.get('analyzed_files', 0),
                "critical_violations": len([v for v in violations if 'critical' in v.get('explanation', '').lower()])
            }
        }
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n✅ Report saved to: {output_file}")
        
        return report
    
    def legal_only(self, pdf_path: str, question: str = None):
        """Run only the legal analysis (Module B)"""
        if question is None:
            question = (
                "Summarize the key compliance requirements from this document "
                "in plain English for software developers."
            )
        
        return legal_analyst_tool(pdf_path, question)
    
    def audit_only(self, repo_url: str, brief: str = None, brief_file: str = None):
        """Run only the code audit (Module C)"""
        if brief_file:
            with open(brief_file, 'r') as f:
                brief = f.read()
        elif brief is None:
            raise ValueError("Must provide either 'brief' or 'brief_file'")
        
        auditor = CodeAuditorAgent(model_name=self.model_name)
        return auditor.scan_repository(repo_url, brief)
    
    def qa_session(self, repo_url: str, interactive: bool = True, questions: list = None):
        """Run Q&A session (Module C - qa_tool)"""
        qa_tool = RepoQATool(model_name=self.model_name)
        
        if interactive:
            return qa_tool.ask_questions_interactive(repo_url)
        elif questions:
            results = []
            for q in questions:
                answer = qa_tool.ask_question(repo_url, q)
                results.append({"question": q, "answer": answer})
            return results
        else:
            raise ValueError("Must enable interactive mode or provide questions")


def main():
    """CLI Entry Point"""
    parser = argparse.ArgumentParser(
        description='Guardian AI - Unified Compliance & Code Analysis System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  
  # Full Pipeline: PDF + Repo → Complete Report
  python guardian_cli.py full gdpr.pdf https://github.com/user/repo -o report.json
  
  # Legal Analysis Only
  python guardian_cli.py legal gdpr.pdf
  
  # Code Audit Only (with pre-made brief)
  python guardian_cli.py audit https://github.com/user/repo --brief-file rules.txt
  
  # Interactive Q&A
  python guardian_cli.py qa https://github.com/user/repo
  
  # Q&A with specific questions
  python guardian_cli.py qa https://github.com/user/repo -q "What does this project do?" -q "How is authentication handled?"
        """
    )
    
    parser.add_argument(
        '--model',
        default='gemini-2.5-pro-preview-03-25',
        help='Gemini model to use'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # FULL PIPELINE
    full_parser = subparsers.add_parser('full', help='Run complete pipeline (PDF + Repo → Report)')
    full_parser.add_argument('pdf', help='Path to regulatory PDF')
    full_parser.add_argument('repo', help='GitHub repository URL')
    full_parser.add_argument('-o', '--output', help='Output JSON file path')
    
    # LEGAL ONLY
    legal_parser = subparsers.add_parser('legal', help='Analyze regulatory PDF only')
    legal_parser.add_argument('pdf', help='Path to regulatory PDF')
    legal_parser.add_argument('-q', '--question', help='Custom question to ask')
    
    # AUDIT ONLY
    audit_parser = subparsers.add_parser('audit', help='Audit code repository only')
    audit_parser.add_argument('repo', help='GitHub repository URL')
    audit_parser.add_argument('--brief', help='Technical brief as string')
    audit_parser.add_argument('--brief-file', help='File containing technical brief')
    audit_parser.add_argument('-o', '--output', help='Output JSON file path')
    
    # Q&A
    qa_parser = subparsers.add_parser('qa', help='Interactive Q&A about repository')
    qa_parser.add_argument('repo', help='GitHub repository URL')
    qa_parser.add_argument('-q', '--question', action='append', help='Question to ask (can specify multiple)')
    qa_parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize Guardian AI
    guardian = GuardianAI(model_name=args.model)
    
    try:
        if args.command == 'full':
            result = guardian.full_pipeline(args.pdf, args.repo, args.output)
            print("\n" + "="*70)
            print("FINAL REPORT")
            print("="*70)
            print(f"\nViolations Found: {result['total_violations']}")
            print(f"Files Scanned: {result['summary']['total_files_scanned']}")
            print(f"Files Analyzed: {result['summary']['files_analyzed']}")
            
        elif args.command == 'legal':
            result = guardian.legal_only(args.pdf, args.question)
            print("\n" + "="*70)
            print("TECHNICAL BRIEF")
            print("="*70)
            print(result)
            
        elif args.command == 'audit':
            result = guardian.audit_only(args.repo, args.brief, args.brief_file)
            violations = result.get('violations', [])
            print(f"\nViolations Found: {len(violations)}")
            print(json.dumps(violations[:5], indent=2))  # Show first 5
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n✅ Results saved to: {args.output}")
            
        elif args.command == 'qa':
            if args.interactive or not args.question:
                guardian.qa_session(args.repo, interactive=True)
            else:
                results = guardian.qa_session(args.repo, interactive=False, questions=args.question)
                for r in results:
                    print(f"\nQ: {r['question']}")
                    print(f"A: {r['answer']}\n")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

### Step 2: Update Module Imports

**Create `__init__.py` files** in each module directory to make them proper Python packages:

```python
# Guardian-Legal-analyzer-main/__init__.py
from .legal_tool import legal_analyst_tool

# Github_scanner/__init__.py
from .code_tool import CodeAuditorAgent, code_auditor_agent
from .qa_tool import RepoQATool
```

---

### Step 3: Create Configuration File

**`config.yaml`** - Centralized configuration:

```yaml
# Guardian AI Configuration

models:
  legal_analysis: "gemini-pro"
  code_audit: "gemini-2.5-flash"
  compliance_check: "gemini-2.5-pro-preview-03-25"
  qa_system: "gemini-2.5-pro-preview-03-25"

paths:
  legal_analyzer: "Guardian-Legal-analyzer-main"
  code_scanner: "Github_scanner"
  orchestrator: "GuardianAI-Orchestrator"
  chroma_db: "./chroma_db"

settings:
  chunk_size: 30
  max_violations_display: 10
  enable_caching: true
  verbose: true
```

---

### Step 4: Testing Suite

**`test_integration.py`** - Integration tests:

```python
"""
Integration tests for Guardian AI system
"""

import os
import sys
import json
from pathlib import Path

# Add to path
sys.path.append(str(Path(__file__).parent))

from guardian_cli import GuardianAI


def test_full_pipeline():
    """Test complete PDF → Code audit pipeline"""
    print("\n" + "="*70)
    print("TEST: Full Pipeline Integration")
    print("="*70)
    
    guardian = GuardianAI()
    
    # Use sample files
    pdf_path = "GuardianAI-Orchestrator/sample_regulation.pdf"
    repo_url = "https://github.com/kolipakulaHARSHA/FINANCE_MANAGEMENT_APP"
    
    report = guardian.full_pipeline(pdf_path, repo_url, "test_report.json")
    
    # Validate report structure
    assert 'status' in report
    assert 'violations' in report
    assert 'technical_brief' in report
    assert report['status'] == 'success'
    
    print("\n✅ Full pipeline test PASSED")
    print(f"   Violations found: {len(report['violations'])}")
    
    return report


def test_legal_only():
    """Test legal analysis in isolation"""
    print("\n" + "="*70)
    print("TEST: Legal Analysis Only")
    print("="*70)
    
    guardian = GuardianAI()
    
    brief = guardian.legal_only("GuardianAI-Orchestrator/sample_regulation.pdf")
    
    assert isinstance(brief, str)
    assert len(brief) > 0
    
    print("\n✅ Legal analysis test PASSED")
    print(f"   Brief length: {len(brief)} characters")
    
    return brief


def test_audit_only():
    """Test code audit with predefined brief"""
    print("\n" + "="*70)
    print("TEST: Code Audit Only")
    print("="*70)
    
    guardian = GuardianAI()
    
    brief = """
    - All functions must have docstrings
    - User input must be validated
    - Passwords must be hashed
    """
    
    result = guardian.audit_only(
        repo_url="https://github.com/kolipakulaHARSHA/FINANCE_MANAGEMENT_APP",
        brief=brief
    )
    
    assert 'violations' in result
    assert isinstance(result['violations'], list)
    
    print("\n✅ Audit test PASSED")
    print(f"   Violations found: {len(result['violations'])}")
    
    return result


def test_module_independence():
    """Verify modules can still run independently"""
    print("\n" + "="*70)
    print("TEST: Module Independence")
    print("="*70)
    
    # Test Module B standalone
    sys.path.append('Guardian-Legal-analyzer-main')
    from legal_tool import legal_analyst_tool
    
    brief = legal_analyst_tool(
        "GuardianAI-Orchestrator/sample_regulation.pdf",
        "Summarize compliance requirements",
        use_existing_db=False
    )
    assert len(brief) > 0
    print("   ✓ Module B works standalone")
    
    # Test Module C standalone
    sys.path.append('Github_scanner')
    from code_tool import CodeAuditorAgent
    
    auditor = CodeAuditorAgent()
    result = auditor.scan_repository(
        "https://github.com/kolipakulaHARSHA/FINANCE_MANAGEMENT_APP",
        "Check for security issues"
    )
    assert 'violations' in result
    print("   ✓ Module C works standalone")
    
    print("\n✅ Module independence test PASSED")


if __name__ == "__main__":
    # Check API key
    if not os.environ.get('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY not set")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("GUARDIAN AI - INTEGRATION TEST SUITE")
    print("="*70)
    
    try:
        # Run tests
        test_module_independence()
        brief = test_legal_only()
        audit_result = test_audit_only()
        full_report = test_full_pipeline()
        
        print("\n" + "="*70)
        print("ALL TESTS PASSED ✅")
        print("="*70)
        print(f"\nIntegration is working correctly!")
        print(f"Full pipeline generated {len(full_report['violations'])} violations")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

---

## 📋 Implementation Checklist

### Phase 1: Setup (30 minutes)
- [ ] Create `guardian_cli.py` in root directory
- [ ] Add `__init__.py` to both module directories
- [ ] Create `config.yaml`
- [ ] Update `.gitignore` to exclude `test_report.json`

### Phase 2: Integration (1 hour)
- [ ] Implement `GuardianAI` class
- [ ] Add `full_pipeline()` method
- [ ] Add individual module methods (legal_only, audit_only, qa_session)
- [ ] Create CLI argument parser

### Phase 3: Testing (30 minutes)
- [ ] Create `test_integration.py`
- [ ] Test full pipeline
- [ ] Test individual modules
- [ ] Verify module independence

### Phase 4: Documentation (30 minutes)
- [ ] Update main README.md
- [ ] Add usage examples
- [ ] Create INTEGRATION_GUIDE.md
- [ ] Update architecture diagrams

---

## 🎬 Demo Script (For Hackathon)

### Demo 1: Full Pipeline (The "Wow" Factor)

```bash
# Show the complete AI workflow
python guardian_cli.py full \
  GuardianAI-Orchestrator/sample_regulation.pdf \
  https://github.com/user/webapp \
  -o compliance_report.json

# Then show the beautiful JSON report
cat compliance_report.json | python -m json.tool
```

**What judges see:**
1. AI reads a complex PDF regulation ✨
2. AI understands what to look for 🧠
3. AI scans entire codebase automatically 🔍
4. AI finds specific violations with explanations 📋
5. Professional JSON report generated 📊

### Demo 2: Individual Modules (Show Flexibility)

```bash
# Show it can work in pieces too
python guardian_cli.py legal sample_regulation.pdf

python guardian_cli.py audit https://github.com/user/repo \
  --brief "Check for security issues"

python guardian_cli.py qa https://github.com/user/repo --interactive
```

### Demo 3: Real-World Use Case

```bash
# "Let's check a real open-source project against GDPR"
python guardian_cli.py full \
  regulations/gdpr.pdf \
  https://github.com/popular/webapp \
  -o gdpr_compliance.json
```

---

## 🔧 Advanced Features (Optional Enhancements)

### 1. Web Dashboard
```python
# guardian_web.py
from flask import Flask, render_template, request, jsonify
from guardian_cli import GuardianAI

app = Flask(__name__)
guardian = GuardianAI()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    pdf = request.files['pdf']
    repo_url = request.form['repo_url']
    
    # Save PDF temporarily
    pdf_path = f"/tmp/{pdf.filename}"
    pdf.save(pdf_path)
    
    # Run analysis
    report = guardian.full_pipeline(pdf_path, repo_url)
    
    return jsonify(report)
```

### 2. Batch Processing
```python
def batch_analyze(pdf_path: str, repo_list_file: str):
    """Analyze multiple repositories against one regulation"""
    guardian = GuardianAI()
    
    with open(repo_list_file) as f:
        repos = [line.strip() for line in f if line.strip()]
    
    reports = []
    for repo in repos:
        print(f"\nAnalyzing {repo}...")
        report = guardian.full_pipeline(pdf_path, repo)
        reports.append(report)
    
    return reports
```

### 3. Continuous Monitoring
```python
# Watch for GitHub commits and auto-audit
from github import Github

def monitor_repo(repo_url: str, pdf_path: str):
    """Monitor repository and audit on each commit"""
    guardian = GuardianAI()
    g = Github(os.environ['GITHUB_TOKEN'])
    
    repo = g.get_repo(repo_url)
    latest_commit = repo.get_commits()[0].sha
    
    while True:
        current_commit = repo.get_commits()[0].sha
        
        if current_commit != latest_commit:
            print(f"New commit detected: {current_commit}")
            report = guardian.full_pipeline(pdf_path, repo_url)
            
            if report['total_violations'] > 0:
                send_alert(report)  # Email/Slack notification
            
            latest_commit = current_commit
        
        time.sleep(300)  # Check every 5 minutes
```

---

## 📊 Architecture Comparison

| Feature | Option 1: Wrapper | Option 2: Agent | Option 3: Hybrid |
|---------|-------------------|-----------------|------------------|
| **Implementation Time** | 2 hours | 6 hours | 4 hours |
| **Complexity** | Low | High | Medium |
| **Reliability** | High | Medium | High |
| **Flexibility** | Medium | High | High |
| **Demo Impact** | Good | Excellent | Excellent |
| **Maintenance** | Easy | Hard | Medium |
| **Best For** | Hackathon MVP | Production System | Scalable Product |

---

## 🎯 Recommendation: **Option 1 (Lightweight Wrapper)**

For your hackathon, I strongly recommend **Option 1** because:

1. ✅ **Fast Implementation** - Can be done in 2-3 hours
2. ✅ **Reliable** - Fixed workflow, predictable behavior
3. ✅ **Demo-Ready** - Clear steps, impressive output
4. ✅ **Maintainable** - Easy to debug and extend
5. ✅ **Preserves Work** - Doesn't require rewriting existing modules

You can always upgrade to Option 2 or 3 later after the hackathon!

---

## 🚀 Next Steps

1. **Immediate (Next 30 min):**
   - Create `guardian_cli.py` with basic structure
   - Test imports from all three modules

2. **Short-term (Next 2 hours):**
   - Implement full pipeline method
   - Add CLI argument parsing
   - Create test script

3. **Before Demo (Final hour):**
   - Test with real repositories
   - Prepare demo script
   - Create beautiful output formatting

4. **Post-Hackathon:**
   - Add web dashboard
   - Implement batch processing
   - Consider agent upgrade

---

## 💡 Key Success Factors

1. **Keep it Simple** - Don't over-engineer for the hackathon
2. **Make it Visual** - Pretty output impresses judges
3. **Show Integration** - Emphasize how three AI systems work together
4. **Handle Errors Gracefully** - Demo might have network issues
5. **Have Backup** - Pre-generate reports in case live demo fails

---

## 📞 Support During Integration

If you encounter issues:

1. **Import errors** - Check Python paths and `__init__.py` files
2. **API rate limits** - Use smaller test repos first
3. **ChromaDB locks** - Clear `./chroma_db/` if needed
4. **Memory issues** - Process repos in smaller chunks

Ready to integrate? Start with Step 1 - create `guardian_cli.py`! 🚀
