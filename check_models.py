import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: API Key not found!")
else:
    genai.configure(api_key=api_key)
    print("Checking available GENERATION models for your API key...\n")
    
    found_any = False
    try:
        for m in genai.list_models():
            # Check if the model supports text generation (generateContent)
            if "generateContent" in m.supported_generation_methods:
                print(f"Supported Model: {m.name}")
                found_any = True
                
        if not found_any:
            print("No generation models found for this API key.")
    except Exception as e:
        print(f"API Error: {e}")