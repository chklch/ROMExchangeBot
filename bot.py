import discord
from discord.ext import commands
import requests
# import json

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return

    if message.content.startswith(bot.user.mention):
        # msg = 'Hello {0.author.mention}'.format(message)
        #
        msg = message.content.split(bot.user.mention)
        if len(msg) == 2:
            query = msg[1]
            url = "https://www.romexchange.com/api"

            params = {
                'item': query,
                'exact': "false"
            }

            response = requests.get(url=url, params=params)
            # import pdb; pdb.set_trace()
            json_response = response.json()

            for item in json_response:
                item_name = item["name"]
                await message.channel.send(item_name)

@bot.command()
async def greet(ctx):
    await ctx.send(":smiley: :wave: Hello, there!")

bot.run("NTQ3MDg3NTIxOTY4OTQ3MjEx.D0x8LA.FzOkJ9jjlK91PRS6LlNDj0JcPMM")
