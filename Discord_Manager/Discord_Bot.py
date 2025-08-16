import os
import discord
from discord.ext import commands, tasks
from discord import Option, Member, ApplicationContext
from Backend.Embeds_UIs import WelcomeEmbed, WelcomeView
import Backend
import pytz
from Backend.Embeds_UIs.CreateAnnouncmentView import AnnouncementStep1
from Managers.Platform_Manager import create_embed, get_stats
from UI import send_rules, CreateTicket, TrainingTypeView
from roles import UserRoles
import json
import pycountry
import datetime
import time
import asyncio

status = 2

detailed_status = "Controlled Instability — System operating under active protocol updates and adjustments, executing live patch deployment with continuous diagnostics monitoring."

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, dm_command=True)

bot.persistent_views_added=False

def parse_to_unix(date_str):
    #24-18:30
    day, time_part = date_str.split('-')
    hour, minute = map(int, time_part.split(':'))
    now = datetime.datetime.now()
    try:
        target = datetime.datetime(year=now.year, month=now.month, day=int(day), hour=hour, minute=minute)
    except ValueError:
        next_month = now.month + 1 if now.month < 12 else 1
        year = now.year if now.month < 12 else now.year + 1
        target = datetime.datetime(year=year, month=next_month, day=int(day), hour=hour, minute=minute)
    return int(target.timestamp())

@bot.event
async def on_member_join(member: discord.Member):
    welcome_channel = bot.get_channel(1240029491473158276)
    if welcome_channel is None:
        welcome_channel = await member.guild.fetch_channel(1240029491473158276)

    embed = WelcomeEmbed(member)
    view = WelcomeView()
    await welcome_channel.send(embed=embed, view=view)

@bot.event
async def on_ready():
    if not hasattr(bot, "persistent_views_added") or not bot.persistent_views_added:
        bot.add_view(WelcomeView())  # registriere persistent view fürs UI (Buttons)
        bot.add_view(Enlist_View())  # registriere persistent Enlist-View
        bot.persistent_views_added = True
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print("Bot is ready!")
    await bot.change_presence(status=discord.Status.idle, activity=None)
    await load_status_message()

@bot.slash_command(name="role_information")
async def RoleInformation(ctx: discord.ApplicationContext):
    support = await ctx.interaction.guild.fetch_channel(1240626005165477930)
    promotion = await ctx.interaction.guild.fetch_channel(1386863372028612729)
    embed = discord.Embed(
        title="📘 ROLE INFORMATION AND HIERARCHY",
        color=discord.Color.blue()
    )

    # DELTA CLASS
    embed.add_field(
        name="🔱 __DELTA CLASS__\nHighest Authority",
        value=(
            "• **The Engine**\n"
            "• **The Engineer**\n"
            "• **Overseers** – 400 points + personally appointed\n"
            "• **Head Commandant** – 500 points + personally appointed"
        ),
        inline=False
    )

    # GAMMA CLASS
    embed.add_field(
        name="💠 __GAMMA CLASS__\nHigh Authority",
        value="• **Gamma Director** – 200 points",
        inline=False
    )

    # BETA CLASS
    embed.add_field(
        name="🔶 __BETA CLASS__\nMedium Authority",
        value=(
            "• **Beta Commandant** – 100 points\n"
            "• **Senior Insurgent** – 40 points\n"
            "• **Insurgent** – 180 points; Can host raids, game nights, and trainings"
        ),
        inline=False
    )

    # ALPHA CLASS
    embed.add_field(
        name="🔹 __ALPHA CLASS__\nLowest Authority",
        value=(
            "• **Elite** – 120 points\n"
            "• **Senior Operative** – 100 points\n"
            "• **Operative** – 50 points\n"
            "• **Insurgent** – 30 points\n"
            "• **Militant** – 10 points\n"
            "• **Mercenary** – Attended one event or training\n"
            "• **Enlisted** – Just joined"
        ),
        inline=False
    )

    # SPECIAL ROLES
    embed.add_field(
        name="⭐ __SPECIAL ROLES__",
        value=(
            "• **VIP**\n"
            "• **Server Booster**\n"
            "• **YouTube Creator** – under 50,000 subscribers"
        ),
        inline=False
    )

    # MODERATOR ROLES
    embed.add_field(
        name="🛡 __MODERATOR ROLES__",
        value=(
            "• **Administrator**\n"
            "• **Senior Moderator**\n"
            "• **Moderator**\n"
            "• **Junior Moderator**\n"
            "_Apply when moderator applications are open._"
        ),
        inline=False
    )

    # POINT SYSTEM
    embed.add_field(
        name="📈 __Ways to Earn Points__",
        value=(
            "• Joining a **Raid** – max. 15 pts\n"
            "• Joining a **Training** – max. 5 pts\n"
            f"• **Enlisting someone** – max. 5 pts {support.mention}\n"
            "• Hosting a **Game Night** – max. 3 pts"
        ),
        inline=False
    )

    # Promotion reminder
    embed.add_field(
        name="📌 __Promotion Process__",
        value=(
            "When you meet the requirements for any roles in **ALPHA** or **BETA** class, "
            f"apply for a promotion in {promotion.mention}."
        ),
        inline=False
    )
    await ctx.send(embed=embed)
    await ctx.respond("Created!", ephemeral=True)

@bot.slash_command(name="create_training", description="Create a training with UI selection")
async def create_training_ui(
    ctx,
    co_host: Member,
    day: int,
    hr: int,
    minute: int,
    users_needed: int
):
    view = TrainingTypeView(ctx.author, ctx, co_host, day, hr, minute, users_needed)
    await ctx.respond("Please select the training types and then click **Submit training**.", view=view, ephemeral=True)

class RaidTypeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Breach 610"),
            discord.SelectOption(label="O5 nuke"),
            discord.SelectOption(label="Breach John"),
            discord.SelectOption(label="privat server event"),
            discord.SelectOption(label="special event"),
            discord.SelectOption(label="other")
        ]
        super().__init__(
            placeholder="Select raid type...",
            min_values=1,
            max_values=6,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.author:
            await interaction.response.send_message("Only the creator can use this UI.", ephemeral=True)
            return
        self.view.selected_type = ", ".join(self.values)
        await interaction.response.defer()

class DaySelect(discord.ui.Select):
    def __init__(self):
        from datetime import datetime, timedelta
        today = datetime.now()
        options = [
            discord.SelectOption(label=(today + timedelta(days=i)).strftime("%d.%m."), value=str((today + timedelta(days=i)).day))
            for i in range(14)  # 14 days selection
        ]
        super().__init__(
            placeholder="Select day...",
            min_values=1,
            max_values=1,
            options=options
        )
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.author:
            await interaction.response.send_message("Only the creator can use this UI.", ephemeral=True)
            return
        self.view.selected_day = int(self.values[0])
        await interaction.response.defer()

class HourSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=str(i).zfill(2)) for i in range(0, 24)]
        super().__init__(
            placeholder="Select hour...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.author:
            await interaction.response.send_message("Only the creator can use this UI.", ephemeral=True)
            return
        self.view.selected_hr = int(self.values[0])
        await interaction.response.defer()

class MinuteSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=str(i).zfill(2)) for i in range(0, 60, 15)]
        super().__init__(
            placeholder="Select minute...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.author:
            await interaction.response.send_message("Only the creator can use this UI.", ephemeral=True)
            return
        self.view.selected_minute = int(self.values[0])
        await interaction.response.defer()

class UsersNeededSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=str(i)) for i in range(1, 21)]
        super().__init__(
            placeholder="Select users needed...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.author:
            await interaction.response.send_message("Only the creator can use this UI.", ephemeral=True)
            return
        self.view.selected_users_needed = int(self.values[0])
        await interaction.response.defer()

class SendRaidButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Submit raid", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if interaction.user != view.author:
            await interaction.response.send_message("Only the creator can use this UI.", ephemeral=True)
            return
        # Check if all options are selected
        if not all([
            hasattr(view, "selected_day"),
            hasattr(view, "selected_hr"),
            hasattr(view, "selected_minute"),
            hasattr(view, "selected_users_needed"),
            hasattr(view, "selected_type"),
            hasattr(view, "co_host")
        ]):
            await interaction.response.send_message("Please select all options.", ephemeral=True)
            return

        role_id = 1386851365460119623
        role = view.ctx.guild.get_role(role_id)
        host = view.author
        unix_ts = parse_to_unix(f"{view.selected_day}-{view.selected_hr}:{view.selected_minute}")
        discord_time = f"<t:{unix_ts}:R>"
        embed = discord.Embed(title="A new raid has been created!", color=discord.Color.blue())
        if role:
            embed.add_field(name="", value=role.mention, inline=False)
        else:
            embed.add_field(name="", value="Role not found", inline=False)
        embed.add_field(name="Host", value=host.mention, inline=False)
        embed.add_field(name="Co-Host", value=view.co_host.mention, inline=False)
        embed.add_field(name="Time of Raid:", value=discord_time, inline=False)
        embed.add_field(name="Users Needed", value=view.selected_users_needed, inline=False)
        embed.add_field(name="Raid Objectives:", value=view.selected_type, inline=False)
        embed.set_footer(text=f"Raid created by {host.display_name}", icon_url=host.avatar.url)
        embed.timestamp = datetime.datetime.now()
        message = await view.ctx.channel.send(embed=embed)
        await message.add_reaction("✅")
        await interaction.response.send_message("Raid has been posted in the channel!", ephemeral=True)

class FirstRaidView(discord.ui.View):
    def __init__(self, author, ctx, co_host):
        super().__init__(timeout=60)
        self.author = author
        self.ctx = ctx
        self.co_host = co_host
        self.selected_day = None
        self.selected_users_needed = None
        self.selected_type = None
        self.add_item(DaySelect())
        self.add_item(UsersNeededSelect())
        self.add_item(RaidTypeSelect())
        self.add_item(NextButton())

class NextButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Next", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if interaction.user != view.author:
            await interaction.response.send_message("Only the creator can use this UI.", ephemeral=True)
            return
        # Check if all options are selected
        if not all([
            view.selected_day,
            view.selected_users_needed,
            view.selected_type
        ]):
            await interaction.response.send_message("Please select all options.", ephemeral=True)
            return
        # Show second view
        second_view = SecondRaidView(
            view.author, view.ctx, view.co_host,
            view.selected_day, view.selected_users_needed, view.selected_type
        )
        await interaction.response.send_message(
            "Please select the time and then click **Submit raid**.",
            view=second_view,
            ephemeral=True
        )

class SecondRaidView(discord.ui.View):
    def __init__(self, author, ctx, co_host, day, users_needed, raid_type):
        super().__init__(timeout=60)
        self.author = author
        self.ctx = ctx
        self.co_host = co_host
        self.day = day
        self.users_needed = users_needed
        self.raid_type = raid_type
        self.selected_hr = None
        self.selected_minute = None
        self.add_item(HourSelect())
        self.add_item(MinuteSelect())
        self.add_item(SendRaidButton2())

class SendRaidButton2(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Submit raid", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if interaction.user != view.author:
            await interaction.response.send_message("Only the creator can use this UI.", ephemeral=True)
            return
        if view.selected_hr is None or view.selected_minute is None:
            await interaction.response.send_message("Please select hour and minute.", ephemeral=True)
            return

        role_id = 1386851365460119623
        role = view.ctx.guild.get_role(role_id)
        host = view.author
        unix_ts = parse_to_unix(f"{view.day}-{view.selected_hr}:{view.selected_minute}")
        discord_time = f"<t:{unix_ts}:R>"
        embed = discord.Embed(title="A new raid has been created!", color=discord.Color.blue())
        if role:
            embed.add_field(name="", value=role.mention, inline=False)
        else:
            embed.add_field(name="", value="Role not found", inline=False)
        embed.add_field(name="Host", value=host.mention, inline=False)
        embed.add_field(name="Co-Host", value=view.co_host.mention, inline=False)
        embed.add_field(name="Time of Raid:", value=discord_time, inline=False)
        embed.add_field(name="Users Needed", value=view.users_needed, inline=False)
        embed.add_field(name="Raid Objectives:", value=view.raid_type, inline=False)
        embed.set_footer(text=f"Raid created by {host.display_name}", icon_url=host.avatar.url)
        embed.timestamp = datetime.datetime.now()
        message = await view.ctx.channel.send(embed=embed)
        await message.add_reaction("✅")
        await interaction.response.send_message("Raid has been posted in the channel!", ephemeral=True)

# Slash-Command:
@bot.slash_command(name="create_raid", description="Create a raid with a clear selection UI")
async def create_raid_ui(
    ctx,
    co_host: Member
):
    view = FirstRaidView(ctx.author, ctx, co_host)
    await ctx.respond(
        "Please select the day, users needed and raid type, then click **Next**.",
        view=view,
        ephemeral=True
    )
    
@bot.slash_command(name="start_raid", description="Create the start message after /create_raid")
async def startRaid(ctx: discord.ApplicationContext, co_host: discord.Member, target: Option(str, "for exampel Breach 610"), game_link: str):
    embed = discord.Embed(title="Raid started")
    embed.add_field(name="Host", value=ctx.author.mention, inline=False)
    embed.add_field(name="Co-Host", value=co_host.mention, inline=False)
    embed.add_field(name="Target", value=target, inline=False)
    embed.add_field(name="Join this server!", value=game_link, inline=False)
    await ctx.send(embed=embed)
    await ctx.respond("Raid created!", ephemeral=True)
    
@bot.slash_command(name="ticket_ui", description="Creat the Ticket creating Ui.")
async def ticketUI(ctx:discord.ApplicationContext):
    await ctx.respond("Ticket UI created", ephemeral=True)
    await ctx.send(view=CreateTicket())

@bot.slash_command(name="rules", description="Show the server rules")
async def rules(ctx):
    await send_rules(ctx.channel)

@bot.slash_command(name="claim", description="Claim the current ticket channel")
async def claim(ctx):
    channel = ctx.channel
    # Optional: Prüfe, ob dies ein Ticket-Channel ist
    await ctx.respond(f"{ctx.author.mention} claimed the ticket.", ephemeral=False)
    # Logge das Claiming
    log_channel = ctx.guild.get_channel(1398847172463689728)
    if log_channel:
        await log_channel.send(f"📌 **Ticket claimed:** {channel.mention} by {ctx.author.mention}")

@bot.slash_command(name="close", description="Close the current ticket channel and save transcript")
async def close(ctx):
    channel = ctx.channel
    await ctx.respond("🔄 Ticket will be closed and saved", ephemeral=True)
    # Transcript generieren
    messages = [msg async for msg in channel.history(limit=None, oldest_first=True)]
    transcript_lines = [
        f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {msg.author.id}: {msg.content}"
        for msg in messages
    ]
    import os
    from datetime import datetime
    os.makedirs("transcripts", exist_ok=True)
    filename = f"transcripts/{channel.name}-{datetime.utcnow().strftime('%Y-%d.%m-%H-%M-%S')}.txt"
    filename_id = f"{channel.name}-{datetime.utcnow().strftime('%Y-%d.%m-%H-%M-%S')}"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(transcript_lines))
    # Log-Nachricht
    log_channel = ctx.guild.get_channel(1398847172463689728)
    if log_channel:
        import discord
        file = discord.File(filename)
        await log_channel.send(
            content=f"📁 **Ticket closed** {channel.name} by {ctx.author.mention}\n Recreate this Ticket with /load_ticket the Id is:\n ``{filename_id}``",
            file=file
        )
    await channel.delete()
    
@bot.slash_command(name="load_ticket", description="Load a ticket from a transcript file")
async def load_ticket(ctx: discord.ApplicationContext, id: discord.Option(str, "Example: ticket-fabian2_011-2025-27.07-02-26-18", required=True)):
    if not os.path.exists("transcripts/" + id+".txt"):
        await ctx.respond("Please enter a valid transcript. (Error: 404 File not found)", ephemeral=True)
        return
    with open("transcripts/" + id+".txt", "r") as f:
        transcript_content = f.read()
    if not transcript_content:
        await ctx.respond("The transcript file is empty or does not exist.", ephemeral=True)
        return
    
    # Create a new ticket channel
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }
    ticket_channel = await ctx.guild.create_text_channel(
        name=f"transcript-{ctx.author.name}",
        overwrites=overwrites,
        reason="Ticket created from transcript"
    )

    msg = await ctx.respond(f"The ticket is being recreated in {ticket_channel.mention}...")

    import re

    pattern = re.compile(r"^\[(?P<timestamp>[^\]]+)\]\s+(?P<userid>\d+):\s*(?P<content>.*)")

    messages = []
    current_msg = None

    for line in transcript_content.splitlines():
        if not line.strip():
            # Leere Zeile: zum aktuellen content hinzufügen, wenn vorhanden
            if current_msg:
                current_msg['content'] += '\n'
            continue

        match = pattern.match(line)
        if match:
            # Neue Nachricht beginnt, vorherige speichern
            if current_msg:
                messages.append(current_msg)

            current_msg = {
                "timestamp": match.group("timestamp"),
                "userid": int(match.group("userid")),
                "content": match.group("content").rstrip()  # Inhalt der ersten Zeile
            }
        else:
            # Zeile gehört zum content der letzten Nachricht (mehrzeilig)
            if current_msg:
                current_msg['content'] += '\n' + line.rstrip()
            else:
                # Wenn keine aktuelle Nachricht (z.B. am Anfang), ignorieren oder loggen
                print(f"⚠️ Zeile ohne Header und ohne aktuelle Nachricht: {line}")

    # Letzte Nachricht hinzufügen
    if current_msg:
        messages.append(current_msg)


    # Jetzt Nachrichten senden
    for msg in messages:
        user = discord.utils.get(ctx.guild.members, id=msg["userid"])
        user_mention = user.mention if user else f"<@{msg['userid']}>"
        await ticket_channel.send(f"[{msg['timestamp']}] {user_mention}:")
        if msg["content"].strip():
            await ticket_channel.send(msg["content"].strip())


    await msg.edit_original_response(
        content=f"✅ Ticket successfully recreated!\n{ticket_channel.mention}"
    )

from Managers.Data_Manager import Set_Variable_By_UserId, Get_Variable_By_UserId

@bot.slash_command(name="set_user_variable")
async def set_user_variable(ctx: discord.ApplicationContext, user:Member, variable:str, value:str):
    await ctx.defer()
    Set_Variable_By_UserId(variable, value, str(user.id))
    await ctx.respond(f"{variable} of {user.mention} were set to {value}.")
    
@bot.slash_command(name="get_user_variable")
async def get_user_variable(ctx: discord.ApplicationContext, user:Member, variable:str):
    await ctx.defer()
    value = Get_Variable_By_UserId(variable, str(user.id))
    if value is None:
        await ctx.respond(f"{variable} of {user.mention} is empty", ephemeral=True)
    else:
        await ctx.respond(f"{variable} of {user.mention} is: {value}", ephemeral=True)
        
@bot.slash_command(name="add_user_variable")
async def add_user_variable(ctx: discord.ApplicationContext, user:Member, variable:str, add:int):
    await ctx.defer()
    value = Get_Variable_By_UserId(variable, str(user.id))
    if value is None:
        Set_Variable_By_UserId(variable, add, user.id)
        await ctx.respond(f"Added {add} to {variable} of {user.mention}. (New Total: {add} )")
    else:
        Set_Variable_By_UserId(variable, (int(value) + add), user.id)
        await ctx.respond(f"Added {add} to {variable} of {user.mention}. (New Total: {int(value)+add} )")
        
@bot.slash_command(name="pts-balance", description="Zeigt deinen Punktestand", dm_permission=True)
async def slash_pts_balance(ctx: discord.ApplicationContext):
    await ctx.defer()
    pts = Get_Variable_By_UserId("pts", ctx.author.id)
    await ctx.respond(embed=Backend.Embeds_UIs.PointBalanceEmbed(pts, ctx.author))
    
@bot.slash_command(name="monitor", description="Live system monitor", dm_permission=True)
async def monitor(ctx):
    msg = await ctx.send(embed=create_embed(status))

    try:
        while True:
            await asyncio.sleep(2)
            new_embed = create_embed(status)
            await msg.edit(embed=new_embed)
    except asyncio.CancelledError:
        pass  # z. B. bei manuellem Stop oder Bot-Neustart

bot.embed_data = {}

@bot.slash_command(name="get_member_mention", dm_permission=True)
async def get_member_mention(ctx: discord.ApplicationContext, member:Member):
    ctx.respond(f"Mention him/her with ``{member.mention}`` in Announcements.", ephemeral=True)

@bot.slash_command(name="select_announcement_channel", description="Set the target channel for your announcement.")
async def select_announcement_channel(ctx: discord.ApplicationContext, channel: discord.TextChannel):
    bot.embed_data[ctx.user.id] = {"target_channel_id": channel.id}
    await ctx.respond(f"✅ Target channel set to {channel.mention}.", ephemeral=True)


@bot.slash_command(name="create_announcement", description="Start the announcement creation process.")
async def create_announcement(ctx: discord.ApplicationContext):
    # Wenn der Command im Server verwendet wird → DM starten
    if ctx.channel.type != discord.ChannelType.private:
        try:
            await ctx.user.send(
                "👋 Let's start creating your announcement!\n\n"
                "You'll be guided step-by-step.\n"
                "1. Use ``/select_announcement_channel`` in th target channel.\n"
                "2. Come back and use ``/create_announcement`` then you will recive further steps."
            )
            await ctx.respond("📬 I've sent you a DM to continue the process.", ephemeral=True)
        except discord.Forbidden:
            await ctx.respond("❌ I can't send you a DM. Please enable DMs in your privacy settings.", ephemeral=True)
        return

    # In DMs: prüfen ob Channel gesetzt ist
    user_data = bot.embed_data.get(ctx.user.id)
    if not user_data or "target_channel_id" not in user_data:
        await ctx.respond("❌ You haven't selected a target channel yet. Use `/select_announcement_channel` in a server channel first.", ephemeral=True)
        return

    # Starte die UI (z. B. erste Modal/View)
    await ctx.send("📌 Let's configure your announcement.")
    await ctx.send_modal(AnnouncementStep1(bot))

        
@bot.slash_command(name="announcement_demo", description="Create an announcement for the server")
async def announcement_demo(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="This is a Titel. Must be 256 characters or fewer.",
        description=(
            "This is a Description. Must be 4096 characters or fewer.\n\n"
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="This is a footer. Must be 2048 characters or fewer.")
    embed.timestamp = datetime.datetime.now()
    await ctx.respond(embed=embed, ephemeral=True)
    
@bot.slash_command(name="bot_change")
async def bot_change(ctx: discord.ApplicationContext):
    everyone_role = ctx.guild.default_role
    embed = discord.Embed(
    title="📢 Bot Transition Announcement",
    description=(
        "**Hey everyone!** 👋\n"
        "We wanted to let you know that we're currently in the process of **switching over to our own custom bot** 🤖. "
        "This is a big step for us, and while we're excited about the improvements it will bring, "
        "we understand that it might cause some confusion along the way.\n\n"

        "🔄 **Timeline:**\n"
        "We aim to **fully complete the transition within the next 2–3 weeks**. "
        "That said, please keep in mind that even after the switch, some systems may still be a bit rough around the edges "
        "as we fine-tune everything.\n\n"

        "❗ **What stays:**\n"
        "The only bot we won’t be replacing is **Bloxlink** 🔗 — it's deeply integrated and not worth the trouble to swap out.\n\n"

        "🔔 **Heads-up on pings:**\n"
        "During the testing phase, you may receive the occasional unexpected **ping** 🔔. "
        "We apologize in advance and will try to keep disruptions to a minimum.\n\n"

        "🙏 **We appreciate your understanding and patience** as we work to improve the experience for everyone. "
        "If you run into any issues or have feedback, feel free to reach out!\n\n"

        "Thanks for sticking with us! 💙\n"
        f"||{everyone_role.mention}||"
    ),
    color=discord.Color.from_rgb(255,0,0)
)
    embed.set_footer(text="Transitioning to our own custom bot")
    embed.timestamp = datetime.datetime.now()
    await ctx.send(embed=embed)
    
MESSAGE_STORE = "status_message.json"

status_message = None

async def load_status_message():
    global status_message
    try:
        with open(MESSAGE_STORE, "r") as f:
            data = json.load(f)
        channel = bot.get_channel(data["channel_id"])
        if channel:
            status_message = await channel.fetch_message(data["message_id"])
            print("Status message loaded successfully.")
    except Exception as e:
        print(f"Could not load status message: {e}")

async def save_status_message(message):
    data = {
        "channel_id": message.channel.id,
        "message_id": message.id
    }
    with open(MESSAGE_STORE, "w") as f:
        json.dump(data, f)
    print("Status message saved.")

def get_status_emoji():
    if status == 1:
        return "🟢"
    elif status == 2:
        return "🟡"
    elif status == 3:
        return "🔴"
    return "❔"

def create_embed():
    embed = discord.Embed(
    title=f"Site 64 Insurgents Manager's Status: {get_status_emoji()}",
    description=detailed_status,
    timestamp=datetime.datetime.now(datetime.timezone.utc),
    color=discord.Color.from_rgb(255, 0, 0)
    )
    embed.set_footer(text="Last Update")
    return embed
    
def create_name():
    return f"{get_status_emoji()}│status"

@bot.slash_command(name="status")
async def status_cmd(ctx):
    global status_message
    await ctx.defer()

    if status_message is None:
        # Nachricht zum ersten Mal senden
        embed = create_embed()
        status_message = await ctx.send(embed=embed)
        await save_status_message(status_message)
    else:
        # Nachricht updaten
        embed = create_embed()
        await status_message.edit(embed=embed)

    await ctx.respond("Status updated successfully.", ephemeral=True)

# Beispiel: periodisches Update (alle 60 Sekunden)
last_status = None

@tasks.loop(seconds=30)
async def periodic_status_update():
    if status_message:
        global last_status
        if last_status != status and last_status != None:
            try:
                await status_message.create_thread(
                    name=f"discussion_{datetime.date.today()}",
                    auto_archive_duration=4320
                )
            except Exception as e:
                pass
        await status_message.channel.edit(name=create_name())
        embed = create_embed()
        await status_message.edit(embed=embed)
        last_status = status

@periodic_status_update.before_loop
async def before_loop():
    await bot.wait_until_ready()

periodic_status_update.start()

STATUS_FILE = "status.json"

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            data = json.load(f)
            return data.get("description", "No description available"),  data.get("status", 1)  # Default: 1 (Online)

detailed_status, status = load_status()

def save_status(status_value: int):
    with open(STATUS_FILE, "w") as f:
        json.dump({"status": status_value}, f)

@bot.slash_command(name="change_status")
async def change_status(
    ctx,
    new_status: discord.Option(
        int,
        "New status (1: Online, 2: Controlled Instability, 3: Lockdown Mode)",
        choices=[
            discord.OptionChoice(name="Online", value=1),
            discord.OptionChoice(name="Controlled Instability", value=2),
            discord.OptionChoice(name="Lockdown Mode", value=3)
        ]
    ), # type: ignore
    description: discord.Option(
        str,
        "Description of the new status, if not provided defaults to 'No description available'",
        required=False
    ) # type: ignore
):
    global status
    status = new_status
    save_status(status)
    if new_status == 1:
        await bot.change_presence(status=discord.Status.online, activity=None)
    elif new_status == 2:
        await bot.change_presence(status=discord.Status.idle, activity=None)
    elif new_status == 3:
        await bot.change_presence(status=discord.Status.dnd, activity=None)
    await ctx.respond(f"Status changed to {get_status_emoji()}.", ephemeral=True)

def load_country_mapping(file_path="all_country_names_multilang.txt"):
    mapping = {}
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            parts = line.split(":")
            if len(parts) != 2:
                continue
            alpha_2, translations = parts
            entries = translations.strip().split(" ")
            for entry in entries:
                try:
                    lang_code, name = entry.split("=", 1)
                    lang_code = lang_code.strip()
                    name = name.strip().strip("'").lower()
                    mapping[name] = alpha_2.upper()
                except:
                    continue
    return mapping

# Load at startup
country_name_to_code = load_country_mapping()

@bot.slash_command(name="convert_to_cet", description="Convert time from any country or timezone to Central European Time (CET)")
async def convert_to_cet(
    ctx,
    input_time: Option(str, "Time in format YYYY-MM-DD HH:MM"),
    timezone_name: Option(str, "Timezone (e.g. Asia/Tokyo)", required=False),
    country: Option(str, "Country (in English or native name)", required=False)
):
    source_tz = None

    # Timezone name has priority
    if timezone_name:
        try:
            source_tz = pytz.timezone(timezone_name)
        except pytz.UnknownTimeZoneError:
            await ctx.respond(f"❌ Unknown timezone: `{timezone_name}`", ephemeral=True)
            return

    # Country fallback
    elif country:
        country_key = country.lower().strip()
        alpha_2 = country_name_to_code.get(country_key)
        if not alpha_2:
            await ctx.respond(f"❌ Country not recognized: `{country}`", ephemeral=True)
            return
        tz_list = pytz.country_timezones.get(alpha_2)
        if not tz_list:
            await ctx.respond(f"❌ No timezones found for country: `{country}`", ephemeral=True)
            return
        source_tz = pytz.timezone(tz_list[0])

    else:
        await ctx.respond("❌ Please provide either a timezone or a country.", ephemeral=True)
        return

    # Parse time
    try:
        naive_dt = datetime.datetime.strptime(input_time, "%Y-%m-%d %H:%M")
    except ValueError:
        await ctx.respond("❌ Invalid time format. Use `YYYY-MM-DD HH:MM`.", ephemeral=True)
        return

    # Convert
    localized_dt = source_tz.localize(naive_dt)
    cet = pytz.timezone("Europe/Berlin")
    cet_dt = localized_dt.astimezone(cet)

    embed = discord.Embed(
        title="🕒 Time Conversion",
        description=(
            f"**Original:** `{localized_dt.strftime('%Y-%m-%d %H:%M %Z')}`\n"
            f"**Converted to CET:** `{cet_dt.strftime('%Y-%m-%d %H:%M %Z')}`"
        ),
        color=discord.Color.green(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text="Includes daylight saving time (if active)")
    await ctx.respond(embed=embed)
    
class Enlist_Embed(discord.Embed):
    def __init__(self):
        super().__init__(
            title="📜 Enlist Here",
            description=(
                "Welcome to **Site 64 Insurgents**!\n\n"
                "To join, please click the button below and complete the enlistment form.\n"
                "If you are not able to verify your Roblox account, via Bloxlink, please click Manual Enlistment.\n"
                "After you complete the form, a member will review your application as soon as possible."
            ),
            color=discord.Color.from_rgb(255, 0, 0)
        )
        self.set_footer(text="You may be asked for additional information, never share personal information or sensitive data.")

class Enlist_Modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Enlistment Form")
        self.add_item(discord.ui.TextInput(
            label="Why do you want to join?",
            placeholder="Why do you want to join Site 64 Insurgents? What interests you?",
            min_length=10,
            max_length=500,
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="CI Gamepass",
            placeholder="Do you have the CI Gamepass? (Yes/Y/No/N)",
            min_length=1,
            max_length=3,
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="How will you participate?",
            placeholder="E.g., events, moderation, helping others.",
            min_length=3,
            max_length=150,
            required=True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        channel = await guild.create_text_channel(
            name=f"enlist-{interaction.user.name}",
            overwrites=overwrites,
            reason="New enlistment submitted"
        )
        await channel.send(
            f"{interaction.user.mention} has submitted their enlistment.\n"
            f"**Why do you want to join Site 64 Insurgents?**\n```{self.children[0].value}```\n"
            f"**CI Gamepass:** `{self.children[1].value}`\n"
            f"**How will you participate?**\n```{self.children[2].value}```"
        )
        await interaction.response.send_message(
            f"Your Enlistment has been submitted!\n{channel.mention}", ephemeral=True
        )

class Enlist_Manual_Modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Enlistment Form")
class Enlist_Manual_Modal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Enlistment Form")
        self.add_item(discord.ui.TextInput(
            label="Roblox Username",
            placeholder="Enter your Roblox username.",
            min_length=3,
            max_length=20,
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="Roblox Profile/UserId",
            placeholder="Profile link or UserId (one is enough)",
            min_length=3,
            max_length=100,
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="Why do you want to join?",
            placeholder="Why do you want to join Site 64 Insurgents? What interests you?",
            min_length=10,
            max_length=500,
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="CI Gamepass",
            placeholder="Do you have the CI Gamepass? (Yes/Y/No/N)",
            min_length=1,
            max_length=3,
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="How will you participate?",
            placeholder="E.g., events, moderation, helping others.",
            min_length=3,
            max_length=150,
            required=True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        channel = await guild.create_text_channel(
            name=f"manual-enlist-{interaction.user.name}",
            overwrites=overwrites,
            reason="Manual enlistment submitted"
        )
        await channel.send(
            f"{interaction.user.mention} has submitted a manual enlistment.\n"
            f"**Roblox Username:** `{self.children[0].value}`\n"
            f"**Roblox Profile/UserId:** `{self.children[1].value}`\n"
            f"**Why do you want to join Site 64 Insurgents?**\n```{self.children[2].value}```\n"
            f"**CI Gamepass:** `{self.children[3].value}`\n"
            f"**How will you participate?**\n```{self.children[4].value}```"
        )
        await interaction.response.send_message(
            f"Your Manual Enlistment has been submitted!\n{channel.mention}", ephemeral=True
        )
        super().__init__(timeout=None)

    @discord.ui.button(label="📨 Enlist", style=discord.ButtonStyle.green, custom_id="enlist_button")
    async def enlist_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(Enlist_Modal())

    @discord.ui.button(label="✉️ Manual Enlistment", style=discord.ButtonStyle.blurple, custom_id="manual_enlistment_button")
    async def manual_enlistment_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(Enlist_Manual_Modal())
        
@bot.slash_command(name="create_enlist_gui", description="Create the Enlist Gui")
async def create_enlist_gui(ctx: discord.ApplicationContext):
    await ctx.defer()
    await ctx.channel.send(embed=Enlist_Embed(), view=Enlist_View())
    await ctx.respond("Done", ephemeral=True)

import platform

if platform.system() == "Windows":
    secrets_path = "C:\\Users\\User\\Desktop\\home\\fabian\\secrets.json"
else:
    secrets_path = "/home/fabian/secrets.json"

with open(secrets_path, "r") as f:
    data = json.load(f)
    BOT_TOKEN = data["BOT_TOKEN"]

bot.run(BOT_TOKEN)