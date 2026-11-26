from pathlib import Path
import streamlit as st
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent

def garantir_estrutura_banco():
    conexao = sqlite3.connect(BASE_DIR / 'banco.db')
    cursor = conexao.cursor()
    for sql_cmd in [
        "ALTER TABLE configuracoes ADD COLUMN logo_url TEXT DEFAULT ''",
        "ALTER TABLE produtos ADD COLUMN preco REAL NOT NULL DEFAULT 0.0",
        "ALTER TABLE produtos ADD COLUMN imagem_url TEXT DEFAULT ''",
        "ALTER TABLE pedidos ADD COLUMN nome_cliente TEXT NOT NULL DEFAULT 'Cliente Balcão'",
        "ALTER TABLE pedidos ADD COLUMN telefone_cliente TEXT DEFAULT ''",
        "ALTER TABLE tickets ADD COLUMN status_pagamento TEXT NOT NULL DEFAULT 'aprovado'",
        "ALTER TABLE cadastro_motoboys ADD COLUMN disponivel INTEGER NOT NULL DEFAULT 1"
    ]:
        try:
            cursor.execute(sql_cmd)
        except sqlite3.OperationalError:
            pass
    conexao.commit()
    conexao.close()

def obter_configuracoes():
    garantir_estrutura_banco()
    conexao = sqlite3.connect(BASE_DIR / 'banco.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT nome_restaurante, logo_url FROM configuracoes WHERE id = 1")
    res = cursor.fetchone()
    conexao.close()
    if res:
        return (res[0] if res[0] else "La Pasta"), (res[1] if res[1] else "")
    return "La Pasta", ""

def salvar_configuracoes(novo_nome, nova_logo):
    conexao = sqlite3.connect(BASE_DIR / 'banco.db')
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE configuracoes SET nome_restaurante = ?, logo_url = ? WHERE id = 1",
        (novo_nome, nova_logo)
    )
    conexao.commit()
    conexao.close()

def _navegar_seguro(rota: str):
    disponiveis = st.session_state.get("rotas_disponiveis")
    if disponiveis is None:
        existe = (BASE_DIR / rota).exists()
    else:
        existe = rota in disponiveis

    if existe:
        st.switch_page(rota)
    else:
        st.toast(f"Arquivo '{rota}' ainda não encontrado.", icon="⚠️")

def render_sidebar(pagina_atual: str):
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

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
            novo_nome = st.text_input("Nome do Restaurante:", value=nome_restaurante, key=f"nome_rest_{pagina_atual}")
            nova_url = st.text_input("Endereço da Logo (HTTPS):", value=logo_atual, placeholder="https://...", key=f"logo_rest_{pagina_atual}")
            if st.button("Salvar", key=f"btn_salvar_cfg_{pagina_atual}", type="primary", use_container_width=True):
                if novo_nome.strip():
                    salvar_configuracoes(novo_nome.strip(), nova_url.strip())
                    st.rerun()

        st.divider()
        if st.button("📊 Dashboard", key=f"nav_dash_{pagina_atual}", use_container_width=True, type="primary" if pagina_atual == "dashboard" else "secondary"):
            _navegar_seguro("pages/dashboard.py")
        if st.button("🧾 Recibos", key=f"nav_rec_{pagina_atual}", use_container_width=True, type="primary" if pagina_atual == "recibos" else "secondary"):
            _navegar_seguro("pages/recibos.py")
        if st.button("🍽️ Cardápio", key=f"nav_card_{pagina_atual}", use_container_width=True, type="primary" if pagina_atual == "cardapio" else "secondary"):
            _navegar_seguro("pages/cardapio.py")
        if st.button("🛵 Alocação", key=f"nav_aloc_{pagina_atual}", use_container_width=True, type="primary" if pagina_atual == "alocacao" else "secondary"):
            _navegar_seguro("pages/alocacao.py")
        if st.button("📦 Gestão de Entregas", key=f"nav_ent_{pagina_atual}", use_container_width=True, type="primary" if pagina_atual == "his_entregas" else "secondary"):
            _navegar_seguro("pages/his_entregas.py")
        if st.button("🍝 Gestão de Produtos", key=f"nav_prod_{pagina_atual}", use_container_width=True, type="primary" if pagina_atual == "produtos_crud" else "secondary"):
            _navegar_seguro("pages/produtos_crud.py")

        st.divider()
        if st.button("🚪 Sair", key=f"nav_sair_{pagina_atual}", use_container_width=True):
            if "usuario_logado" in st.session_state:
                del st.session_state.usuario_logado
            _navegar_seguro("la_pasta_login.py")

    return nome_restaurante, logo_atual