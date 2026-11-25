import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Gestão de Produtos", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
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

IMAGEM_PRODUTO_PADRAO = "https://unsplash.com"

def preparar_tabelas():
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()
    
    for comando in [
        "ALTER TABLE configuracoes ADD COLUMN logo_url TEXT DEFAULT ''",
        "ALTER TABLE produtos ADD COLUMN preco REAL NOT NULL DEFAULT 0.0",
        "ALTER TABLE produtos ADD COLUMN imagem_url TEXT DEFAULT ''"
    ]:
        try:
            cursor.execute(comando)
        except sqlite3.OperationalError:
            pass

    conexao.commit()
    conexao.close()

def obter_configuracoes():
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT nome_restaurante, logo_url FROM configuracoes WHERE id = 1")
    res = cursor.fetchone()
    conexao.close()
    if res:
        return (res[0] if res[0] else "La Pasta"), (res[1] if res[1] else "")
    return "La Pasta", ""

def salvar_configuracoes(novo_nome, nova_logo):
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE configuracoes SET nome_restaurante = ?, logo_url = ? WHERE id = 1",
        (novo_nome, nova_logo)
    )
    conexao.commit()
    conexao.close()

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

preparar_tabelas()
nome_restaurante, logo_atual = obter_configuracoes()

with st.sidebar:
    if logo_atual:
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <img src="{logo_atual}" style="width: 80%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 14px; border: 1px solid #dee2e6;">
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <div style="width: 80%; aspect-ratio: 1 / 1; border-radius: 14px; border: 2px dashed #9ca3af; display: flex; align-items: center; justify-content: center; color: #6b7280; font-size: 0.85rem; text-align: center; padding: 10px;">
                    Sem Logo
                </div>
            </div>
        """, unsafe_allow_html=True)

    with st.popover("🖼️ Editar Logo e Nome", use_container_width=True):
        novo_nome = st.text_input("Nome do Restaurante:", value=nome_restaurante)
        nova_url = st.text_input("Endereço da Logo (HTTPS):", value=logo_atual, placeholder="https://...")
        if st.button("Salvar", key="btn_salvar_prod_cfg", type="primary", use_container_width=True):
            if novo_nome.strip():
                salvar_configuracoes(novo_nome.strip(), nova_url.strip())
                st.rerun()

    st.divider()
    if st.button("Dashboard", key="btn_dash_prod", use_container_width=True):
        st.switch_page("pages/dashboard.py")
    if st.button("Relatórios", key="btn_rel_prod", use_container_width=True):
        st.switch_page("pages/his_entregas.py")
    if st.button("Gestão de Produtos", key="btn_prod_prod", use_container_width=True):
        st.switch_page("pages/produtos_crud.py")
    if st.button("Alocação", key="btn_aloc_prod", use_container_width=True):
        st.switch_page("pages/alocacao.py")

    st.divider()
    if st.button("Sair", key="btn_sair_prod", use_container_width=True):
        if "usuario_logado" in st.session_state:
            del st.session_state.usuario_logado
        st.switch_page("la_pasta_login.py")

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
            n_cat = c3.selectbox("Categoria:", ["Massa", "bebidas", "ingrediente"])
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
    for idx, row in df_produtos.iterrows():
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
                        categorias = ["Massa", "bebidas", "ingrediente"]
                        idx_cat = categorias.index(row["categoria"]) if row["categoria"] in categorias else 0
                        ed_cat = e3.selectbox("Categoria:", categorias, index=idx_cat)
                        try:
                            prep_int = int(float(row["preparo_min"]))
                        except (ValueError, TypeError):
                            prep_int = 15
                        ed_prep = e4.number_input("Preparo (min):", min_value=1, value=prep_int, step=1)
                        ed_img = st.text_input("Imagem (HTTPS):", value=str(row["imagem_url"] or ""))

                        if st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True):
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

                                def excluir_produto(prod_id):
                                    conexao = sqlite3.connect('banco.db')
                                    cursor = conexao.cursor()
                                    cursor.execute("DELETE FROM produtos WHERE id = ?", (prod_id,))
                                    conexao.commit()
                                    conexao.close()

                                st.rerun()
                            else:
                                st.warning("O nome não pode ficar vazio.")
else:
    st.info("Nenhum produto encontrado. Clique em '➕ Novo Produto' para cadastrar.")
