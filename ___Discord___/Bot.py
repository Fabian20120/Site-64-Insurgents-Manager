import json
import discord
import platform
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Load Cogs
async def load_cogs():
    from ___Discord___.Systems.Server_Management.XP import XP_Manager
    await bot.add_cog(XP_Manager(bot))
    await bot.tree.sync()  # Slash Commands synchronisieren

@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")
    await load_cogs()

if platform.system() == "Windows":
    secrets_path = "C:\\Users\\User\\Desktop\\home\\fabian\\secrets.json"
else:
    secrets_path = "/home/fabian/secrets.json"

with open(secrets_path, "r") as f:
    data = json.load(f)
    BOT_TOKEN = data["BOT_TOKEN"]

bot.run(BOT_TOKEN)