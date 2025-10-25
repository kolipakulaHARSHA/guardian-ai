"""
Example usage scripts for Guardian AI GitHub Scanner
Demonstrates various ways to use the tool programmatically.
"""

import os
import json
from github_repo_tool import GitHubRepoTool
from repo_qa_agent import RepoQAAgent


def example_1_basic_scan():
    """Example 1: Basic repository scanning without AI."""
    print("=" * 60)
    print("Example 1: Basic Repository Scanning")
    print("=" * 60)
    
    tool = GitHubRepoTool()
    
    # Clone a small repository
    repo_url = "https://github.com/pallets/flask"
    print(f"\nCloning {repo_url}...")
    
    result = tool.clone_repository(repo_url)
    
    if result['status'] == 'success':
        print(f"✓ Cloned successfully to: {result['local_path']}")
        
        # Get repository summary
        summary = tool.get_repository_summary()
        
        print(f"\nRepository: {summary['repo_metadata']['repo_name']}")
        print(f"Total files: {summary['total_files']}")
        print(f"Total size: {summary['total_size'] / 1024:.2f} KB")
        
        print("\nImportant files found:")
        for file_name in summary['important_files']:
            print(f"  ✓ {file_name}")
        
        print("\nTop file types:")
        sorted_stats = sorted(
            summary['file_statistics'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:5]
        
        for ext, stats in sorted_stats:
            print(f"  {ext}: {stats['count']} files")
        
        # Search for Python files
        python_files = tool.search_files("*.py")
        print(f"\nFound {len(python_files)} Python files")
        
        # Read README
        readme = tool.read_file("README.md")
        if 'content' in readme:
            print(f"\nREADME.md preview (first 200 chars):")
            print(readme['content'][:200] + "...")
        
        # Cleanup
        tool.cleanup()
        print("\n✓ Cleanup completed")
    else:
        print(f"✗ Error: {result['error']}")


def example_2_qa_simple():
    """Example 2: Simple question answering."""
    print("\n" + "=" * 60)
    print("Example 2: Simple Question Answering")
    print("=" * 60)
    
    # Note: Requires GOOGLE_API_KEY environment variable
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠ Skipping - GOOGLE_API_KEY not set")
        return
    
    agent = RepoQAAgent(model_name="gemini-2.5-flash")
    
    # Clone and index a small repository
    repo_url = "https://github.com/pallets/click"
    print(f"\nCloning and indexing {repo_url}...")
    
    result = agent.clone_and_index_repository(
        repo_url,
        file_extensions=['.py', '.md', '.rst']
    )
    
    if result['status'] == 'success':
        print(f"✓ Indexed {result['index_info']['documents_count']} documents")
        
        # Ask some questions
        questions = [
            "What is this project?",
            "What are the main features?",
            "How do I install it?"
        ]
        
        for question in questions:
            print(f"\n❓ {question}")
            answer = agent.ask_question(question)
            print(f"💡 {answer['answer'][:300]}...")
            print(f"   Sources: {answer['source_count']} files")
        
        # Cleanup
        agent.cleanup()
        print("\n✓ Cleanup completed")
    else:
        print(f"✗ Error: {result}")


def example_3_compliance_check():
    """Example 3: Compliance checking."""
    print("\n" + "=" * 60)
    print("Example 3: Compliance Checking")
    print("=" * 60)
    
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠ Skipping - GOOGLE_API_KEY not set")
        return
    
    agent = RepoQAAgent(model_name="gemini-2.5-flash")
    
    repo_url = "https://github.com/pallets/flask"
    print(f"\nChecking compliance for {repo_url}...")
    
    result = agent.clone_and_index_repository(repo_url)
    
    if result['status'] == 'success':
        print("✓ Repository indexed")
        
        # Define compliance guidelines
        guidelines = [
            "The project must have a LICENSE file",
            "The project must have a README with installation instructions",
            "The project must have contribution guidelines",
            "The code should include tests",
            "The project should have security documentation"
        ]
        
        print("\nRunning compliance checks...")
        compliance = agent.check_compliance(guidelines)
        
        print("\n📋 Compliance Report:")
        for i, check in enumerate(compliance['compliance_checks'], 1):
            print(f"\n{i}. {check['guideline']}")
            print(f"   {check['assessment'][:200]}...")
            print(f"   Evidence: {', '.join(check['evidence_sources'][:2])}")
        
        # Save report
        with open('compliance_report.json', 'w') as f:
            json.dump(compliance, f, indent=2)
        print("\n✓ Report saved to compliance_report.json")
        
        # Cleanup
        agent.cleanup()
        print("✓ Cleanup completed")


def example_4_repository_insights():
    """Example 4: Get automated repository insights."""
    print("\n" + "=" * 60)
    print("Example 4: Repository Insights")
    print("=" * 60)
    
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠ Skipping - GOOGLE_API_KEY not set")
        return
    
    agent = RepoQAAgent(model_name="gemini-2.5-flash")
    
    repo_url = "https://github.com/psf/requests"
    print(f"\nAnalyzing {repo_url}...")
    
    result = agent.clone_and_index_repository(
        repo_url,
        file_extensions=['.py', '.md', '.rst', '.txt']
    )
    
    if result['status'] == 'success':
        print("✓ Repository indexed")
        
        print("\n🔍 Getting insights...")
        insights = agent.get_repository_insights()
        
        print("\n📊 Repository Insights:")
        for question, answer in insights.items():
            print(f"\n• {question}")
            print(f"  {answer[:250]}...")
        
        # Cleanup
        agent.cleanup()
        print("\n✓ Cleanup completed")


def example_5_custom_analysis():
    """Example 5: Custom analysis combining both tools."""
    print("\n" + "=" * 60)
    print("Example 5: Custom Analysis")
    print("=" * 60)
    
    # First, use basic tool to get structure
    tool = GitHubRepoTool()
    repo_url = "https://github.com/pytest-dev/pytest"
    
    print(f"\nStep 1: Scanning repository structure...")
    clone_result = tool.clone_repository(repo_url)
    
    if clone_result['status'] == 'success':
        # Get all Python files
        python_files = tool.search_files("*.py")
        test_files = [f for f in python_files if 'test' in f.lower()]
        
        print(f"✓ Found {len(python_files)} Python files")
        print(f"  - {len(test_files)} appear to be test files")
        
        # Get configuration files
        config_files = tool.search_files("*.ini") + tool.search_files("*.cfg") + tool.search_files("*.toml")
        print(f"  - {len(config_files)} configuration files")
        
        # Read package info if available
        if tool.read_file("setup.py").get('type') == 'text':
            print("  - Has setup.py")
        if tool.read_file("pyproject.toml").get('type') == 'text':
            print("  - Has pyproject.toml")
        
        # Now use AI for deeper analysis
        if os.environ.get('GOOGLE_API_KEY'):
            print("\nStep 2: AI-powered analysis...")
            agent = RepoQAAgent(model_name="gemini-2.5-flash")
            agent.repo_tool = tool  # Reuse the cloned repo
            
            # Index only Python and markdown files
            index_result = agent.index_repository(['.py', '.md'])
            print(f"✓ Indexed {index_result['documents_count']} documents")
            
            # Ask specific technical questions
            questions = [
                "What testing framework does this project use?",
                "What are the main architectural components?",
                "How is the plugin system designed?"
            ]
            
            for question in questions:
                answer = agent.ask_question(question)
                print(f"\n❓ {question}")
                print(f"💡 {answer['answer'][:200]}...")
        
        # Cleanup
        tool.cleanup()
        print("\n✓ Cleanup completed")


def main():
    """Run all examples."""
    print("\n🚀 Guardian AI GitHub Scanner - Examples\n")
    
    # Run examples
    example_1_basic_scan()
    
    # Examples 2-5 require Google API key
    if os.environ.get('GOOGLE_API_KEY'):
        example_2_qa_simple()
        example_3_compliance_check()
        example_4_repository_insights()
        example_5_custom_analysis()
    else:
        print("\n⚠ Examples 2-5 require GOOGLE_API_KEY environment variable")
        print("Set it with: $env:GOOGLE_API_KEY='your-key-here'")
    
    print("\n" + "=" * 60)
    print("✓ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
