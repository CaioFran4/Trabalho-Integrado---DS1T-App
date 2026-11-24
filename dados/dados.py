import sqlite3
import random

def conectar():
    return sqlite3.connect('banco.db')

def inicializar_banco():
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user TEXT NOT NULL UNIQUE DEFAULT '12345678',
            senha TEXT NOT NULL DEFAULT '123'
        )
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO usuario (id_user, senha)
        VALUES ('12345678', '123')
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_prod TEXT NOT NULL,
            descricao TEXT NOT NULL DEFAULT 'Sem descrição',
            categoria TEXT NOT NULL DEFAULT 'Massa' CHECK(categoria IN ('Massa', 'bebidas', 'igrediente'))
        )
    ''')
    
    conexao.commit()
    conexao.close()

def gerar_id_unico(cursor):
    while True:
        novo_id = str(random.randint(10000000, 99999999))
        cursor.execute("SELECT 1 FROM usuario WHERE id_user = ?", (novo_id,))
        if not cursor.fetchone():
            return novo_id

if __name__ == "__main__":
    inicializar_banco()