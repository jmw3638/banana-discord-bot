# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
import os
from discord.ext.commands import Bot
from datetime import datetime
import random
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

overwatchHeroTankList = ["D.VA", "Doomfist", "Junkerqueen","Orisa","Reinhardt","Roadhod","Sigma","Winston","Wrecking Ball","Zarya"]
overwatchHeroSupportList = ["Ashe", "Bastion", "Cassidy","Echo","Genji","Hanzo","Junkrat","Mei","Pharah","Reaper","Sojourn","Soldier 76","Sombra(Please Dont)","Symmetra","Torbjorn","Tracer","Widowmaker"]
overwatchHeroDPSList = ["Ana", "Baptiste", "Brigitte","Kiriko","Lucio","Mercy","Moira","Zenyatta"]
client = discord.Client(intents=intents)
bot = Bot("!")
@bot.command()
async def Ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")

@bot.command()
async def RandomTankHero(ctx):
    tankHero=random.choice(overwatchHeroTankList)
    await ctx.send(tankHero)

@bot.command()
async def RandomSupportHero(ctx):
    supportHero=random.choice(overwatchHeroSupportList)
    await ctx.send(supportHero)

@bot.command()
async def RandomDPSHero(ctx):
    dpsHero=random.choice(overwatchHeroDPSList)
    await ctx.send(dpsHero)

def setEmbedVariables(embedCreater,message,valueString):
    embedCreater.add_field(name ="Link",value=valueString)
    embedCreater.set_author(name = message.author,icon_url=message.author.avatar.url)
    embedCreater.timestamp = message.created_at
    return embedCreater

def CreateEmbedMessage(message):
    link = str(message.jump_url)
    embedCreater = discord.Embed(description=message.content, color=0x00ff00)
    valueString = "[Go To Message]"+"("+link+")"
    embedCreater = setEmbedVariables(embedCreater,message,valueString)
    if len(message.attachments) > 0:
        embedCreater.set_image(url = message.attachments[0].url)
    return embedCreater

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == client.user.id:
        return

    if payload.emoji.name == "🍞":
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reactions = message.reactions

        for reaction in reactions:
            if str(reaction) == "🍌" and reaction.count==1:
                await client.get_channel(1011728618604474428).send(embed=CreateEmbedMessage(message))
        
token = os.environ.get('BOT_TOKEN')
client.run(token)

