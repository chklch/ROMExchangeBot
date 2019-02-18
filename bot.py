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
        msg = message.content.split(bot.user.mention + " ")
        if len(msg) == 2:
            query = msg[1]
            url = "https://www.romexchange.com/api"

            params = {
                "exact": "false",
                "item": query,
            }

            response = requests.get(url=url, params=params)
            json_response = response.json()

            if len(json_response) == 0:
                await message.channel.send("Could not find '{0}'".format(query))
                return

            if len(json_response) > 6:
                item_list = list(map(lambda item: item["name"], json_response))
                item_list_filtered = list(filter(lambda item: item.find("[") == -1, item_list))
                item_list_filtered_with_mention = list(map(lambda item: "{0} {1}".format(bot.user.mention, item), item_list_filtered))

                item_string = '\n'.join(item_list_filtered_with_mention)

                await message.channel.send("Too many results returned.  Try the following?\n\n{0}".format(item_string))
                return

            for item in json_response:
                item_name = item["name"]
                item_image_url = item["image"]
                item_global_price = '{:,.0f}'.format(item["global"]["latest"])
                item_sea_price = '{:,.0f}'.format(item["sea"]["latest"])

                field_message = "Global: {0}z\nSEA: {1}z".format(item_global_price, item_sea_price)

                embedded_message = discord.Embed(color=0x1ef1bd)
                embedded_message.title = item_name
                embedded_message.description = field_message

                if item_image_url is not None:
                    embedded_message.set_image(url=item_image_url)

                await message.channel.send(embed=embedded_message)


bot.run("NTQ3MDg3NTIxOTY4OTQ3MjEx.D0x8LA.FzOkJ9jjlK91PRS6LlNDj0JcPMM")
