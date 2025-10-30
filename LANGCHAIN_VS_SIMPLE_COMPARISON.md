# LangChain Agent vs Guardian Agent Simple - Comparison

## Architecture Differences

### 1. **Orchestration Approach**

**guardian_agent_simple.py:**
- **Manual orchestration** with LLM-based reasoning
- Three-step workflow:
  1. **PLANNING**: LLM creates an execution plan (which tools, in what order)
  2. **EXECUTION**: Manually executes each tool based on the plan
  3. **SYNTHESIS**: LLM synthesizes final answer from all tool results
- Has explicit `_create_plan()`, `_execute_plan()`, and `_synthesize_answer()` methods
- More control over execution flow
- Custom state management (e.g., `qa_repo_url` for session persistence)

**langchain_agent.py:**
- **LangChain framework** orchestration
- Uses `create_tool_calling_agent()` and `AgentExecutor`
- Agent autonomously decides when to call tools based on system prompt
- Single `run()` method handles everything automatically
- Less manual control, relies on LangChain's built-in agent logic
- **No state management** - stateless execution

---

## 2. **State Management & QA Sessions**

**guardian_agent_simple.py:**
- ✅ **Stateful agent** with persistent QA sessions
- Maintains `self.qa_repo_url` to track active repository
- Maintains `self.qa_tool_instance` for reusing indexed repositories
- Supports multi-turn conversations about the same repository
- Context is passed to planning: "A QA session is currently active for repository: {url}"
- Methods: `start_qa_session()`, `end_qa_session()`
- Interactive mode can reuse the same repo across queries

**langchain_agent.py:**
- ❌ **Stateless** - no session management
- Creates new `QATool` instance for every query
- Re-clones and re-indexes repository on every question
- Cannot maintain context across multiple questions about the same repo
- **Performance impact**: Wastes time and API calls re-indexing

---

## 3. **Audit Mode Intelligence**

**guardian_agent_simple.py:**
- ✅ **Smart mode selection** in planning phase
- LLM decides between `audit`, `compliance`, or `hybrid` based on query
- Planning prompt explains each mode:
  - **AUDIT**: Exhaustive line-by-line (slow, precise)
  - **COMPLIANCE**: Fast RAG search (quick overview)
  - **HYBRID**: RAG + targeted deep scan (balanced, recommended default)
- Default to `hybrid` for compliance queries
- Fallback planning if JSON parsing fails

**langchain_agent.py:**
- ⚠️ **Less intelligent mode selection**
- Tools define modes, but agent may not choose optimally
- System prompt mentions mode exists but doesn't explain trade-offs
- No explicit guidance on when to use each mode
- Agent might default to wrong mode for the query type

---

## 4. **Hybrid Audit Implementation**

Both implement the same Enhanced Intelligent Hybrid V2 algorithm, but with differences:

**guardian_agent_simple.py:**
- More verbose logging with `self._log()` to session history
- Better error handling in each step
- Explicit Step 0-6 logging
- Returns structured dict with summary and details
- Fallback to full audit if any step fails
- Example:
  ```python
  self._log("Step 1: Translating guidelines into searchable code patterns...")
  self._log(f"✓ Generated {len(guideline_patterns)} pattern categories.")
  ```

**langchain_agent.py:**
- Uses `print()` statements directly
- Similar structure but less detailed logging
- Returns string summary instead of dict
- Stores violations globally for JSON export (`_last_audit_results`)
- Same 7-step process but slightly different error messages

---

## 5. **Tool Definitions**

**guardian_agent_simple.py:**
- Tools are **methods** within the `GuardianAgent` class
- Direct access to instance state (`self.qa_tool_instance`, `self.qa_repo_url`)
- Methods: `_run_legal_analyst()`, `_run_code_auditor()`, `_run_qa()`
- Can share state between tool calls

**langchain_agent.py:**
- Tools are **decorated functions** using `@tool`
- Must be pure functions (can't access instance state)
- Functions: `legal_analyzer()`, `code_auditor()`, `repository_qa()`
- Global variable `_last_audit_results` used to share data

---

## 6. **JSON Export**

**guardian_agent_simple.py:**
```python
{
  "timestamp": "2025-10-28T...",
  "query": "...",
  "violations": [...],
  "plan": {...},
  "tool_results": {...},
  "final_answer": "...",
  "metadata": {
    "guardian_version": "1.0",
    "mode": "agent_orchestration"
  }
}
```
- Includes planning details
- Includes all tool results
- More comprehensive metadata

**langchain_agent.py:**
```python
{
  "timestamp": "2025-10-28T...",
  "query": "...",
  "violations": [...],
  "stats": {...},
  "final_answer": "...",
  "metadata": {
    "guardian_version": "1.0-langchain",
    "mode": "hybrid",
    "repo_url": "..."
  }
}
```
- Includes statistics (pass1/pass2 breakdown)
- **Does NOT include** planning or intermediate results
- Less verbose, more focused on violations

---

## 7. **Interactive Mode**

**guardian_agent_simple.py:**
- ✅ **Full interactive mode** with command support
- Commands: `exit`, `help`, `start_qa <url>`, `end_qa`, `history`, `clear`
- Maintains conversation history
- Shows active QA session in prompt
- User-friendly CLI interface

**langchain_agent.py:**
- ❌ **No interactive mode**
- Single query execution only
- Must restart for each query
- No command system
- More like a script than an interactive agent

---

## 8. **Code Quality & Debugging**

**guardian_agent_simple.py:**
- Extensive logging throughout
- Session log stored in `self.session_log`
- Better error messages with context
- Graceful fallbacks at multiple levels
- More mature codebase (1007 lines)

**langchain_agent.py:**
- Basic print statements
- Less comprehensive error handling
- Fixed multiple bugs during development (syntax, slice errors)
- Newer implementation (434 lines)
- Still being refined

---

## 9. **Dependencies**

**guardian_agent_simple.py:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
```
- Uses LangChain **only for LLM calls**
- No agent framework dependencies
- More minimal dependency footprint

**langchain_agent.py:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
```
- Full LangChain agent framework
- More dependencies
- Requires LANGCHAIN_API_KEY for tracing (optional)
- Uses LangSmith for debugging (if configured)

---

## 10. **Pattern Generation**

Both use the **same detailed prompt** for pattern generation (fixed in recent update):
- Multi-paragraph instructions
- Concrete examples with format
- JSON object with guideline categories
- Same JSON cleaning logic

---

## Summary Table

| Feature | guardian_agent_simple.py | langchain_agent.py |
|---------|-------------------------|-------------------|
| **Orchestration** | Manual, 3-step process | LangChain AgentExecutor |
| **State Management** | ✅ Stateful sessions | ❌ Stateless |
| **QA Session Reuse** | ✅ Yes | ❌ No (re-indexes every time) |
| **Mode Intelligence** | ✅ Smart LLM-based selection | ⚠️ Basic |
| **Interactive Mode** | ✅ Full CLI with commands | ❌ None |
| **JSON Export** | ✅ Comprehensive | ✅ Focused on violations |
| **Planning Visibility** | ✅ Exported in JSON | ❌ Not available |
| **Error Handling** | ✅ Multiple fallback levels | ⚠️ Basic |
| **Logging** | ✅ Session log with history | ⚠️ Print statements |
| **Maturity** | ✅ Production-ready | ⚠️ Under development |
| **Lines of Code** | 1007 | 434 |
| **Dependencies** | LangChain (LLM only) | LangChain (full framework) |

---

## Recommendations

### Use **guardian_agent_simple.py** when:
- You need **stateful, multi-turn conversations**
- You want to **reuse indexed repositories** (QA sessions)
- You need **interactive mode** with command support
- You want **comprehensive logging and debugging**
- You need **production-ready stability**
- You want **more control** over execution flow

### Use **langchain_agent.py** when:
- You want **LangChain framework integration**
- You need **single-shot queries** (no state needed)
- You prefer **declarative tool definitions** (`@tool` decorator)
- You want **LangSmith tracing/debugging** support
- You're building on **LangChain ecosystem** (agents, chains, etc.)
- You want a **simpler, more concise codebase**

---

## Missing Features in LangChain Agent

To achieve feature parity with `guardian_agent_simple.py`, the LangChain agent needs:

1. ❌ **Stateful QA sessions** - Maintain repository context across queries
2. ❌ **Interactive mode** - CLI with commands (`start_qa`, `end_qa`, `history`, etc.)
3. ❌ **Session logging** - Keep conversation history accessible
4. ❌ **Planning export** - Include plan in JSON output
5. ❌ **Tool results export** - Include all intermediate tool outputs
6. ❌ **Smart mode selection** - Better guidance for choosing audit modes
7. ❌ **Fallback planning** - Manual extraction if JSON parsing fails

---

## Conclusion

**guardian_agent_simple.py** is the **more mature, feature-complete implementation** with better state management, interactive capabilities, and production readiness.

**langchain_agent.py** is a **cleaner, more modern implementation** that leverages the LangChain framework but lacks several key features like session management and interactive mode.

For most use cases, **guardian_agent_simple.py is recommended** due to its superior handling of multi-turn conversations and QA session reuse, which significantly reduces API calls and improves performance.
