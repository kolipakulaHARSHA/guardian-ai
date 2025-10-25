"""
List available Gemini models from Google AI API
"""
import requests
import json

api_key = "AIzaSyCqGVoHi9VuiNOG0QAbBwPrFe1xuXXEP2s"

# Make API call to list models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    
    print("=" * 70)
    print("AVAILABLE GEMINI MODELS")
    print("=" * 70)
    
    if 'models' in data:
        # Filter models that support generateContent
        generation_models = [
            m for m in data['models'] 
            if 'generateContent' in m.get('supportedGenerationMethods', [])
        ]
        
        print(f"\nFound {len(generation_models)} models that support text generation:\n")
        
        for i, model in enumerate(generation_models, 1):
            name = model.get('name', 'Unknown')
            display_name = model.get('displayName', 'N/A')
            description = model.get('description', 'No description')
            
            print(f"{i}. Model: {name}")
            print(f"   Display Name: {display_name}")
            print(f"   Description: {description[:100]}...")
            print(f"   Supported Methods: {', '.join(model.get('supportedGenerationMethods', []))}")
            print()
        
        # Show which model names to use
        print("=" * 70)
        print("MODEL NAMES TO USE IN LANGCHAIN:")
        print("=" * 70)
        for model in generation_models[:5]:
            # Extract just the model ID (remove 'models/' prefix)
            model_id = model['name'].replace('models/', '')
            print(f"  - {model_id}")
        
    else:
        print("No models found in response")
        print(f"Response: {json.dumps(data, indent=2)}")
        
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
