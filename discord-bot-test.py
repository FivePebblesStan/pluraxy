import discord
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

frontersRes = requests.request("GET", url1, headers=headers, data=payload)

sysID = frontersRes.json()[0]["content"]["uid"]

frontersNum = len(frontersRes.json())
fronters = {}
for i in range(frontersNum):
    id = frontersRes.json()[i]["content"]["member"]
    memUrl = "https://api.apparyllis.com/v1/member/" + sysID + "/" + id
    memRes = requests.request("GET", memUrl, headers=headers, data=payload)
    fronters["fronter{0}".format(i)] = memRes.json()["content"]["name"]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

class testView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label=":3", style=discord.ButtonStyle.green)
    async def wawawa(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(fronters["fronter0"] + " says: wawawawawawawwawawa", ephemeral=True)

class whoModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="New Message")
        self.ctx = ctx
        self.input = TextInput(label="Simplyplural username of recipient's system", placeholder="eg: Viridescent")
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        username = self.input.value
        #add a thing to check if user inputted is in the list of registered users
        await interaction.response.send_message("You entered: " + username, ephemeral=True)

class wawa(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def bwa(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(whoModal(self.ctx))

@bot.command(name="message")
async def message(ctx):
    view = wawa(ctx)
    await ctx.send("Click the button to compose a new message", view=view)

@bot.command(name="test")
async def test(ctx):
    view = testView(ctx)
    message = ""
    for i in range(frontersNum):
        message = message + fronters["fronter{0}".format(i)] + " "
    await ctx.send("Current fronter(s) is/are " + message + "!", view=view)

bot.run(token)
