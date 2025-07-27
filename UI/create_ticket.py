import discord
from discord.ext import commands
from discord import ui, Interaction, PermissionOverwrite, Embed, Color
from roles import UserRoles

LOG_CHANNEL_ID = 1398847172463689728  # Passe die ID ggf. an

class CreateTicket(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.select(
        custom_id="ticket_type",
        placeholder="Select Ticket Type",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Questions", description="You have questions related to the server or SSRP."),
            discord.SelectOption(label="Suggestions", description="You have suggestions to improve the server."),
            discord.SelectOption(label="Staff question", description="You have a question for the staff team."),
            discord.SelectOption(label="Report a player", description="You want to report a player/user/staff for breaking the rules."),
            discord.SelectOption(label="Bug report", description="You want to report a bug or issue with the server or SSRP."),
            discord.SelectOption(label="Appeal", description="You want to appeal a punishment or ban."),
            discord.SelectOption(label="Points", description="You want to receive points for a specific reason."),
            discord.SelectOption(label="Other", description="You have another reason to create a ticket.")
        ]
    )
    async def select_callback(self, select: ui.Select, interaction: Interaction):
        reason = select.values[0]
        user = interaction.user

        # Rollen holen
        sr_mod = interaction.guild.get_role(UserRoles.Senior_Moderator)
        mod = interaction.guild.get_role(UserRoles.Moderator)
        admin = interaction.guild.get_role(UserRoles.Administrator)
        prog = interaction.guild.get_role(UserRoles.Programmer)

        overwrites = {
            interaction.guild.default_role: PermissionOverwrite(view_channel=False),
            user: PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
        }
        # Staff-Rollen hinzufügen, falls vorhanden
        for role in [sr_mod, mod, admin]:
            if role:
                overwrites[role] = PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True)
        if reason in ["Suggestions", "Bug report"] and prog:
            overwrites[prog] = PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True)

        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{user.name}", overwrites=overwrites, reason=f"Ticket: {reason}"
        )

        await interaction.response.send_message(f"✅ Your ticket got created: {channel.mention}", ephemeral=True)

        # Thematisch angepasste Nachricht
        message_map = {
            "Questions": "Please ask your question. A staff member will get back to you as soon as possible.",
            "Suggestions": "Share your idea or suggestion here. We really appreciate your feedback!",
            "Staff question": "Please describe your question for the staff team as clearly as possible.",
            "Report a player": "Please provide the player's name, date/time, and a description of the incident. Evidence (screenshots/videos) is very helpful.",
            "Bug report": "Please describe the bug clearly, when and where it occurs, and steps to reproduce it if possible.",
            "Appeal": "Please include your Discord or in-game name, the date of the punishment, and your appeal statement.",
            "Points": "Please explain why you should receive points (e.g. event participation or redemption).",
            "Other": "Please describe your request as clearly as possible. We're happy to assist you."
        }

        embed = Embed(title=f"{reason} Ticket", color=Color.blurple())
        embed.add_field(name="Hello!", value=message_map.get(reason, "Please describe your issue."), inline=False)
        embed.add_field(name="Staff Team", value=" ".join(
            role.mention for role in [sr_mod, mod, admin] if role
        ), inline=False)
        embed.set_footer(text=f"Ticket by {user.display_name}")

        await channel.send(
            content=f"{user.mention}\n\nUse `/claim` to claim this ticket and `/close` to close it.",
            embed=embed
        )

        # Log-Channel benachrichtigen
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"📩 New ticket created: {channel.mention} by {user.mention} (Reason: **{reason}**)"
            )