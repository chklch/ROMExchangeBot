import discord
from discord.ext import commands

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
            await message.channel.send("Will search for " + query)

@bot.command()
async def greet(ctx):
    await ctx.send(":smiley: :wave: Hello, there!")

bot.run("NTQ3MDg3NTIxOTY4OTQ3MjEx.D0x8LA.FzOkJ9jjlK91PRS6LlNDj0JcPMM")
