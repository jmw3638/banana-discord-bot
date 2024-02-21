import os
import requests
import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
from discord.ext.commands import Bot
from discord import FFmpegPCMAudio
from logic import ChooseLocalOrApi
from voicelines import GetVoiceLines
from pets import CatSaying, RandomPet
from openai import OpenAI
import random
import asyncio

overwatchHeroTankList = ["D.VA", "Doomfist", "Junkerqueen","Orisa","Reinhardt","Roadhog","Sigma","Winston","Wrecking Ball","Zarya","Ramattra"]
overwatchHeroDPSList = ["Ashe", "Bastion", "Cassidy","Echo","Genji","Hanzo","Junkrat","Mei","Pharah","Reaper","Sojourn","Soldier 76","Sombra(Please Dont)","Symmetra","Torbjorn","Tracer","Widowmaker"]
overwatchHeroSupportList = ["Ana", "Baptiste", "Brigitte","Kiriko","Lucio","Mercy","Moira","Zenyatta"]
overwatchRoleList = ["Tank", "DPS", "Support"]
overwatchGameModeList = ["Competitive", "Quick Play", "Custom Games", "Arcade"]
mainServerId=discord.Object(id=222147212681936896)
sideServerId=discord.Object(id=1101665956314501180)
gptkey = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=gptkey)
elevenlabskey = os.environ.get('xi-api-key')

async def SendCatImage(interaction, file_url, name, sent_message):
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        # Create a temporary file to hold the image
        with open('temp_image.jpg', 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        # Send the image to Discord
        discord_file = discord.File('temp_image.jpg', filename='image.jpg')

        await interaction.response.send_message(sent_message, file=discord_file)

        os.remove('temp_image.jpg')
    else:
        print(file_url)
        print(name)
        await interaction.response.send_message('Sorry, I could not fetch the image.')

def DefineAllCommands(tree):
    mainServerId=discord.Object(id=222147212681936896)
    sideServerId=discord.Object(id=1101665956314501180)
    servers = [mainServerId, sideServerId]
    for server in servers:

        @tree.command(name="askbread", description="Responds with a custom message generated by OpenAI, incorporating humor related to banana bread.", guild=server)
        async def askbread(interaction: discord.Interaction, user_input: str):
            completion_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a discord bot assistant, named banana bread, I want you to bake in some funny humor related to banana bread in your responses. Also I want you to be condesending but in a funny way."},
                    {"role": "user", "content": user_input}
                ]
            )
            response_message = completion_response.choices[0].message.content
            await interaction.response.send_message(response_message)

        @tree.command(name="speak", description="Speaks the response generated by GPT-3 in a voice channel.", guild=server)
        async def speak(interaction: discord.Interaction, user_input: str):
            completion_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a discord bot assistant, named banana bread, I want you to bake in some funny humor related to banana bread in your responses. Also, I want you to be condescending but in a funny way."},
                    {"role": "user", "content": user_input}
                ]
            )
            response_message = completion_response.choices[0].message.content

            await interaction.response.send_message(f"🗣️ **Banana Bread says:** \"{response_message}\"")

            # ElevenLabs API request to get the MP3 file
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": elevenlabskey
            }
            data = {
                "text": response_message,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            # Male Bread: BM4igwEfmKXiGdbdbJdk
            # Female Bread: Iq2WyJggqdxjND19FFJw
            url = "https://api.elevenlabs.io/v1/text-to-speech/Iq2WyJggqdxjND19FFJw"
            response = requests.post(url, json=data, headers=headers)

            file_path = 'temp_response.mp3'
            with open(file_path, 'wb') as f:
                f.write(response.content)

            if interaction.user.voice:
                voice_channel = interaction.user.voice.channel
                vc = await voice_channel.connect()
                audio_source = FFmpegPCMAudio(file_path)
                if not vc.is_playing():
                    vc.play(audio_source, after=lambda e: print('Finished playing', e))

                    while vc.is_playing():
                        await asyncio.sleep(1)

                    await vc.disconnect()
                else:
                    await interaction.response.send_message("I'm currently speaking. Please wait until I'm finished.")
                    await vc.disconnect()
            else:
                await interaction.response.send_message("You are not in a voice channel.")

        @tree.command(name="randomtank", description="rolls a random tank hero from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchHeroTankList))

        @tree.command(name="randomsupport", description="rolls a random support hero from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchHeroSupportList))

        @tree.command(name="randomvoiceline", description="rolls a random voiceline from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(GetVoiceLines()))

        @tree.command(name="randomdps", description="rolls a random support dps from overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchHeroDPSList))

        @tree.command(name="randomroleow", description="rolls a random role for overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchRoleList))

        @tree.command(name="randomgamemodeow", description="rolls a random game mode for overwatch", guild=server)
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(overwatchGameModeList))

        @tree.command(name = "yesno", description = "picks yes or no", guild=server) 
        async def first_command(interaction):
            await interaction.response.send_message(random.choice(["Yes", "No"]))

        @tree.command(name = "pickfromlist", description = "input things to be chosen seperated by a ,. Ex. Overwatch,League", guild=server) 
        async def self(interaction: discord.Interaction, items: str):
            await interaction.response.send_message(random.choice(items.split(',')))

        @tree.command(name = "sleepygenerator", description = "will give an amt of Z's that are randomly uppercased and lower", guild=server) 
        async def self(interaction: discord.Interaction, items: int):
            itemCount=items
            zString = "" if itemCount<=200 else "Limiting to 200 Z's:   "
            if (itemCount > 200):
                itemCount=200
            while (itemCount>0):
                randomZ="Z" if random.randint(1,2) == 1 else "z"
                zString = zString+randomZ
                itemCount-=1
            await interaction.response.send_message(zString)
    
        @tree.command(name = "randomnumber", description = "Choose a random number between 2 inputs", guild=server) 
        async def self(interaction: discord.Interaction, items: str):
            try:
                await interaction.response.send_message(random.randint(int(items.split(',')[0]),int(items.split(',')[1])))
            except:
                await interaction.response.send_message("Either you messed up or I did. But It was prob you")

        @tree.command(name="rhythmroll", description="rolls number 1-100", guild=server) 
        async def first_command(interaction):
            await interaction.response.send_message(random.randint(0,100))

        @tree.command(name="randompet", description="Random pet picture from friends!", guild=server) 
        async def random_pet(interaction):
            # Fetch the image from GitHub/cataas
            file_url, name = ChooseLocalOrApi()
            sent_message = f'Sure! Here\'s a random picture from {name}!'
            await SendCatImage(interaction, file_url, name, sent_message)

        @tree.command(name="catsays", description="Random Cat with text input", guild=server) 
        async def self(interaction: discord.Interaction, message: str):
            file_url, name = CatSaying(message)
            sent_message = f'Sure! Here\'s the picture from {name}!'
            await SendCatImage(interaction, file_url, name, sent_message)

        @tree.command(name="joinvoice", description="Joins a voice channel", guild=server)
        async def join_voice_channel(interaction: discord.Interaction):
            if interaction.user.voice:
                voice_channel = interaction.user.voice.channel
                if interaction.client.voice_clients:
                    await interaction.response.send_message("I'm already in a voice channel.")
                else:
                    vc = await voice_channel.connect()
                    await interaction.response.send_message(f"Joined {voice_channel.name}.")
            else:
                await interaction.response.send_message("You are not in a voice channel.")

        @tree.command(name="leavevoice", description="Leaves the voice channel", guild=server)
        async def leave_voice_channel(interaction: discord.Interaction):
            if interaction.client.voice_clients:
                for vc in interaction.client.voice_clients:
                    if vc.guild == interaction.guild:
                        await vc.disconnect()
                        await interaction.response.send_message("I have left the voice channel.")
                        return
                await interaction.response.send_message("I'm not in any voice channel in this server.")
            else:
                await interaction.response.send_message("I'm not in any voice channel.")