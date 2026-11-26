import streamlit as st
import sqlite3
import pandas as pd
from dados.sidebar import render_sidebar

st.set_page_config(page_title="Gestão de Produtos", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .prod-img {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border-radius: 12px;
        border: 1px solid #dee2e6;
    }
    .status-badge-disp {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge-indisp {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

IMAGEM_PRODUTO_PADRAO = "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=400"

def cadastrar_produto(nome, descricao, categoria, status, preparo_min, preco, imagem_url):
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO produtos (nome_prod, descricao, categoria, status, preparo_min, preco, imagem_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, descricao, categoria, status, str(preparo_min), float(preco), imagem_url))
    conexao.commit()
    conexao.close()

def atualizar_produto(prod_id, nome, descricao, categoria, status, preparo_min, preco, imagem_url):
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE produtos
        SET nome_prod = ?, descricao = ?, categoria = ?, status = ?, preparo_min = ?, preco = ?, imagem_url = ?
        WHERE id = ?
    """, (nome, descricao, categoria, status, str(preparo_min), float(preco), imagem_url, prod_id))
    conexao.commit()
    conexao.close()

def excluir_produto(prod_id):
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (prod_id,))
    conexao.commit()
    conexao.close()

nome_restaurante, _ = render_sidebar("produtos_crud")

col_titulo, col_novo = st.columns([4, 1], vertical_alignment="center")
with col_titulo:
    st.write(f"## 🍝 Gestão de Produtos — {nome_restaurante}")
with col_novo:
    with st.popover("➕ Novo Produto", use_container_width=True):
        with st.form("form_novo_produto", clear_on_submit=True):
            n_nome = st.text_input("Nome do Produto:")
            n_desc = st.text_area("Descrição:", value="Sem descrição")
            c1, c2 = st.columns(2)
            n_preco = c1.number_input("Preço (R$):", min_value=0.0, step=0.50, format="%.2f")
            n_status = c2.selectbox("Status:", ["Disponivel", "Indisponivel"])
            c3, c4 = st.columns(2)
            n_cat = c3.selectbox("Categoria:", ["Massa", "bebidas", "igrediente"])
            n_prep = c4.number_input("Preparo (min):", min_value=1, value=15, step=1)
            n_img = st.text_input("URL da Imagem (HTTPS):", placeholder="https://...")

            if st.form_submit_button("Cadastrar Produto", type="primary", use_container_width=True):
                if n_nome.strip():
                    cadastrar_produto(n_nome.strip(), n_desc.strip(), n_cat, n_status, n_prep, n_preco, n_img.strip())
                    st.rerun()
                else:
                    st.warning("Informe o nome do produto.")

st.write("")

col_busca, col_status = st.columns([3, 1])
busca_nome = col_busca.text_input("🔍 Buscar produto:", placeholder="Digite o nome do prato ou bebida...")
filtro_status = col_status.selectbox("📌 Filtrar status:", ["Todos", "Disponivel", "Indisponivel"])

st.write("")

conexao = sqlite3.connect('banco.db')
df_produtos = pd.read_sql_query("""
    SELECT id, nome_prod, descricao, categoria, status, preparo_min, preco, imagem_url
    FROM produtos
    ORDER BY id DESC
""", conexao)
conexao.close()

if busca_nome.strip():
    df_produtos = df_produtos[df_produtos["nome_prod"].str.contains(busca_nome.strip(), case=False, na=False)]

if filtro_status != "Todos":
    df_produtos = df_produtos[df_produtos["status"] == filtro_status]

if not df_produtos.empty:
    cols = st.columns(3)
    for idx, row in df_produtos.reset_index(drop=True).iterrows():
        col_atual = cols[idx % 3]
        prod_id = int(row["id"])
        img_url = str(row["imagem_url"]).strip() if row["imagem_url"] else ""
        if not img_url.startswith("http"):
            img_url = IMAGEM_PRODUTO_PADRAO

        preco_val = float(row["preco"]) if row["preco"] is not None else 0.0
        preco_fmt = f"R$ {preco_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        status_atual = str(row["status"])
        badge_class = "status-badge-disp" if status_atual == "Disponivel" else "status-badge-indisp"

        with col_atual:
            with st.container(border=True):
                c_img, c_info = st.columns([1, 2], vertical_alignment="center")
                with c_img:
                    st.markdown(f'<img src="{img_url}" class="prod-img">', unsafe_allow_html=True)
                with c_info:
                    st.markdown(f"<span class='{badge_class}'>{status_atual}</span>", unsafe_allow_html=True)
                    st.markdown(f"#### {row['nome_prod']}")
                    st.markdown(f"**{preco_fmt}** · ⏱️ {row['preparo_min']} min")

                st.caption(row["descricao"])

                with st.popover("✏️ Editar", use_container_width=True):
                    with st.form(f"form_edit_{prod_id}"):
                        ed_nome = st.text_input("Nome:", value=row["nome_prod"])
                        ed_desc = st.text_area("Descrição:", value=row["descricao"])
                        e1, e2 = st.columns(2)
                        ed_preco = e1.number_input("Preço (R$):", min_value=0.0, value=preco_val, step=0.50, format="%.2f")
                        ed_status = e2.selectbox(
                            "Status:",
                            ["Disponivel", "Indisponivel"],
                            index=0 if status_atual == "Disponivel" else 1
                        )
                        e3, e4 = st.columns(2)
                        categorias = ["Massa", "bebidas", "igrediente"]
                        idx_cat = categorias.index(row["categoria"]) if row["categoria"] in categorias else 0
                        ed_cat = e3.selectbox("Categoria:", categorias, index=idx_cat)
                        try:
                            prep_int = int(float(row["preparo_min"]))
                        except (ValueError, TypeError):
                            prep_int = 15
                        ed_prep = e4.number_input("Preparo (min):", min_value=1, value=prep_int, step=1)
                        ed_img = st.text_input("Imagem (HTTPS):", value=str(row["imagem_url"] or ""))

                        c_btn1, c_btn2 = st.columns(2)
                        if c_btn1.form_submit_button("Salvar", type="primary", use_container_width=True):
                            if ed_nome.strip():
                                atualizar_produto(
                                    prod_id,
                                    ed_nome.strip(),
                                    ed_desc.strip(),
                                    ed_cat,
                                    ed_status,
                                    ed_prep,
                                    ed_preco,
                                    ed_img.strip()
                                )
                                st.rerun()
                            else:
                                st.warning("O nome não pode ficar vazio.")
                        if c_btn2.form_submit_button("Excluir", use_container_width=True):
                            excluir_produto(prod_id)
                            st.rerun()
else:
    st.info("Nenhum produto encontrado. Clique em '➕ Novo Produto' para cadastrar.")