import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# --- IMPORTS ---
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = os.environ.get("GOOGLE_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL") 

# --- AUTO-CREATE BRAIN FUNCTION ---
def build_brain_if_missing():
    if not os.path.exists("faiss_index"):
        print("🧠 Brain not found! Creating it now...")
        try:
            if not os.path.exists("data"):
                os.makedirs("data") 
                print("⚠️ No data folder found. Created empty one.")
                return

            loader = DirectoryLoader("data", glob="*.pdf", loader_cls=PyPDFLoader)
            documents = loader.load()
            
            if not documents:
                print("⚠️ No PDFs found in data folder.")
                return

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            text_chunks = text_splitter.split_documents(documents)
            
            embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=API_KEY)
            vector_store = FAISS.from_documents(text_chunks, embeddings)
            vector_store.save_local("faiss_index")
            print("🎉 Brain created successfully on the server!")
        except Exception as e:
            print(f"❌ Error creating brain: {e}")
    else:
        print("🧠 Brain already exists.")

# Run builder on startup
build_brain_if_missing()

# --- AI SETUP ---
def get_ai_response(user_text):
    try:
        if not API_KEY:
            return "Error: Google API Key is missing."

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=API_KEY)
        vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = vector_store.similarity_search(user_text, k=3)
        
        # --- THE FIX IS HERE ---
        # We added convert_system_message_to_human=True to stop the error
        llm = ChatGoogleGenerativeAI(
            model="gemma-3-27b-it", 
            google_api_key=API_KEY, 
            temperature=0.3,
            convert_system_message_to_human=True
        )
        
        chain = load_qa_chain(llm, chain_type="stuff")
        
        return chain.run(input_documents=docs, question=user_text)
    except Exception as e:
        print(f"AI Error: {e}")
        return "I encountered an error connecting to my brain."

# --- ROUTES ---
@app.route("/", methods=["GET"])
def index():
    return "Telegram Bot is Running! 🚀"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_text = update["message"]["text"]
        
        answer = get_ai_response(user_text)

        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": answer})
    return "OK", 200

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    webhook_endpoint = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    telegram_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    response = requests.post(telegram_api, json={"url": webhook_endpoint})
    return f"Webhook setup result: {response.text}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)