import discord
import os
import random
import requests
from discord.ext import commands
from dotenv import load_dotenv
from discord.ui import Modal, TextInput, View, Button

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="px.", intents=intents)
active_games = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

class testView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="wawawa", style=discord.ButtonStyle.green)
    async def wawawa(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("wawawa", ephemeral=True)

@bot.command(name="test")
async def test(ctx):
    view = testView(ctx)
    await ctx.send("hi!", view=view)

token = open("discord-token.txt").read()
bot.run(token)
