import os
import requests
import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
from discord.ext.commands import Bot
from logic import ChooseLocalOrApi
from voicelines import GetVoiceLines
from pets import CatSaying, RandomPet
from openai import OpenAI
import random
import asyncio
from pymongo import MongoClient
from database import *
from collections import deque
import uuid


voice_response_queue = deque()
sideServerId=discord.Object(id=1101665956314501180)
gptkey = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=gptkey)
elevenlabskey = os.environ.get('xi-api-key')
mongo_client = MongoClient(os.environ.get("MONGODB_URI"))
db = mongo_client.bananabread
roles_collection = db.roles
meanBreadStory="You are a discord bot assistant, named \" The banana bread Bot \", I want you to be as rude and sarcastic as possible."
bananaBreadStory="You are a discord bot assistant, named \" The banana bread Bot \", I want you to bake in some funny humor related to banana bread in your responses. Also, I want you to be condescending but in a funny way."

async def generate_and_play_speech(interaction, text, voice_id):
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabskey
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", 
        "voice_id": voice_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style_exaggeration": 0.0,
            "speaker_boost": True
        }
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            file_path = f'temp_response_{uuid.uuid4()}.mp3'
            with open(file_path, 'wb') as f:
                f.write(response.content)
            await play_audio(interaction, file_path)
        else:
            await interaction.followup.send("Failed to synthesize speech.")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

async def process_voice_queue():
    while True:
        if not voice_response_queue:
            await asyncio.sleep(1)  # Idle wait
            continue

        task = voice_response_queue.popleft()  # Dequeue the first task
        interaction, text, voice_id = task
        await generate_and_play_speech(interaction, text, voice_id)


async def connect_to_voice_channel(voice_channel, guild):
    try:
        if guild.voice_client:  # Bot is already in a voice channel
            if guild.voice_client.channel != voice_channel:
                await guild.voice_client.move_to(voice_channel)
            return guild.voice_client
        else:
            return await voice_channel.connect()
    except discord.Forbidden:
        await voice_channel.send("I don't have permission to join that voice channel.")
        return None
    except Exception as e:
        print(f"Failed to connect to voice channel: {e}")
        return None

async def play_audio(vc, file_path):
    try:
        audio_source = FFmpegPCMAudio(file_path)
        vc.play(audio_source)
        while vc.is_playing():
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        await vc.disconnect()

async def SendCatImage(interaction, file_url, name, sent_message):
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        with open('temp_image.jpg', 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        discord_file = discord.File('temp_image.jpg', filename='image.jpg')

        await interaction.response.send_message(sent_message, file=discord_file)

        os.remove('temp_image.jpg')
    else:
        print(file_url)
        print(name)
        await interaction.response.send_message('Sorry, I could not fetch the image.')

async def is_admin(interaction: discord.Interaction) -> bool:
    """Check if the user has the administrator permission."""
    return interaction.user.guild_permissions.administrator

def DefineAllCommands(tree):
    sideServerId=discord.Object(id=1101665956314501180)
    sideServerId2=discord.Object(id=1210021401772429352)
    servers = [sideServerId,sideServerId2]

    @tree.command(name="cleanupvc", description="Cleans up voice chats.", guilds=servers)
    async def cleanupvc(interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("Something went wrong with guild interaction.")
            return

        vcListToClean = [vc for vc in guild.voice_channels if vc.name.endswith("'s VC") and len(vc.members) == 0]

        if not vcListToClean:
            await interaction.response.send_message("No empty VC's found to clean up.")
            return

        for vc in vcListToClean:
            await vc.delete(reason="VC Cleanup")

        await interaction.response.send_message(f"Cleaned up {len(vcListToClean)} VC(s).")

    @tree.command(name="askbread", description="Responds with a custom message generated by OpenAI, incorporating humor related to banana bread.", guilds=servers)
    async def askbread(interaction: discord.Interaction, user_input: str):
        if interaction.user.id == 168776263257817088 or interaction.user.id == 212635381391294464 or interaction.user.id == 209477219158982658:
            story = meanBreadStory
        else:
            story = bananaBreadStory
        completion_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": story},
                {"role": "user", "content": user_input}
            ]
        )
        response_message = completion_response.choices[0].message.content
        await interaction.response.send_message(response_message)

    @tree.command(name="speak", description="Speaks the response generated by GPT-3 in a voice channel.", guilds=servers)
    async def speak(interaction: discord.Interaction, user_input: str, speaker: str = "bread"):
        voice_state = interaction.user.voice
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message("You are not in a VC, please use the \"askbread\" command for only text responses.")
            return  
        speaker_voices = {
            "JP": "uERblY4ce8BC2FzPBGxR",
            "bread": "saUfe5jyFdcsZbN5Yt1c",
            "Chris": "H8uduO2F47eLZMUNZvUf",
        }
        voice_id = speaker_voices.get(speaker, speaker_voices["bread"])  # Default to "bread" if speaker is not found

        # Determine which story to use based on the user ID
        if interaction.user.id in [168776263257817088, 212635381391294464, 209477219158982658]:
            story = meanBreadStory
        else:
            story = bananaBreadStory

        # Generate the response using GPT-3.5-turbo
        completion_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": story},
                {"role": "user", "content": user_input}
            ]
        )
        generated_text = completion_response.choices[0].message.content
        await interaction.response.send_message(f"🗣️ **Banana Bread says:** \"{generated_text}\"")
        voice_response_queue.append((interaction, generated_text, voice_id))

    @tree.command(name = "yesno", description = "picks yes or no", guilds=servers) 
    async def yesno(interaction):
        await interaction.response.send_message(random.choice(["Yes", "No"]))

    @tree.command(name = "pickfromlist", description = "input things to be chosen seperated by a ,. Ex. Overwatch,League", guilds=servers) 
    async def pickfromlist(interaction: discord.Interaction, items: str):
        await interaction.response.send_message(random.choice(items.split(',')))

    @tree.command(name="sleepygenerator", description="will give an amount of Z's that are randomly uppercased and lower", guilds=servers)
    async def sleepygenerator(interaction: discord.Interaction, items: int):
        itemCount = min(items, 200)
        zString = ''.join(random.choice(['Z', 'z']) for _ in range(itemCount))
        if items > 200:
            zString = "Limiting to 200 Z's: " + zString
        await interaction.response.send_message(zString)

    @tree.command(name = "randomnumber", description = "Choose a random number between 2 inputs ex: 1,100", guilds=servers) 
    async def self(interaction: discord.Interaction, items: str):
        try:
            await interaction.response.send_message(random.randint(int(items.split(',')[0]),int(items.split(',')[1])))
        except:
            await interaction.response.send_message("Either you messed up or I did. But It was prob you")

    @tree.command(name="rhythmroll", description="rolls number 1-100", guilds=servers) 
    async def first_command(interaction):
        await interaction.response.send_message(random.randint(0,100))

    @tree.command(name="randompet", description="Random pet picture from friends!", guilds=servers) 
    async def random_pet(interaction):
        # Fetch the image from GitHub/cataas
        file_url, name = ChooseLocalOrApi()
        sent_message = f'Sure! Here\'s a random picture from {name}!'
        await SendCatImage(interaction, file_url, name, sent_message)

    @tree.command(name="catsays", description="Random Cat with text input", guilds=servers) 
    async def self(interaction: discord.Interaction, message: str):
        file_url, name = CatSaying(message)
        sent_message = f'Sure! Here\'s the picture from {name}!'
        await SendCatImage(interaction, file_url, name, sent_message)
        

