"""
Test script for the Legal Analyst Tool with ChromaDB persistence management
This demonstrates how the tool will be used by Person A (Orchestrator)
"""

import os
from legal_tool import legal_analyst_tool, clear_database, get_database_info, get_database_chunk_count

def main():
    # Show current database status (without opening it to avoid locks)
    print("=" * 80)
    print("TESTING LEGAL ANALYST TOOL - PERSISTENCE MANAGEMENT")
    print("=" * 80)
    
    db_info = get_database_info()
    print("\n📊 Current Database Status:")
    if db_info['exists']:
        print(f"   ✅ Database exists at: {db_info['path']}")
        print(f"   💾 Size: {db_info['size_mb']} MB")
    else:
        print(f"   ℹ️  No database found - will create new one")
    
    # Example 1: Using the tool with a sample PDF
    pdf_path = "sample_regulation1.pdf"  # Update this path
    
    # The question that the orchestrator will ask
    question = """Create a concise, bullet-pointed technical brief for a developer. 
    This brief should list the key compliance requirements from this document that can be 
    checked in a codebase. Focus on actionable items that can be verified through code analysis.
    
    For each requirement, specify:
    - What to check
    - Where to check it (file types, code patterns)
    - Example violations
    """
    
    print("\n" + "=" * 80)
    print(f"\n📄 PDF Path: {pdf_path}")
    print(f"\n❓ Question: {question}")
    print("\n" + "=" * 80)
    
    if not os.path.exists(pdf_path):
        print(f"\n⚠️  ERROR: PDF file not found at '{pdf_path}'")
        return
    
    # Ask user about search mode
    if db_info['exists']:
        print("\n" + "=" * 80)
        print("🔍 SEARCH MODE SELECTION")
        print("=" * 80)
        print("\nHow should the tool search for relevant information?")
        print("\nOptions:")
        print("  [1] Single PDF Mode - Search only the current PDF (default)")
        print("  [2] Multi-PDF Mode - Search all PDFs in the database")
        print("  [3] Query All Mode - Broader search across all PDFs (top 10 chunks)")
        
        while True:
            response = input("\nSelect mode (1/2/3) [default: 1]: ").strip()
            if response == '' or response == '1':
                filter_mode = True
                mode_name = "Single PDF Mode"
                break
            elif response == '2':
                filter_mode = False
                mode_name = "Multi-PDF Mode"
                break
            elif response == '3':
                mode_name = "Query All Mode"
                filter_mode = None  # Special flag for query_all_pdfs
                break
            else:
                print("⚠️  Please enter 1, 2, or 3")
        
        print(f"\n✅ Selected: {mode_name}")
    else:
        # No database exists, default to single PDF mode
        filter_mode = True
        mode_name = "Single PDF Mode (new database)"
    
    try:
        # Call the tool (this is what Person A will do)
        if filter_mode is None:
            # Use query_all_pdfs for mode 3
            from legal_tool import query_all_pdfs
            print("\n" + "=" * 80)
            print("🔍 Using Query All Mode - Searching across all PDFs")
            print("=" * 80)
            
            result_dict = query_all_pdfs(question, k=10)
            result = result_dict['answer']
            
            print(f"\n📊 Search Results:")
            print(f"   � PDFs referenced: {', '.join(result_dict['sources'])}")
            print(f"   📄 Chunk distribution:")
            for pdf, count in result_dict['chunk_distribution'].items():
                print(f"      • {pdf}: {count} chunks")
        else:
            # Use regular legal_analyst_tool with filter_by_current_pdf parameter
            result = legal_analyst_tool(pdf_path, question, filter_by_current_pdf=filter_mode)
        
        print("\n" + "=" * 80)
        print("✅ TECHNICAL BRIEF GENERATED:")
        print("=" * 80)
        print(result)
        print("=" * 80)
        
        # Show updated database status
        print("\n📊 Updated Database Status:")
        db_info = get_database_info()
        if db_info['exists']:
            print(f"   ✅ Database at: {db_info['path']}")
            chunk_count = get_database_chunk_count()  # Now safe to check
            print(f"   📄 Total chunks: {chunk_count}")
            print(f"   💾 Size: {db_info['size_mb']} MB")
        
        print("\n✅ Success! Your Legal Analyst Tool is working correctly.")
        print("\nThis technical brief will be passed to Person C (Code Auditor)")
        print("who will use it to analyze code repositories for violations.")
        
        print("\n" + "=" * 80)
        print("ℹ️  PERSISTENCE TIPS:")
        print("=" * 80)
        print("• Run again with 'Y' to accumulate multiple PDFs (chat memory)")
        print("• Run again with 'N' to analyze only the new PDF")
        print("• Database persists at: ./chroma_db/")
        print("• Use clear_database() function to start completely fresh")
        print("\n" + "=" * 80)
        print("ℹ️  SEARCH MODE TIPS:")
        print("=" * 80)
        print("• Mode 1 (Single PDF): Fast, focused on current document only")
        print("• Mode 2 (Multi-PDF): Searches all accumulated PDFs together")
        print("• Mode 3 (Query All): Broader search with more chunks (top 10)")
        print("• Orchestrator can set filter_by_current_pdf=True/False programmatically")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check that GOOGLE_API_KEY is set in your .env file")
        print("2. Verify the PDF file is readable and not corrupted")
        print("3. Check your internet connection (needed for API calls)")
        print(f"\n\nFull error details:\n{type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
