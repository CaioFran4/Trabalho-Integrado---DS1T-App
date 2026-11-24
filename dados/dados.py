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
            categoria TEXT NOT NULL DEFAULT 'Massa' CHECK(categoria IN ('Massa', 'bebidas', 'igrediente')),
            status TEXT NOT NULL CHECK (status IN ('Disponivel', 'Indisponivel'))
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            motoboy_id INTEGER NOT NULL,
            rua TEXT NOT NULL,
            numero TEXT NOT NULL,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            complemento TEXT,
            status TEXT NOT NULL,
            data_pedido TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    ''')
    
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS historico_recentes AS
        SELECT 
            p.id AS pedido_id,
            p.ticket_id,
            p.motoboy_id,
            p.rua,
            p.numero,
            p.bairro,
            p.cidade,
            p.complemento,
            p.status,
            p.data_pedido,
            pr.nome_prod AS produto,
            hp.quantidade,
            hp.preco_unitario,
            (hp.quantidade * hp.preco_unitario) AS subtotal
        FROM pedidos p
        LEFT JOIN historico_pedidos hp ON p.id = hp.pedido_id
        LEFT JOIN produtos pr ON hp.produto_id = pr.id
        ORDER BY p.data_pedido DESC
    ''')
    
    conexao.commit()
    conexao.close()

def gerar_id_unico(cursor):
    while True:
        novo_id = str(random.randint(10000000, 99999999))
        cursor.execute("SELECT 1 FROM usuario WHERE id_user = ?", (novo_id,))
        if not cursor.fetchone():
            return novo_id


    inicializar_banco()
    
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view')")
    print("Tabelas e Views no banco:", cursor.fetchall())
    print("-" * 40)

    cursor.execute("PRAGMA table_info(produtos)")
    for coluna in cursor.fetchall():
        print(coluna)

    conexao.close()