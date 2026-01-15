response = requests.request("GET", "https://api.apparyllis.com/v1/privacyBuckets", headers=headers, data=payload)
bucketsNum = len(response.json())
bucketsOpt = []
for i in range(bucketsNum):
    bucketsOpt.append(discord.SelectOption(label=response.json()[i]["content"]["name"] + response.json()[i]["content"]["icon"], value=response.json()[i]["id"]))

#

class wea(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.select(options=bucketsOpt, min_values=1, max_values=bucketsNum)
    async def waaaa(self, interaction: Interaction, select):
        await interaction.response.send_message(f"The chosen buckets are: {select.values}", ephemeral=True)

@bot.command(name="buckets")
async def ww(ctx):
    view = wea(ctx)
    await ctx.send("Choose buckets", view=view, ephemeral=True)
