import discord

async def send_rules(channel):
    embed = discord.Embed(
        title="──────── RULES ────────",
        description=(
            "**1.** Follow Discord Terms of Service & Community Guidelines;\n"
            "[DiscordTOS](https://discord.com/terms), [Discord Guidelines](https://discord.com/guidelines)\n"
            "**2.** Be respectful to others.\n"
            "**3.** Use bot commands only in <#1240431397752144024> only, exceptions apply to Beta Class+.\n"
            "**4.** Vulgar (NSFW) language or images will not be tolerated.\n"
            "**5.** No expression of graphic behaviour is tolerated.\n"
            "**6.** No alt accounts, you are only allowed to have one account here.\n"
            "**7.** Spamming/flooding the chat is prohibited; copy and pasted text (\"copypastas\") will be deleted also result in a punishment.\n"
            "**8.** Make sure your name is possible to ping/mention (@); names like *neryo* will be renamed.\n"
            "**9.** Exploiting, looking for shortcomings in rules will result in a punishment.\n"
            "**10.** Do not annoy/troll anyone when they do not wish to be bothered.\n"
            "**11.** Do not discuss punishments such as warnings, mutes, and bans in any channels. It is a sore topic and creates a negative atmosphere. If you have a problem or would like to discuss the punishment with staff, please DM the staff of your choice.\n"
            "**12.** No staff disrespect - Staff decisions are final, and disrespect will not be tolerated.\n"
            "**13.** Any type of Self-Promotion is NOT allowed. This includes YouTube channels, Discord servers, Instagram profiles etc. (In and out of DMs)\n"
            "**14.** This is an English Only Server, this means your are not allowed speaking other languages like Russian, or German.\n"
            "**Note:** Before talking in channels, make sure to read the pins as they contain important information (including rules) specific to that channel. \n"

        ),
        color=discord.Color.red()
    )
    await channel.send(embed=embed)