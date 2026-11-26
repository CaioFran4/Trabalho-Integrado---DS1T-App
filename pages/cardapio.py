import streamlit as st
import sqlite3
import pandas as pd
from dados.sidebar import render_sidebar

st.set_page_config(page_title="Cardápio", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .prato-card-img {
        width: 100%;
        height: 170px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    .preco-destaque {
        font-size: 1.25rem;
        font-weight: 800;
        color: #16a34a;
    }
    .badge-disp {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-esgotado {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

IMAGEM_FALLBACK = "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=600"

nome_restaurante, _ = render_sidebar("cardapio")

if "carrinho_cardapio" not in st.session_state:
    st.session_state.carrinho_cardapio = {}

st.write(f"## 🍽️ Cardápio — {nome_restaurante}")
st.write("")

col_busca, col_cat, col_disp = st.columns([2.5, 1.5, 1.2])
busca_prato = col_busca.text_input("🔍 Buscar prato:", placeholder="Ex: Carbonara, Lasanha, Suco...")
filtro_cat = col_cat.selectbox("📂 Categoria:", ["Todas", "Massa", "bebidas", "igrediente"])
apenas_disp = col_disp.checkbox("Apenas disponíveis", value=False)

conexao = sqlite3.connect('banco.db')
df_pratos = pd.read_sql_query("""
    SELECT id, nome_prod, descricao, categoria, status, preparo_min, preco, imagem_url
    FROM produtos
    ORDER BY 
        CASE status WHEN 'Disponivel' THEN 0 ELSE 1 END,
        categoria ASC,
        nome_prod ASC
""", conexao)
conexao.close()

if busca_prato.strip():
    termo = busca_prato.strip()
    df_pratos = df_pratos[
        df_pratos["nome_prod"].str.contains(termo, case=False, na=False) |
        df_pratos["descricao"].str.contains(termo, case=False, na=False)
    ]

if filtro_cat != "Todas":
    df_pratos = df_pratos[df_pratos["categoria"].str.lower() == filtro_cat.lower()]

if apenas_disp:
    df_pratos = df_pratos[df_pratos["status"] == "Disponivel"]

col_lista, col_comanda = st.columns([3, 1.2], gap="large")

with col_lista:
    if not df_pratos.empty:
        cols = st.columns(3)
        for idx, row in df_pratos.reset_index(drop=True).iterrows():
            col_atual = cols[idx % 3]
            pid = int(row["id"])
            disponivel = row["status"] == "Disponivel"
            preco = float(row["preco"] or 0.0)
            preco_fmt = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            img_url = str(row["imagem_url"]).strip() if row["imagem_url"] else ""
            if not img_url.startswith("http"):
                img_url = IMAGEM_FALLBACK

            with col_atual:
                with st.container(border=True):
                    st.markdown(f'<img src="{img_url}" class="prato-card-img">', unsafe_allow_html=True)
                    badge_html = '<span class="badge-disp">Disponível</span>' if disponivel else '<span class="badge-esgotado">Indisponível</span>'
                    st.markdown(f"{badge_html} &nbsp; <small>⏱️ {row['preparo_min']} min</small>", unsafe_allow_html=True)
                    st.markdown(f"#### {row['nome_prod']}")
                    st.caption(row["descricao"])
                    st.markdown(f'<p class="preco-destaque">{preco_fmt}</p>', unsafe_allow_html=True)

                    if st.button(
                        "➕ Adicionar ao Pedido",
                        key=f"add_card_{pid}",
                        disabled=not disponivel,
                        use_container_width=True
                    ):
                        atual = st.session_state.carrinho_cardapio.get(pid, {
                            "nome": row["nome_prod"],
                            "preco": preco,
                            "qtd": 0
                        })
                        atual["qtd"] += 1
                        st.session_state.carrinho_cardapio[pid] = atual
                        st.rerun()
    else:
        st.info("Nenhum prato encontrado no cardápio para os filtros selecionados.")

with col_comanda:
    with st.container(border=True):
        st.markdown("### 🛒 Novo Pedido Rápido")
        carrinho = st.session_state.carrinho_cardapio

        if carrinho:
            total_pedido = 0.0
            for pid, item in list(carrinho.items()):
                sub = item["preco"] * item["qtd"]
                total_pedido += sub
                c_i, c_q, c_r = st.columns([2.5, 1, 0.8], vertical_alignment="center")
                c_i.write(f"**{item['nome']}**")
                c_q.write(f"{item['qtd']}x")
                if c_r.button("🗑️", key=f"rem_{pid}"):
                    del st.session_state.carrinho_cardapio[pid]
                    st.rerun()

            st.divider()
            total_fmt = f"R$ {total_pedido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f"#### Total: {total_fmt}")

            with st.form("form_fechar_pedido_cardapio"):
                cli_nome = st.text_input("Nome do Cliente:", value="Cliente Balcão")
                cli_rua = st.text_input("Rua:", value="Av. Principal")
                c_n, c_b = st.columns(2)
                cli_num = c_n.text_input("Número:", value="100")
                cli_bairro = c_b.text_input("Bairro:", value="Centro")
                cli_cidade = st.text_input("Cidade:", value="Jandira")
                cli_comp = st.text_input("Complemento:", placeholder="Opcional")

                if st.form_submit_button("✅ Finalizar e Gerar Ticket", type="primary", use_container_width=True):
                    conn = sqlite3.connect('banco.db')
                    cur = conn.cursor()

                    cur.execute("INSERT INTO tickets (status_pagamento) VALUES ('aprovado')")
                    ticket_id = cur.lastrowid

                    cur.execute("SELECT id FROM cadastro_motoboys WHERE disponivel = 1 LIMIT 1")
                    moto_row = cur.fetchone()
                    if not moto_row:
                        cur.execute("SELECT id FROM cadastro_motoboys LIMIT 1")
                        moto_row = cur.fetchone()
                    motoboy_id = moto_row[0] if moto_row else 1

                    cur.execute("""
                        INSERT INTO pedidos (ticket_id, motoboy_id, rua, numero, bairro, cidade, complemento, status, nome_cliente)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendente', ?)
                    """, (ticket_id, motoboy_id, cli_rua, cli_num, cli_bairro, cli_cidade, cli_comp, cli_nome))
                    pedido_id = cur.lastrowid

                    for pid, item in carrinho.items():
                        cur.execute("""
                            INSERT INTO historico_pedidos (pedido_id, produto_id, quantidade, preco_unitario)
                            VALUES (?, ?, ?, ?)
                        """, (pedido_id, pid, item["qtd"], item["preco"]))

                    conn.commit()
                    conn.close()
                    st.session_state.carrinho_cardapio = {}
                    st.success(f"Pedido #{pedido_id} registrado!")
                    st.rerun()
        else:
            st.caption("Selecione pratos ao lado para montar um pedido e gerar ticket automaticamente.")