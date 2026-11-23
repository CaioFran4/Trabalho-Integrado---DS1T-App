import streamlit as st
import sqlite3

st.set_page_config(page_title="Login", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none;
    }
    header, footer, #MainMenu {
        visibility: hidden;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    </style>
""", unsafe_allow_html=True)

def verificar_login(id_digitado, senha_digitada):
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    cursor.execute(
        "SELECT 1 FROM usuario WHERE id_user = ? AND senha = ?",
        (id_digitado, senha_digitada)
    )
    usuario = cursor.fetchone()
    conexao.close()
    return usuario is not None

_, col_centro, _ = st.columns([1, 2, 1])

with col_centro:
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)

        id_user = st.text_input(label='Coloque seu id:', max_chars=8)
        senha_user = st.text_input(label='Coloque sua senha:', type='password')

        st.write("")

        with st.container(horizontal=True, horizontal_alignment="center"):
            btn_cadastrar = st.button("Cadastre-se")
            btn_entrar = st.button("Entrar", type="primary")

        if btn_cadastrar:
            st.switch_page("pages/cadastro.py")

        if btn_entrar:
            if not id_user or not senha_user:
                st.warning("Preencha seu ID e sua senha.")
            elif verificar_login(id_user, senha_user):
                st.session_state.usuario_logado = id_user
                st.switch_page("pages/home.py")
            else:
                st.error("ID ou senha incorretos.")