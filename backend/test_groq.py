import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

api_key = os.getenv("GROQ_API_KEY")

print(f"🔑 API Key: {api_key[:15] if api_key else 'NOT FOUND'}...")

try:
    from groq import Groq
    client = Groq(api_key=api_key)
    
    # Best English models only
    models_to_test = [
        "qwen/qwen3.8-27b",
        "qwen/qwen3.6-27b",
        "groq/compound",
        "openai/gpt-oss-20b"
    ]
    
    print("\n📡 Testing best English models...\n")
    
    for model in models_to_test:
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Always respond in English."},
                    {"role": "user", "content": "Say 'Hello WeatherGPT!' in one line"}
                ],
                model=model,
                max_tokens=50,
            )
            print(f"✅ {model}: {response.choices[0].message.content}")
        except Exception as e:
            print(f"❌ {model}: {str(e)[:80]}...")
            
except Exception as e:
    print(f"❌ Error: {e}")