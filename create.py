import sqlite3

# Conectar a la base de datos SQLite (esto la creará si no existe)
conn = sqlite3.connect('usuarios.db')
c = conn.cursor()

# Crear una tabla
c.execute('''CREATE TABLE IF NOT EXISTS transacciones_canales_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT,
    operacion TEXT,
    cantidad INTEGER,
    valor_anterior INTEGER,
    nuevo_valor INTEGER,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

''')

# Guardar (confirmar) los cambios y cerrar la conexión a la base de datos
conn.commit()
conn.close()