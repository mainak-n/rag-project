import os
import sys

# --- STEP 1: IMPORTS ---
print("------------------------------------------------")
print("[INFO] STEP 1: Importing libraries...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("   [OK] Dotenv loaded")
    
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    print("   [OK] Google AI Embeddings loaded")
    
    from langchain_community.vectorstores import FAISS
    print("   [OK] FAISS (Database) loaded")
    
    from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
    print("   [OK] PDF Loaders loaded")
    
    # --- FIX: Try the new import path first, fall back to old if needed ---
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    print("   [OK] Text Splitter loaded")
    
except ImportError as e:
    print("\n[ERROR] CRITICAL IMPORT ERROR:")
    print(f"   Could not import a required library. Error detail: {e}")
    print("   [ACTION] PLEASE RUN: pip install langchain-text-splitters")
    sys.exit(1)

# --- STEP 2: CHECK KEYS ---
print("\n[INFO] STEP 2: Checking API Keys...")
my_api_key = os.getenv("VITE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not my_api_key:
    print("   [ERROR] No API Key found in .env file.")
    print("   [ACTION] Make sure you have a file named '.env' with 'VITE_API_KEY=AIza...' inside it.")
    sys.exit(1)
else:
    print(f"   [OK] API Key found: {my_api_key[:4]}********")


def create_vector_db():
    print("\n[INFO] STEP 3: Looking for PDFs...")
    # Check if directory exists
    if not os.path.exists("data"):
        print("   [ERROR] 'data' folder not found.")
        print("   [ACTION] Create a folder named 'data' and put your PDFs inside.")
        return

    # Load PDFs
    loader = DirectoryLoader("data", glob="*.pdf", loader_cls=PyPDFLoader)
    try:
        documents = loader.load()
    except Exception as e:
        print(f"   [ERROR] loading PDFs: {e}")
        return

    if len(documents) == 0:
        print("   [WARNING] No PDFs found in 'data' folder.")
        return
    else:
        print(f"   [OK] Found {len(documents)} pages of text.")

    # Split Text
    print("\n[INFO] STEP 4: Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    print(f"   [OK] Created {len(texts)} chunks of knowledge.")

    # Create Embeddings
    print("\n[INFO] STEP 5: Sending data to Google AI (this takes time)...")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=my_api_key
        )
        vector_store = FAISS.from_documents(texts, embeddings)
        print("   [OK] Embeddings received from Google.")
    except Exception as e:
        print(f"   [ERROR] connecting to Google: {e}")
        print("   [ACTION] Check if your API Key is valid and has credits.")
        return

    # Save
    print("\n[INFO] STEP 6: Saving database to disk...")
    vector_store.save_local("faiss_index")
    print("   [SUCCESS] The 'faiss_index' folder has been created.")
    print("   [ACTION] You can now run 'python app.py'")
    print("------------------------------------------------")

if __name__ == "__main__":
    create_vector_db()