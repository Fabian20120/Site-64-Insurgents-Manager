import json
import os
import discord
from discord.ext import commands

POINT_SAVE = "points.json"

def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    return {}

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def add_points(user_id, points, file_path=POINT_SAVE):
    data = load_json(file_path)
    if user_id in data:
        data[user_id] += abs(points)
    else:
        data[user_id] = abs(points)
    save_json(file_path, data)

def sub_points(user_id, points, file_path=POINT_SAVE):
    data = load_json(file_path)
    if user_id in data:
        data[user_id] -= abs(points)
    save_json(file_path, data)
    
def get_points(user_id, file_path=POINT_SAVE):
    data = load_json(file_path)
    return data.get(user_id, 0)

class Point_Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="add_points")
    async def add_points(self, ctx, user: discord.User, points: int):
        add_points(user.id, points)
        await ctx.send(f"Added {points} points to {user.name}.")

    @commands.slash_command(name="sub_points")
    async def sub_points(self, ctx, user: discord.User, points: int):
        sub_points(user.id, points)
        await ctx.send(f"Subtracted {points} points from {user.name}.")

    @commands.slash_command(name="get_points")
    async def get_points(self, ctx, user: discord.User):
        points = get_points(user.id)
        await ctx.send(f"{user.name} has {points} points.")
        
    @commands.slash_command(name="points")
