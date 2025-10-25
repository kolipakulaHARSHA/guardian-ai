# Guardian Legal Analyzer 🛡️

An AI-powered Legal Analyst Tool that uses RAG (Retrieval-Augmented Generation) to analyze regulatory PDF documents and generate technical compliance briefs for developers.

## 🚀 Features

- **RAG-based Analysis**: Uses LangChain and ChromaDB for intelligent document processing
- **Smart Deduplication**: Content-based hashing prevents duplicate chunks in the database
- **Persistent Memory**: Accumulate knowledge from multiple PDFs or analyze single documents
- **Google Gemini Integration**: Powered by Gemini 2.5 Flash for accurate technical briefs
- **Developer-Focused Output**: Generates actionable compliance requirements with code examples

## 📋 Prerequisites

- Python 3.8 or higher
- Google API Key (for Gemini)
- PDF regulatory documents

## 🔧 Installation

1. **Clone the repository**
```bash
git clone https://github.com/MathewKurian484/Guardian-Legal-analyzer.git
cd Guardian-Legal-analyzer
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**
```bash
# Create .env file
echo GOOGLE_API_KEY=your-api-key-here > .env
```

## 📝 Usage

### Basic Usage

```python
from legal_tool import legal_analyst_tool

# Analyze a PDF
result = legal_analyst_tool(
    pdf_file_path="sample_regulation.pdf",
    question="Create a technical brief for developers listing compliance requirements.",
    use_existing_db=True  # True=accumulate, False=fresh, None=prompt
)

print(result)
```

### Command Line

```bash
python test_legal_tool.py
```

### Database Management

```python
from legal_tool import clear_database, get_database_info, get_database_chunk_count

# Clear database
clear_database()

# Get database info
info = get_database_info()
print(f"Database size: {info['size_mb']} MB")

# Get chunk count
count = get_database_chunk_count()
print(f"Total chunks: {count}")
```

## 🏗️ Architecture

### RAG Pipeline

1. **Document Loading**: PDF files loaded using PyPDFLoader
2. **Text Splitting**: Documents split into 1000-character chunks with 200-character overlap
3. **Content Hashing**: SHA-256 hash generated for each chunk to prevent duplicates
4. **Embedding**: Google Embeddings (models/embedding-001) create vector representations
5. **Vector Storage**: ChromaDB stores embeddings with persistent storage
6. **Retrieval**: Top 5 most relevant chunks retrieved based on question
7. **Generation**: Gemini 2.5 Flash generates technical brief from context

### Deduplication

- Uses **content-based IDs** (SHA-256 hash of chunk text)
- Automatically skips duplicate chunks across multiple runs
- Works even with PDFs that have the same filename
- Prevents database bloat from repeated processing

## 📊 Project Structure

```
guardian-ai/
├── legal_tool.py           # Main RAG implementation
├── test_legal_tool.py      # Testing script
├── .env                    # API keys (not committed)
├── .gitignore             # Git ignore rules
├── requirements.txt        # Python dependencies
├── chroma_db/             # Vector database (not committed)
└── sample_regulation.pdf  # Example regulatory document
```

## 🔑 Key Functions

### `legal_analyst_tool(pdf_file_path, question, use_existing_db)`
Main function to analyze PDFs and generate technical briefs.

**Parameters:**
- `pdf_file_path` (str): Path to PDF document
- `question` (str): Question to answer from the document
- `use_existing_db` (bool|None): Database persistence mode
  - `True`: Keep existing data (accumulate)
  - `False`: Delete and start fresh
  - `None`: Ask user interactively

**Returns:** Plain-text technical brief as string

### `clear_database()`
Manually delete the ChromaDB database.

### `get_database_info()`
Get database information without opening it (avoids file locks).

### `get_database_chunk_count()`
Get the current number of chunks in the database.

## 🛠️ Configuration

Edit these constants in `legal_tool.py`:

```python
CHROMA_DB_DIR = "./chroma_db"  # Vector database location
chunk_size = 1000              # Size of text chunks
chunk_overlap = 200            # Overlap between chunks
temperature = 0.3              # LLM temperature (0-1)
```

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

## 📄 License

MIT License

## 👥 Team

**Person B**: Legal Analyst Tool (RAG) - Mathew Kurian

Part of the Guardian AI Compliance Co-Pilot project.

## 🙏 Acknowledgments

- LangChain for RAG framework
- ChromaDB for vector storage
- Google Gemini for LLM capabilities
- PyPDF for document processing

---

**Made with ❤️ for the AI Compliance Hackathon**
