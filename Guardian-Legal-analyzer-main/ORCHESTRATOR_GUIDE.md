# Orchestrator Integration Guide 🎯

## Overview

The Legal Analyst Tool provides **3 different query modes** for the orchestrator to control how the RAG system searches the database.

---

## 📊 The Three Modes

### Mode 1: Single PDF Mode (Isolated Analysis)
**Use when:** Analyzing a specific regulation in isolation

```python
from legal_tool import legal_analyst_tool

# Only searches chunks from the current PDF
result = legal_analyst_tool(
    pdf_file_path="wcag_2.1.pdf",
    question="What are the accessibility requirements?",
    use_existing_db=True,           # Keep accumulated PDFs
    filter_by_current_pdf=True      # ← Only search THIS PDF
)

# Output shows: "🔍 Searching only current PDF: wcag_2.1.pdf"
# Result contains compliance requirements ONLY from wcag_2.1.pdf
```

**When to use:**
- User wants to analyze a specific regulation document
- Need to isolate requirements from one regulation
- Avoid mixing rules from different regulatory frameworks

---

### Mode 2: Multi-PDF Mode (Cross-Regulation Analysis)
**Use when:** Want to consider all accumulated regulations

```python
from legal_tool import legal_analyst_tool

# Searches ALL chunks in database
result = legal_analyst_tool(
    pdf_file_path="gdpr.pdf",       # Still needed for adding to DB
    question="What are the data privacy requirements?",
    use_existing_db=True,           # Keep accumulated PDFs
    filter_by_current_pdf=False     # ← Search ALL PDFs
)

# Output shows: "🔍 Searching all PDFs in database"
# Output shows: "📄 Sources used: wcag_2.1.pdf, gdpr.pdf, hipaa.pdf"
# Result combines relevant chunks from ALL regulations
```

**When to use:**
- User wants comprehensive compliance across multiple regulations
- Comparing requirements across frameworks
- Finding common patterns in regulations

---

### Mode 3: Query All Mode (Broad Search)
**Use when:** Need detailed cross-regulation queries with source tracking

```python
from legal_tool import query_all_pdfs

# Dedicated function for cross-PDF queries
result = query_all_pdfs(
    question="What are the encryption requirements?",
    k=10  # Retrieve 10 chunks (vs 5 in other modes)
)

# Returns structured response:
# {
#     'answer': "Technical brief text...",
#     'sources': ['wcag_2.1.pdf', 'gdpr.pdf', 'hipaa.pdf'],
#     'chunk_distribution': {
#         'wcag_2.1.pdf': 2,
#         'gdpr.pdf': 5,
#         'hipaa.pdf': 3
#     }
# }

print(result['answer'])
print(f"Sources: {result['sources']}")
```

**When to use:**
- Need to know which regulations contributed to the answer
- Want broader search (10 chunks vs 5)
- Building a report showing regulation coverage

---

## 🎬 Example Orchestrator Workflow

```python
from legal_tool import legal_analyst_tool, query_all_pdfs, get_database_chunk_count

class ComplianceOrchestrator:
    def __init__(self):
        self.github_url = None
        self.regulations = []
    
    def process_user_request(self, github_url: str, pdf_paths: list[str]):
        """
        Main orchestrator flow
        """
        self.github_url = github_url
        
        # Step 1: Process each PDF (accumulate in database)
        for pdf_path in pdf_paths:
            print(f"Processing: {pdf_path}")
            
            # Add to database (use_existing_db=True to accumulate)
            legal_analyst_tool(
                pdf_file_path=pdf_path,
                question="dummy",  # Not using answer yet
                use_existing_db=True,
                filter_by_current_pdf=True  # Doesn't matter here
            )
        
        # Step 2: Check database size
        total_chunks = get_database_chunk_count()
        print(f"Database now has {total_chunks} chunks")
        
        # Step 3: Query based on user intent
        
        # SCENARIO A: User wants specific regulation analysis
        if user_wants_specific_regulation:
            result = legal_analyst_tool(
                pdf_file_path=pdf_paths[0],  # The specific one
                question="Create technical brief...",
                use_existing_db=True,
                filter_by_current_pdf=True  # ← Isolate this PDF
            )
        
        # SCENARIO B: User wants comprehensive analysis
        elif user_wants_comprehensive:
            result = legal_analyst_tool(
                pdf_file_path=pdf_paths[-1],  # Any PDF (just for metadata)
                question="Create technical brief...",
                use_existing_db=True,
                filter_by_current_pdf=False  # ← Use ALL PDFs
            )
        
        # SCENARIO C: User wants detailed source tracking
        elif user_wants_source_tracking:
            result = query_all_pdfs(
                question="Create technical brief...",
                k=10  # Broader search
            )
            print(f"Answer drew from: {result['sources']}")
        
        # Step 4: Pass to Code Auditor (Person C)
        self.send_to_code_auditor(result, github_url)
```

---

## 📈 Example: 4 PDFs with 24 Total Chunks

Let's say you've accumulated:
- `wcag_2.1.pdf` → 6 chunks
- `gdpr.pdf` → 6 chunks  
- `hipaa.pdf` → 6 chunks
- `pci_dss.pdf` → 6 chunks

**Total: 24 chunks in database**

### Mode 1 (Single PDF):
```python
# Processing pci_dss.pdf with filter_by_current_pdf=True
legal_analyst_tool("pci_dss.pdf", question, use_existing_db=True, filter_by_current_pdf=True)

# Searches: Only the 6 chunks from pci_dss.pdf
# Retrieves: Top 5 chunks from pci_dss.pdf
# Sources shown: pci_dss.pdf
```

### Mode 2 (Multi-PDF):
```python
# Processing pci_dss.pdf with filter_by_current_pdf=False
legal_analyst_tool("pci_dss.pdf", question, use_existing_db=True, filter_by_current_pdf=False)

# Searches: All 24 chunks (from all 4 PDFs)
# Retrieves: Top 5 most relevant chunks (could be from any PDF)
# Sources shown: pci_dss.pdf, wcag_2.1.pdf (whichever are most relevant)
```

### Mode 3 (Query All):
```python
# Dedicated cross-regulation query
query_all_pdfs(question, k=10)

# Searches: All 24 chunks (from all 4 PDFs)
# Retrieves: Top 10 most relevant chunks (broader coverage)
# Sources shown with distribution:
#   • pci_dss.pdf: 4 chunks
#   • hipaa.pdf: 3 chunks
#   • gdpr.pdf: 2 chunks
#   • wcag_2.1.pdf: 1 chunk
```

---

## 🔑 Key Points for Orchestrator

1. **Always set `use_existing_db=True`** when processing multiple PDFs
   - This accumulates knowledge across regulations

2. **Use `filter_by_current_pdf`** to control search scope
   - `True` = isolated regulation analysis
   - `False` = comprehensive multi-regulation analysis

3. **Use `query_all_pdfs()`** when you need
   - Detailed source tracking
   - Broader search (10 chunks vs 5)
   - Structured response with metadata

4. **Database persists automatically**
   - All PDFs stay in `./chroma_db/` until manually cleared
   - Duplicate chunks are automatically skipped

5. **Sources are always shown**
   - You'll see which PDFs contributed to each answer
   - Helps with traceability and compliance reporting

---

## 🧪 Testing the Modes

Run the test script to see all three modes in action:

```bash
python test_modes.py
```

This will demonstrate:
- How each mode searches differently
- What output you get from each mode
- Which sources contribute to each answer

---

## 💡 Recommendations for Orchestrator

**For User Flow: GitHub URL + Single PDF**
→ Use **Mode 1** (Single PDF Mode)
- User likely wants that specific regulation analyzed
- Clean, focused results

**For User Flow: GitHub URL + Multiple PDFs**
→ Use **Mode 3** (Query All Mode)
- Shows comprehensive compliance
- Tracks which regulations apply
- Generates holistic technical brief

**For Incremental Analysis**
→ Use **Mode 2** (Multi-PDF Mode)
- As user adds more PDFs, query grows more comprehensive
- Like a growing knowledge base

---

Made with ❤️ for the Guardian AI Orchestrator
