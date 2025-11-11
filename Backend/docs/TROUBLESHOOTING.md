# Troubleshooting Guide - Guardian AI

## Common Issues and Solutions

### ❌ Error: "Your default credentials were not found"

**Full Error:**
```
google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found. 
To set up Application Default Credentials, see https://cloud.google.com/docs/authentication/external/set-up-adc
```

**Cause:**
The Google API key environment variable is not properly set or not being passed to the Google AI components.

**Solutions:**

#### Solution 1: Set Environment Variable (PowerShell)
```powershell
$env:GOOGLE_API_KEY="your-api-key-here"
```

#### Solution 2: Load from .env file
Create `.env` file in `Github_scanner/` directory:
```bash
GOOGLE_API_KEY=your-api-key-here
```

The code will automatically load it.

#### Solution 3: Verify it's set
```powershell
# Check if variable is set
$env:GOOGLE_API_KEY

# Should output your API key
```

#### Solution 4: Set for entire session
Add to your PowerShell profile or run before each command:
```powershell
$env:GOOGLE_API_KEY="AIzaSyCqGVoHi9VuiNOG0QAbBwPrFe1xuXXEP2s"
```

**Fixed in version:** The code now explicitly passes the API key to all Google AI components.

---

### ❌ Error: "can't open file 'cli.py'"

**Full Error:**
```
C:\PYTHON\python.exe: can't open file 'E:\\Hackathon\\Guardian\\cli.py': [Errno 2] No such file or directory
```

**Cause:**
Running the command from the wrong directory.

**Solution:**
Always run from the `Github_scanner` directory:
```powershell
cd E:\Hackathon\Guardian\Github_scanner
python .\cli.py <command>
```

Or use full path:
```powershell
python E:\Hackathon\Guardian\Github_scanner\cli.py <command>
```

---

### ❌ Error: Import errors or module not found

**Cause:**
Virtual environment not activated or dependencies not installed.

**Solution:**
```powershell
# Activate virtual environment
cd E:\Hackathon\Guardian
.\venv\Scripts\Activate.ps1

# Install dependencies
cd Github_scanner
pip install -r requirements.txt
```

---

### ❌ Error: Repository clone fails

**Cause:**
- Private repository (requires authentication)
- Invalid URL
- Network issues

**Solution:**
```powershell
# For private repos, use GitHub token
git config --global credential.helper store

# Or use public repos
python cli.py scan https://github.com/public/repo
```

---

### ❌ Error: JSON parsing errors in audit mode

**Cause:**
LLM sometimes returns text instead of pure JSON.

**Solution:**
The code automatically handles this by:
1. Extracting JSON from markdown code blocks
2. Retrying with different parsing strategies
3. Logging warnings and continuing

If persistent, the LLM might be having issues. Try:
```powershell
# Use a different model
python cli.py audit <repo-url> --model gemini-2.5-pro-preview-05-06
```

---

### ❌ Error: Out of API quota

**Cause:**
Exceeded free tier limits or daily quota.

**Solution:**
1. Check your quota: https://makersuite.google.com/app/apikey
2. Wait for quota reset (usually daily)
3. Upgrade to paid tier if needed
4. Use smaller chunk sizes to reduce calls:
   ```powershell
   python cli.py audit <repo-url> --chunk-size 40
   ```

---

### ❌ Error: Cleanup fails on Windows

**Cause:**
Read-only files or files in use.

**Solution:**
The code now automatically handles this with `_handle_remove_readonly()` function.

If still fails:
```powershell
# Manually delete temp directories
Remove-Item -Recurse -Force .\cloned_repos
Remove-Item -Recurse -Force $env:TEMP\guardian_audit_*
```

---

## Working Examples

### ✅ Correct Usage

#### 1. Scan Repository
```powershell
cd E:\Hackathon\Guardian\Github_scanner
$env:GOOGLE_API_KEY="your-key"
python .\cli.py scan https://github.com/user/repo
```

#### 2. Compliance Check (RAG)
```powershell
cd E:\Hackathon\Guardian\Github_scanner
$env:GOOGLE_API_KEY="your-key"
python .\cli.py compliance https://github.com/user/repo \
  -g "Must have README" "Must have tests"
```

#### 3. Code Audit (Line-by-line)
```powershell
cd E:\Hackathon\Guardian\Github_scanner
$env:GOOGLE_API_KEY="your-key"
python .\cli.py audit https://github.com/user/repo \
  --brief "All functions must have docstrings"
```

#### 4. Ask Questions
```powershell
cd E:\Hackathon\Guardian\Github_scanner
$env:GOOGLE_API_KEY="your-key"
python .\cli.py ask https://github.com/user/repo \
  -q "What does this project do?"
```

---

## Quick Diagnostic Commands

```powershell
# 1. Check Python version (should be 3.12+)
python --version

# 2. Check if in virtual environment
Get-Command python | Select-Object Source

# 3. Check API key
$env:GOOGLE_API_KEY

# 4. Check installed packages
pip list | Select-String "langchain"

# 5. Test API key with simple script
python -c "import os; print('API Key set:', bool(os.environ.get('GOOGLE_API_KEY')))"

# 6. Check current directory
pwd
```

---

## Environment Setup Checklist

- [ ] Python 3.12+ installed
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Virtual environment activated (`.\venv\Scripts\Activate.ps1`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] GOOGLE_API_KEY set (`$env:GOOGLE_API_KEY="..."`)
- [ ] In correct directory (`Github_scanner/`)

---

## Getting Help

If you're still having issues:

1. Check the error message carefully
2. Verify all prerequisites are met
3. Try with a public repository first
4. Check your API quota
5. Look at the full stack trace

For API key issues specifically:
```powershell
# Create .env file
echo "GOOGLE_API_KEY=your-key-here" > .env

# The code will auto-load it
python .\cli.py --help
```

---

## Performance Tips

### For Large Repositories

**Use RAG mode instead of Audit:**
```powershell
# Fast (30 seconds)
python cli.py compliance <repo-url> -g "guidelines"

# Slow (hours)
python cli.py audit <repo-url> --brief "guidelines"
```

### For Small Repositories

**Audit mode is fine:**
```powershell
python cli.py audit <repo-url> --brief "guidelines" --detailed
```

### For Quick Checks

**Use scan first:**
```powershell
# Step 1: Quick overview
python cli.py scan <repo-url>

# Step 2: If interesting, dive deeper
python cli.py compliance <repo-url> -g "rules"
```

---

## API Key Security

⚠️ **IMPORTANT:** Never commit `.env` files or hardcode API keys!

The `.gitignore` already excludes:
- `.env`
- `.env.local`

To check:
```powershell
git status
# Should NOT show .env file
```

---

## Updates Applied

✅ **Fixed in latest version:**
- API key now explicitly passed to all Google AI components
- Better error messages for missing API key
- Auto-loading from .env file
- Improved cleanup on Windows
- Better JSON parsing with error handling

---

## Contact

For issues specific to this tool:
1. Check this troubleshooting guide
2. Review the documentation in `*.md` files
3. Check GitHub issues

For Gemini API issues:
- https://ai.google.dev/gemini-api/docs
