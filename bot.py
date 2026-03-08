import discord
import requests
import asyncio
import os
import threading
from flask import Flask

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def query_ai(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(MODEL_URL, headers=headers, json=payload, timeout=60)

        if response.status_code != 200:
            print("HF ERROR:", response.text)
            return "⚠️ API error."

        data = response.json()

        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]

        return "⚠️ Generation error."

    except Exception as e:
        print("Request error:", e)
        return "⚠️ Request failed."

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

        await message.channel.send("⏳ Generating...")

        response = await asyncio.to_thread(query_ai, prompt)

        await message.channel.send(response[:2000])

# --- serveur web pour Railway ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run).start()

client.run(DISCORD_TOKEN)
