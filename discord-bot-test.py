import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv
from discord.ui import Modal, TextInput, View, Button, Select

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

#==================================================#

frontersRes = requests.request("GET", url1, headers=headers, data=payload)

sysID = frontersRes.json()[0]["content"]["uid"]

frontersNum = len(frontersRes.json())
fronters = {}
fronterOpt = []
for i in range(frontersNum):
    id = frontersRes.json()[i]["content"]["member"]
    memUrl = "https://api.apparyllis.com/v1/member/" + sysID + "/" + id
    memRes = requests.request("GET", memUrl, headers=headers, data=payload)
    fronters["fronter{0}".format(i)] = memRes.json()["content"]["name"]
    fronterOpt.append(discord.SelectOption(label=memRes.json()["content"]["name"]))

#view for px.test
class testView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label=":3", style=discord.ButtonStyle.green)
    async def wawawa(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(fronters["fronter0"] + " says: wawawawawawawwawawa", ephemeral=True)

#class setting up modal for px.message
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

#view for px.message (uses whoModal)
class wawa(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def bwa(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(whoModal(self.ctx))

#view for px.dropdown
class optionView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.select(min_values=1, max_values=1, options=fronterOpt)
    async def waaa(self, interaction: discord.Interaction, select):
        await interaction.response.send_message(f"The fronter sending this message will be {select.values[0]}", ephemeral=True)

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

@bot.command(name="dropdown")
async def dropdown(ctx):
    view = optionView(ctx)
    await ctx.send("Choose a fronter to send message", view=view)

bot.run(token)
