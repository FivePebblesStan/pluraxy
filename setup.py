import discord
import requests
from discord import Interaction
from discord.ext import commands
from dotenv import load_dotenv
from discord.ui import Modal, TextInput, View, Button, Select

load_dotenv()
token = open("discord-token.txt").read()

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="px.", intents=intents)
client = discord.Client(intents=intents)
active_games = {}
payload = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

#==================================================#

def bucket_name(sp_token, bucket_id):
    url = "https://api.apparyllis.com/v1/privacyBucket/" + bucket_id
    headers = {'Authorization': sp_token}
    response = requests.request("GET", url, headers=headers, data=payload)
    bucketName = response.json()["content"]["name"] + " " + response.json()["content"]["icon"]
    return bucketName

def get_buckets(sp_token):
    response = requests.request("GET", "https://api.apparyllis.com/v1/privacyBuckets", headers={'Authorization': sp_token}, data=payload)
    bucketsNum = len(response.json())
    bucketsOpt = []
    for i in range(bucketsNum):
        bucketsOpt.append(discord.SelectOption(label=response.json()[i]["content"]["name"] + response.json()[i]["content"]["icon"], value=response.json()[i]["id"]))
    return bucketsOpt

def edit_file(*key, value):
    with open("pluraxy-users.txt", "r") as file:
        usersDict = eval(file.read())
        keyString = "usersDict[\"" + "\"][\"".join(key) + "\"] = " + str(value)
        exec(keyString)
    with open("pluraxy-users.txt", "w") as file:
        file.write(str(usersDict))

#++++++++++++++++++++++++++++++++++++++++++++++++++#

#view for px.setup
class setupView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Enter token", style=discord.ButtonStyle.green)
    async def bwa(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(startModal(self.ctx))
        button.disabled = True
        await interaction.edit_original_response(view=self)

#modal for px.setup
class startModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="Set Up Account")
        self.ctx = ctx
        self.input = TextInput(label="Your SimplyPlural read token")
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        spToken = self.input.value
        headers = {'Authorization': spToken}
        response = requests.request("GET", "https://api.apparyllis.com/v1/me", headers=headers, data=payload)
        if response.status_code != 200:
            await interaction.followup.send("Something went wrong. Please make sure your SimplyPlural token is correct and try again.", view=setupView(self.ctx), ephemeral=True)
        else:
            await interaction.followup.send("Your SimplyPlural token is valid. Hello, " + response.json()["content"]["username"] +"!", view=nextView(self.ctx), ephemeral=True)
        user = await self.ctx.bot.fetch_user(self.ctx.author.id)

        tempDict = {"spToken": spToken,
                    "spUser": response.json()["content"]["username"],
                    "disUser": str(user)}
        edit_file(str(self.ctx.author.id), value=tempDict)


#view for part2 of px.setup
class nextView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def eepy(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        button.disabled = True
        await interaction.edit_original_response(view=self)
        await interaction.followup.send("Now, please choose which SimplyPlural buckets you'd like to be accessible via the Pluraxy messaging system.\n"
                                                "Only those that are in the buckets you choose will be messageable by other Pluraxy users.", view=bucketsView(self.ctx), ephemeral=True)

class bucketsView(View):
    def __init__(self, ctx):
        super().__init__()
        with open("pluraxy-users.txt", "r") as file:
            self.usersDict = eval(file.read())
        bucketsOpt = get_buckets(self.usersDict[str(ctx.author.id)]["spToken"])
        self.ctx = ctx
        self.waaaa.options = bucketsOpt
        self.waaaa.min_values = 1
        self.waaaa.max_values = len(bucketsOpt)

    @discord.ui.select()
    async def waaaa(self, interaction: Interaction, select):
        await interaction.response.defer(thinking=True, ephemeral=True)
        buckets = select.values
        buckOpt = {}
        buckList = []
        headers = {'Authorization': self.usersDict[str(self.ctx.author.id)]["spToken"]}
        for i in range(len(buckets)):
            bucketName = "bucket" + str(i)
            buckOpt[bucketName] = buckets[i]
            url = "https://api.apparyllis.com/v1/privacyBucket/" + buckets[i]
            response = requests.request("GET", url, headers=headers, data=payload)
            buckList.append(response.json()["content"]["name"] + " " + response.json()["content"]["icon"])
        await interaction.followup.send(f"The selected bucket(s) is/are: " + ", ".join(buckList), view=nexttView(self.ctx), ephemeral=True)

        edit_file(str(self.ctx.author.id), "buckets", value=buckOpt)

#view for interstep2.5 of px.setup
class nexttView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def eepy(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        button.disabled = True
        await interaction.edit_original_response(view=self)
        await interaction.followup.send("Lastly, would you like it so that only users who are friends with you on SimplyPlural can message those in your system?", view=friendsView(self.ctx), ephemeral=True)

#view for pt.3 of px.setup
class friendsView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Only SP friends can message", style=discord.ButtonStyle.grey)
    async def eepiest(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        button.disabled = True
        otherButton = discord.utils.get(self.children, label="Anyone can message")
        otherButton.disabled = True
        await interaction.edit_original_response(view=self)
        await interaction.followup.send("Alright, only SP friends will be able to message.\n"
                                                "Pluraxy setup is now complete, thank you! You can now use the bot.\n"
                                                "Type px.message to send a message to someone!", ephemeral=True)
        edit_file(str(self.ctx.author.id), "onlyFriends", value="True")

    @discord.ui.button(label="Anyone can message", style=discord.ButtonStyle.grey)
    async def eepier(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        button.disabled = True
        otherButton = discord.utils.get(self.children, label="Only SP friends can message")
        otherButton.disabled = True
        await interaction.edit_original_response(view=self)
        await interaction.followup.send("Alright, anyone will be able to message.\n"
                                                "Pluraxy setup is now complete, thank you! You can now use the bot.\n"
                                                "Type px.message to send a message to someone!", ephemeral=True)
        edit_file(str(self.ctx.author.id), "onlyFriends", value="False")

@bot.command(name="setup")
async def setup(ctx):
    with open("pluraxy-users.txt", "r") as file:
        usersDict = eval(file.read())
    if usersDict.get(str(ctx.author.id)) is None:
        view = setupView(ctx)
        await ctx.send("Welcome to Pluraxy, a bot for messaging alters! Thank you for using this bot ^^\n"
                       "Currently, Pluraxy only uses SimplyPlural in order to fetch system info. PluralKit may be added at some point as well.\n"
                       "To begin account setup using SimplyPlural, click the button! You will need a read token for your SimplyPlural account.", view=view)
    else:
        await ctx.send("You've already set up your Pluraxy account!")
