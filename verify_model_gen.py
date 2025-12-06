
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {'Yes' if api_key else 'No'}", flush=True)

if not api_key:
    exit(1)

genai.configure(api_key=api_key)

# Test models with and without prefix
models_to_test = ['gemini-flash-latest', 'models/gemini-flash-latest', 'gemini-1.5-flash']

for model_name in models_to_test:
    print(f"\nTesting model: {model_name}...", flush=True)
    try:
        model = genai.GenerativeModel(model_name)
        start_time = time.time()
        response = model.generate_content("Reply with 'OK'")
        duration = time.time() - start_time
        print(f"SUCCESS with {model_name} in {duration:.2f}s", flush=True)
        print(f"Response: {response.text}", flush=True)
        break # Stop on first success just to be quick
    except Exception as e:
        print(f"FAILED with {model_name}: {e}", flush=True)
