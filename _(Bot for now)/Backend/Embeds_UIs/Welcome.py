import discord

SUPPORT_CHANNEL_ID = 1240626005165477930
RULES_CHANNEL_ID = 1240031594463363103
GENERAL_CHANNEL_ID = 1240029491473158279

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # persistent view

    @discord.ui.button(label="Read the Rules", style=discord.ButtonStyle.primary, custom_id="btn_rules")
    async def rules_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        rules_channel = interaction.guild.get_channel(RULES_CHANNEL_ID)
        if rules_channel:
            await interaction.response.send_message(
                f"Please check out the rules here: {rules_channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Rules channel not found.", ephemeral=True)

    @discord.ui.button(label="Get Support", style=discord.ButtonStyle.success, custom_id="btn_support")
    async def support_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        support_channel = interaction.guild.get_channel(SUPPORT_CHANNEL_ID)
        if support_channel:
            await interaction.response.send_message(
                f"Our support team is here to help you! Please visit {support_channel.mention} for assistance.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Support channel not found.", ephemeral=True)

    @discord.ui.button(label="Say Hello", style=discord.ButtonStyle.secondary, custom_id="btn_hello")
    async def hello_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        general_channel = interaction.guild.get_channel(GENERAL_CHANNEL_ID)
        if general_channel:
            await interaction.response.send_message(
                f"Our general text channel: {general_channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Text channel not found.", ephemeral=True)


def Create_Embed(member: discord.Member):
    lang = getattr(member, "locale", "en").lower()
    is_german = lang.startswith("de")

    if is_german:
        title = "👋 Willkommen bei Site 64 Insurgents!"
        description = (
            f"{member.mention}, schön, dass du hier bist!\n\n"
            "Wenn du Fragen hast oder Hilfe brauchst, frag einfach drauf los.\n"
            "Du kannst das Team erwähnen oder andere Mitglieder fragen – wir helfen dir gern!\n\n"
            "*Viel Spaß und halte dich an die Regeln!*"
        )
    else:
        title = "👋 Welcome to Site 64 Insurgents!"
        description = (
            f"{member.mention}, we’re glad to have you here!\n\n"
            "Feel free to ask anything if you need help.\n"
            "You can tag our staff or simply ask other members — we're all here to support you.\n\n"
            "*Enjoy your stay and follow the rules!*"
        )

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.from_rgb(255, 0, 0)
    )
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)

    return embed
