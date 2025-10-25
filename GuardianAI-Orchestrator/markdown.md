# Guardian AI - Hackathon Project Plan (Agentic Auditor Version)

## 1. Project Goal (MVP)

Our goal is to build a backend for an AI Compliance Co-Pilot. This system will feature a **Chief Orchestrator Agent** that delegates tasks to two other specialized, AI-powered tools: a **Legal Analyst Tool** for understanding regulations and a **Code Auditor Agent** for intelligently scanning codebases.

**The final output will be a structured JSON report detailing all violations found, with clear explanations for each one.**

## 2. High-Level Workflow

This new workflow involves a "hand-off" of context from one specialist to another, managed by the central Orchestrator.

```mermaid
graph TD
    A[User Request] --> B{Person A: Chief Orchestrator Agent};
    B -- "Task 1: Create a technical brief from this PDF" --> C(Person B: LegalAnalystTool);
    C -- "Tool uses RAG" --> D[Vector DB (ChromaDB)];
    C -- "Result: Here is a technical brief (in plain English)" --> B;
    B -- "Task 2: Audit this repo using this technical brief" --> E(Person C: CodeAuditorAgent);
    E -- "Agent uses LLM to analyze code snippets" --> F[Codebase Files];
    E -- "Result: Here is a JSON list of violations" --> B;
    B -- "Task 3: Synthesize the final report" --> B;
    B --> G[Final Report];

    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#ccf,stroke:#333,stroke-width:2px
    style E fill:#cfc,stroke:#333,stroke-width:2px
```

**Narrative Explanation:**
1.  The **Orchestrator (Person A)** receives the user's request.
2.  It delegates the task of understanding the regulation to the **LegalAnalystTool (Person B)**.
3.  The LegalAnalystTool uses RAG to produce a **human-readable technical brief** (e.g., "Check all image tags for alt attributes," "Ensure user data is handled with encryption"). **Crucially, this is no longer a JSON of regex patterns.**
4.  The Orchestrator receives this brief. It then delegates the code audit to the **CodeAuditorAgent (Person C)**, providing it with the repo URL and the plain-English technical brief.
5.  The CodeAuditorAgent clones the repo, iterates through the files, and for each relevant code snippet, it **asks an LLM** if that snippet violates the rules described in the technical brief.
6.  The CodeAuditorAgent compiles a list of all confirmed violations and returns it to the Orchestrator.
7.  The Orchestrator assembles the final report.

## 3. The Contract: `contracts.py`

The contract is updated to reflect the new nature of the data being passed.

```python
# contracts.py

# Built by: Person B (Legal Analyst)
# Called by: Person A (Orchestrator)
def legal_analyst_tool(pdf_file_path: str, question: str) -> str:
    """
    Analyzes a regulatory PDF document using RAG.
    Takes the file path of the PDF and a question (e.g., "Create a technical brief for a developer...").
    Returns a string containing a plain-English, human-readable technical brief.
    """
    pass

# Built by: Person C (Code Auditor)
# Called by: Person A (Orchestrator)
def code_auditor_agent(repo_url: str, technical_brief: str) -> str:
    """
    Scans a public GitHub repository using an AI agent to find violations.
    Takes the repo URL and a plain-English technical brief describing the rules.
    Returns a JSON string list of all violations found, including explanations.
    """
    pass
```

## 4. Work Split & Detailed Tasks

---

### **Person A: The Chief Orchestrator Agent**

*   **Your Mission:** To be the project manager. You will build the agent that understands the user's goal and correctly delegates tasks to your two specialist tools.
*   **Key Libraries:** `langchain`
*   **File:** `main.py`

#### Your Step-by-Step Plan:

1.  **Setup and Contracts:**
    *   Create the `main.py` file.
    *   Work with the team to finalize the new `contracts.py`.
    *   Create mock versions of the `legal_analyst_tool` and `code_auditor_agent` so you can build your agent in parallel. The mock for the auditor should return a hardcoded JSON string representing a list of violations.

2.  **Define the Agent's Toolbox:**
    *   Import `Tool` from `langchain.agents`.
    *   Create a `tools` list containing your two tools.
    *   Write very clear descriptions for each tool in the `Tool` constructor.
        *   `LegalAnalystTool`: "Use this tool FIRST to analyze a PDF and create a technical brief for the Code Auditor."
        *   `CodeAuditorAgent`: "Use this tool SECOND, after you have a technical brief. It takes a repo URL and the brief to find code violations."

3.  **Craft the Master Prompt (ReAct):**
    *   Create the ReAct prompt template.
    *   Your prompt must guide the agent to follow a **two-step process**: always use the Legal tool first, then use the Code Auditor tool with the output of the first tool.

4.  **Assemble and Test the Agent:**
    *   Import `initialize_agent` and `AgentType`.
    *   Initialize the LLM (`GoogleGenerativeAI`).
    *   Create the `agent_executor` using `initialize_agent`, passing it your tools, LLM, and prompt. Set `verbose=True` to see the agent's thoughts.
    *   Run the agent with a user request. **Your primary goal is to verify that the agent correctly calls the Legal tool first, then takes its output and uses it as the input for the Code Auditor tool.**

5.  **Final Integration:**
    *   Once Person B and C have finished, replace your mock tools with their real, imported functions.
    *   The output from the `code_auditor_agent` should already be the final report. Your job is now simpler: just receive this final report and pass it on.

---

### **Person B: The Legal Analyst Tool (RAG)**

*   **Your Mission:** To be the team's legal expert. Your tool will distill a complex regulatory document into a simple, clear set of instructions for another AI to use.
*   **Key Libraries:** `langchain`, `langchain-google-genai`, `chromadb`, `pypdf`
*   **File:** `legal_tool.py`

#### Your Step-by-Step Plan:

1.  **Setup and Function Definition:**
    *   Create `legal_tool.py`.
    *   Define the `legal_analyst_tool` function as specified in `contracts.py`.

2.  **Document Ingestion and Vectorization:**
    *   Use `PyPDFLoader` to load the text from the provided PDF.
    *   Use `RecursiveCharacterTextSplitter` to break the document into small, semantic chunks.
    *   Initialize `GoogleGenerativeAIEmbeddings`.
    *   Use `Chroma.from_documents()` to create the in-memory RAG vector store from the text chunks.

3.  **Build and Run the QA Chain:**
    *   Initialize the LLM (`GoogleGenerativeAI`).
    *   Create a `RetrievalQA` chain that links your LLM to your vector store's retriever.
    *   The `question` your function will receive from the Orchestrator will be something like: `"Create a concise, bullet-pointed technical brief for a developer. This brief should list the key compliance requirements from this document that can be checked in a codebase."`
    *   Your function's final step is to execute `qa_chain.run(question)` and return the resulting string. This string is the "technical brief."

4.  **Independent Testing:**
    *   In a `if __name__ == "__main__":` block, test your function with a sample PDF and the question above to ensure it produces a high-quality, human-readable brief.

---

### **Person C: The Code Auditor Agent**

*   **Your Mission:** To be the team's senior developer. You will build an AI-powered tool that can read code and apply a set of plain-English rules to find violations.
*   **Key Libraries:** `GitPython`, `os`, `langchain-google-genai`
*   **File:** `code_tool.py`

#### Your Step-by-Step Plan:

1.  **Setup and Function Definition:**
    *   Create `code_tool.py`.
    *   Define the `code_auditor_agent` function as specified in `contracts.py`.

2.  **Repository Cloning and Cleanup:**
    *   Use `tempfile` to create a temporary directory.
    *   Use `git.Repo.clone_from(repo_url, temp_dir)` to clone the repository.
    *   Structure your code with a `try...finally` block to ensure `shutil.rmtree(temp_dir)` is **always** called at the end, even if errors occur.

3.  **File Iteration and Filtering:**
    *   Use `os.walk(temp_dir)` to loop through all files in the cloned repository.
    *   Inside the loop, add a filter to ignore certain file types. You don't want to analyze images, executables, or large library files. Focus on relevant extensions (e.g., `.js`, `.py`, `.html`, `.java`).

4.  **The Core AI Logic (The "Inner Agent"):**
    *   For each relevant file:
        *   Read the file's content into a string.
        *   You can process the file in chunks (e.g., 20-40 lines at a time) to avoid making the prompt too large.
        *   For each chunk of code, you will make a **direct call to the Gemini LLM**.
        *   **Craft a specific "Code Analysis" prompt:**
            ```
            You are an expert code auditor. Your task is to determine if the following code snippet violates any of the rules in the provided technical brief.

            **TECHNICAL BRIEF:**
            [Insert the `technical_brief` string here]

            **CODE SNIPPET:**
            ```[language]
            [Insert the chunk of code here]
            ```
            ---
            Analyze the code snippet against the brief. If you find one or more violations, respond with a JSON list. Each item in the list should be a dictionary with the keys: "violating_code", "explanation", and "rule_violated". If there are no violations in this snippet, respond with an empty list: [].

            Your response must be ONLY the JSON list.
            ```
        *   Parse the JSON response from the LLM. If it's not an empty list, add the findings to your master `violations` list (remembering to add the file path and line number).

5.  **Finalize and Test the Tool:**
    *   After iterating through all files, your function should return the complete `violations` list, converted into a JSON string using `json.dumps()`.
    *   Test your function independently. Give it a real GitHub URL and a hardcoded `technical_brief` string to see if it correctly identifies and explains violations.