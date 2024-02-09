import sqlite3

# Conectar a la base de datos SQLite (esto la creará si no existe)
conn = sqlite3.connect('usuarios.db')
c = conn.cursor()

# Crear una tabla
c.execute('''
 CREATE TABLE IF NOT EXISTS transacciones_canceladas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                monto REAL,
                tasa REAL,
                monto_calculado REAL,
                timestamp_mensaje_enviado TIMESTAMP,
                timestamp_mensaje_aceptado TIMESTAMP
            );
''')

# Guardar (confirmar) los cambios y cerrar la conexión a la base de datos
conn.commit()
conn.close()