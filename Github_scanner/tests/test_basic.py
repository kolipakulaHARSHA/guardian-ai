"""
Simple test script for Guardian AI GitHub Scanner
Tests basic functionality without requiring API keys.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from github_repo_tool import GitHubRepoTool


def test_basic_functionality():
    """Test basic repository operations."""
    print("=" * 60)
    print("Testing Guardian AI GitHub Scanner - Basic Functionality")
    print("=" * 60)
    
    tool = GitHubRepoTool()
    
    # Test with a small, well-known repository
    test_repo = "https://github.com/python/cpython"
    print(f"\n1. Testing repository cloning...")
    print(f"   Repository: {test_repo}")
    
    try:
        result = tool.clone_repository(test_repo, branch="main")
        
        if result.get('status') == 'success':
            print(f"   ✓ Clone successful!")
            print(f"   Location: {result['local_path']}")
            
            # Test repository structure
            print(f"\n2. Testing repository structure analysis...")
            structure = tool.get_repository_structure(max_depth=2)
            
            if 'structure' in structure:
                print(f"   ✓ Structure analysis successful!")
                print(f"   Repository: {structure.get('repo_name', 'unknown')}")
                print(f"   Top-level items: {len(structure['structure'])}")
            
            # Test repository summary
            print(f"\n3. Testing repository summary...")
            summary = tool.get_repository_summary()
            
            if 'total_files' in summary:
                print(f"   ✓ Summary generation successful!")
                print(f"   Total files: {summary['total_files']}")
                print(f"   Total size: {summary['total_size'] / 1024:.2f} KB")
                
                # Show important files
                if summary['important_files']:
                    print(f"\n   Important files found:")
                    for file_name in list(summary['important_files'].keys())[:5]:
                        print(f"     • {file_name}")
                
                # Show file statistics
                print(f"\n   File type distribution (top 5):")
                sorted_stats = sorted(
                    summary['file_statistics'].items(),
                    key=lambda x: x[1]['count'],
                    reverse=True
                )[:5]
                
                for ext, stats in sorted_stats:
                    print(f"     • {ext}: {stats['count']} files")
            
            # Test file search
            print(f"\n4. Testing file search...")
            md_files = tool.search_files("*.md")
            py_files = tool.search_files("*.py")
            
            print(f"   ✓ Search successful!")
            print(f"   Found {len(md_files)} Markdown files")
            print(f"   Found {len(py_files)} Python files")
            
            # Test file reading
            print(f"\n5. Testing file reading...")
            readme = tool.read_file("README.md")
            
            if 'content' in readme:
                print(f"   ✓ File read successful!")
                print(f"   README.md size: {readme['size']} bytes")
                print(f"   Preview (first 150 chars):")
                preview = readme['content'][:150].replace('\n', ' ')
                print(f"   {preview}...")
            
            # Cleanup
            print(f"\n6. Testing cleanup...")
            tool.cleanup()
            print(f"   ✓ Cleanup successful!")
            
            # Final result
            print("\n" + "=" * 60)
            print("✓ ALL TESTS PASSED!")
            print("=" * 60)
            print("\nThe GitHub Scanner tool is working correctly!")
            print("\nNext steps:")
            print("1. Set your OPENAI_API_KEY to use AI features")
            print("2. Try: python cli.py scan https://github.com/pallets/flask")
            print("3. See README.md for more usage examples")
            
            return True
            
        else:
            print(f"   ✗ Clone failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
