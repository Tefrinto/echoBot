import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
import asyncio
import sys
from datetime import datetime

# Load environment variables
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# Set up basic logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)


# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)


# Scheduled task for bingbong playing every hour
async def globalBingBong():
    HorasMudae = [2, 5, 8, 11, 14, 17, 20, 23]
    HoraAhora = datetime.now().hour
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            if len(vc.members) > 0:
                voice_client = await vc.connect()
                music_folder = "sounds/bingbong"
                music_files = sorted(
                    [f for f in os.listdir(music_folder) if f.endswith(".mp3")]
                )

                if(HoraAhora in HorasMudae):
                    selected_song = "chibi.mp3"
                else:
                    selected_song = random.choices(music_files, weights=[0.00, 99.99, 0.01], k=1)[
                    0
                    ]

                while not voice_client.is_connected():
                    await asyncio.sleep(0.1)

                voice_client.play(
                    discord.FFmpegPCMAudio(os.path.join(music_folder, selected_song))
                )

                while voice_client.is_playing():
                    await asyncio.sleep(0.1)

                await voice_client.disconnect()


# Handling events
## Event when the bot is ready
@bot.event
async def on_ready():
    logging.info("Starting global BingBong task:")

    if await globalBingBong():
        logging.info("Finished successfully global BingBong Task")
    else:
        logging.info("Finished successfully global BingBong Task")

    await bot.close()


# Run the bot
if __name__ == "__main__":
    if token:
        bot.run(token)
    else:
        logging.critical("Error: DISCORD_TOKEN not found in environment variables.")
        exit(1)
