import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
import json
import os

def get_user_template():
    config = load_config()
    UserDataTemplate = {
   "xp": 0,
    "total_xp": 0,
    "chatting_xp": 0,
    "reaction_xp": 0,
    "xp_needed": config["xp"]["first_level"],
    "level": 1,
    "rank": 0
}
    return UserDataTemplate

def load_config():
    if os.path.exists("DataStore/XP/Configuration/config.json"):
        with open("DataStore/XP/Configuration/config.json", "r") as f:
            return json.load(f)
    return "404"

def get_user_rank(user_id):
    user_id = str(user_id)
    if os.path.exists(f"DataStore/XP/UserData/{user_id}.json"):
        with open(f"DataStore/XP/UserData/{user_id}.json", "r") as f:
            data = json.load(f)
            return data
    else:
        config = load_config()
        if config == "404":
            return "404", "Error loading configuration"
        with open(f"DataStore/XP/UserData/{user_id}.json", "w") as f:
            json.dump(get_user_template(), f, indent=4)
            return get_user_template()
    return "404"

def get_user_xp(user_id):
    user_data = get_user_rank(user_id)
    if user_data != "404":
        return user_data["total_xp"] if "total_xp" in user_data else 0
    return 0

def update_user_rank(user_id):
    user_id = str(user_id)
    user_data = get_user_rank(user_id)
    template = get_user_template()
    for key in template.keys():
        if key not in user_data:
            user_data[key] = template[key]
    with open(f"DataStore/XP/UserData/{user_id}.json", "w") as f:
        json.dump(user_data, f, indent=4)
        return True

def set_user_xp(user_id, xp):
    user_id = str(user_id)
    user_data = get_user_rank(user_id)
    user_data["xp"] = abs(xp)
    user_data["total_xp"] = abs(xp)
    with open(f"DataStore/XP/UserData/{user_id}.json", "w") as f:
        json.dump(user_data, f, indent=4)
        return True

def add_user_xp(user_id, xp):
    user_id = str(user_id)
    user_data = get_user_rank(user_id)
    user_data["xp"] += abs(xp)
    user_data["total_xp"] += abs(xp)
    with open(f"DataStore/XP/UserData/{user_id}.json", "w") as f:
        json.dump(user_data, f, indent=4)
    return True

def set_user_level(user_id, level):
    user_id = str(user_id)
    user_data = get_user_rank(user_id)
    user_data["level"] = abs(level)
    with open(f"DataStore/XP/UserData/{user_id}.json", "w") as f:
        json.dump(user_data, f, indent=4)
        return True

def save_leaderboard(leaderboard):
    with open("DataStore/XP/RankSave/leaderboard.json", "w") as f:
        json.dump(leaderboard, f, indent=4)
        
def load_leaderboard():
    if os.path.exists("DataStore/XP/RankSave/leaderboard.json"):
        with open("DataStore/XP/RankSave/leaderboard.json", "r") as f:
            return json.load(f)
    return []

def update_leaderboard():
    leaderboard_dict = load_leaderboard()
    # Umwandeln in Liste
    # Alle UserData-Dateien laden
    user_data_dir = "DataStore/XP/UserData/"
    leaderboard = []
    for filename in os.listdir(user_data_dir):
        if filename.endswith(".json"):
            user_id = filename[:-5]
            with open(os.path.join(user_data_dir, filename), "r") as f:
                data = json.load(f)
                data["user_id"] = user_id
                leaderboard.append(data)
    # Sortieren nach XP
    leaderboard.sort(key=lambda x: x.get("total_xp", 0), reverse=True)
    # Ränge setzen und in UserData zurückschreiben
    for i, user in enumerate(leaderboard):
        user["rank"] = i + 1
        # In UserData speichern
        user_id = user["user_id"]
        with open(os.path.join(user_data_dir, f"{user_id}.json"), "w") as f:
            json.dump(user, f, indent=4)
    # Leaderboard als Dict speichern
    leaderboard_dict = {user["user_id"]: user for user in leaderboard}
    save_leaderboard(leaderboard_dict)
    
def format_number(n):
        if n >= 1_000_000_000:
            return f"{n/1_000_000_000:.1f}B"
        elif n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        elif n >= 1_000:
            return f"{n/1_000:.1f}k"
        else:
            return str(n)
        
def level_to_xp(level):
    config = load_config()
    xp = 0
    for lvl in range(1, level, 1):
        if lvl == 1:
            print(level)
            xp = 75
        else:
            xp += (config["xp"]["increment"]*(lvl-1))+75
            print("Level:", lvl, "XP:", xp)
    return xp

def update_user_level(user_id):
    user_id = str(user_id)
    user_data = get_user_rank(user_id)
    config = load_config()
    xp = user_data["total_xp"]
    user_data["level"] = 1
    user_data["xp_needed"] = config["xp"]["first_level"]
    while xp >= user_data["xp_needed"] and user_data["level"] < config["max_level"]:
        print(xp, user_data["xp_needed"])
        user_data["level"] += 1
        xp -= user_data["xp_needed"]
        user_data["xp_needed"] = int(user_data["xp_needed"] + config["xp"]["increment"])
    user_data["xp"] = xp
    with open(f"DataStore/XP/UserData/{user_id}.json", "w") as f:
        json.dump(user_data, f, indent=4)
        return True

class XP_Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rank", description="Zeigt dein XP-Profil als Bild")
    async def rank(self, interaction: discord.Interaction, member: discord.User = None):
        await interaction.response.defer()
        if member is None:
            member = interaction.user
        update_user_rank(member.id)
        update_leaderboard()
        update_user_level(member.id)

        # Daten des Users abrufen
        user_data = get_user_rank(member.id)
        xp = user_data["xp"] if "xp" in user_data else "Err404"
        xp_needed = user_data["xp_needed"] if "xp_needed" in user_data else "Err404"
        level = user_data["level"] if "level" in user_data else "Err404"
        rank = user_data["rank"] if "rank" in user_data else "Err404"
        # XP-Werte kürzen
        xp_str = format_number(xp) if isinstance(xp, int) else str(xp)
        xp_needed_str = format_number(xp_needed) if isinstance(xp_needed, int) else str(xp_needed)

        # Profilbild herunterladen
        async with aiohttp.ClientSession() as session:
            async with session.get(member.display_avatar.url) as resp:
                avatar_bytes = await resp.read()

        # Profilbild rund machen
        def make_rounded(im):
            # Erstelle eine größere Maske für bessere Kantenglättung
            scale = 4
            big_size = (im.size[0]*scale, im.size[1]*scale)
            mask = Image.new("L", big_size, 0)
            draw = ImageDraw.Draw(mask)
            # Ellipse leicht kleiner und mittig
            draw.ellipse((scale, scale, big_size[0]-scale, big_size[1]-scale), fill=255)
            mask = mask.resize(im.size, Image.LANCZOS)
            im.putalpha(mask)
            return im

        scale = 4
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((115*scale, 115*scale))
        avatar = make_rounded(avatar)
        
        # Bild erstellen
        img = Image.new("RGBA", (800*scale, 200*scale), (30,33,36))
        draw = ImageDraw.Draw(img)
        # Hintergrund-Dreieck
        draw.polygon([(540*scale,0),(800*scale,0),(800*scale,200*scale),(690*scale,200*scale)], fill=(235,0,0))
        # Profilbild einfügen
        img.paste(avatar, (15*scale, 15*scale), avatar)
        # Text
        try:
            # Schriftarten laden
            font_bold = ImageFont.truetype("arialbd.ttf", 32*scale)  # Fett
            font = ImageFont.truetype("arial.ttf", 28*scale)         # Normal
            small_font = ImageFont.truetype("arial.ttf", 30*scale)
        except:
            font_bold = ImageFont.load_default()
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        # Position berechnen
        x = 145*scale
        y = 25*scale
        draw.text((x, y), "@", font=small_font, fill=(255,255,255))
        # Breite des "@" holen
        at_width = draw.textlength("@", font=small_font)
        draw.text((x+at_width, y), member.name, font=font_bold, fill=(255,255,255))
        
        # Abgerundeter Strich unter Username
        line_x = 145*scale
        line_y = 68*scale
        line_w = int(draw.textlength(f"@{member.name}", font=font_bold))+20*scale
        line_h = 4*scale
        draw.rounded_rectangle([line_x, line_y, line_x+line_w, line_y+line_h], radius=3*scale, fill=(235,0,0))
        # Fortschrittsbalken direkt unter Profilbild
        bar_x, bar_y, bar_w, bar_h = 15*scale, 145*scale, 625*scale, 35*scale
        # Fortschrittsbalken zeichnen
        draw.rounded_rectangle([bar_x, bar_y, bar_x+bar_w, bar_y+bar_h], radius=15*scale, fill=(255,255,255))

        # Fortschritt berechnen
        progress = int((xp / xp_needed) * bar_w) if xp_needed > 0 else 0

        # Füllung als eigenes Image mit Maske
        if progress > 0:
            fill_img = Image.new("RGBA", (bar_w, bar_h), (74,76,81,0))
            fill_draw = ImageDraw.Draw(fill_img)
            fill_draw.rounded_rectangle([0, 0, progress, bar_h], radius=15*scale, fill=(200,0,0))
            # Maske für die Füllung
            mask = Image.new("L", (bar_w, bar_h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([0, 0, bar_w, bar_h], radius=15*scale, fill=255)
            fill_img.putalpha(mask)
            img.paste(fill_img, (bar_x, bar_y), fill_img)

        # Level, XP, Rank unter Strich
        draw.text((145*scale, 90*scale), f"Level: {level}   XP: {xp_str} / {xp_needed_str}   Rank: {rank}", font=font, fill=(255,255,255))

        img = img.resize((800, 200), Image.LANCZOS)
        
        # Bild speichern
        with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)
            await interaction.followup.send(file=discord.File(fp=image_binary, filename=f"{member.name}'s_xp_card.png"))

    @app_commands.command(name="set_level", description="Setzt das Level eines Users")
    async def set_level(self, interaction: discord.Interaction, member: discord.User, amount: int):
        set_user_xp(member.id, level_to_xp(amount))
        update_user_level(member.id)
        update_leaderboard()
        await interaction.response.send_message(f"Set {member.name}'s Level to {amount}.")
        
    @app_commands.command(name="set_xp", description="Setzt die XP eines Users")
    async def set_xp(self, interaction: discord.Interaction, member: discord.User, amount: int):
        set_user_xp(member.id, amount)
        update_user_level(member.id)
        update_leaderboard()
        await interaction.response.send_message(f"Set {member.name}'s XP to {amount}.")

    @app_commands.command(name="add_xp", description="Fügt XP zu einem User hinzu")
    async def add_xp(self, interaction: discord.Interaction, member: discord.User, amount: int):
        current_xp = get_user_xp(member.id)
        set_user_xp(member.id, current_xp + amount)
        update_user_level(member.id)
        update_leaderboard()
        await interaction.response.send_message(f"Added {amount} XP to {member.name}.")

async def setup(bot):
    await bot.add_cog(XP_Manager(bot))