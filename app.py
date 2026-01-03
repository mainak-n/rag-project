import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# --- STABLE IMPORTS ---
# These work 100% with langchain==0.1.20
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

load_dotenv()
app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("VITE_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
# Your Render URL (Make sure this matches your actual URL in Render Dashboard)
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL") 

# --- AI SETUP ---
def get_ai_response(user_text):
    try:
        if not API_KEY:
            return "Error: Google API Key is missing."

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=API_KEY)
        
        # Load the Brain
        # allow_dangerous_deserialization is required for local pickle files
        vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        
        # Search & Answer
        docs = vector_store.similarity_search(user_text, k=3)
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
    # 1. Receive data from Telegram
    update = request.get_json()
    
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        
        # Check if text exists (ignore stickers/photos)
        if "text" in update["message"]:
            user_text = update["message"]["text"]
            print(f"User {chat_id} said: {user_text}")

            # 2. Generate Answer
            answer = get_ai_response(user_text)

            # 3. Send Reply back to Telegram
            send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": answer
            }
            requests.post(send_url, json=payload)
    
    return "OK", 200

# --- ONE-TIME SETUP ROUTE ---
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    # Construct the webhook URL
    webhook_endpoint = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    telegram_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    
    print(f"Setting webhook to: {webhook_endpoint}")
    
    response = requests.post(telegram_api, json={"url": webhook_endpoint})
    return f"Webhook setup result: {response.text}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)