import os
import discord
from discord.ext import commands
from discord import Option, Member
from UI import send_rules, CreateTicket, TrainingTypeView
import json
import datetime
import time

bot = commands.Bot(command_prefix='!')

bot.persistent_views_added=False

def parse_to_unix(date_str):
    # Erwartetes Format: "24-18:30"
    day, time_part = date_str.split('-')
    hour, minute = map(int, time_part.split(':'))
    now = datetime.datetime.now()
    try:
        target = datetime.datetime(year=now.year, month=now.month, day=int(day), hour=hour, minute=minute)
    except ValueError:
        # Falls Tag im aktuellen Monat vorbei ist, nimm nächsten Monat
        next_month = now.month + 1 if now.month < 12 else 1
        year = now.year if now.month < 12 else now.year + 1
        target = datetime.datetime(year=year, month=next_month, day=int(day), hour=hour, minute=minute)
    return int(target.timestamp())

@bot.event
async def on_ready():
    if not bot.persistent_views_added:
        bot.add_view(CreateTicket())
        bot.persistent_views_added=True
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print(f"Bot is ready!")
    
import discord
from discord.ext import commands

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
            "• **The Leader**\n"
            "• **The Commandant**\n"
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
    log_channel = ctx.guild.get_channel(1240038929479110697)
    if log_channel:
        await log_channel.send(f"📌 **Ticket claimed:** {channel.mention} by {ctx.author.mention}")

@bot.slash_command(name="close", description="Close the current ticket channel and save transcript")
async def close(ctx):
    channel = ctx.channel
    await ctx.respond("🔄 Ticket will be closed and saved", ephemeral=True)
    # Transcript generieren
    messages = [msg async for msg in channel.history(limit=None, oldest_first=True)]
    transcript_lines = [
        f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {msg.author}: {msg.content}"
        for msg in messages
    ]
    import os
    from datetime import datetime
    os.makedirs("transcripts", exist_ok=True)
    filename = f"transcripts/{channel.name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(transcript_lines))
    # Log-Nachricht
    log_channel = ctx.guild.get_channel(1240038929479110697)
    if log_channel:
        import discord
        file = discord.File(filename)
        await log_channel.send(
            content=f"📁 **Ticket closed** {channel.name} by {ctx.author.mention}",
            file=file
        )
    await channel.delete()

async def is_allowed(ctx):
    # Beispiel: Nur Administratoren dürfen den Command nutzen
    return ctx.author.guild_permissions.administrator

with open("/home/fabian/secrets.json", "r") as f:
    data = json.load(f)
    BOT_TOKEN = data["BOT_TOKEN"]

bot.run(BOT_TOKEN)
