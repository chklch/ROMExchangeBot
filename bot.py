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
            query = msg[1].strip()

            params = {
                "exact": "false",
                "item": query,
                "slim": "true",
            }

            print("Searching for:" + query)
            response = requests.get(url=rom_exchange_api, params=params)
            json_response = response.json()

            response_messages = _get_response_messages(query, json_response)

            item_messages = response_messages[0]
            helper_messages = response_messages[1]

            if item_messages is not None:
                for item_message in item_messages:
                    await message.channel.send(embed=item_message)

            if helper_messages is not None:
                for help_message in helper_messages:
                    await message.channel.send(help_message)


def _get_response_messages(query, json_response):
    if len(json_response) == 0:
        print("LOGS::NOT_FOUND:" + query)
        return None, ["Could not find '{0}'".format(query)]

    _print_query_info(query, json_response)

    if _item_exact_match(query, json_response):
        return _get_exact_response_message(query, json_response)

    if len(json_response) > 6:
        item_list = list(map(lambda item: item["name"], json_response))
        item_list_filtered = list(filter(lambda item: item.find("[") == -1, item_list))
        item_list_filtered_with_mention = list(
            map(lambda item: "{0} {1}".format(bot.user.mention, item), item_list_filtered))

        item_string = '\n'.join(item_list_filtered_with_mention)

        print("LOGS::TOO_MANY: Query: {0} Response:{1}".format(query, ', '.join(item_list)))
        return None, ["Too many results returned.  Try the following?\n\n{0}".format(item_string)]

    item_messages = list()
    for item in json_response:
        embedded_message = _get_item_embed_message(item)

        item_messages.append(embedded_message)
    return item_messages, None


def _item_exact_match(query, json_response):
    item_name_list = list(map(lambda item: item["name"], json_response))
    exact_item = list(filter(lambda name: name.lower() == query.lower(), item_name_list))
    return len(exact_item) == 1


def _get_exact_response_message(query, json_response):
    json_exact_item_list = list(filter(lambda item: item["name"].lower() == query.lower(), json_response))

    json_item = None
    if len(json_exact_item_list) == 1:
        json_item = json_exact_item_list[0]

    if len(json_exact_item_list) > 1:
        item_list = list(map(lambda item: item["name"], json_response))
        print("ERROR::EXACT_TOO_MANY: Multiple matches Query: {0} Response:{1}".format(query, ', '.join(item_list)))
        return

    json_item_list = [json_item] + list(filter(lambda item: item["name"].lower().startswith(query.lower() + " ["), json_response))
    item_messages = list()
    for item in json_item_list:
        item_messages.append(_get_item_embed_message(item))

    filtered_json_response = _get_filtered_response(json_item_list, json_response)

    too_many_message = None

    if len(filtered_json_response) > 0:
        item_list = list(map(lambda item: item["name"], filtered_json_response))
        item_list_filter = list(filter(lambda item: item.find("[") == -1, item_list))
        item_list_filtered_with_mention = list(
            map(lambda item: "{0} {1}".format(bot.user.mention, item), item_list_filter))

        item_string = '\n'.join(item_list_filtered_with_mention)

        print("LOGS::EXACT_TOO_MANY: Query: {0} Response:{1}".format(query, ', '.join(item_list)))
        too_many_message = "Other results found.  Were you looking for these?\n\n{0}".format(item_string)

    if too_many_message is None:
        return item_messages, None
    return item_messages, [too_many_message]


def _get_filtered_response(json_item_list, json_response):
    remove_names = list(map(lambda item: item["name"], json_item_list))
    filtered_response = list()
    for item in json_response:
        if item["name"] not in remove_names:
            filtered_response.append(item)

    return filtered_response

def _get_item_embed_message(json_item):
    item_name = json_item["name"]
    item_image_url = json_item["image"]
    item_global_price = '{:,.0f}'.format(json_item["global"]["latest"])
    item_global_week_change = _get_formatted_week_change(json_item["global"]["week"]["change"])
    item_sea_price = '{:,.0f}'.format(json_item["sea"]["latest"])
    item_sea_week_change = _get_formatted_week_change(json_item["sea"]["week"]["change"])
    field_message = "Global: {0}z ({1} in 1 week)\nSEA: {2}z ({3} this week)".format(item_global_price,
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
    return embedded_message


def _get_formatted_week_change(value):
    formatted_string = "{:.2%}".format(value / 100)

    if value > 0:
        formatted_string = "+" + formatted_string

    return formatted_string


def _print_query_info(query, json_response):
    debug_list = list(map(lambda item: item["name"], json_response))
    print("LOGS::INFO: Query: {0} Response:{1}".format(query, ', '.join(debug_list)))


bot.run(bot_token)
