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

#acutal code starts here

#url1 is to get all the fronters data
url1 = "https://api.apparyllis.com/v1/fronters/"

payload = {}
headers = {
  'Authorization': api_key
}

#gets all the fronters data (thats all the numbers and member ids and fronting times and everything. (frontersRes = fronters response)
#its an array (or, well, list, since py only has lists) of fronters with a bunch of data:
#each thing in the list (aka fronter) has three dictionary entries, the third of which is a nested dictionary from which we pull all our stuff
frontersRes = requests.request("GET", url1, headers=headers, data=payload)

#gets the systems userid (grabs it from the first fronter, it is the uid dictionary entry in that nested dictionary)
sysID = frontersRes.json()[0]["content"]["uid"]

#gets the amount of fronters (all this works even if theres only one fronter, yay!)
frontersNum = len(frontersRes.json())
#uhh idk what this isi exactly. but it makes it possible to make a dictionary entry with the current loop number so?? works
fronters = {}
#for loop <3 runs once per member
for i in range(frontersNum):
    #gets the member id for nth fronter (gets it from the "member" entry in the nested dictionary)
    id = frontersRes.json()[i]["content"]["member"]
    #puts together the url the api needs to get the info about this particular member - the system id we got earlier, and this members id
    memUrl = "https://api.apparyllis.com/v1/member/" + sysID + "/" + id
    #memRes = member response
    #gets from the api a bunch of stuff about the member - its all dictionary enteries (no lists/arrays here!). same thing of three dictionary entries, third one has a nested
    memRes = requests.request("GET", memUrl, headers=headers, data=payload)
    #makes a new dictionary entry in the fronters var that is this fronters name (gotten from the "name" entry in the members nested dictionary)
    #this dictionary entry is called 'fronter + [current loop]', basically. dont really know how the whole "fronter{0}".format(i) yhing works but it does, it uses the loopsnumber!
    fronters["fronter{0}".format(i)] = memRes.json()["content"]["name"]

#oh this sends me a message in the console saying the bot is online
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

#uhhh. idk? i dont know exactly what this first bit does, i should figure it out, thats important
#but basically all this makes the 'view' that i then append onto the message that the bot sends, and this 'view' has the :3 button
class testView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    #yeah this all sets the button up
    #this button sends an ephemeral message of the first fronter saying 'wawawawawaa'. specifically the first fronter. also its green :3
    @discord.ui.button(label=":3", style=discord.ButtonStyle.green)
    async def wawawa(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(fronters["fronter0"] + " says: wawawawawawawwawawa", ephemeral=True)

#the px.test command!
@bot.command(name="test")
async def test(ctx):
    #sets this message up to use the view establed earlier
    view = testView(ctx)
    #makes a variable to store a string list of fronters
    message = ""
    #for loop! basically appends each fronters name together into the message string. uses that dictionary of fronters' names we made in the earlier loop
    #doesnt do commas :(
    for i in range(frontersNum):
        message = message + fronters["fronter{0}".format(i)] + " "
    #sends the message of who the current fronters are! WITH the wawa button bcs the view is added
    await ctx.send("Current fronter(s) is/are " + message + "!", view=view)

#acutally runs the bot :3
bot.run(token)
