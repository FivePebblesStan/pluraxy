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

#++++++++++++++++++++++++++++++++++++++++++++++++++#

#view for px.setup
class setupView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
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
        global spToken
        spToken = self.input.value

        headers = {'Authorization': spToken}
        response = requests.request("GET", "https://api.apparyllis.com/v1/me", headers=headers, data=payload)
        if response.status_code != 200:
            await interaction.response.send_message("Something went wrong. Please make sure your SimplyPlural token is correct and try again.", ephemeral=True)
        else:
            await interaction.response.send_message("Your SimplyPlural token is valid. Hello, " + response.json()["content"]["username"] +"!", view=nextView(self.ctx), ephemeral=True)
        user = await self.ctx.bot.fetch_user(self.ctx.author.id)

        with open("pluraxy-users.txt", "r") as file:
            usersDict = eval(file.read())
            tempDict = {"spToken" : spToken,
                        "spUser" : response.json()["content"]["username"],
                        "disUser" : str(user)}
            usersDict[str(self.ctx.author.id)] = tempDict
        with open("pluraxy-users.txt", "w") as file:
            file.write(str(usersDict))

#view for part2 of px.setup
class nextView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def eepy(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Now, please choose which SimplyPlural buckets you'd like to be accessible via the Pluraxy messaging system.\n"
                                                "Only those that are in the buckets you choose will be messageable by other Pluraxy users.", view=bucketsView(self.ctx), ephemeral=True)
        #button.disabled = True
        #await interaction.edit_original_response(view=self)

class bucketsView(View):
    def __init__(self, ctx):
        super().__init__()
        with open("pluraxy-users.txt", "r") as file:
            usersDict = eval(file.read())
        bucketsOpt = get_buckets(usersDict[str(ctx.author.id)]["spToken"])
        self.ctx = ctx
        self.waaaa.options = bucketsOpt
        self.waaaa.min_values = 1
        self.waaaa.max_values = len(bucketsOpt)

    @discord.ui.select()
    async def waaaa(self, interaction: Interaction, select):
        await interaction.response.send_message(f"The selected bucket(s) is/are: {select.values}", view=nexttView(self.ctx), ephemeral=True)
        buckets = select.values
        buckOpt = {}
        for i in range(len(buckets)):
            bucketName = "bucket" + str(i)
            buckOpt[bucketName] = buckets[i]
        with open("pluraxy-users.txt", "r") as file:
            usersDict = eval(file.read())
            usersDict[str(self.ctx.author.id)]["buckets"] = buckOpt
        with open("pluraxy-users.txt", "w") as file:
            file.write(str(usersDict))

#view for interstep2.5 of px.setup
class nexttView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def eepy(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Lastly, would you like it so that only users who are friends with you on SimplyPlural can message those in your system?", view=friendsView(self.ctx), ephemeral=True)
        #button.disabled = True
        #await interaction.edit_original_response(view=self)

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
        with open("pluraxy-users.txt", "a") as file:
            file.write("true\n")
        #button.disabled = True
        #await interaction.edit_original_response(view=self)

    @discord.ui.button(label="Anyone can message", style=discord.ButtonStyle.grey)
    async def eepier(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Alright, anyone will be able to message.\n"
                                                "Pluraxy setup is now complete, thank you! You can now use the bot.\n"
                                                "Type px.message to send a message to someone!", ephemeral=True)
        with open("pluraxy-users.txt", "a") as file:
            file.write("false\n")
        #button.disabled = True
        #await interaction.edit_original_response(view=self)

@bot.command(name="setup")
async def setup(ctx):
    view = setupView(ctx)
    await ctx.send("Welcome to Pluraxy, a bot for messaging alters! Thank you for using this bot ^^\n"
                   "Currently, Pluraxy only uses SimplyPlural in order to fetch system info. PluralKit may be added at some point as well.\n"
                   "To begin account setup using SimplyPlural, click the start button!", view=view)

bot.run(token)
#client.run(token)
