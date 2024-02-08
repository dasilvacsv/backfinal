import discord
from discord.ext import commands
import aiosqlite
import os
from dotenv import load_dotenv

# Define los intents que tu bot necesitará.
intents = discord.Intents.default()
intents = discord.Intents().all()

#cargar variables de entorno
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Instancia el bot con los intents.
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def b(ctx, operacion: str, cantidad: int):
    channel_id = str(ctx.channel.id)

    async with aiosqlite.connect('usuarios.db') as db:
        cursor = await db.execute('SELECT valor FROM canales WHERE id = ?', (channel_id,))
        row = await cursor.fetchone()
        valor_anterior = 0 if row is None else row[0]

        # Determinar la operación basada en el signo de la cantidad
        if operacion == '+':
            nuevo_valor = valor_anterior + abs(cantidad)  # Sumar la cantidad absoluta
        elif operacion == '-':
            nuevo_valor = valor_anterior - abs(cantidad)  # Restar la cantidad absoluta
        else:
            await ctx.send('La operación debe ser "+" o "-".')
            return

        # Realizar la actualización o la inserción según corresponda
        if row:
            await db.execute('UPDATE canales SET valor = ? WHERE id = ?', (nuevo_valor, channel_id))
        else:
            await db.execute('INSERT INTO canales (id, valor) VALUES (?, ?)', (channel_id, nuevo_valor))

        # Insertar el log de la transacción para el canal
        operacion_texto = 'sumar' if operacion == '+' else 'restar'
        await db.execute('''
            INSERT INTO transacciones_canales_logs (channel_id, operacion, cantidad, valor_anterior, nuevo_valor) 
            VALUES (?, ?, ?, ?, ?)
        ''', (channel_id, operacion_texto, cantidad, valor_anterior, nuevo_valor))

        await db.commit()

    # Formatear el mensaje para enviar
    signo = "+" if operacion == '+' else "-"
    await ctx.send(f'Valor del canal actualizado de {valor_anterior} a {nuevo_valor} ({signo}{abs(cantidad)})')
    
# Inicia el bot
bot.run(token)
