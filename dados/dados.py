import sqlite3

conexao = sqlite3.connect('banco.db')
cursor = conexao.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_user TEXT NOT NULL,
        senha TEXT NOT NULL
    )
''')

conexao.commit()
conexao.close()