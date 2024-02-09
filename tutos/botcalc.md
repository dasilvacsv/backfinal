# crear la base de datos sql
import sqlite3

# Conectar a la base de datos SQLite (esto la creará si no existe)
conn = sqlite3.connect('usuarios.db')
c = conn.cursor()

# Crear una tabla
c.execute('''CREATE TABLE IF NOT EXISTS usuarios
             (id_discord TEXT PRIMARY KEY, valor INTEGER)''')

# Guardar (confirmar) los cambios y cerrar la conexión a la base de datos
conn.commit()
conn.close()

# crear reinicio canal 
@bot.command()
async def reiniciar(ctx):
    channel_id = str(ctx.channel.id)

    async with aiosqlite.connect('usuarios.db') as db:
        # Verificar primero si el canal ya tiene un registro en la base de datos
        cursor = await db.execute('SELECT valor FROM canales WHERE id = ?', (channel_id,))
        row = await cursor.fetchone()

        # Si el canal ya tiene un registro, actualizarlo
        if row:
            await db.execute('UPDATE canales SET valor = 0 WHERE id = ?', (channel_id,))
            mensaje = "El valor del canal ha sido reiniciado a 0."
        else:
            # Si el canal no tiene un registro, crear uno y establecer el valor en 0
            await db.execute('INSERT INTO canales (id, valor) VALUES (?, 0)', (channel_id,))
            mensaje = "El canal no tenía un valor previo, pero ahora se ha inicializado a 0."

        await db.commit()

    await ctx.send(mensaje)


# prototipo 1
un valor que ingresa directamente al colocarse la tasa

# prototipo 2
un embed que dice el cálculo de cuanto representa eso en fiat

# crear la funcionalidad
funcionalidad de botones de pagado, cancelado tabla, 
valor 1 x valor 2 
embed con el resultado


# funcionalidad 1 bases de datos
Canales: Para almacenar configuraciones específicas del canal, como los países y las tasas de cambio asociadas.

sql
Copy code
CREATE TABLE IF NOT EXISTS canales_config (
    channel_id TEXT PRIMARY KEY,
    pais1 TEXT,
    pais2 TEXT,
    pais1_value REAL,
    pais2_value REAL
);
Transacciones Realizadas: Para almacenar transacciones que han sido marcadas como pagadas.

sql
Copy code
CREATE TABLE IF NOT EXISTS transacciones_realizadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT,
    monto REAL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Transacciones Canceladas: Para almacenar transacciones que han sido canceladas.

sql
Copy code
CREATE TABLE IF NOT EXISTS transacciones_canceladas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT,
    monto REAL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# comandos para configurar canales
@bot.command()
async def set_pais1(ctx, pais: str):
    channel_id = str(ctx.channel.id)

    async with aiosqlite.connect('usuarios.db') as db:
        await db.execute('''
            INSERT INTO canales_config (channel_id, pais1) VALUES (?, ?)
            ON CONFLICT(channel_id) DO UPDATE SET pais1 = excluded.pais1
        ''', (channel_id, pais))
        await db.commit()

    await ctx.send(f'País 1 configurado a {pais} para este canal.')

Comando para configurar los paises y variables de la base de datos

!set_pais1 value_text
!set_pais2

!sp1 set pais name
!spv1 seet pais value

this are the variables to calculate the fiat 

