import discord
from discord.ext import commands
import aiosqlite
import os
from dotenv import load_dotenv
from datetime import datetime

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
async def sp1(ctx, pais: str):
    channel_id = str(ctx.channel.id)

    async with aiosqlite.connect('usuarios.db') as db:
        await db.execute('''
            INSERT INTO canales_config (channel_id, pais1) VALUES (?, ?)
            ON CONFLICT(channel_id) DO UPDATE SET pais1 = excluded.pais1
        ''', (channel_id, pais))
        await db.commit()

    await ctx.send(f'País 1 configurado a {pais} para este canal.')

@bot.command()
async def sp2(ctx, pais: str):
    channel_id = str(ctx.channel.id)

    async with aiosqlite.connect('usuarios.db') as db:
        await db.execute('''
            INSERT INTO canales_config (channel_id, pais2) VALUES (?, ?)
            ON CONFLICT(channel_id) DO UPDATE SET pais2 = excluded.pais2
        ''', (channel_id, pais))
        await db.commit()

    await ctx.send(f'País 2 configurado a {pais} para este canal.')

@bot.command()
async def spv1(ctx, valor: float):
    channel_id = str(ctx.channel.id)

    # Conectar a la base de datos y actualizar/insertar el valor de pais1_value para este canal
    async with aiosqlite.connect('usuarios.db') as db:
        # Intentar actualizar el valor de pais1_value para el canal existente
        cursor = await db.execute('UPDATE canales_config SET pais1_value = ? WHERE channel_id = ?', (valor, channel_id))
        
        # Si el canal no estaba previamente configurado, insertar una nueva fila con el valor de pais1_value
        if cursor.rowcount == 0:
            await db.execute('INSERT INTO canales_config (channel_id, pais1_value) VALUES (?, ?)', (channel_id, valor))
        
        await db.commit()

    await ctx.send(f'Valor para pais1 configurado a {valor} en este canal.')

@bot.command()
async def spv2(ctx, valor: float):
    channel_id = str(ctx.channel.id)

    # Conectar a la base de datos y actualizar/insertar el valor de pais1_value para este canal
    async with aiosqlite.connect('usuarios.db') as db:
        # Intentar actualizar el valor de pais1_value para el canal existente
        cursor = await db.execute('UPDATE canales_config SET pais2_value = ? WHERE channel_id = ?', (valor, channel_id))
        
        # Si el canal no estaba previamente configurado, insertar una nueva fila con el valor de pais1_value
        if cursor.rowcount == 0:
            await db.execute('INSERT INTO canales_config (channel_id, pais2_value) VALUES (?, ?)', (channel_id, valor))
        
        await db.commit()

    await ctx.send(f'Valor para pais2 configurado a {valor} en este canal.')

@bot.command()
async def calcular(ctx, monto: float):
    channel_id = str(ctx.channel.id)

    async with aiosqlite.connect('usuarios.db') as db:
        cursor = await db.execute('SELECT pais1_value, pais2_value FROM canales_config WHERE channel_id = ?', (channel_id,))
        row = await cursor.fetchone()

        if row:
            pais1_value, pais2_value = row
            monto_calculado = monto * pais2_value
            embed = discord.Embed(title="Monto a Pagar", description=f"{monto} * {pais2_value} = {monto_calculado}Bs")
            mensaje = await ctx.send(embed=embed)

            # Añadir reacciones para pagado y cancelado
            await mensaje.add_reaction("✅")  # Emoji de pagado
            await mensaje.add_reaction("❌")  # Emoji de cancelado

            # Aquí necesitarás manejar la lógica para cuando un usuario reacciona a las reacciones
            # Esto podría implicar el uso de un event listener para on_reaction_add

        else:
            await ctx.send("Este canal no está configurado correctamente.")

def obtener_monto_de_embed(embed):
    descripcion = embed.description
    # Asumiendo que la descripción sigue un formato específico, por ejemplo: "{monto} * {tasa} = {precio_bs}Bs"
    partes = descripcion.split(' ')
    monto = float(partes[0])  # El monto es el primer elemento
    tasa = float(partes[2])  # La tasa es el tercer elemento, después del '*'
    return monto, tasa

@bot.event
async def on_reaction_add(reaction, user):
    # Ignorar las propias reacciones del bot
    if user == bot.user or reaction.message.author != bot.user:
        return

    # Verificar que la reacción sea en un mensaje de transacción
    if reaction.message.embeds and "Monto a Pagar" in reaction.message.embeds[0].title:
        channel_id = str(reaction.message.channel.id)
        monto, tasa = obtener_monto_de_embed(reaction.message.embeds[0])
        precio_bs = monto * tasa
        timestamp_mensaje_enviado = reaction.message.created_at
        timestamp_mensaje_aceptado = datetime.utcnow()  # Usar `from datetime import datetime`

        async with aiosqlite.connect('usuarios.db') as db:
            if reaction.emoji == "✅":
                # Transacción realizada
                await db.execute('''INSERT INTO transacciones_realizadas 
                                    (channel_id, monto, tasa, monto_calculado, timestamp_mensaje_enviado, timestamp_mensaje_aceptado) 
                                    VALUES (?, ?, ?, ?, ?, ?)''', 
                                    (channel_id, monto, tasa, precio_bs, timestamp_mensaje_enviado, timestamp_mensaje_aceptado))
                await db.commit()
                await reaction.message.channel.send(f"La transacción fue realizada.\nInformación de transacción:\nCantidad a enviar: {monto}\nTasa: {tasa}\nPrecio en Bs: {precio_bs}")
            elif reaction.emoji == "❌":
                # Transacción no realizada
                await db.execute('''INSERT INTO transacciones_canceladas 
                                    (channel_id, monto, tasa, monto_calculado, timestamp_mensaje_enviado, timestamp_mensaje_aceptado) 
                                    VALUES (?, ?, ?, ?, ?, ?)''', 
                                    (channel_id, monto, tasa, precio_bs, timestamp_mensaje_enviado, timestamp_mensaje_aceptado))
                await db.commit()
                await reaction.message.channel.send(f"La transacción no fue realizada.\nInformación de transacción:\nCantidad a enviar: {monto}\nTasa: {tasa}\nPrecio en Bs: {precio_bs}")

            # Eliminar el mensaje original para evitar múltiples reacciones
            await reaction.message.delete()


bot.run(token)
