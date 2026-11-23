import streamlit as st
import sqlite3

st.set_page_config(page_title="Cadastro", initial_sidebar_state="collapsed")

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

def criar_tabela():
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    conexao.commit()
    conexao.close()

criar_tabela()

_, col_centro, _ = st.columns([1,2,1])

with col_centro:
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center;'>Cadastro</h2>", unsafe_allow_html=True)

        id_user = st.text_input(label='Crie seu id:')
        senha_user = st.text_input(label='Crie sua senha:', type='password')
        confirma_senha = st.text_input(label='Confirme sua senha:', type='password')

        st.write("")

        with st.container(horizontal=True, horizontal_alignment="center"):
            btn_voltar = st.button("Voltar")
            btn_cadastrar = st.button("Cadastrar", type="primary")

        if btn_voltar:
            st.switch_page("app.py")

        if btn_cadastrar:
            if not id_user or not senha_user:
                st.warning("Preencha todos os campos.")
            elif senha_user != confirma_senha:
                st.error("Senhas divergentes.")
            else:
                try:
                    conexao = sqlite3.connect('banco.db')
                    cursor = conexao.cursor()
                    cursor.execute(
                        "INSERT INTO usuario (id_user, senha) VALUES (?, ?)",
                        (id_user, senha_user)
                    )
                    conexao.commit()
                    conexao.close()

                    st.session_state.usuario_logado = id_user
                    st.switch_page("pages/home.py")

                except sqlite3.IntegrityError:
                    st.error("Este ID já está em uso. Escolha outro.")