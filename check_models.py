import os
import base64
import requests
from groq import Groq
from dotenv import load_dotenv

# .env file se saare secrets securely load karega
load_dotenv()

groq_key = os.environ.get("GROQ_API_KEY")
webhook_url = os.environ.get("GDRIVE_WEBHOOK_URL")

# ==========================================
# TEST 1: GROQ AI MODELS CHECK (FROM .ENV)
# ==========================================
if not groq_key:
    print("❌ ERROR: .env file me GROQ_API_KEY nahi mili!")
else:
    try:
        client = Groq(api_key=groq_key)
        models = client.models.list()
        print("✅ GROQ CONNECTED! Aapke account me ye models chal rahe hain:")
        for m in models.data[:8]:
            print("  -", m.id)
    except Exception as e:
        print("❌ Groq Error:", e)

print("\n" + "="*50 + "\n")

# ==========================================
# TEST 2: 5TB GOOGLE DRIVE CHECK (FROM .ENV)
# ==========================================
if not webhook_url:
    print("❌ ERROR: .env file me GDRIVE_WEBHOOK_URL nahi mila!")
    print("👉 Apni .env file me GDRIVE_WEBHOOK_URL=https://script.google.com/... add karein.")
else:
    print("⏳ .env se Webhook URL mil gaya! 5TB Google Drive me test file bhej rahe hain...")
    payload = {
        "filename": "vijay_secure_test.txt",
        "mime_type": "text/plain",
        "file_base64": base64.b64encode(b"Hello Vijay Bhai! 100% Secure .env Connection Working!").decode("utf-8"),
        "sub_folder": "Test_Folder"
    }
    try:
        r = requests.post(webhook_url, json=payload, timeout=30)
        print("✅ DRIVE RESPONSE:", r.text)
    except Exception as e:
        print("❌ Drive Connection Error:", e)