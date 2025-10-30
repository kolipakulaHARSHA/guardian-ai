"""
Test script to verify parallel scanning is working correctly.
"""

import os
import sys
from pathlib import Path

# Add module paths
sys.path.insert(0, str(Path(__file__).parent / 'Github_scanner'))

from code_tool import CodeAuditorAgent

def test_parallel_vs_sequential():
    """Compare parallel vs sequential scanning performance."""
    
    print("="*80)
    print("PARALLEL SCANNING TEST")
    print("="*80)
    
    # Initialize auditor
    auditor = CodeAuditorAgent(
        model_name="gemini-2.5-flash",
        max_workers=3  # Test with 3 parallel workers
    )
    
    print(f"\n✓ Auditor initialized")
    print(f"  - Max workers: {auditor.max_workers}")
    print(f"  - Parallel enabled: {auditor.enable_parallel}")
    print(f"  - Chunk size: {auditor.chunk_size} lines")
    
    # Test with a small repo
    test_brief = """
    Code should not contain:
    - Hardcoded credentials or API keys
    - Deprecated JavaScript functions like 'eval()'
    - Inline styles in HTML/JSX
    """
    
    print(f"\n📋 Test Brief:")
    print(test_brief)
    
    # Test repository
    test_repo = "https://github.com/Aadisheshudupa/3DTinKer"
    
    print(f"\n🔍 Test Repository: {test_repo}")
    print("\nThis test will:")
    print("  1. Clone the repository")
    print("  2. Run a quick scan with parallel processing")
    print("  3. Show real-time progress")
    
    try:
        result = auditor.scan_repository(test_repo, test_brief)
        
        print(f"\n{'='*80}")
        print("RESULTS")
        print(f"{'='*80}")
        print(f"✓ Status: {result['status']}")
        print(f"  - Files analyzed: {result.get('analyzed_files', 0)}")
        print(f"  - Violations found: {result.get('total_violations', 0)}")
        
        if result.get('violations'):
            print(f"\n📊 Sample violations (first 3):")
            for i, violation in enumerate(result['violations'][:3], 1):
                print(f"\n  {i}. {violation.get('file', 'unknown')}")
                print(f"     Line {violation.get('line_number', '?')}: {violation.get('rule_violated', 'N/A')}")
        
        print(f"\n{'='*80}")
        print("✓ Test completed successfully!")
        print("Parallel scanning is working! 🚀")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parallel_vs_sequential()
