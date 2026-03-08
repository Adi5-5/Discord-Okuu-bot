import discord
import requests
import asyncio
import os
import threading
from flask import Flask

# --- Tokens ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# --- Modèle AI Hugging Face ultra-léger ---
MODEL_URL = "https://api-inference.huggingface.co/models/distilgpt2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# --- Discord setup ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# --- Fonction de requête AI ---
def query_ai(prompt):
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True},
        "parameters": {"max_new_tokens": 150}
    }

    try:
        response = requests.post(MODEL_URL, headers=headers, json=payload)
        if response.status_code != 200:
            print("HF API Error:", response.text)
            return "🔴 API Error (🖕)."
        data = response.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        if isinstance(data, dict):
            return data.get("generated_text", "⚠️ Pas de réponse")
        return "⚠️ Erreur génération."
    except Exception as e:
        print("Request failed:", e)
        return "⚠️ Request failed."

# --- Events Discord ---
@client.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Mention ou réponse
    if client.user in message.mentions:
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
        if not prompt:
            return

        await message.channel.send("⏳ Please wait... ☢️")
        response = await asyncio.to_thread(query_ai, prompt)
        await message.channel.send(response[:2000])

# --- Serveur web pour Railway ---
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot running"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run).start()

# --- Run Discord bot ---
client.run(DISCORD_TOKEN)
