import discord
import asyncio
import os
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
MINUTOS = 5

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
timers: dict[int, asyncio.Task] = {}

async def recordar(canal, usuario, mensaje_id):
    await asyncio.sleep(MINUTOS * 60)
    try:
        await canal.send(f"⏰ {usuario.mention} Han pasado **{MINUTOS} minutos** desde que pusiste **ww**. ¡Ya puedes volver! 👋")
    except discord.Forbidden:
        pass
    timers.pop(usuario.id, None)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    palabras = message.content.strip().lower().split()
    if "ww" in palabras:
        usuario = message.author
        canal = message.channel
        if usuario.id in timers:
            timers[usuario.id].cancel()
            await canal.send(f"🔄 {usuario.mention} Reiniciando tu timer a {MINUTOS} minutos.")
        else:
            await canal.send(f"✅ {usuario.mention} Te avisaré en **{MINUTOS} minutos**. ¡Descansa!")
        timers[usuario.id] = asyncio.create_task(recordar(canal, usuario, message.id))
    await bot.process_commands(message)

@bot.command(name="cancelww")
async def cancelar_ww(ctx):
    if ctx.author.id in timers:
        timers[ctx.author.id].cancel()
        timers.pop(ctx.author.id)
        await ctx.send(f"❌ {ctx.author.mention} Timer cancelado.")
    else:
        await ctx.send(f"{ctx.author.mention} No tienes ningún timer activo.")

bot.run(TOKEN)
