import discord
import datetime

def parse_to_unix(date_str):
    # 24-18:30
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

class TrainingTypeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="MTF"),
            discord.SelectOption(label="RRT"),
            discord.SelectOption(label="CD"),
            discord.SelectOption(label="CI"),
            discord.SelectOption(label="Med"),
            discord.SelectOption(label="ScD"),
            discord.SelectOption(label="ISD"),
            discord.SelectOption(label="IA"),
            discord.SelectOption(label="O5"),
            discord.SelectOption(label="SiD"),
        ]
        super().__init__(
            placeholder="Select training types...",
            min_values=1,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_types = self.values
        await interaction.response.defer()
        
class SendTrainingButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Submit training", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if interaction.user != view.author:
            await interaction.response.send_message("Only the creator can use this UI.", ephemeral=True)
            return
        if not view.selected_types:
            await interaction.response.send_message("Please select at least one training type.", ephemeral=True)
            return

        role_id = 1386851365460119623
        role = view.ctx.guild.get_role(role_id)
        host = view.author
        unix_ts = parse_to_unix(f"{view.day}-{view.hr}:{view.minute}")
        discord_time = f"<t:{unix_ts}:R>"
        embed = discord.Embed(title="A new training has been created!", color=discord.Color.blue())
        if role:
            embed.add_field(name="", value=role.mention, inline=False)
        else:
            embed.add_field(name="", value="Role not found", inline=False)
        embed.add_field(name="Host", value=host.mention, inline=False)
        embed.add_field(name="Co-Host", value=view.co_host.mention, inline=False)
        embed.add_field(name="Users Needed", value=view.users_needed, inline=False)
        embed.add_field(name="Main objectives:", value=", ".join(view.selected_types), inline=False)
        embed.add_field(name="Time of Training:", value=discord_time, inline=False)
        embed.set_footer(text=f"Training created by {host.display_name}", icon_url=host.avatar.url)
        embed.timestamp = datetime.datetime.now()
        await view.ctx.channel.send(embed=embed)
        await interaction.response.send_message("Training has been posted in the channel!", ephemeral=True)

class TrainingTypeView(discord.ui.View):
    def __init__(self, author, ctx, co_host, day, hr, minute, users_needed):
        super().__init__(timeout=None)
        self.selected_types = []
        self.author = author
        self.ctx = ctx
        self.co_host = co_host
        self.day = day
        self.hr = hr
        self.minute = minute
        self.users_needed = users_needed
        self.add_item(TrainingTypeSelect())
        self.add_item(SendTrainingButton())