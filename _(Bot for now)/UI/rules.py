import discord

async def send_rules(channel):
    embed = discord.Embed(
        title="📜 Server Rules",
        color=discord.Color.red()
    )

    embed.add_field(
        name="🔗 **Discord Policies**",
        value="**[Terms of Service](https://discord.com/terms)** • **[Community Guidelines](https://discord.com/guidelines)**",
        inline=False
    )

    embed.add_field(
        name="🧍 **General Behavior**",
        value=(
            "**Respect:** Be respectful to others.\n"
            "**No NSFW:** Vulgar language or imagery is not allowed.\n"
            "**No Violence:** Graphic behavior is prohibited.\n"
            "**One Account:** No alt accounts — one per user.***¹**\n"
            "**No Spam:** Spamming or flooding is not allowed.\n"
            "**No Trolling:** Don’t annoy others if they don’t want it.\n"
            "**Staff Respect:** Staff decisions are final — no disrespect."
        ),
        inline=False
    )

    embed.add_field(
        name="🛠️ **Server Usage**",
        value=(
            "**Bot Commands:** Only use bot commands in <#1240431397752144024> (except Beta Class+).\n"
            "**Pingable Name:** Your username must be mentionable.\n"
            "**No Exploiting:** Don’t abuse loopholes in the rules.\n"
            "**Punishment Privacy:** Don’t discuss warnings, mutes, or bans in public."
        ),
        inline=False
    )

    embed.add_field(
        name="📢 **Promotion & Language**",
        value=(
            "**No Self-Promo:** Promotion of anything (even in DMs) is forbidden.\n"
            "**English Only:** Only English is allowed — no other languages."
        ),
        inline=False
    )

    embed.add_field(
        name="📌 **Note**",
        value=(
            "**Read Pins:** Before chatting, check pinned messages — they may include important, channel-specific rules."
        ),
        inline=False
    )
    embed.set_footer(
    text=(
            "¹ If you want to use an alternate account or joined with a new one, please open a ticket "
            "and state your reason. We can transfer or merge bot data so that two accounts are possible.\n"
        )
    )
    
    await channel.send(embed=embed)