# legal_tool.py
# Person B: The Legal Analyst Tool (RAG)

import os
import shutil
import hashlib
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

# Load environment variables from .env file
load_dotenv()

# ChromaDB persistence directory
CHROMA_DB_DIR = "./chroma_db"


def legal_analyst_tool(pdf_file_path: str, question: str, use_existing_db: bool = None, filter_by_current_pdf: bool = True) -> str:
    """
    Analyzes a regulatory PDF document using RAG.
    Takes the file path of the PDF and a question (e.g., "Create a technical brief for a developer...").
    Returns a string containing a plain-English, human-readable technical brief.
    
    Args:
        pdf_file_path: Path to the PDF document to analyze
        question: The question to answer based on the document
        use_existing_db: If True, keep existing ChromaDB data and add to it
                        If False, delete existing data and start fresh
                        If None, ask the user interactively
        filter_by_current_pdf: If True, only search chunks from the current PDF (default)
                              If False, search all chunks in database (multi-PDF mode)
    
    Returns:
        A plain-English technical brief as a string
    """
    
    # Check if ChromaDB already exists
    db_exists = os.path.exists(CHROMA_DB_DIR)
    
    # Decide whether to keep or delete existing database
    if db_exists:
        if use_existing_db is None:
            # Ask the user interactively
            print("\n" + "=" * 80)
            print("📁 EXISTING DATABASE DETECTED")
            print("=" * 80)
            print(f"\nA ChromaDB database already exists at: {CHROMA_DB_DIR}")
            print("\nOptions:")
            print("  [Y] Keep existing data (accumulate PDFs - like chat memory)")
            print("  [N] Delete and start fresh (analyze only this PDF)")
            
            while True:
                response = input("\nKeep existing database? (Y/N): ").strip().upper()
                if response in ['Y', 'N']:
                    use_existing_db = (response == 'Y')
                    break
                print("⚠️  Please enter Y or N")
        
        if use_existing_db:
            print("\n✅ Keeping existing database - will add new PDF to existing knowledge")
        else:
            print("\n🗑️  Deleting existing database - starting fresh")
            # Need to wait for Windows to release file handles
            import time
            import gc
            gc.collect()  # Force garbage collection to close any open handles
            time.sleep(0.5)  # Give Windows time to release file locks
            
            # Try to delete, with retry logic for Windows
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    shutil.rmtree(CHROMA_DB_DIR)
                    print("✅ Database deleted")
                    break
                except PermissionError as e:
                    if attempt < max_retries - 1:
                        print(f"⏳ Waiting for file locks to release (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(1)
                    else:
                        print(f"⚠️  Warning: Could not delete database. Trying alternative approach...")
                        # Alternative: rename the directory and create a new one
                        backup_name = f"{CHROMA_DB_DIR}_backup_{int(time.time())}"
                        try:
                            os.rename(CHROMA_DB_DIR, backup_name)
                            print(f"✅ Old database moved to: {backup_name}")
                            print("   You can manually delete it later when the process releases the files")
                        except Exception as rename_error:
                            raise Exception(f"Cannot delete or rename database. Please close all programs using it and try again. Error: {e}")
    else:
        print("\n📝 No existing database found - creating new one")
    
    # Step 1: Document Ingestion
    loader = PyPDFLoader(pdf_file_path)
    documents = loader.load()
    
    # Step 2: Text Splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from the document")
    
    # Step 2.5: Generate unique IDs for each chunk based on content hash
    # This prevents duplicates even if the same PDF is processed multiple times
    chunk_ids = []
    for chunk in chunks:
        # Create a unique ID based on the actual text content
        content_hash = hashlib.sha256(chunk.page_content.encode()).hexdigest()
        # Use first 16 chars of hash as ID (still virtually collision-free)
        chunk_ids.append(content_hash[:16])
    
    # Step 3: Create Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Step 4: Create or Load Vector Store
    if os.path.exists(CHROMA_DB_DIR) and use_existing_db:
        # Load existing database and add new chunks
        # print("Loading existing vector store...")
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embeddings
        )
        chunks_before = vectorstore._collection.count()
        # print(f"Existing database loaded ({chunks_before} chunks)")
        
        # Check which chunks already exist by querying existing IDs
        try:
            existing_data = vectorstore._collection.get(ids=chunk_ids, include=[])
            existing_ids = set(existing_data['ids']) if existing_data['ids'] else set()
        except Exception:
            # If get fails, assume no existing IDs
            existing_ids = set()
        
        # Filter out chunks that already exist
        new_chunks = []
        new_chunk_ids = []
        for i, (chunk, chunk_id) in enumerate(zip(chunks, chunk_ids)):
            if chunk_id not in existing_ids:
                new_chunks.append(chunk)
                new_chunk_ids.append(chunk_id)
        
        duplicates_skipped = len(chunks) - len(new_chunks)
        
        if new_chunks:
            # print(f"Adding {len(new_chunks)} new unique chunks to existing database...")
            if duplicates_skipped > 0:
                print(f"⏭️  {duplicates_skipped} duplicate chunks detected (skipping)")
            vectorstore.add_documents(documents=new_chunks, ids=new_chunk_ids)
            # print(f"✅ {len(new_chunks)} new chunks added to database")
        else:
            print(f"⏭️  All {len(chunks)} chunks already exist in database (skipping)")
    else:
        # Create new database
        # print("Creating new vector store...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_DB_DIR,
            ids=chunk_ids
        )
        # print(f"✅ New database created at: {CHROMA_DB_DIR}")
    
    # Get total chunks in database
    total_chunks = vectorstore._collection.count()
    print(f"📊 Total chunks in database: {total_chunks}")
    
    # Step 5: Initialize LLM
    # print("\nInitializing LLM...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )
    
    # Step 6: Retrieve relevant documents and create context
    # print("Retrieving relevant documents...")
    
    if filter_by_current_pdf:
        # Single PDF Mode: Only search chunks from the current PDF
        current_pdf_name = os.path.basename(pdf_file_path)
        
        # Get all documents and filter by current PDF
        retriever = vectorstore.as_retriever(search_kwargs={"k": 20})  # Get more to filter
        all_relevant_docs = retriever.invoke(question)
        
        # Filter to only chunks from the current PDF
        relevant_docs = [
            doc for doc in all_relevant_docs 
            if doc.metadata.get('source', '').endswith(current_pdf_name)
        ][:5]  # Take top 5 from current PDF
        
        if relevant_docs:
            print(f"🔍 Searching only current PDF: {current_pdf_name}")
        else:
            # Fallback: if no chunks from current PDF found, use all
            print(f"⚠️  No chunks from current PDF found, using all chunks")
            relevant_docs = all_relevant_docs[:5]
    else:
        # Multi-PDF Mode: Search all chunks in database
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        relevant_docs = retriever.invoke(question)
        print(f"🔍 Searching all PDFs in database")
    
    # Show which documents the chunks came from
    source_files = set()
    for doc in relevant_docs:
        if 'source' in doc.metadata:
            source_files.add(os.path.basename(doc.metadata['source']))
    if source_files:
        print(f"📄 Sources used: {', '.join(source_files)}")
    
    # Step 7: Create context from retrieved documents
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    # Step 8: Create prompt and get answer
    # print("Generating technical brief...")
    prompt = f"""Answer the question based only on the following context from a regulatory document:

Context:
{context}

Question: {question}

Answer:"""
    
    response = llm.invoke(prompt)
    result = response.content
    
    return result


def clear_database():
    """
    Manually clear the ChromaDB database.
    Useful for starting completely fresh.
    """
    if os.path.exists(CHROMA_DB_DIR):
        shutil.rmtree(CHROMA_DB_DIR)
        print(f"✅ Database cleared: {CHROMA_DB_DIR}")
        return True
    else:
        print(f"ℹ️  No database found at: {CHROMA_DB_DIR}")
        return False


def query_all_pdfs(question: str, k: int = 10) -> dict:
    """
    Query across all PDFs in the database with broader search.
    Use this for cross-regulation queries.
    
    Args:
        question: The question to answer
        k: Number of chunks to retrieve (default 10 for broader search)
    
    Returns:
        dict with 'answer' (str) and 'sources' (list of PDF filenames)
    """
    if not os.path.exists(CHROMA_DB_DIR):
        return {
            'answer': "No database found. Please process at least one PDF first.",
            'sources': []
        }
    
    print(f"🔍 Querying all PDFs in database (retrieving top {k} chunks)")
    
    # Load database
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )
    
    total_chunks = vectorstore._collection.count()
    print(f"📊 Searching across {total_chunks} total chunks")
    
    # Retrieve relevant documents
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    relevant_docs = retriever.invoke(question)
    
    # Track which PDFs contributed
    source_files = {}
    for doc in relevant_docs:
        if 'source' in doc.metadata:
            source_name = os.path.basename(doc.metadata['source'])
            source_files[source_name] = source_files.get(source_name, 0) + 1
    
    print(f"📄 Sources contributing to answer:")
    for source, count in source_files.items():
        print(f"   • {source}: {count} chunks")
    
    # Create context and generate answer
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )
    
    prompt = f"""Answer the question based only on the following context from multiple regulatory documents:

Context:
{context}

Question: {question}

Answer:"""
    
    response = llm.invoke(prompt)
    
    return {
        'answer': response.content,
        'sources': list(source_files.keys()),
        'chunk_distribution': source_files
    }


def get_database_info():
    """
    Get information about the current database without opening it.
    This avoids file locks on Windows.
    """
    if not os.path.exists(CHROMA_DB_DIR):
        return {
            'exists': False,
            'total_chunks': 0,
            'size_mb': 0
        }
    
    # Calculate folder size
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(CHROMA_DB_DIR):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                # Skip files that can't be accessed
                pass
    
    return {
        'exists': True,
        'total_chunks': "Check after loading",  # Don't open DB to avoid locks
        'size_mb': round(total_size / (1024 * 1024), 2),
        'path': CHROMA_DB_DIR
    }


def get_database_chunk_count():
    """
    Get the current chunk count from the database.
    Only call this when you're sure you won't need to delete the database after.
    """
    if not os.path.exists(CHROMA_DB_DIR):
        return 0
    
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embeddings
        )
        chunk_count = vectorstore._collection.count()
        
        # Explicitly delete the vectorstore to release file handles
        del vectorstore
        import gc
        gc.collect()
        
        return chunk_count
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Independent testing
    # Make sure to set your GOOGLE_API_KEY environment variable
    # export GOOGLE_API_KEY='your-api-key-here' (Linux/Mac)
    # $env:GOOGLE_API_KEY='your-api-key-here' (Windows PowerShell)
    
    # Test with a sample PDF
    pdf_path = "sample_regulation1.pdf"  # Replace with your actual PDF path
    
    test_question = """Create a concise, bullet-pointed technical brief for a developer. 
    This brief should list the key compliance requirements from this document that can be 
    checked in a codebase. Focus on actionable items that can be verified through code analysis."""
    
    if os.path.exists(pdf_path):
        print("=" * 80)
        print("TESTING LEGAL ANALYST TOOL")
        print("=" * 80)
        
        brief = legal_analyst_tool(pdf_path, test_question)
        
        print("\n" + "=" * 80)
        print("TECHNICAL BRIEF GENERATED:")
        print("=" * 80)
        print(brief)
        print("=" * 80)
    else:
        print(f"Test PDF not found at: {pdf_path}")
        print("Please provide a sample PDF to test the tool.")
