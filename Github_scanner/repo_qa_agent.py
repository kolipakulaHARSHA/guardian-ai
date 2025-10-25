"""
Repository Question-Answering Agent for Guardian AI
Uses LangChain to provide intelligent question answering about repository contents.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import os

# Import LangChain components
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from github_repo_tool import GitHubRepoTool


class RepoQAAgent:
    """
    An agent that can answer questions about a GitHub repository
    using RAG (Retrieval Augmented Generation).
    """
    
    def __init__(
        self,
        google_api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0
    ):
        """
        Initialize the Repository QA Agent.
        
        Args:
            google_api_key: Google API key (if not set in environment)
            model_name: Gemini model to use (gemini-2.5-flash, gemini-2.5-pro-preview-05-06, etc.)
            temperature: Temperature for response generation
        """
        self.repo_tool = GitHubRepoTool()
        self.vectorstore = None
        self.qa_chain = None
        
        # Set API key
        if google_api_key:
            os.environ["GOOGLE_API_KEY"] = google_api_key
        
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.documents: List[Document] = []
    
    def clone_and_index_repository(
        self,
        repo_url: str,
        branch: str = "main",
        file_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Clone a repository and index its contents for question answering.
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch to clone
            file_extensions: File types to index (e.g., ['.py', '.js', '.md'])
            
        Returns:
            Status dictionary
        """
        # Clone the repository
        clone_result = self.repo_tool.clone_repository(repo_url, branch)
        
        if clone_result.get('status') == 'error':
            return clone_result
        
        # Load and index documents
        index_result = self.index_repository(file_extensions)
        
        return {
            'status': 'success',
            'clone_info': clone_result,
            'index_info': index_result
        }
    
    def index_repository(
        self,
        file_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Index the current repository for question answering.
        
        Args:
            file_extensions: File types to index
            
        Returns:
            Indexing status and statistics
        """
        if not self.repo_tool.current_repo_path:
            return {'error': 'No repository cloned'}
        
        # Default extensions for code and documentation
        if file_extensions is None:
            file_extensions = [
                '.py', '.js', '.ts', '.jsx', '.tsx',
                '.java', '.cpp', '.c', '.h', '.cs',
                '.md', '.txt', '.rst',
                '.json', '.yaml', '.yml', '.toml',
                '.html', '.css', '.scss'
            ]
        
        print("Loading documents from repository...")
        self.documents = []
        
        # Load all files with specified extensions
        for ext in file_extensions:
            files = self.repo_tool.search_files(f"*{ext}")
            
            for file_path in files:
                file_info = self.repo_tool.read_file(file_path)
                
                if file_info.get('type') == 'text' and 'content' in file_info:
                    # Create a document with metadata
                    doc = Document(
                        page_content=file_info['content'],
                        metadata={
                            'source': file_path,
                            'file_name': Path(file_path).name,
                            'extension': Path(file_path).suffix,
                            'size': file_info['size']
                        }
                    )
                    self.documents.append(doc)
        
        if not self.documents:
            return {
                'status': 'warning',
                'message': 'No documents found to index',
                'documents_count': 0
            }
        
        print(f"Loaded {len(self.documents)} documents")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        print("Splitting documents into chunks...")
        splits = text_splitter.split_documents(self.documents)
        print(f"Created {len(splits)} chunks")
        
        # Create vector store
        print("Creating vector store...")
        self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        
        # Create QA prompt template
        template = """Answer the question based only on the following context:

{context}

Question: {question}

Answer: """
        
        self.prompt = ChatPromptTemplate.from_template(template)
        
        # Create QA chain using LCEL
        def format_docs(docs):
            return "\n\n".join([doc.page_content for doc in docs])
        
        self.qa_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        print("Repository indexed successfully!")
        
        return {
            'status': 'success',
            'documents_count': len(self.documents),
            'chunks_count': len(splits),
            'indexed_extensions': file_extensions
        }
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Ask a question about the repository.
        
        Args:
            question: Question to ask
            
        Returns:
            Answer and source documents
        """
        if not self.qa_chain:
            return {
                'error': 'Repository not indexed. Please clone and index a repository first.'
            }
        
        print(f"\nQuestion: {question}")
        
        # Get relevant documents
        docs = self.retriever.invoke(question)
        
        # Get answer using LCEL chain
        answer = self.qa_chain.invoke(question)
        
        # Extract source information
        sources = []
        for doc in docs:
            sources.append({
                'file': doc.metadata.get('source', 'unknown'),
                'content_preview': doc.page_content[:200] + '...'
            })
        
        return {
            'question': question,
            'answer': answer,
            'sources': sources,
            'source_count': len(sources)
        }
    
    def check_compliance(
        self,
        compliance_guidelines: List[str]
    ) -> Dict[str, Any]:
        """
        Check if the repository follows specific compliance guidelines.
        
        Args:
            compliance_guidelines: List of compliance requirements to check
            
        Returns:
            Compliance check results
        """
        if not self.qa_chain:
            return {
                'error': 'Repository not indexed. Please clone and index a repository first.'
            }
        
        compliance_results = []
        
        for guideline in compliance_guidelines:
            # Ask about each guideline
            question = f"Does this repository comply with the following requirement: {guideline}? Please provide specific evidence from the code or documentation."
            
            result = self.ask_question(question)
            
            compliance_results.append({
                'guideline': guideline,
                'assessment': result.get('answer', 'Unable to assess'),
                'evidence_sources': [src['file'] for src in result.get('sources', [])]
            })
        
        return {
            'status': 'success',
            'compliance_checks': compliance_results,
            'total_guidelines_checked': len(compliance_guidelines)
        }
    
    def get_repository_insights(self) -> Dict[str, Any]:
        """
        Get automated insights about the repository.
        
        Returns:
            Dictionary of repository insights
        """
        if not self.qa_chain:
            return {'error': 'Repository not indexed'}
        
        questions = [
            "What is the main purpose of this repository?",
            "What programming languages and frameworks are used?",
            "What are the key dependencies?",
            "Is there documentation? Where is it located?",
            "Are there any security considerations mentioned?"
        ]
        
        insights = {}
        
        for question in questions:
            result = self.ask_question(question)
            insights[question] = result.get('answer', 'No answer available')
        
        return insights
    
    def cleanup(self):
        """Clean up resources."""
        self.repo_tool.cleanup()
        self.vectorstore = None
        self.qa_chain = None
        self.documents = []


# Example usage
if __name__ == "__main__":
    import json
    
    # Initialize the agent with Gemini
    agent = RepoQAAgent(model_name="gemini-2.5-flash")
    
    # Clone and index a repository
    print("Cloning and indexing repository...")
    result = agent.clone_and_index_repository(
        "https://github.com/microsoft/vscode",
        file_extensions=['.md', '.json', '.ts']
    )
    print(json.dumps(result, indent=2))
    
    # Ask questions
    questions = [
        "What is this project about?",
        "What are the main features?",
        "How do I contribute to this project?"
    ]
    
    for question in questions:
        answer = agent.ask_question(question)
        print(f"\nQ: {answer['question']}")
        print(f"A: {answer['answer']}")
        print(f"Sources: {answer['source_count']} files")
    
    # Check compliance
    guidelines = [
        "The project must have a LICENSE file",
        "The project must have a README with installation instructions",
        "The project must have a CONTRIBUTING guide"
    ]
    
    compliance = agent.check_compliance(guidelines)
    print("\nCompliance Check:")
    print(json.dumps(compliance, indent=2))
    
    # Clean up
    # agent.cleanup()
