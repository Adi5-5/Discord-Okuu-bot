import discord
import requests
import asyncio
import os

DISCORD_TOKEN = os.getenv("MTQ3Nzc1MDgyNzAwNjQyNzI1MA.GlOBPa.u8f2re6jNlbmQ7-OrIv5RgxvSeaKjSR82JgdkA")
HF_TOKEN = os.getenv("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")

# Modèle AI Hugging Face (rapide et stable pour Discord)
MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def query_ai(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 200, "temperature": 0.7}
    }
    response = requests.post(MODEL_URL, headers=headers, json=payload)
    if response.status_code != 200:
        return "Erreur API."
    data = response.json()
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]
    return "Erreur génération."

@client.event
async def on_ready():
    print(f"Bot connecté en tant que {client.user} (Utsuho)")

@client.event
async def on_message(message):
    # Ignore ses propres messages
    if message.author == client.user:
        return

    # Vérifie s'il est mentionné ou si le message répond à un de ses messages
    is_mentioned = client.user in message.mentions
    is_reply_to_utsuho = message.reference and message.reference.resolved.author == client.user if message.reference else False

    if is_mentioned or is_reply_to_utsuho:
        # Nettoyage du message : enlever la mention du bot
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()

        await message.channel.send("⏳ Génération...")

        # Appelle l’IA
        response = await asyncio.to_thread(query_ai, prompt)

        # Envoie la réponse
        await message.channel.send(response[:2000])

client.run("MTQ3Nzc1MDgyNzAwNjQyNzI1MA.GlOBPa.u8f2re6jNlbmQ7-OrIv5RgxvSeaKjSR82JgdkA")