import discord
from discord import app_commands
import json, platform

class Client(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.tree.sync()
        print("Slash-Commands wurden synchronisiert.")

intents = discord.Intents.all()
client = Client(intents=intents)

@client.tree.command(name="hello", description="Sag Hallo!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hallo {interaction.user.mention}!")

if platform.system() == "Windows":
    secrets_path = "C:\\Users\\User\\Desktop\\home\\fabian\\secrets.json"
else:
    secrets_path = "/home/fabian/secrets.json"

with open(secrets_path, "r") as f:
    data = json.load(f)
    BOT_TOKEN = data["BOT_TOKEN"]

client.run(BOT_TOKEN)
