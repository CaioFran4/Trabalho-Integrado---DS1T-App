import sqlite3
from datetime import datetime, timedelta

def popular_banco_teste():
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()

    # 1. Produtos (Massa, bebidas, igrediente + status + preparo_min)
    produtos_teste = [
        ("Spaghetti Carbonara", "Massa artesanal com bacon e molho cremoso", "Massa", "Disponivel", "20"),
        ("Lasanha Bolonhesa", "Camadas de massa fresca com carne moída e queijo", "Massa", "Disponivel", "30"),
        ("Fettuccine Alfredo", "Massa ao molho branco de parmesão", "Massa", "Indisponivel", "18"),
        ("Refrigerante Lata 350ml", "Coca-Cola ou Guaraná gelado", "bebidas", "Disponivel", "2"),
        ("Suco Natural de Laranja", "500ml feito na hora", "bebidas", "Disponivel", "5"),
        ("Queijo Parmesão Extra", "Porção adicional de 50g", "igrediente", "Disponivel", "1")
    ]
    cursor.executemany("""
        INSERT INTO produtos (nome_prod, descricao, categoria, status, preparo_min)
        VALUES (?, ?, ?, ?, ?)
    """, produtos_teste)

    # 2. Motoboys
    motoboys_teste = [
        ("Carlos Silva", "(11) 98888-1111", "ABC1D23", "carlos.png"),
        ("Marcos Oliveira", "(11) 97777-2222", "XYZ9K88", "marcos.png"),
        ("Rafael Santos", "(11) 96666-3333", "JKL4M56", "rafael.png")
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO cadastro_motoboys (nome_motoboy, telefone, placa, foto)
        VALUES (?, ?, ?, ?)
    """, motoboys_teste)

    # 3. Tickets (gera 5 códigos hexadecimais automáticos)
    for _ in range(5):
        cursor.execute("INSERT INTO tickets DEFAULT VALUES")

    # 4. Pedidos de Hoje (horários variados para testar o gráfico oscilante)
    hoje = datetime.now()
    horarios = [
        hoje.replace(hour=11, minute=15).strftime("%Y-%m-%d %H:%M:%S"),
        hoje.replace(hour=12, minute=30).strftime("%Y-%m-%d %H:%M:%S"),
        hoje.replace(hour=13, minute=45).strftime("%Y-%m-%d %H:%M:%S"),
        hoje.replace(hour=19, minute=10).strftime("%Y-%m-%d %H:%M:%S"),
        hoje.replace(hour=20, minute=40).strftime("%Y-%m-%d %H:%M:%S")
    ]

    pedidos_teste = [
        (1, 1, "Av. Brigadeiro", "100", "Centro", "Barueri", "Apto 12", "Entregue", horarios[0]),
        (2, 2, "Rua das Flores", "45", "Jardim Silveira", "Barueri", "", "Entregue", horarios[1]),
        (3, 1, "Rua São Paulo", "890", "Alphaville", "Barueri", "Bloco B", "Em rota", horarios[2]),
        (4, 3, "Av. Paulista", "320", "Aldeia", "Barueri", "Casa 2", "Pendente", horarios[3]),
        (5, 2, "Rua Rio Branco", "55", "Boa Vista", "Barueri", "", "Entregue", horarios[4])
    ]
    cursor.executemany("""
        INSERT INTO pedidos (ticket_id, motoboy_id, rua, numero, bairro, cidade, complemento, status, data_pedido)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, pedidos_teste)

    # 5. Histórico de Itens dos Pedidos (para calcular faturamento e gráfico)
    itens_teste = [
        (1, 1, 2, 45.00),  # Pedido 1: 2x Carbonara = R$ 90,00 (11h)
        (1, 4, 2, 7.00),   # Pedido 1: 2x Refri = R$ 14,00
        (2, 2, 3, 52.00),  # Pedido 2: 3x Lasanha = R$ 156,00 (12h)
        (3, 1, 1, 45.00),  # Pedido 3: 1x Carbonara = R$ 45,00 (13h)
        (4, 2, 4, 52.00),  # Pedido 4: 4x Lasanha = R$ 208,00 (19h)
        (5, 1, 2, 45.00),  # Pedido 5: 2x Carbonara = R$ 90,00 (20h)
        (5, 5, 2, 12.00)   # Pedido 5: 2x Suco = R$ 24,00
    ]
    cursor.executemany("""
        INSERT INTO historico_pedidos (pedido_id, produto_id, quantidade, preco_unitario)
        VALUES (?, ?, ?, ?)
    """, itens_teste)

    # 6. Registro de Lucro de Teste
    cursor.execute("""
        INSERT INTO lucro (faturamento_bruto, despesas)
        VALUES (627.00, 210.50)
    """)

    conexao.commit()
    conexao.close()
    print("✅ Dados de teste inseridos com sucesso no banco.db!")

if __name__ == "__main__":
    popular_banco_teste()