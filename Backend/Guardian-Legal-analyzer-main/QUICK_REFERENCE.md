# Quick Reference: 3 Query Modes for Orchestrator

## TL;DR

```python
from legal_tool import legal_analyst_tool, query_all_pdfs

# MODE 1: Single PDF (Isolated)
result = legal_analyst_tool(pdf, question, use_existing_db=True, filter_by_current_pdf=True)

# MODE 2: Multi-PDF (All)  
result = legal_analyst_tool(pdf, question, use_existing_db=True, filter_by_current_pdf=False)

# MODE 3: Query All (Broad + Source Tracking)
result = query_all_pdfs(question, k=10)
```

## When to Use Which

| Mode | Use Case | Search Scope | Returns |
|------|----------|--------------|---------|
| **Mode 1** | Analyze specific regulation | Current PDF only (6 chunks) | String (technical brief) |
| **Mode 2** | Comprehensive compliance | All PDFs (24 chunks) | String (technical brief) |
| **Mode 3** | Cross-regulation with sources | All PDFs (24 chunks) | Dict with answer + sources |

## Example Output

### Mode 1 Output:
```
Created 6 chunks from the document
🔍 Searching only current PDF: wcag_2.1.pdf
📄 Sources used: wcag_2.1.pdf
📊 Total chunks in database: 24

(Technical brief from wcag_2.1.pdf only)
```

### Mode 2 Output:
```
Created 6 chunks from the document
🔍 Searching all PDFs in database
📄 Sources used: wcag_2.1.pdf, gdpr.pdf, hipaa.pdf
📊 Total chunks in database: 24

(Technical brief from all relevant PDFs)
```

### Mode 3 Output:
```
🔍 Querying all PDFs in database (retrieving top 10 chunks)
📊 Searching across 24 total chunks
📄 Sources contributing to answer:
   • wcag_2.1.pdf: 4 chunks
   • gdpr.pdf: 3 chunks
   • hipaa.pdf: 3 chunks

Returns:
{
    'answer': "(Technical brief)",
    'sources': ['wcag_2.1.pdf', 'gdpr.pdf', 'hipaa.pdf'],
    'chunk_distribution': {'wcag_2.1.pdf': 4, 'gdpr.pdf': 3, 'hipaa.pdf': 3}
}
```

## Orchestrator Decision Tree

```
User submits: GitHub URL + PDFs
       |
       v
How many PDFs?
       |
       +-- 1 PDF --> Use MODE 1 (Single PDF)
       |             Focused analysis
       |
       +-- Multiple PDFs
                |
                v
           User wants detailed sources?
                |
                +-- YES --> Use MODE 3 (Query All)
                |           Shows which regulations apply
                |
                +-- NO --> Use MODE 2 (Multi-PDF)
                            Comprehensive brief
```

See `ORCHESTRATOR_GUIDE.md` for full documentation.
