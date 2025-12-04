import discord
import os
import requests
from discord.ext import commands
from dotenv import load_dotenv
from discord.ui import Modal, TextInput, View, Button

load_dotenv()
api_key = open("api-key.txt").read()
token = open("discord-token.txt").read()

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="px.", intents=intents)
active_games = {}

url1 = "https://api.apparyllis.com/v1/fronters/"

payload = {}
headers = {
  'Authorization': api_key
}

response1 = requests.request("GET", url1, headers=headers, data=payload)

sysID = response1.json()[0]["content"]["uid"]
memID1 = response1.json()[0]["content"]["member"]

url2 = "https://api.apparyllis.com/v1/member/" + sysID + "/" + memID1

response2 = requests.request("GET", url2, headers=headers, data=payload)

fronter = response2.json()["content"]["name"]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

class testView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label=":3", style=discord.ButtonStyle.green)
    async def wawawa(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(fronter + "says: wawawawawawawwawawa", ephemeral=True)

@bot.command(name="test")
async def test(ctx):
    view = testView(ctx)
    await ctx.send("Current fronter is " + fronter + "!", view=view)

bot.run(token)
