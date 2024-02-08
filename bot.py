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
# Inicia el bot
bot.run(token)
