"""
Command-Line Interface for Guardian AI GitHub Scanner
Provides an interactive way to scan repositories and check compliance.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

try:
    from repo_qa_agent import RepoQAAgent
    from github_repo_tool import GitHubRepoTool
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
  
  # Check compliance
  python cli.py compliance https://github.com/user/repo --guidelines-file guidelines.txt
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
