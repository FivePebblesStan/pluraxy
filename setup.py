import discord
import requests
from discord import Interaction
from discord._types import ClientT
from discord.ext import commands
from dotenv import load_dotenv
from discord.ui import Modal, TextInput, View, Button, Select

load_dotenv()
#api_key = open("api-key.txt").read()
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

def get_sys_trait(sp_token,trait):
    "sp_token is the token, trait is an aspect like uid, username, desc, isAsystem. it returns a string of the trait"
    url = "https://api.apparyllis.com/v1/me/"
    headers = {'Authorization': sp_token}
    response1 = requests.request("GET", url, headers=headers, data=payload)
    return response1.json()["content"][trait]

def get_attribute_for_all_alters(sp_token,trait):
    "sp_token is the token, and the trait is the desired aspect. it returns a list of strings of traits"
    #trait options are: name, buckets, color, desc, pronouns, archived, preventsFrontNotifs
    sysID = get_sys_trait(sp_token, "uid")
    url = "https://api.apparyllis.com/v1/members/"+sysID
    headers = {'Authorization': sp_token}
    response = requests.request("GET", url, headers=headers, data=payload)
    traits = []
    for alter in response.json():
        traits.append(alter["content"][trait])
    return traits

def choose_bucket(sp_token, alter_name):
    "cmon. you know what sp_token is. alter_name is the name of an alter that has the bucket you want "
    name_buckets = list(map(lambda x: get_attribute_for_all_alters(sp_token,x),["name","buckets"]))
    messy_bucket = [a[1] if a[0] == alter_name else None for a in zip(name_buckets[0],name_buckets[1])]
    bucket = next(val for val in messy_bucket if val is not None)[0]
    return bucket

#++++++++++++++++++++++++++++++++++++++++++++++++++#

#view for px.setup
class setupView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def bwa(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(startModal(self.ctx))

#modal for px.setup
class startModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="Set Up Account")
        self.ctx = ctx
        self.input = TextInput(label="Your SimplyPlural read token")
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        global spToken
        spToken = self.input.value

        headers = {'Authorization': spToken}
        response = requests.request("GET", "https://api.apparyllis.com/v1/me", headers=headers, data=payload)
        if response.status_code != 200:
            await interaction.response.send_message("Something went wrong. Please make sure your SimplyPlural token is correct and try again.", ephemeral=True)
        else:
            await interaction.response.send_message("Your SimplyPlural token is valid. Hello, " + response.json()["content"]["username"] +"!", view=nextView(self.ctx), ephemeral=True)
        user = await self.ctx.bot.fetch_user(userId)
        with open("pluraxy-users.txt", "a") as file:
            file.write(spToken + ", " + response.json()["content"]["username"] + ", " + str(userId) + ", " + str(user))


#view for interstep1.5 of px.setup
class nextView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def eepy(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("The way Pluraxy knows which alters in your are messageable is via looking at the buckets of a SimplyPlural profile you choose, and allowing messaging to all the profiles in those buckets.\n"
                                                "E.g. profile 1 is in buckets A and B, profile 2 is in buckets B and C, and profile 3 is in buckets C and D. If profile 1 is chosen as the bucket basis, only profiles 1 and 2 will be messageable, not profile 3.\n"
                                                "So, please press this button and type in the name of a profile on your SimplyPlural that is in all the buckets you would like to be accessible. (You may create a temporary extra profile for this purpose if necessary.)", view=bucketsView(self.ctx), ephemeral=True)

# view for pt2 of px.setup
class bucketsView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Choose a profile", style=discord.ButtonStyle.green)
    async def www(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(bucketsModal(self.ctx))

#modal for pt2 of px.setup
class bucketsModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="Set Up Account")
        self.ctx = ctx
        self.input = TextInput(label="Profile name")
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        profile = self.input.value
        global buckets
        buckets = choose_bucket(spToken, profile)
        await interaction.response.send_message("The selected bucket(s) is/are: " + buckets + "\n"
                                                "-# (If you created a temporary profile for this, you may now delete it)", view=nexttView(self.ctx), ephemeral=True)
        with open("pluraxy-users.txt", "a") as file:
            file.write(", " + buckets + "\n")

#view for interstep2.5 of px.setup
class nexttView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def eepy(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Lastly, would you like it so that only users who are friends with you on SimplyPlural can message those in your system?", view=friendsView(self.ctx), ephemeral=True)

#view for pt.3 of px.setup
class friendsView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Only SP friends can message", style=discord.ButtonStyle.grey)
    async def eepiest(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Alright, only SP friends will be able to message.\n"
                                                "Pluraxy setup is now complete, thank you! You can now use the bot.\n"
                                                "Type px.message to send a message to someone!", ephemeral=True)

    @discord.ui.button(label="Anyone can message", style=discord.ButtonStyle.grey)
    async def eepier(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Alright, anyone will be able to message.\n"
                                                "Pluraxy setup is now complete, thank you! You can now use the bot.\n"
                                                "Type px.message to send a message to someone!", ephemeral=True)

@bot.command(name="setup")
async def setup(ctx):
    global userId
    userId = ctx.author.id
    view = setupView(ctx)
    await ctx.send("Welcome to Pluraxy, a bot for messaging alters! Thank you for using this bot ^^\n"
                   "Currently, Pluraxy only uses SimplyPlural in order to fetch system info. PluralKit may be added at some point as well.\n"
                   "To begin account setup using SimplyPlural, click the start button!", view=view)

bot.run(token)
#client.run(token)
