# Migration Guide: OpenAI → Google Gemini

## Changes Made

Your Guardian AI GitHub Scanner has been updated to use **Google Gemini API** instead of OpenAI.

### What Changed

1. **API Key**: Now uses `GOOGLE_API_KEY` instead of `OPENAI_API_KEY`
2. **Default Model**: Changed from `gpt-3.5-turbo` to `gemini-1.5-flash`
3. **Dependencies**: Replaced `langchain-openai` with `langchain-google-genai`
4. **Embeddings**: Now uses Google's `models/embedding-001`

### Files Modified

- ✅ `.env.example` - Updated API key reference
- ✅ `requirements.txt` - Replaced OpenAI with Google packages
- ✅ `repo_qa_agent.py` - Changed to use Gemini models
- ✅ `cli.py` - Updated default model to gemini-1.5-flash
- ✅ `examples.py` - Updated all examples to use Gemini

### Migration Steps

#### 1. Uninstall Old Dependencies (Optional)
```powershell
pip uninstall langchain-openai tiktoken -y
```

#### 2. Install New Dependencies
```powershell
cd Github_scanner
pip install langchain-google-genai
```

#### 3. Get Google API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

#### 4. Set Environment Variable
```powershell
# Temporary (current session)
$env:GOOGLE_API_KEY = "your-google-api-key-here"

# Permanent (create .env file)
# Copy .env.example to .env
cp .env.example .env
# Then edit .env and add your key
```

### Available Gemini Models

You can now use these models with the `-m` flag:

- **gemini-1.5-flash** (default) - Fast, efficient, good for most tasks
- **gemini-1.5-pro** - More powerful, better reasoning
- **gemini-pro** - Previous generation model

### Updated Usage

#### Basic Scan (No Changes)
```powershell
python cli.py scan https://github.com/pallets/flask
```

#### Ask Questions (Updated)
```powershell
# Set Google API key
$env:GOOGLE_API_KEY = "your-key-here"

# Default uses gemini-1.5-flash
python cli.py ask https://github.com/pallets/flask -q "What is Flask?"

# Use gemini-1.5-pro for better quality
python cli.py ask https://github.com/django/django -m gemini-1.5-pro -q "How does the ORM work?"

# Interactive mode
python cli.py ask https://github.com/pallets/flask --interactive
```

#### Compliance Checking (Updated)
```powershell
# Default uses gemini-1.5-flash
python cli.py compliance https://github.com/your-org/repo

# Use gemini-1.5-pro for more thorough analysis
python cli.py compliance https://github.com/your-org/repo -m gemini-1.5-pro

# With custom guidelines
python cli.py compliance https://github.com/your-org/repo --guidelines-file compliance_guidelines.txt
```

### Python API Changes

#### Before (OpenAI)
```python
from repo_qa_agent import RepoQAAgent

agent = RepoQAAgent(
    openai_api_key="sk-...",
    model_name="gpt-4"
)
```

#### After (Gemini)
```python
from repo_qa_agent import RepoQAAgent

agent = RepoQAAgent(
    google_api_key="your-google-key",
    model_name="gemini-1.5-pro"
)
```

### Pricing Comparison

**Google Gemini** is more cost-effective than OpenAI:

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| gemini-1.5-flash | Free tier available | Free tier available |
| gemini-1.5-pro | $3.50 | $10.50 |

vs OpenAI:
| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| gpt-3.5-turbo | $0.50 | $1.50 |
| gpt-4 | $30.00 | $60.00 |

**Note:** Gemini has a generous free tier for testing!

### Benefits of Gemini

✅ **Free tier** - Great for development and testing
✅ **Cost-effective** - Lower pricing for production
✅ **Fast** - gemini-1.5-flash is very quick
✅ **Long context** - Supports up to 1M tokens
✅ **Multimodal** - Can handle images (future feature)

### Troubleshooting

#### Error: "Import langchain_google_genai could not be resolved"
```powershell
pip install langchain-google-genai
```

#### Error: "GOOGLE_API_KEY not set"
```powershell
$env:GOOGLE_API_KEY = "your-key-here"
```

#### Error: "API key not valid"
- Check your API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Make sure you copied the entire key
- Verify the key is enabled

### Rollback to OpenAI (If Needed)

If you need to switch back to OpenAI:

1. Restore `requirements.txt`:
   ```
   langchain-openai>=0.0.5
   tiktoken>=0.5.2
   ```

2. Install OpenAI packages:
   ```powershell
   pip install langchain-openai tiktoken
   ```

3. Set OpenAI API key:
   ```powershell
   $env:OPENAI_API_KEY = "sk-your-key"
   ```

4. Use `-m gpt-3.5-turbo` or `-m gpt-4` in commands

### Testing the Migration

Run the test to verify everything works:

```powershell
cd Github_scanner

# Set your Google API key
$env:GOOGLE_API_KEY = "your-key-here"

# Test basic functionality
python examples.py
```

### Summary

✅ All code updated to use Google Gemini
✅ Default model: gemini-1.5-flash
✅ API key: GOOGLE_API_KEY
✅ Same functionality, better pricing
✅ Ready to use!

---

**Next Steps:**
1. Install new dependencies: `pip install langchain-google-genai`
2. Get Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Set `$env:GOOGLE_API_KEY = "your-key"`
4. Test: `python cli.py ask https://github.com/pallets/flask -q "What is Flask?"`
