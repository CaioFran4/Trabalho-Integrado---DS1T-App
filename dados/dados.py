import streamlit as st
import sqlite3
import random
import base64
import glob

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

def gerar_id_unico(cursor):
    while True:
        novo_id = str(random.randint(10000000, 99999999))
        cursor.execute("SELECT 1 FROM usuario WHERE id_user = ?", (novo_id,))
        if not cursor.fetchone():
            return novo_id

def carregar_imagem_base64():
    arquivos_img = glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("*.jpeg")
    if arquivos_img:
        with open(arquivos_img, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

criar_tabela()

_, col_centro, _ = st.columns()

with col_centro:
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center;'>Cadastro</h2>", unsafe_allow_html=True)
        
        img_b64 = carregar_imagem_base64()
        if img_b64:
            st.markdown(f"""
                <div style='display: flex; justify-content: center; margin-bottom: 15px;'>
                    <img src='data:image/png;base64,{img_b64}' style='width: 75px; height: 75px; border-radius: 50%; object-fit: cover; border: 2px solid #ccc;'>
                </div>
            """, unsafe_allow_html=True)

        if "id_recem_criado" in st.session_state:
            st.success("Cadastro realizado com sucesso!")
            st.info(f"Anote seu ID de acesso (8 dígitos): **{st.session_state.id_recem_criado}**")
            
            if st.button("Entrar na Home", type="primary", use_container_width=True):
                st.session_state.usuario_logado = st.session_state.id_recem_criado
                del st.session_state.id_recem_criado
                st.switch_page("pages/home.py")

        else:
            senha_user = st.text_input(label='Crie sua senha:', type='password')
            confirma_senha = st.text_input(label='Confirme sua senha:', type='password')

            st.write("")

            with st.container(horizontal=True, horizontal_alignment="center"):
                btn_voltar = st.button("Voltar")
                btn_cadastrar = st.button("Cadastrar", type="primary")

            if btn_voltar:
                st.switch_page("la_pasta_login.py")

            if btn_cadastrar:
                if not senha_user:
                    st.warning("Crie uma senha para continuar.")
                elif senha_user != confirma_senha:
                    st.error("As senhas não coincidem.")
                else:
                    conexao = sqlite3.connect('banco.db')
                    cursor = conexao.cursor()

                    id_gerado = gerar_id_unico(cursor)

                    cursor.execute(
                        "INSERT INTO usuario (id_user, senha) VALUES (?, ?)",
                        (id_gerado, senha_user)
                    )
                    conexao.commit()
                    conexao.close()

                    st.session_state.id_recem_criado = id_gerado
                    st.rerun()