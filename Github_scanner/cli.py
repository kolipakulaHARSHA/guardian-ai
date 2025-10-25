"""
Command-Line Interface for Guardian AI GitHub Scanner
Provides an interactive way to scan repositories and check compliance.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import List, Optional

# Load environment variables from .env file if it exists
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

try:
    from repo_qa_agent import RepoQAAgent
    from github_repo_tool import GitHubRepoTool
    from code_tool import code_auditor_agent, CodeAuditorAgent
except ImportError:
    print("Error: Make sure you're running this from the Github_scanner directory")
    print("Or install the package in development mode")
    sys.exit(1)


def scan_repository(args):
    """Scan a repository and provide a summary."""
    tool = GitHubRepoTool()
    
    print(f"Cloning repository: {args.repo_url}")
    result = tool.clone_repository(args.repo_url, args.branch)
    
    if result.get('status') == 'error':
        print(f"Error: {result.get('error')}")
        return
    
    print(f"✓ Successfully cloned to: {result['local_path']}\n")
    
    # Get repository summary
    print("Analyzing repository...")
    summary = tool.get_repository_summary()
    
    print("\n=== Repository Summary ===")
    print(f"Repository: {summary['repo_metadata']['repo_name']}")
    print(f"Total Files: {summary['total_files']}")
    print(f"Total Size: {summary['total_size'] / 1024:.2f} KB")
    
    print("\n=== Important Files ===")
    for file_name, path in summary['important_files'].items():
        print(f"  ✓ {file_name}")
    
    print("\n=== File Statistics ===")
    for ext, stats in sorted(summary['file_statistics'].items(), 
                             key=lambda x: x[1]['count'], reverse=True)[:10]:
        print(f"  {ext}: {stats['count']} files ({stats['total_size'] / 1024:.2f} KB)")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n✓ Full summary saved to: {args.output}")
    
    if not args.keep:
        tool.cleanup()
        print("\n✓ Cleaned up cloned repository")


def ask_questions(args):
    """Clone repository and answer questions using AI."""
    print("Initializing QA Agent...")
    agent = RepoQAAgent(model_name=args.model)
    
    print(f"\nCloning and indexing repository: {args.repo_url}")
    result = agent.clone_and_index_repository(
        args.repo_url,
        args.branch,
        file_extensions=args.extensions.split(',') if args.extensions else None
    )
    
    if result.get('status') == 'error':
        print(f"Error: {result.get('error')}")
        return
    
    index_info = result.get('index_info', {})
    print(f"✓ Indexed {index_info.get('documents_count', 0)} documents "
          f"({index_info.get('chunks_count', 0)} chunks)\n")
    
    # Interactive question mode
    if args.interactive:
        print("=== Interactive Question Mode ===")
        print("Ask questions about the repository (type 'exit' to quit)\n")
        
        while True:
            question = input("Question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                break
            
            if not question:
                continue
            
            answer = agent.ask_question(question)
            print(f"\nAnswer: {answer['answer']}")
            print(f"Sources ({answer['source_count']} files):")
            for src in answer['sources'][:3]:
                print(f"  - {src['file']}")
            print()
    
    # Single question mode
    elif args.question:
        answer = agent.ask_question(args.question)
        print(f"Question: {answer['question']}\n")
        print(f"Answer: {answer['answer']}\n")
        print(f"Sources ({answer['source_count']} files):")
        for src in answer['sources']:
            print(f"  - {src['file']}")
    
    if not args.keep:
        agent.cleanup()
        print("\n✓ Cleaned up resources")


def check_compliance(args):
    """Check repository compliance against guidelines."""
    print("Initializing Compliance Checker...")
    agent = RepoQAAgent(model_name=args.model)
    
    print(f"\nCloning and indexing repository: {args.repo_url}")
    result = agent.clone_and_index_repository(args.repo_url, args.branch)
    
    if result.get('status') == 'error':
        print(f"Error: {result.get('error')}")
        return
    
    print(f"✓ Repository indexed successfully\n")
    
    # Load compliance guidelines
    guidelines = []
    if args.guidelines_file:
        with open(args.guidelines_file, 'r') as f:
            guidelines = [line.strip() for line in f if line.strip()]
    elif args.guidelines:
        guidelines = args.guidelines
    else:
        # Default compliance checks
        guidelines = [
            "The project must have a LICENSE file",
            "The project must have a README with installation instructions",
            "The project must have proper documentation",
            "The code should follow security best practices",
            "The project should have a clear contribution guide"
        ]
    
    print("=== Running Compliance Checks ===\n")
    compliance = agent.check_compliance(guidelines)
    
    for i, check in enumerate(compliance['compliance_checks'], 1):
        print(f"{i}. Guideline: {check['guideline']}")
        print(f"   Assessment: {check['assessment']}")
        print(f"   Evidence from: {', '.join(check['evidence_sources'][:3])}")
        print()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(compliance, f, indent=2)
        print(f"✓ Compliance report saved to: {args.output}")
    
    if not args.keep:
        agent.cleanup()
        print("\n✓ Cleaned up resources")


def audit_code(args):
    """
    Perform line-by-line code audit following PROGRESS.md Person C specifications.
    This uses exhaustive scanning instead of RAG.
    """
    print("="*70)
    print("CODE AUDITOR AGENT - Line-by-Line Analysis")
    print("="*70)
    
    # Create technical brief from guidelines
    if args.brief_file:
        with open(args.brief_file, 'r') as f:
            technical_brief = f.read()
    elif args.brief:
        technical_brief = '\n'.join(args.brief)
    else:
        # Default technical brief
        technical_brief = """
        Code Quality Requirements:
        1. All functions must have docstrings explaining their purpose
        2. Code should follow security best practices
        3. No hardcoded credentials or sensitive data
        4. Proper error handling should be in place
        """
    
    print(f"\nRepository: {args.repo_url}")
    print(f"\nTechnical Brief:")
    print(technical_brief)
    print("\n" + "="*70)
    
    # Run the audit using contract function
    if args.detailed:
        # Use the class for more control
        auditor = CodeAuditorAgent(
            model_name=args.model,
            chunk_size=args.chunk_size
        )
        result = auditor.scan_repository(args.repo_url, technical_brief)
        violations = result['violations']
        
        # Display detailed results
        print(f"\n\n=== AUDIT RESULTS ===")
        print(f"Total files scanned: {result['total_files']}")
        print(f"Files analyzed: {result['analyzed_files']}")
        print(f"Violations found: {result['total_violations']}")
        print("="*70)
    else:
        # Use contract function directly
        violations_json = code_auditor_agent(args.repo_url, technical_brief)
        violations = json.loads(violations_json)
        
        print(f"\n\n=== AUDIT RESULTS ===")
        print(f"Violations found: {len(violations)}")
        print("="*70)
    
    # Display violations
    if violations:
        display_count = args.max_display if args.max_display else len(violations)
        
        for i, violation in enumerate(violations[:display_count], 1):
            print(f"\nViolation {i}:")
            print(f"  File: {violation.get('file_path', 'N/A')}")
            print(f"  Line: {violation.get('line_number', 'N/A')}")
            print(f"  Rule Violated: {violation.get('rule_violated', 'N/A')}")
            print(f"  Explanation: {violation.get('explanation', 'N/A')}")
            
            code = violation.get('violating_code', 'N/A')
            if len(code) > 150:
                code = code[:150] + "..."
            print(f"  Code:\n    {code}")
        
        if len(violations) > display_count:
            print(f"\n... and {len(violations) - display_count} more violations")
    else:
        print("\n✓ No violations found! Repository complies with all rules.")
    
    # Save to file if requested
    if args.output:
        output_data = {
            'repository': args.repo_url,
            'technical_brief': technical_brief,
            'total_violations': len(violations),
            'violations': violations
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\n✓ Audit report saved to: {args.output}")


def main():
    parser = argparse.ArgumentParser(
        description="Guardian AI - GitHub Repository Scanner and Compliance Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a repository
  python cli.py scan https://github.com/user/repo
  
  # Ask questions interactively
  python cli.py ask https://github.com/user/repo --interactive
  
  # Ask a specific question
  python cli.py ask https://github.com/user/repo -q "What is this project about?"
  
  # Check compliance (RAG mode)
  python cli.py compliance https://github.com/user/repo --guidelines-file guidelines.txt
  
  # Code audit (Line-by-line mode - PROGRESS.md Person C)
  python cli.py audit https://github.com/user/repo --brief "All functions must have docstrings"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan and summarize a repository')
    scan_parser.add_argument('repo_url', help='GitHub repository URL')
    scan_parser.add_argument('-b', '--branch', default='main', help='Branch to clone (default: main)')
    scan_parser.add_argument('-o', '--output', help='Output file for JSON summary')
    scan_parser.add_argument('-k', '--keep', action='store_true', help='Keep cloned repository')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask questions about a repository')
    ask_parser.add_argument('repo_url', help='GitHub repository URL')
    ask_parser.add_argument('-b', '--branch', default='main', help='Branch to clone (default: main)')
    ask_parser.add_argument('-q', '--question', help='Question to ask')
    ask_parser.add_argument('-i', '--interactive', action='store_true', help='Interactive question mode')
    ask_parser.add_argument('-m', '--model', default='gemini-2.5-flash', help='LLM model to use (default: gemini-2.5-flash)')
    ask_parser.add_argument('-e', '--extensions', help='Comma-separated file extensions to index')
    ask_parser.add_argument('-k', '--keep', action='store_true', help='Keep cloned repository')
    
    # Compliance command
    compliance_parser = subparsers.add_parser('compliance', help='Check repository compliance')
    compliance_parser.add_argument('repo_url', help='GitHub repository URL')
    compliance_parser.add_argument('-b', '--branch', default='main', help='Branch to clone (default: main)')
    compliance_parser.add_argument('-f', '--guidelines-file', help='File containing compliance guidelines')
    compliance_parser.add_argument('-g', '--guidelines', nargs='+', help='Compliance guidelines')
    compliance_parser.add_argument('-m', '--model', default='gemini-2.5-flash', help='LLM model to use (default: gemini-2.5-flash)')
    compliance_parser.add_argument('-o', '--output', help='Output file for compliance report')
    compliance_parser.add_argument('-k', '--keep', action='store_true', help='Keep cloned repository')
    
    # Audit command (Person C - PROGRESS.md line-by-line scanning)
    audit_parser = subparsers.add_parser('audit', help='Line-by-line code audit (Person C from PROGRESS.md)')
    audit_parser.add_argument('repo_url', help='GitHub repository URL')
    audit_parser.add_argument('-f', '--brief-file', help='File containing technical brief')
    audit_parser.add_argument('-b', '--brief', nargs='+', help='Technical brief (compliance rules)')
    audit_parser.add_argument('-m', '--model', default='gemini-2.5-flash', help='LLM model to use (default: gemini-2.5-flash)')
    audit_parser.add_argument('-c', '--chunk-size', type=int, default=30, help='Lines per chunk (default: 30, range: 20-40)')
    audit_parser.add_argument('-o', '--output', help='Output file for audit report')
    audit_parser.add_argument('--max-display', type=int, help='Maximum violations to display (default: all)')
    audit_parser.add_argument('--detailed', action='store_true', help='Show detailed scan statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'scan':
            scan_repository(args)
        elif args.command == 'ask':
            ask_questions(args)
        elif args.command == 'compliance':
            check_compliance(args)
        elif args.command == 'audit':
            audit_code(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
