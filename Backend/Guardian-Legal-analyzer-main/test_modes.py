"""
Test script demonstrating the 3 different query modes for the orchestrator
"""

from legal_tool import legal_analyst_tool, query_all_pdfs, get_database_chunk_count

def test_mode_1_single_pdf():
    """
    MODE 1: Single PDF Mode (filter_by_current_pdf=True)
    Use when: Analyzing a specific regulation in isolation
    Only searches chunks from the current PDF
    """
    print("\n" + "=" * 80)
    print("MODE 1: SINGLE PDF MODE (Current PDF Only)")
    print("=" * 80)
    
    pdf_path = "sample_regulation.pdf"
    question = "What are the compliance requirements for data encryption?"
    
    # This will only search chunks from sample_regulation.pdf
    result = legal_analyst_tool(
        pdf_file_path=pdf_path,
        question=question,
        use_existing_db=True,  # Keep accumulated PDFs
        filter_by_current_pdf=True  # But only search this PDF
    )
    
    print("\n📝 Answer (from current PDF only):")
    print(result)
    print("\n" + "=" * 80)


def test_mode_2_multi_pdf():
    """
    MODE 2: Multi-PDF Mode (filter_by_current_pdf=False)
    Use when: Want to consider all accumulated regulations
    Searches all 24 chunks (from 4 PDFs for example)
    """
    print("\n" + "=" * 80)
    print("MODE 2: MULTI-PDF MODE (All Accumulated PDFs)")
    print("=" * 80)
    
    pdf_path = "sample_regulation.pdf"
    question = "What are the compliance requirements for data encryption?"
    
    # This will search ALL chunks in database
    result = legal_analyst_tool(
        pdf_file_path=pdf_path,
        question=question,
        use_existing_db=True,  # Keep accumulated PDFs
        filter_by_current_pdf=False  # Search ALL PDFs
    )
    
    print("\n📝 Answer (from all PDFs):")
    print(result)
    print("\n" + "=" * 80)


def test_mode_3_query_all():
    """
    MODE 3: Query All Mode (dedicated function)
    Use when: Cross-regulation queries
    - Retrieves 10 chunks instead of 5 (broader search)
    - Shows which PDFs contributed to the answer
    - Returns structured response with source information
    """
    print("\n" + "=" * 80)
    print("MODE 3: QUERY ALL MODE (Broad Cross-Regulation Search)")
    print("=" * 80)
    
    question = "What are the compliance requirements for data encryption?"
    
    # This uses dedicated query_all_pdfs() function
    result = query_all_pdfs(
        question=question,
        k=10  # Retrieve 10 chunks for broader coverage
    )
    
    print("\n📝 Answer:")
    print(result['answer'])
    
    print("\n📄 Sources that contributed:")
    for source in result['sources']:
        count = result['chunk_distribution'][source]
        print(f"   • {source}: {count} chunks")
    
    print("\n" + "=" * 80)


def main():
    print("\n" + "🎯" * 40)
    print("ORCHESTRATOR INTEGRATION GUIDE - 3 QUERY MODES")
    print("🎯" * 40)
    
    # Check database status
    total_chunks = get_database_chunk_count()
    print(f"\n📊 Current database: {total_chunks} total chunks")
    
    if total_chunks == 0:
        print("\n⚠️  No database found!")
        print("Please run test_legal_tool.py first to create a database")
        return
    
    print("\n" + "=" * 80)
    print("ORCHESTRATOR USAGE EXAMPLES:")
    print("=" * 80)
    
    # Show example code for orchestrator
    print("""
# For the orchestrator (Person A), here's how to use each mode:

# MODE 1: Analyze ONLY the current PDF (isolated regulation)
result = legal_analyst_tool(
    pdf_file_path="regulation.pdf",
    question="What are the requirements?",
    use_existing_db=True,
    filter_by_current_pdf=True  # ← Single PDF mode
)

# MODE 2: Analyze considering ALL PDFs (multi-regulation context)
result = legal_analyst_tool(
    pdf_file_path="regulation.pdf",  # Still needed for metadata
    question="What are the requirements?",
    use_existing_db=True,
    filter_by_current_pdf=False  # ← Multi-PDF mode
)

# MODE 3: Broad cross-regulation query (dedicated function)
result = query_all_pdfs(
    question="What are the requirements?",
    k=10  # Number of chunks to retrieve
)
# Returns: {'answer': str, 'sources': list, 'chunk_distribution': dict}
    """)
    
    print("\n" + "=" * 80)
    print("Choose a mode to test:")
    print("=" * 80)
    print("1. Single PDF Mode (current PDF only)")
    print("2. Multi-PDF Mode (all accumulated PDFs)")
    print("3. Query All Mode (broad cross-regulation search)")
    print("4. Test all modes")
    print("0. Exit")
    
    choice = input("\nEnter choice (0-4): ").strip()
    
    if choice == "1":
        test_mode_1_single_pdf()
    elif choice == "2":
        test_mode_2_multi_pdf()
    elif choice == "3":
        test_mode_3_query_all()
    elif choice == "4":
        test_mode_1_single_pdf()
        test_mode_2_multi_pdf()
        test_mode_3_query_all()
    elif choice == "0":
        print("Exiting...")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
