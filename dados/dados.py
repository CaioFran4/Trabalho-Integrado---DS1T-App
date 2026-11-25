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
            categoria TEXT NOT NULL DEFAULT 'Massa' CHECK(categoria IN ('Massa', 'bebidas', 'ingrediente')),
            status TEXT NOT NULL DEFAULT 'Disponivel' CHECK (status IN ('Disponivel', 'Indisponivel')),
            preparo_min TEXT NOT NULL DEFAULT '15'
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
            status TEXT NOT NULL DEFAULT 'Em entrega' CHECK(status IN ('Entregue', 'Em entrega', 'Cancelado')),
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL DEFAULT (lower(hex(randomblob(4)))),
            data_emissao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastro_motoboys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_motoboy TEXT NOT NULL,
            telefone TEXT NOT NULL,
            placa TEXT NOT NULL UNIQUE,
            foto TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lucro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,    
            faturamento_bruto REAL NOT NULL,
            despesas REAL NOT NULL,
            lucro_liquido REAL GENERATED ALWAYS AS (faturamento_bruto - despesas) STORED,
            data_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            nome_restaurante TEXT NOT NULL DEFAULT 'La Pasta',
            logo_url TEXT DEFAULT ''
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO configuracoes (id, nome_restaurante)
        VALUES (1, 'La Pasta')
    ''')

    cursor.execute("PRAGMA table_info(configuracoes)")
    colunas_config = [col[1] for col in cursor.fetchall()]
    if "logo_url" not in colunas_config:
        cursor.execute("ALTER TABLE configuracoes ADD COLUMN logo_url TEXT DEFAULT ''")

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
    
    conexao = conectar()
    cursor = conexao.cursor()

    print("--- COLUNAS DE CONFIGURACOES ---")
    cursor.execute("PRAGMA table_info(configuracoes)")
    for col in cursor.fetchall():
        print(col)

    print("\n--- DADOS DE CONFIGURACOES ---")
    cursor.execute("SELECT * FROM configuracoes")
    print(cursor.fetchall())

    conexao.close()