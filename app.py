import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
# These imports will now work 100%
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
# Check for key in environment (Cloud) OR .env file (Local)
API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("VITE_API_KEY")

if not API_KEY:
    print("CRITICAL WARNING: No Google API Key found. The bot will crash.")

@app.route("/", methods=["GET"])
def health_check():
    return "WhatsApp Bot is Running! 🚀"

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').lower()
    print(f"User asked: {incoming_msg}")
    
    # 1. Load the Brain
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=API_KEY
        )
        # allow_dangerous_deserialization is required for local FAISS files
        vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Error loading FAISS: {e}")
        return str(MessagingResponse().message("Error: My memory file (faiss_index) is missing."))

    # 2. Search for relevant context
    docs = vector_store.similarity_search(incoming_msg, k=3)
    
    # 3. Setup Gemma 3 (27B)
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemma-3-27b-it", 
            google_api_key=API_KEY, 
            temperature=0.3
        )
        chain = load_qa_chain(llm, chain_type="stuff")
        
        # 4. Ask the AI
        answer = chain.run(input_documents=docs, question=incoming_msg)
    except Exception as e:
        print(f"AI Error: {e}")
        answer = "I'm having trouble connecting to the AI brain right now."

    # 5. Reply
    resp = MessagingResponse()
    resp.message(answer)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)