import discord
import asyncio

class AnnouncementStep1(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Step 1: Embed Basics")
        self.bot = bot

        self.title_input = discord.ui.InputText(
            label="Embed Title",
            placeholder="Enter a title",
            max_length=256
        )
        self.description_input = discord.ui.InputText(
            label="Embed Description",
            style=discord.InputTextStyle.long,
            placeholder="Enter a description"
        )

        self.add_item(self.title_input)
        self.add_item(self.description_input)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        self.bot.embed_data[user_id]["title"] = self.title_input.value
        self.bot.embed_data[user_id]["description"] = self.description_input.value

        await interaction.response.send_message(
            "✅ Step 1 complete. Continue with the next step:",
            view=Step2View(self.bot),
            ephemeral=True
        )


class Step2View(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Upload Thumbnail", style=discord.ButtonStyle.blurple)
    async def upload_thumbnail(self, button, interaction: discord.Interaction):
        await self._handle_upload(interaction, "thumbnail")

    @discord.ui.button(label="Upload Image", style=discord.ButtonStyle.blurple)
    async def upload_image(self, button, interaction: discord.Interaction):
        await self._handle_upload(interaction, "image")

    @discord.ui.button(label="Set Embed Color", style=discord.ButtonStyle.blurple)
    async def set_color(self, button, interaction: discord.Interaction):
        await interaction.response.send_modal(ColorModal(self.bot))

    @discord.ui.button(label="Set Author", style=discord.ButtonStyle.blurple)
    async def set_author(self, button, interaction: discord.Interaction):
        await interaction.response.send_modal(AuthorModal(self.bot))

    @discord.ui.button(label="Set Footer", style=discord.ButtonStyle.blurple)
    async def set_footer(self, button, interaction: discord.Interaction):
        await interaction.response.send_modal(FooterModal(self.bot))

    @discord.ui.button(label="Add Field", style=discord.ButtonStyle.blurple)
    async def add_field(self, button, interaction: discord.Interaction):
        await interaction.response.send_modal(FieldModal(self.bot))

    @discord.ui.button(label="Add Timestamp", style=discord.ButtonStyle.blurple)
    async def add_timestamp(self, button, interaction: discord.Interaction):
        self.bot.embed_data[interaction.user.id]["timestamp"] = True
        await interaction.response.send_message("✅ Timestamp will be added.", ephemeral=True)

    @discord.ui.button(label="Finish & Send", style=discord.ButtonStyle.green)
    async def finish_button(self, button, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = self.bot.embed_data.get(user_id)
        if not data:
            await interaction.response.send_message("❌ No data found. Restart.", ephemeral=True)
            return

        embed = discord.Embed(
            title=data.get("title"),
            description=data.get("description"),
            color=data.get("color", discord.Color.blurple())
        )

        if data.get("thumbnail"):
            embed.set_thumbnail(url=data["thumbnail"])
        if data.get("image"):
            embed.set_image(url=data["image"])
        if data.get("author"):
            embed.set_author(name=data["author"], icon_url=data.get("author_icon"))
        if data.get("footer"):
            embed.set_footer(text=data["footer"], icon_url=data.get("footer_icon"))
        if data.get("timestamp"):
            embed.timestamp = discord.utils.utcnow()
        if data.get("fields"):
            for field in data["fields"]:
                embed.add_field(name=field["name"], value=field["value"], inline=field.get("inline", False))

        channel = self.bot.get_channel(data["target_channel_id"])
        if channel:
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ Announcement sent!", ephemeral=True)
            del self.bot.embed_data[user_id]
        else:
            await interaction.response.send_message("❌ Couldn't find the target channel.", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, button, interaction: discord.Interaction):
        self.bot.embed_data.pop(interaction.user.id, None)
        await interaction.response.send_message("❌ Announcement creation cancelled.", ephemeral=True)

    async def _handle_upload(self, interaction: discord.Interaction, key: str):
        await interaction.response.send_message(
            f"📎 Please upload the {key} image as an attachment in your next message.", ephemeral=True
        )

        def check(m):
            return m.author.id == interaction.user.id and m.channel == interaction.channel and m.attachments

        try:
            msg = await self.bot.wait_for("message", timeout=60.0, check=check)
            attachment = msg.attachments[0]
            if not attachment.content_type.startswith("image/"):
                await interaction.followup.send("❌ That file is not an image.", ephemeral=True)
                return

            self.bot.embed_data[interaction.user.id][key] = attachment.url
            await interaction.followup.send(f"✅ {key.capitalize()} uploaded and saved.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⌛ Upload timed out.", ephemeral=True)


class ColorModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Set Embed Color")
        self.bot = bot
        self.color_input = discord.ui.InputText(label="Hex Color (e.g. #00ffcc)", placeholder="#00ffcc")
        self.add_item(self.color_input)

    async def callback(self, interaction: discord.Interaction):
        hex_color = self.color_input.value.strip().lstrip("#")
        try:
            color = discord.Color(int(hex_color, 16))
            self.bot.embed_data[interaction.user.id]["color"] = color
            await interaction.response.send_message("✅ Color set successfully!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid color code.", ephemeral=True)


class AuthorModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Set Author")
        self.bot = bot
        self.author_name = discord.ui.InputText(label="Author Name", required=True)
        self.author_icon = discord.ui.InputText(label="Author Icon URL", required=False)
        self.add_item(self.author_name)
        self.add_item(self.author_icon)

    async def callback(self, interaction: discord.Interaction):
        self.bot.embed_data[interaction.user.id]["author"] = self.author_name.value
        self.bot.embed_data[interaction.user.id]["author_icon"] = self.author_icon.value
        await interaction.response.send_message("✅ Author set.", ephemeral=True)
        
        
class IconChoiceView(discord.ui.View):
    def __init__(self, bot, user_id, field_name: str, label: str):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.field_name = field_name
        self.label = label

    @discord.ui.button(label="Use URL", style=discord.ButtonStyle.primary, emoji="🔗")
    async def url_button(self, button, interaction):
        await interaction.response.send_modal(
            IconURLModal(self.bot, self.user_id, self.field_name, f"Set {self.label} via URL")
        )

    @discord.ui.button(label="Upload Image", style=discord.ButtonStyle.secondary, emoji="📁")
    async def upload_button(self, button, interaction):
        await interaction.response.send_message(
            f"📥 Please upload your image file for {self.label.lower()} now.", ephemeral=True
        )

        def check(m):
            return (
                m.author.id == self.user_id
                and m.attachments
                and m.channel == interaction.channel
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            attachment = msg.attachments[0]
            self.bot.embed_data[self.user_id][self.field_name] = attachment.url
            await msg.reply(f"✅ {self.label} set successfully via upload!", mention_author=False)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Upload timed out. Please try again.", ephemeral=True)


class FooterModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Set Footer")
        self.bot = bot
        self.footer_text = discord.ui.InputText(label="Footer Text", required=True)
        self.footer_icon = discord.ui.InputText(label="Footer Icon URL", required=False)
        self.add_item(self.footer_text)
        self.add_item(self.footer_icon)

    async def callback(self, interaction: discord.Interaction):
        self.bot.embed_data[interaction.user.id]["footer"] = self.footer_text.value
        self.bot.embed_data[interaction.user.id]["footer_icon"] = self.footer_icon.value
        await interaction.response.send_message("✅ Footer set.", ephemeral=True)

      
class IconURLModal(discord.ui.Modal):
    def __init__(self, bot, user_id, field_name: str, title: str):
        super().__init__(title=title)
        self.bot = bot
        self.user_id = user_id
        self.field_name = field_name

        self.url_input = discord.ui.InputText(
            label="Enter the image URL",
            placeholder="https://example.com/image.png",
            required=True
        )
        self.add_item(self.url_input)

    async def callback(self, interaction: discord.Interaction):
        self.bot.embed_data[self.user_id][self.field_name] = self.url_input.value
        await interaction.response.send_message(f"✅ {self.field_name.replace('_', ' ').title()} set via URL.", ephemeral=True)


class FieldModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Add Embed Field")
        self.bot = bot
        self.field_name = discord.ui.InputText(label="Field Name", required=True)
        self.field_value = discord.ui.InputText(label="Field Value", style=discord.InputTextStyle.long, required=True)
        self.inline = discord.ui.InputText(label="Inline? (true/false)", placeholder="false", required=False)
        self.add_item(self.field_name)
        self.add_item(self.field_value)
        self.add_item(self.inline)

    async def callback(self, interaction: discord.Interaction):
        inline = self.inline.value.strip().lower() == "true"
        field = {
            "name": self.field_name.value,
            "value": self.field_value.value,
            "inline": inline
        }
        self.bot.embed_data[interaction.user.id].setdefault("fields", []).append(field)
        await interaction.response.send_message("✅ Field added.", ephemeral=True)
