import discord

def BalanceEmbed(pts, user: discord.Member):
    embed = discord.Embed(
        title="**Point System - Balance**",
        description=f"``{pts}`` **Points**",
        color=discord.Color.from_rgb(255,0,0)
    )
    
    embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
    return embed