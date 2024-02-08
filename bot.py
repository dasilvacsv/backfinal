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
async def historial(ctx):
    # Conectarse a la base de datos y recuperar los registros de transacciones
    async with aiosqlite.connect('usuarios.db') as db:
        cursor = await db.execute('''
            SELECT fecha, operacion, cantidad, valor_anterior, nuevo_valor 
            FROM transacciones_canales_logs 
            WHERE channel_id = ? 
            ORDER BY fecha DESC 
            LIMIT 10
        ''', (str(ctx.channel.id),))
        rows = await cursor.fetchall()

    # Encabezados de la tabla
    headers = ["Fecha", "Operación", "Cantidad", "Valor Anterior", "Valor Nuevo", "Saldo Final"]

    # Datos de la tabla
    data = []
    for row in rows:
        # Parsear la fecha a un formato legible
        fecha = row[0]  # Asumiendo que la columna timestamp es la primera
        operacion = row[1]
        cantidad = f"{row[2]:,.2f} Bs."
        valor_anterior = f"{row[3]:,.2f} Bs."
        nuevo_valor = f"{row[4]:,.2f} Bs."
        saldo_final = f"{row[4]:,.2f} Bs."  # El saldo final es el nuevo_valor
        
        # Agregar la fila a los datos
        data.append([fecha, operacion, cantidad, valor_anterior, nuevo_valor, saldo_final])

    # Convertir los datos a una tabla ASCII
    tabla = "```"  # Usar triple comillas para formato de código en Discord
    tabla += "\n".join(["\t".join(headers)] + ["\t".join(map(str, row)) for row in data])
    tabla += "```"

    # Enviar el mensaje al canal de Discord
    await ctx.send(tabla)

@bot.event
async def on_message(message):
    # Ignorar mensajes del propio bot para evitar bucles infinitos
    if message.author == bot.user:
        return

    # Comprobar si el mensaje comienza con '+' o '-' seguido de dígitos
    if message.content.startswith(('+', '-')) and message.content[1:].isdigit():
        operacion = message.content[0]  # Captura '+' o '-'
        cantidad = int(message.content[1:])  # Captura el número después del signo

        # Llama a una función que maneja la actualización, pasando el contexto, la operación y la cantidad
        await actualizar_valor(message, operacion, cantidad)

    # Esto permite que los comandos normales del bot funcionen
    await bot.process_commands(message)

async def actualizar_valor(message, operacion, cantidad):
    channel_id = str(message.channel.id)

    async with aiosqlite.connect('usuarios.db') as db:
        cursor = await db.execute('SELECT valor FROM canales WHERE id = ?', (channel_id,))
        row = await cursor.fetchone()
        valor_anterior = 0 if row is None else row[0]

        # Determinar la nueva operación basada en el signo de la cantidad
        if operacion == '+':
            nuevo_valor = valor_anterior + cantidad  # Sumar la cantidad
        elif operacion == '-':
            nuevo_valor = valor_anterior - cantidad  # Restar la cantidad

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

        # Enviar el mensaje de confirmación al canal
        await message.channel.send(f'Valor del canal actualizado de {valor_anterior} a {nuevo_valor} ({operacion}{cantidad})')

@bot.command()
async def reiniciar(ctx):

    channel_id = str(ctx.channel.id)

    async with aiosqlite.connect('usuarios.db') as db:
        # Obtener el valor actual del canal
        cursor = await db.execute('SELECT valor FROM canales WHERE id = ?', (channel_id,))
        row = await cursor.fetchone()
        valor_anterior = 0 if row is None else row[0]

        # Reiniciar el valor del canal a 0
        if row:
            await db.execute('UPDATE canales SET valor = 0 WHERE id = ?', (channel_id,))
        else:
            # Si no hay un registro previo, insertar uno con valor 0
            await db.execute('INSERT INTO canales (id, valor) VALUES (?, 0)', (channel_id,))

        # Registrar la operación de reinicio en transacciones_canales_logs
        # En este registro, "cantidad" reflejará el valor anterior antes del reinicio
        await db.execute('''
            INSERT INTO transacciones_canales_logs (channel_id, operacion, cantidad, valor_anterior, nuevo_valor)
            VALUES (?, 'reiniciar', ?, ?, 0)
        ''', (channel_id, valor_anterior, valor_anterior))

        await db.commit()

    # Enviar confirmación al canal
    await ctx.send(f"El valor del canal ha sido reiniciado de {valor_anterior} a 0 y la acción ha sido registrada.")

bot.run(token)
