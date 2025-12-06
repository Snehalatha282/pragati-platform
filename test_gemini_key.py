
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

print(f"Loaded API Key: {api_key}")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env")
    exit(1)

try:
    genai.configure(api_key=api_key)
    with open('models.txt', 'w') as f:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"{m.name}\n")
    
    print("Models listed to models.txt", flush=True)

except Exception as e:
    with open('models.txt', 'w') as f:
        f.write(f"ERROR: {e}")
    print(f"ERROR: {e}", flush=True)
