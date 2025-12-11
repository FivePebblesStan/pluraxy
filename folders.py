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

payload = {}
headers = {
  'Authorization': api_key
}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

url1 = "https://api.apparyllis.com/v1/me"
sysID = requests.request("GET", url1, headers=headers, data=payload)
url2 = "https://api.apparyllis.com/v1/groups/" + sysID.json()["id"]
groupRes = requests.request("GET", url2, headers=headers, data=payload)

print(groupRes.text)

foldersNum = len(groupRes.json())
folders = []
for i in range(foldersNum):
    folders.append(i)
    """if 0<len(groupRes.json()[i]["content"]["name"])<101:
        folders.append(discord.SelectOption(label=groupRes.json()[i]["content"]["name"]))"""

print(folders)

#view for px.folders
class foldersView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.select(min_values=1, max_values=1, options=folders)
    async def waaa(self, interaction: discord.Interaction, select):
        await interaction.response.send_message(f"The selected folder for messageable members will be {select.values[0]}", ephemeral=True)

@bot.command(name="folders")
async def folders(ctx):
    view = foldersView(ctx)
    await ctx.send("Choose a folder of messageable system members", view=view)

bot.run(token)
#print(response.text)
