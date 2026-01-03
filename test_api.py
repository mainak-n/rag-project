import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load Key
load_dotenv()
api_key = os.getenv("VITE_API_KEY") or os.getenv("GOOGLE_API_KEY")

print("------------------------------------------------")
print("[INFO] TESTING GOOGLE API CONNECTION...")

if not api_key:
    print("[ERROR] No API Key found in .env file.")
    exit()

try:
    # 2. Simple Hello World
    llm = ChatGoogleGenerativeAI(
        model="gemma-3-27b-it", 
        google_api_key=api_key
    )
    print("   [INFO] Sending request to Google...")
    
    response = llm.invoke("Say 'Hello! The API is working correctly.'")
    
    print("\n[SUCCESS] API Works!")
    print(f"   [AI REPLY]: {response.content}")
    print("------------------------------------------------")

except Exception as e:
    print("\n[FAIL] API ERROR:")
    print(e)
    print("\n[ACTION] Check if your API Key is correct in the .env file.")