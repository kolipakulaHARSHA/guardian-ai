# Quick Start Guide - Guardian AI GitHub Scanner

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```powershell
cd Github_scanner
pip install -r requirements.txt
```

### Step 2: Set Your OpenAI API Key

```powershell
# Copy the example env file
cp .env.example .env

# Edit .env and add your API key, or set it directly:
$env:OPENAI_API_KEY = "sk-your-api-key-here"
```

### Step 3: Try It Out!

#### Scan a Repository (No API Key Needed)
```powershell
python cli.py scan https://github.com/pallets/flask
```

#### Ask Questions (Requires API Key)
```powershell
python cli.py ask https://github.com/pallets/flask -q "What is Flask used for?"
```

#### Interactive Mode
```powershell
python cli.py ask https://github.com/pallets/flask --interactive
```

#### Check Compliance
```powershell
python cli.py compliance https://github.com/your-org/your-repo
```

## 📝 Common Use Cases

### Use Case 1: Quick Repository Analysis
Perfect for understanding a new project quickly.

```powershell
python cli.py scan https://github.com/microsoft/vscode -o vscode_summary.json
```

### Use Case 2: Security Compliance Check
Ensure repositories meet security standards.

Create `security_guidelines.txt`:
```
The project must have a security policy
The project must use dependency scanning
Authentication must be properly implemented
Sensitive data must be encrypted
```

Run compliance check:
```powershell
python cli.py compliance https://github.com/your-org/your-app --guidelines-file security_guidelines.txt -o security_report.json
```

### Use Case 3: Code Understanding
Learn how a specific feature works.

```powershell
python cli.py ask https://github.com/django/django --extensions ".py" -q "How does the Django ORM handle database migrations?"
```

### Use Case 4: Documentation Verification
Check if documentation is complete.

```powershell
python cli.py compliance https://github.com/your-org/your-api -g "Must have API documentation" "Must have examples" "Must have installation guide"
```

## 🔧 Troubleshooting

### Problem: "git: command not found"
**Solution:** Install Git from https://git-scm.com/download/win

### Problem: "Import Error: langchain"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Problem: "OpenAI API Error"
**Solution:** Check your API key is set: `echo $env:OPENAI_API_KEY`

### Problem: "Out of Memory"
**Solution:** Limit file types: `--extensions ".py,.md"`

## 💡 Pro Tips

1. **Save Time**: Use `--keep` flag to keep cloned repos for multiple analyses
2. **Better Results**: Use GPT-4 for complex compliance checks: `-m gpt-4`
3. **Faster Processing**: Limit file extensions to relevant types only
4. **Batch Processing**: Create a script to check multiple repos

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [examples.py](examples.py) for programmatic usage
- Customize compliance guidelines for your organization
- Integrate with your CI/CD pipeline

## 🆘 Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review [examples.py](examples.py) for code samples
- See troubleshooting section above
