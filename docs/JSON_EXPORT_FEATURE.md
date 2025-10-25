# 📁 Guardian AI - JSON Export Feature

## ✅ **NOW AVAILABLE: JSON Export!**

The Guardian AI agent now supports **saving results to JSON format** for easy integration with other systems!

---

## 🆕 **What's New**

### **Before:**
```bash
python guardian_agent_simple.py "Check compliance"
# Output: Only printed to console ❌
```

### **After:**
```bash
# Option 1: Save to JSON file
python guardian_agent_simple.py "Check compliance" --output report.json
# Creates: report.json file ✅

# Option 2: Output JSON to console
python guardian_agent_simple.py "Check compliance" --json
# Prints: JSON to stdout ✅
```

---

## 📊 **JSON Output Format**

The JSON file contains a complete record of the agent's execution:

```json
{
  "timestamp": "2025-10-25T20:44:33.688891",
  "query": "What are the security requirements in sample_regulation.pdf?",
  "model": "gemini-2.5-pro-preview-03-25",
  
  "plan": {
    "tools_needed": ["Legal_Analyzer"],
    "execution_order": ["Legal_Analyzer"],
    "reasoning": "The user is asking to extract requirements...",
    "pdf_path": "sample_regulation.pdf",
    "repo_url": null,
    "audit_mode": null
  },
  
  "tool_results": {
    "legal_brief": "Here are the key compliance requirements...",
    "audit_results": "Audit Results: 12 violations found...",
    "qa_answer": "The repository is a 3D visualization tool..."
  },
  
  "final_answer": "Of course. Based on my analysis...",
  
  "metadata": {
    "guardian_version": "1.0",
    "mode": "agent_orchestration"
  }
}
```

---

## 🎯 **New Command-Line Options**

### **1. `--output` / `-o` (Save to File)**

Save the complete results to a JSON file:

```bash
python guardian_agent_simple.py "Check repo compliance" --output report.json
```

**Output:**
```
🤖 Initializing Guardian AI...
✅ Ready!

[Agent execution...]

✅ Results saved to: report.json

======================================================================
FINAL ANSWER
======================================================================
[Human-readable answer also printed]
```

---

### **2. `--json` (Console JSON Output)**

Print results as JSON to stdout (useful for piping to other tools):

```bash
python guardian_agent_simple.py "Analyze PDF" --json
```

**Output:**
```json
{
  "timestamp": "2025-10-25T20:46:17.249404",
  "query": "Analyze PDF",
  "plan": {...},
  "tool_results": {...},
  "final_answer": "..."
}
```

---

## 💡 **Use Cases**

### **1. Audit Trail / Compliance Records**

```bash
# Save audit results for compliance documentation
python guardian_agent_simple.py "Check https://github.com/user/repo against GDPR.pdf" \
  --output "compliance_audit_$(date +%Y%m%d).json"
```

**Result:** `compliance_audit_20251025.json` with complete audit trail

---

### **2. Integration with Other Tools**

```bash
# Pipe JSON to other tools
python guardian_agent_simple.py "Check compliance" --json | jq '.plan.tools_needed'

# Output:
["Legal_Analyzer", "Code_Auditor"]
```

---

### **3. Batch Processing**

```bash
# Process multiple repos and save all results
for repo in repo1 repo2 repo3; do
  python guardian_agent_simple.py "Check $repo compliance" \
    --output "results/${repo}_report.json"
done
```

---

### **4. Dashboard / Reporting**

```python
# Python script to aggregate results
import json
import glob

reports = []
for file in glob.glob("results/*.json"):
    with open(file) as f:
        reports.append(json.load(f))

# Analyze trends, generate dashboards, etc.
total_violations = sum(
    len(r['tool_results'].get('audit_results', ''))
    for r in reports
)
```

---

## 📋 **Complete JSON Structure**

### **Root Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 timestamp of execution |
| `query` | string | Original user query |
| `model` | string | Gemini model used |
| `plan` | object | Agent's execution plan |
| `tool_results` | object | Raw results from each tool |
| `final_answer` | string | Synthesized human-readable answer |
| `metadata` | object | Version and mode information |

### **Plan Object:**

```json
{
  "tools_needed": ["Legal_Analyzer", "Code_Auditor"],
  "execution_order": ["Legal_Analyzer", "Code_Auditor"],
  "reasoning": "Why these tools in this order",
  "pdf_path": "path/to/pdf.pdf",
  "repo_url": "https://github.com/user/repo",
  "audit_mode": "audit" | "compliance",
  "question": "User's question if QA_Tool used"
}
```

### **Tool Results Object:**

```json
{
  "legal_brief": "Extracted compliance requirements...",
  "audit_results": "Audit findings with violations...",
  "qa_answer": "Answer to user's code question..."
}
```

---

## 🎬 **Demo Examples**

### **Example 1: Simple Legal Analysis**

```bash
python guardian_agent_simple.py \
  "What are the security requirements in sample_regulation.pdf?" \
  --output legal_analysis.json
```

**Result File:** `legal_analysis.json`
```json
{
  "timestamp": "2025-10-25T20:44:33.688891",
  "query": "What are the security requirements in sample_regulation.pdf?",
  "plan": {
    "tools_needed": ["Legal_Analyzer"]
  },
  "tool_results": {
    "legal_brief": "• Data Encryption: TLS 1.2+\n• No Hardcoded Credentials..."
  },
  "final_answer": "Based on my analysis of sample_regulation.pdf..."
}
```

---

### **Example 2: Full Compliance Audit**

```bash
python guardian_agent_simple.py \
  "Check if https://github.com/Aadisheshudupa/3DTinKer complies with sample_regulation.pdf" \
  --output compliance_report.json
```

**Result File:** `compliance_report.json`
```json
{
  "query": "Check if https://github.com/Aadisheshudupa/3DTinKer complies with sample_regulation.pdf",
  "plan": {
    "tools_needed": ["Legal_Analyzer", "Code_Auditor"],
    "audit_mode": "audit"
  },
  "tool_results": {
    "legal_brief": "Requirements extracted...",
    "audit_results": "Violations found:\n1. src/App.jsx (line 45): Missing alt attribute..."
  }
}
```

---

### **Example 3: JSON Console Output for CI/CD**

```bash
# In CI/CD pipeline
RESULT=$(python guardian_agent_simple.py "Check compliance" --json --quiet)
VIOLATIONS=$(echo $RESULT | jq '.tool_results.audit_results')

if [[ $VIOLATIONS =~ "FAIL" ]]; then
  echo "❌ Compliance check failed!"
  exit 1
fi
```

---

## 🔧 **Integration Examples**

### **Python Script Integration**

```python
import subprocess
import json

# Run Guardian AI and get JSON results
result = subprocess.run(
    ['python', 'guardian_agent_simple.py', 
     'Check repo compliance', '--json'],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)

# Process results
print(f"Query: {data['query']}")
print(f"Tools used: {data['plan']['tools_needed']}")
print(f"Answer: {data['final_answer']}")
```

---

### **PowerShell Integration**

```powershell
# Run Guardian AI and parse JSON
$result = python guardian_agent_simple.py "Check compliance" --json | ConvertFrom-Json

# Access fields
Write-Host "Timestamp: $($result.timestamp)"
Write-Host "Tools used: $($result.plan.tools_needed -join ', ')"
Write-Host "Answer: $($result.final_answer)"
```

---

### **Node.js Integration**

```javascript
const { exec } = require('child_process');

exec('python guardian_agent_simple.py "Check compliance" --json', 
  (error, stdout, stderr) => {
    const result = JSON.parse(stdout);
    
    console.log(`Query: ${result.query}`);
    console.log(`Tools: ${result.plan.tools_needed.join(', ')}`);
    console.log(`Answer: ${result.final_answer}`);
});
```

---

## 📦 **Batch Processing Script**

Create a file `batch_audit.sh`:

```bash
#!/bin/bash

# List of repositories to audit
REPOS=(
  "https://github.com/user/repo1"
  "https://github.com/user/repo2"
  "https://github.com/user/repo3"
)

# Compliance document
PDF="sample_regulation.pdf"

# Output directory
mkdir -p audit_results

# Process each repo
for repo in "${REPOS[@]}"; do
  repo_name=$(basename $repo)
  echo "Auditing $repo_name..."
  
  python guardian_agent_simple.py \
    "Check if $repo complies with $PDF" \
    --output "audit_results/${repo_name}_$(date +%Y%m%d).json" \
    --quiet
  
  echo "✅ $repo_name complete"
done

echo "🎉 All audits complete! Results in audit_results/"
```

---

## 🎯 **JSON vs Regular Output**

| Feature | Regular Output | JSON Output |
|---------|----------------|-------------|
| **Human-Readable** | ✅ Yes | ❌ Requires parsing |
| **Machine-Readable** | ❌ No | ✅ Yes |
| **Includes Plan** | ✅ Yes (printed) | ✅ Yes (structured) |
| **Includes Tool Results** | ❌ No | ✅ Yes |
| **Timestamp** | ❌ No | ✅ Yes |
| **CI/CD Integration** | ❌ Difficult | ✅ Easy |
| **Audit Trail** | ❌ No | ✅ Complete |

---

## 📈 **Updated Help Menu**

```bash
python guardian_agent_simple.py --help
```

**Output:**
```
usage: guardian_agent_simple.py [-h] [--interactive] [--model MODEL] 
                                [--quiet] [--output OUTPUT] [--json]
                                [query]

Guardian AI - Intelligent Compliance Agent

positional arguments:
  query                 Your query

options:
  -h, --help            show this help message and exit
  --interactive, -i     Interactive mode
  --model MODEL         Model to use
  --quiet, -q           Less verbose output
  --output OUTPUT, -o OUTPUT
                        Save results to JSON file (e.g., report.json)
  --json                Output results as JSON to console

Examples:
  # Simple query
  python guardian_agent_simple.py "Analyze sample_regulation.pdf"
  
  # Full compliance check
  python guardian_agent_simple.py "Check https://github.com/user/repo against gdpr.pdf"
  
  # Save results to JSON
  python guardian_agent_simple.py "Check repo compliance" --output report.json
  
  # Output as JSON to console
  python guardian_agent_simple.py "Analyze PDF" --json
  
  # Interactive mode
  python guardian_agent_simple.py --interactive
```

---

## ✅ **Summary**

**Status**: ✅ **JSON export feature COMPLETE!**

**New Flags**:
- `--output <file>` - Save results to JSON file
- `--json` - Print JSON to console

**What's Included in JSON**:
- Timestamp
- Query
- Model used
- Agent's plan
- Tool results (raw)
- Final answer
- Metadata

**Use Cases**:
- ✅ Audit trails
- ✅ CI/CD integration
- ✅ Batch processing
- ✅ Dashboard generation
- ✅ Compliance documentation

**Ready for**: Production deployment, hackathon demo, enterprise use! 🏆
