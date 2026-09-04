# backend/check_models.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ No API key found")
    exit(1)

print(f"🔑 Using API Key: {api_key[:15]}...")

try:
    from groq import Groq
    client = Groq(api_key=api_key)
    
    # List available models
    print("\n📋 Fetching available models...")
    models = client.models.list()
    
    print("\n✅ Available Models:")
    for model in models.data:
        print(f"   - {model.id}")
        
except Exception as e:
    print(f"❌ Error: {e}")