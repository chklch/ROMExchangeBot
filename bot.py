from urllib.parse import quote

import discord
from discord.ext import commands
import requests
import sys

bot = commands.Bot(command_prefix='$')
rom_exchange_endpoint = "https://www.romexchange.com/"
rom_exchange_api = rom_exchange_endpoint + "api"
bot_token = sys.argv[1]


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
        msg = message.content.split(bot.user.mention + " ")
        if len(msg) == 2:
            query = msg[1]

            params = {
                "exact": "false",
                "item": query,
            }

            print("Searching for:" + query)
            response = requests.get(url=rom_exchange_api, params=params)
            json_response = response.json()
            if len(json_response) == 0:
                print("LOGS::NOT_FOUND:" + query)
                await message.channel.send("Could not find '{0}'".format(query))
                return

            _print_query_info(query, json_response)

            if len(json_response) > 6:
                item_list = list(map(lambda item: item["name"], json_response))
                item_list_filtered = list(filter(lambda item: item.find("[") == -1, item_list))
                item_list_filtered_with_mention = list(
                    map(lambda item: "{0} {1}".format(bot.user.mention, item), item_list_filtered))

                item_string = '\n'.join(item_list_filtered_with_mention)

                print("LOGS::TOO_MANY: Query: {0} Response:{1}".format(query, ', '.join(item_list)))
                await message.channel.send("Too many results returned.  Try the following?\n\n{0}".format(item_string))
                return

            for item in json_response:
                item_name = item["name"]
                item_image_url = item["image"]
                item_global_price = '{:,.0f}'.format(item["global"]["latest"])
                item_global_week_change = _get_formatted_week_change(item["global"]["week"]["change"])
                item_sea_price = '{:,.0f}'.format(item["sea"]["latest"])
                item_sea_week_change = _get_formatted_week_change(item["sea"]["week"]["change"])

                field_message = "Global: {0}z ({1} in 1 week)\nSEA: {2}z ({3} in 1 week)".format(item_global_price,
                                                                                                 item_global_week_change,
                                                                                                 item_sea_price,
                                                                                                 item_sea_week_change)

                embedded_message = discord.Embed(color=0x1ef1bd)
                embedded_message.title = item_name
                embedded_message.description = field_message

                encoded_item_name = quote(item_name)
                embedded_message.url = rom_exchange_endpoint + "?q=" + encoded_item_name + "&exact=true"

                if item_image_url is not None:
                    embedded_message.set_image(url=item_image_url)

                await message.channel.send(embed=embedded_message)




def _get_formatted_week_change(value):
    formatted_string = "{:.2%}".format(value / 100)

    if value > 0:
        formatted_string = "+" + formatted_string

    return formatted_string


def _print_query_info(query, json_response):
    debug_list = list(map(lambda item: item["name"], json_response))
    print("LOGS::INFO: Query: {0} Response:{1}".format(query, ', '.join(debug_list)))


bot.run(bot_token)
