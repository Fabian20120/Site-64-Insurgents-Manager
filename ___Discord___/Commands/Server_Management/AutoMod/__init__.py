import discord
import json
from discord.commands import slash_command
from discord.ext import commands

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

class ChatFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="set_filter", description="Set a chat filter for the server")