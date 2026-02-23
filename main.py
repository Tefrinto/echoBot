import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
from mathparse import mathparse
import json
from datetime import datetime
import random
import asyncio
import sys

# Load environment variables
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
jaimeId = int(os.getenv("JAIME_USER_ID"))
pabloId = int(os.getenv("PABLO_USER_ID"))
marcosId = int(os.getenv("MARCOS_USER_ID"))
caneteId = int(os.getenv("CANETE_USER_ID"))
storyChannelId = int(os.getenv("STORY_CHANNEL_ID"))
mudaeRol = os.getenv("MUDAE_ROL")
mudaeSubId = int(os.getenv("MUDAE_SUBSCRIBE_MESSAGE_ID"))
mudaeEditId = int(os.getenv("MUDAE_EDIT_MESSAGE_ID"))
mudaeChannelId = int(os.getenv("MUDAE_CHANNEL_ID"))
fireChannelId = int(os.getenv("FIRE_CHANNEL_ID"))
jaimeReactionEmoji = os.getenv("JAIME_REACTION_EMOJI")
intermediosEmoji = os.getenv("INTERMEDIOS_EMOJI")
alonsoStickerId = int(os.getenv("ALONSO_STICKER_ID"))
storySubscribeId = int(os.getenv("STORY_SUBSCRIBE_MESSAGE_ID"))
storyEditId = int(os.getenv("STORY_EDIT_MESSAGE_ID"))
_story_rol_raw = os.getenv("STORY_ROL_ID", "")
storyRolId = int(_story_rol_raw.replace("<@&", "").replace(">", ""))

pablo_message_count = 0
tiradas = ["$m", "$ma", "$mg", "$h", "$hg", "$ha"]

# Set up basic logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

# File to store the last claim message ID
CLAIM_MESSAGE_FILE = "last_claim_message.json"


# Function to load the last claim message ID from file
def load_claim_message_id():
    try:
        with open(CLAIM_MESSAGE_FILE, "r") as f:
            data = json.load(f)
            return data.get("message_id")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


# Function to save the last claim message ID to file
def save_claim_message_id(message_id):
    try:
        with open(CLAIM_MESSAGE_FILE, "w") as f:
            json.dump({"message_id": message_id}, f)
    except Exception as e:
        logging.error(f"Error saving claim message ID: {e}")


# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)


# Scheduled task for mudae claim reset notification
@tasks.loop(hours=3)
async def mudae_claim_reset():
    channel = bot.get_channel(mudaeChannelId)

    last_message_id = load_claim_message_id()
    if last_message_id:
        last_message = await channel.fetch_message(last_message_id)
        await last_message.delete()

    guild = channel.guild
    mudaeRolId = discord.utils.get(guild.roles, name=mudaeRol)
    message = await channel.send(
        f"<@&{mudaeRolId.id}> el claim del mudae ha sido reiniciado"
    )
    save_claim_message_id(message.id)


@mudae_claim_reset.before_loop
async def before_mudae_claim_reset():
    await bot.wait_until_ready()

    now = datetime.now()
    current_hour = now.hour
    next_3h_mark = ((current_hour // 3) + 1) * 3

    if next_3h_mark >= 24:
        next_3h_mark = 0

    hours_to_wait = (next_3h_mark - current_hour - 1 + 24) % 24
    minutes_to_wait = 59 - now.minute + 5
    seconds_to_wait = 59 - now.second

    if seconds_to_wait == 60:
        seconds_to_wait = 0
        minutes_to_wait += 1

    if minutes_to_wait == 60:
        minutes_to_wait = 0
        hours_to_wait = (hours_to_wait + 1) % 24

    total_seconds = hours_to_wait * 3600 + minutes_to_wait * 60 + seconds_to_wait

    logging.info(f"Next 3-hour mark: {next_3h_mark:02d}:05:00")
    logging.info(
        f"Waiting {hours_to_wait}h {minutes_to_wait}m {seconds_to_wait}s before starting mudae claim reset task"
    )

    await asyncio.sleep(total_seconds)


# Handling events
## Event when the bot is ready
@bot.event
async def on_ready():
    logging.info(f"Estamos ready para funcionar, {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")
    now = datetime.now()
    logging.info(f"Current time: {now.strftime('%H:%M:%S')}\n")

    if not mudae_claim_reset.is_running():
        mudae_claim_reset.start()
        logging.info("Started mudae claim reset task")


## Event when a new member joins
@bot.event
async def on_member_join(member):
    await member.send(
        f"Bienvenido al *{member.guild.name}*, {member.name}, ponte cómodo aunque no demasiado."
    )


## Event when a message is sent
@bot.event
async def on_message(message):
    global pablo_message_count

    if message.channel == bot.get_channel(fireChannelId):
        await message.add_reaction("🔥")

    if message.author == bot.user:
        return

    if message.author.id == caneteId and any(
        msg in message.content.lower() for msg in tiradas
    ):
        await message.reply("Cañete tira con / puto perro de mierda 😠")

    if message.author.id == pabloId:
        pablo_message_count += 1
        if pablo_message_count >= 20:
            await message.delete()
            await message.channel.send("Un momentillo, un momentillo, un momentillo ☝️")
            pablo_message_count = 0

    if "hola" in message.content.lower():
        if message.guild:
            await message.delete()
            await message.channel.send(
                f"¿De que vas {message.author.mention}?, aquí el unico que saluda soy yo.\n\nSi quieres saludar a alguien, usa el comando `/saluda`"
            )

    else:
        if (
            "jaime" in message.content.lower()
            or f"<@{jaimeId}>" in message.content
            or f"<@!{jaimeId}>" in message.content
            or message.author.id == jaimeId
        ):
            await message.reply(jaimeReactionEmoji)

        if "eran intermedios" in message.content.lower():
            await message.add_reaction(intermediosEmoji)

        if (
            "fernando" in message.content.lower()
            or "alonso" in message.content.lower()
            or "33" in message.content.lower()
            or "adrian newey" in message.content.lower()
        ):
            sticker = await bot.fetch_sticker(alonsoStickerId)
            await message.reply(stickers=[sticker])
        else:
            try:
                if mathparse.parse(message.content) == 33:
                    sticker = await bot.fetch_sticker(alonsoStickerId)
                    await message.reply(stickers=[sticker])
            except Exception:
                pass

    await bot.process_commands(message)


## Event for reacting to the mudae message
@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    if payload.message_id == mudaeSubId:
        guild = bot.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)

        if user is user.bot:
            return

        emoji_str = str(payload.emoji)
        if emoji_str == "✔️":
            rol = discord.utils.get(guild.roles, name=mudaeRol)
            if rol:
                await user.add_roles(rol)
        elif emoji_str == "❌":
            rol = discord.utils.get(guild.roles, name=mudaeRol)
            if rol:
                await user.remove_roles(rol)

    if payload.message_id == storySubscribeId:
        guild = bot.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)

        if user is user.bot:
            return

        emoji_str = str(payload.emoji)
        rol = guild.get_role(storyRolId)

        if rol:
            if emoji_str == "✔️":
                await user.add_roles(rol)
            elif emoji_str == "❌":
                await user.remove_roles(rol)


## Event for handling mudaeRol added or removed
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        rol_before = discord.utils.get(before.roles, name=mudaeRol)
        rol_after = discord.utils.get(after.roles, name=mudaeRol)

        if rol_before is None and rol_after is not None:
            channel = bot.get_channel(mudaeChannelId)
            message = await channel.fetch_message(mudaeEditId)
            await message.edit(
                content=f"> Actualmente hay **{len([member for member in after.guild.members if discord.utils.get(member.roles, name=mudaeRol)])}** usuarios con el rol."
            )

        elif rol_before is not None and rol_after is None:
            channel = bot.get_channel(mudaeChannelId)
            message = await channel.fetch_message(mudaeEditId)
            await message.edit(
                content=f"> Actualmente hay **{len([member for member in after.guild.members if discord.utils.get(member.roles, name=mudaeRol)])}** usuarios con el rol."
            )

        story_rol_before = discord.utils.get(before.roles, id=storyRolId)
        story_rol_after = discord.utils.get(after.roles, id=storyRolId)

        if story_rol_before != story_rol_after:
            channel = bot.get_channel(storyChannelId)
            if channel and storyEditId:
                try:
                    message = await channel.fetch_message(storyEditId)
                    count = len(
                        [
                            member
                            for member in after.guild.members
                            if discord.utils.get(member.roles, id=storyRolId)
                        ]
                    )
                    await message.edit(
                        content=f"> Actualmente hay **{count}** guías de Glob"
                    )
                except Exception as e:
                    logging.error(f"Error updating story message: {e}")


# Handling command
## Command to get the help message
@bot.hybrid_command(name="ayuda", description="🆘 Muestra un mensaje de ayuda")
async def ayuda(ctx: commands.Context):
    help_message = f"""Ahora mismo no hago mucho, pero iré aprendiendo.

Hay 2 formas de interactuar conmigo:
1. **Comandos de barra**: Usa `/` seguido del comando.
2. **Comandos de prefijo**: Usa `!` seguido del comando.

Puedes usar los siguientes comandos:
- **ayuda**: Muestra este mensaje de ayuda.
- **saluda**: Saluda en general.
- **saluda @usuario**: Saluda a un usuario del servidor.
- **asigna**: Te asigna el rol *{mudaeRol}*.
- **quita**: Te quita el rol *{mudaeRol}*.
- **encuesta "pregunta"**: Crea una encuesta de sí o no con la pregunta proporcionada.
- **bingbong**: 🕰️ Bing Bong 🕰️

También tengo eventos que se activan automáticamente pero tendréis que descubrirlos."""
    await ctx.send(help_message)


## Command to greet a user or in general
@bot.hybrid_command(
    name="saluda", description="👋 Saluda a otro usuario del servidor o en general"
)
async def saluda(ctx: commands.Context, usuario: discord.Member = None):
    if usuario is None:
        message = f"👋 {ctx.author.mention} quiere saludar al servidor en general 👋"
    else:
        message = (
            f"{ctx.author.mention} te quiere saludar solo a tí {usuario.mention} 🫵👋"
        )

    await ctx.send(message)


## Command to assign the mudae role
@bot.hybrid_command(name="asigna", description=f"🔧 Te asigna el rol {mudaeRol}")
async def asigna(ctx):
    rol = discord.utils.get(ctx.guild.roles, name=mudaeRol)
    if rol:
        await ctx.author.add_roles(rol)
        await ctx.send(f"Rol **{mudaeRol}** asignado a {ctx.author.mention} 🕴️")
    else:
        await ctx.send(f"El rol **{mudaeRol}** no existe en este servidor 🕴️")


## Command to remove the mudae role
@bot.hybrid_command(name="quita", description=f"🔧 Te quita el rol {mudaeRol}")
async def quita(ctx):
    rol = discord.utils.get(ctx.guild.roles, name=mudaeRol)
    if rol:
        await ctx.author.remove_roles(rol)
        await ctx.send(f"Rol **{mudaeRol}** quitado a {ctx.author.mention} 🕴️")
    else:
        await ctx.send(f"El rol **{mudaeRol}** no existe en este servidor 🕴️")


## Command to make a poll
@bot.hybrid_command(name="encuesta", description="🗳️ Crea una encuesta")
async def encuesta(ctx: commands.Context, *, pregunta: str = None):
    if pregunta is not None:
        embed = discord.Embed(
            title="Encuesta", description=pregunta, color=discord.Color.yellow()
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")
    else:
        await ctx.send("Por favor, proporciona una pregunta para la encuesta 😡")


## Command for Marcos to make a story with votation
@bot.hybrid_command(name="historia", description="📜 Creas una historia interactiva")
@commands.dm_only()
async def historia(ctx: commands.Context, *, text: str = None):
    if ctx.author.id == marcosId:
        if text is not None:
            splitted = text.split("</>")
            if len(splitted) % 2 == 0 and len(splitted) > 3:
                await ctx.send("Marcos tenias 1 tarea .-.")
                await ctx.send(
                    "El formato de la historia debe ser: !historia 'historia' </> ':emoji:' </> 'opcion' </> ':emoji2' </> 'opcion2' ...."
                )
            else:
                messageEmbed = splitted[0] + "\n\n_Votacion:_\n"
                for m in range(1, len(splitted), 2):
                    messageEmbed += (
                        splitted[m].strip() + " -> " + splitted[m + 1].strip() + "\n"
                    )

                embed = discord.Embed(
                    title="Glob",
                    description=messageEmbed,
                    color=discord.Color.orange(),
                )

                channel = bot.get_channel(storyChannelId)
                if channel:
                    message = await channel.send(content=_story_rol_raw, embed=embed)
                    await ctx.send("Enviado facherisimo")
                else:
                    await ctx.send("bro i cant idk why")
                    return

                for e in range(1, len(splitted), 2):
                    await message.add_reaction(splitted[e].strip())

        else:
            await ctx.send(
                "El formato de la historia debe ser: !historia 'historia' </> ':emoji:' </> 'opcion' </> ':emoji2' </> 'opcion2' ...."
            )
    else:
        await ctx.send("Solo puede usar esto Marcos >:(")


@historia.error
async def historia_error(ctx: commands.Context, error):
    if isinstance(error, commands.PrivateMessageOnly):
        await ctx.send(
            "Hermano, esto solo funciona en mensajes privados (DM)", ephemeral=True
        )


## Command to join the voice chat, play one of the .mp3 randomly and disconnect
@bot.hybrid_command(name="bingbong", description="🕰️ Bing Bong 🕰️")
async def bingbong(ctx: commands.Context):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        music_folder = "sounds/bingbong"
        music_files = sorted(
            [f for f in os.listdir(music_folder) if f.endswith(".mp3")]
        )
        selected_song = random.choices(music_files, weights=[99.99, 0.01], k=1)[0]

        while not voice_client.is_connected():
            await asyncio.sleep(0.1)

        voice_client.play(
            discord.FFmpegPCMAudio(os.path.join(music_folder, selected_song))
        )
        await ctx.send("🕰️ Bing Bong 🕰️")

        while voice_client.is_playing():
            await asyncio.sleep(0.1)

        await voice_client.disconnect()
    else:
        await ctx.send("🕰️ Bing Bong 🕰️")


# Run the bot
if __name__ == "__main__":
    if token:
        bot.run(token)
    else:
        logging.critical("Error: DISCORD_TOKEN not found in environment variables.")
        exit(1)
