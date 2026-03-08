        import discord
import asyncio
import os
import threading
from flask import Flask
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# --- Tokens ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# --- Modèle local SmolLM2 ---
CHECKPOINT = "HuggingFaceTB/SmolLM2-360M-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Chargement du modèle sur {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
model = AutoModelForCausalLM.from_pretrained(CHECKPOINT).to(DEVICE)
print("Modèle chargé ✅")

# --- Discord setup ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# --- Fonction de génération ---
def query_ai(prompt):
    try:
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print("Request failed:", e)
        return "🔴 API Error (🖕)."

# --- Events Discord ---
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

        await message.channel.send("⏳ Generating. . . ☢️")
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
