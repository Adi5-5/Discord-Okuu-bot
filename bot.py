import discord
import requests
import asyncio
import os
import threading
from flask import Flask

# --- Tokens ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # Ton token Discord
HF_TOKEN = os.getenv("HF_TOKEN")            # Ton token Hugging Face

# --- Modèle Hugging Face léger ---
MODEL_NAME = "google/flan-t5-base"
HF_URL = "https://api.huggingface.co/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# --- Discord client ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# --- Fonction pour appeler l'IA ---
def query_ai(prompt):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200
    }
    try:
        response = requests.post(HF_URL, headers=HEADERS, json=payload)
        if response.status_code != 200:
            print("HF API Error:", response.text)
            return "⚠️ API Error"
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("Request failed:", e)
        return "⚠️ Request failed"

# --- Événements Discord ---
@client.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if client.user in message.mentions:
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
        if not prompt:
            return

        await message.channel.send("⏳ Génération en cours...")
        response = await asyncio.to_thread(query_ai, prompt)
        await message.channel.send(response[:2000])

# --- Serveur Flask pour Railway ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run).start()

# --- Lancement du bot ---
client.run(DISCORD_TOKEN)
