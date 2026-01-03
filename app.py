import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# --- UPDATED IMPORTS (Fixes the "Module Not Found" error) ---
# We point directly to the specific file, not the general folder
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

load_dotenv()
app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("VITE_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL") 

# --- AI SETUP ---
def get_ai_response(user_text):
    try:
        if not API_KEY:
            return "Error: Google API Key is missing."

        # Initialize Embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=API_KEY)
        
        # Load the Brain
        # allow_dangerous_deserialization is required for local files
        vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        
        # Search & Answer
        docs = vector_store.similarity_search(user_text, k=3)
        
        # Using a standard, reliable model to avoid API errors
        llm = ChatGoogleGenerativeAI(model="gemma-3-27b-it", google_api_key=API_KEY, temperature=0.3)
        chain = load_qa_chain(llm, chain_type="stuff")
        
        response = chain.run(input_documents=docs, question=user_text)
        return response
    except Exception as e:
        print(f"AI Error: {e}")
        return "I encountered an error connecting to my brain."

# --- TELEGRAM ROUTES ---
@app.route("/", methods=["GET"])
def index():
    return "Telegram Bot is Running! 🚀"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_text = update["message"]["text"]
        
        # Generate Answer
        answer = get_ai_response(user_text)

        # Send Reply
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": answer})
    
    return "OK", 200

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    webhook_endpoint = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    telegram_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    response = requests.post(telegram_api, json={"url": webhook_endpoint})
    return f"Webhook setup result: {response.text}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)