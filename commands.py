import os
import requests
from GPTStories import getBananaBreadStory, getMangoStory, getMeanBananaBreadStory, getObamaStory
import discord
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
from discord.ext.commands import Bot
from logic import ChooseLocalOrApi
from overwatchapi import get_player_data
from voicelines import GetVoiceLines
from pets import CatSaying, RandomPet
from openai import OpenAI
import random
import asyncio
from cachetools import TTLCache

sideServerId=discord.Object(id=1101665956314501180)
gptkey = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=gptkey)
elevenlabskey = os.environ.get('xi-api-key')

meanBreadStory=getMeanBananaBreadStory()
bananaBreadStory=getBananaBreadStory()
obamaStory=getObamaStory()
mangoStory=getMangoStory()

meanReponses=[168776263257817088,209477219158982658,199350814211440640]
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
        await interaction.response.send_message('Sorry, I could not fetch the image.')

async def is_admin(interaction: discord.Interaction) -> bool:
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
        if interaction.user.id in meanReponses:
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
    async def speak(interaction: discord.Interaction, user_input: str, speaker: str = "bread", role: str="bread"):
        await interaction.response.defer()
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.followup.send("You are not in a voice channel. Please use the `askbread` command if you just want text responses.")
            return
        if interaction.guild.voice_client is not None and interaction.guild.voice_client.is_playing():
            await interaction.followup.send("I'm currently speaking. Please try again later.")
            return
        speaker_voices = {
            "bread": "saUfe5jyFdcsZbN5Yt1c",
            "jp": "uERblY4ce8BC2FzPBGxR",
            "obama": "XbDmFt8IDl7dQjpNVO1f",
            "chris": "H8uduO2F47eLZMUNZvUf",
            "mangohawk": "ZuAcH52R3qZnDMjlvT1w",
            "cowboy": "KTPVrSVAEUSJRClDzBw7",
        }

        voice_id = speaker_voices.get(speaker.lower(), speaker_voices["bread"])  # Default to "bread" if speaker is not found

        if role == "bread" and interaction.user.id in meanReponses:
            story = meanBreadStory
        elif role.lower() == "obama":
            story = obamaStory
        elif role.lower() == "mangohawk":
            story = mangoStory
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

        await interaction.followup.send(f"🗣️ **Banana Bread says:** \"{response_message}\"")

        # ElevenLabs API request to get the MP3 file
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": elevenlabskey
        }
        data = {
            "text": response_message,
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
        response = requests.post(url, json=data, headers=headers)

        file_path = f'{interaction.guild.id}_temp_response.mp3'
        with open(file_path, 'wb') as f:
            f.write(response.content)
        if interaction.user.voice:
            voice_channel = interaction.user.voice.channel
            try:
                vc = await voice_channel.connect()
            except discord.Forbidden:
                await interaction.response.send_message("I don't have permission to join that voice channel.")
                return
            except discord.ClientException:
                await interaction.response.send_message("I'm already connected to a voice channel.")
                return
            try:
                audio_source = FFmpegPCMAudio(file_path)
                if not vc.is_playing():
                    vc.play(audio_source, after=lambda e: print('Finished playing', e))

                    while vc.is_playing():
                        await asyncio.sleep(1)
                    await vc.disconnect()
                else:
                    await interaction.response.send_message("I'm currently speaking. Please wait until I'm finished.")
                    await vc.disconnect()
            except Exception as e:
                await interaction.response.send_message(f"🗣️ **Banana Bread Errors with:** \"{e}\"")
        else:
            await interaction.response.send_message("You are not in a voice channel.")


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
            numbers = items.split(',')
            await interaction.response.send_message(random.randint(int(numbers[0]),int(numbers[1])))
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
    async def catsays(interaction: discord.Interaction, message: str):
        file_url, name = CatSaying(message)
        sent_message = f'Sure! Here\'s the picture from {name}!'
        await SendCatImage(interaction, file_url, name, sent_message)

    # Setup cache with TTL of 1 hour (3600 seconds)
    cache = TTLCache(maxsize=100, ttl=3600)

    def fetch_player_profile(player_id):
        """Fetch player profile from API with caching."""
        if player_id in cache:
            return cache[player_id]

        url = f'https://overfast-api.tekrop.fr/players/{player_id}/summary'
        response = requests.get(url)
        if response.status_code == 200:
            profile_data = response.json()
            cache[player_id] = profile_data  # Cache the response
            return profile_data
        else:
            return None

    def fetch_player_stats(player_id):
        """Fetch player stats from API."""
        url = f'https://overfast-api.tekrop.fr/players/{player_id}/stats/summary'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    @tree.command(name="playerdetails", description="Fetches detailed player information including profile and stats.", guilds=servers)
    async def player_details(interaction: discord.Interaction, player_id: str):
        await interaction.response.defer()
        
        # Fetch player profile and stats
        player_profile = fetch_player_profile(player_id)
        player_stats = fetch_player_stats(player_id)
        
        if player_profile and player_stats:
            # Embed for profile information
            embed = discord.Embed(title=f"{player_profile['username']}'s Profile", description=f"*{player_profile['title']}*", color=0x00ff00)
            embed.set_thumbnail(url=player_profile['avatar'])
            embed.set_image(url=player_profile['namecard'])
            
            # Adding competitive details
            for role, details in player_profile['competitive']['pc'].items():
                embed.add_field(name=f"{role.capitalize()} Role", value=f"Division: {details['division']} - Tier: {details['tier']}\nRank: [Icon]({details['rank_icon']})", inline=False)
            
            # Embed for stats information
            stats_message = f"**Games Played:** {player_stats['general']['games_played']}\n"
            stats_message += f"**Games Won:** {player_stats['general']['games_won']}\n"
            stats_message += f"**Games Lost:** {player_stats['general']['games_lost']}\n"
            stats_message += f"**KDA:** {player_stats['general']['kda']}\n"
            stats_message += f"**Time Played:** {player_stats['general']['time_played'] / 3600:.2f} hours\n"  # Convert seconds to hours
            stats_message += f"**Winrate:** {player_stats['general']['winrate']}%"
            
            embed.add_field(name="General Stats", value=stats_message, inline=False)
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Failed to fetch player information. Please check the player ID and try again.")
