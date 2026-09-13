import discord
import asyncio
import os
from discord.ext import commands

# ──────────────────────────────────────────────
#  Configuración
# ──────────────────────────────────────────────
TOKEN = "MTUyMDUzOTAzNTQ4MTgwNTAyMA.Gx5knJ.dftmbBS3qoDzsJyKVi1ncXCkRQuluyO5HAt14U" # pon tu token aquí o en la variable de entorno
MINUTOS = 5                          # tiempo antes del recordatorio

# ──────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True       # necesario para leer el contenido de mensajes

bot = commands.Bot(command_prefix="!", intents=intents)

# Guarda los timers activos: {user_id: asyncio.Task}
timers: dict[int, asyncio.Task] = {}


async def recordar(canal: discord.TextChannel, usuario: discord.Member, mensaje_id: int):
    """Espera MINUTOS minutos y luego menciona al usuario."""
    await asyncio.sleep(MINUTOS * 60)

    # Comprueba que el canal siga existible y el usuario también
    try:
        await canal.send(
            f"⏰ {usuario.mention} Han pasado **{MINUTOS} minutos** desde que pusiste **ww**. "
            f"¡Ya puedes volver! 👋"
        )
    except discord.Forbidden:
        pass  # sin permisos para escribir en ese canal

    # Limpia el timer
    timers.pop(usuario.id, None)


@bot.event
async def on_ready():
    print(f"✅  Bot conectado como {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    # Ignora mensajes del propio bot
    if message.author.bot:
        return

    # Detecta "ww" como palabra completa (insensible a mayúsculas)
    contenido = message.content.strip().lower()
    palabras = contenido.split()

    if "ww" in palabras:
        usuario = message.author
        canal   = message.channel

        # Si ya hay un timer corriendo para este usuario, cancélalo y reinicia
        if usuario.id in timers:
            timers[usuario.id].cancel()
            await canal.send(
                f"🔄 {usuario.mention} Reiniciando tu timer de **ww** a {MINUTOS} minutos."
            )
        else:
            await canal.send(
                f"✅ {usuario.mention} Te avisaré en **{MINUTOS} minutos**. ¡Descansa!"
            )

        # Lanza el timer como tarea asíncrona
        task = asyncio.create_task(
            recordar(canal, usuario, message.id)
        )
        timers[usuario.id] = task

    # Permite que los comandos con prefijo también funcionen
    await bot.process_commands(message)


# ── Comando opcional: cancelar el timer manualmente ──
@bot.command(name="cancelww")
async def cancelar_ww(ctx: commands.Context):
    """Cancela tu timer de ww activo."""
    if ctx.author.id in timers:
        timers[ctx.author.id].cancel()
        timers.pop(ctx.author.id)
        await ctx.send(f"❌ {ctx.author.mention} Timer de **ww** cancelado.")
    else:
        await ctx.send(f"{ctx.author.mention} No tienes ningún timer activo.")


if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("Falta el token. Pon DISCORD_TOKEN como variable de entorno.")
    bot.run(TOKEN)
