from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).parent

candidatos = [
    ("la_pasta_login.py", "Login", "🔐"),
    ("pages/cadastro.py", "Cadastro", "📝"),
    ("pages/dashboard.py", "Dashboard", "📊"),
    ("pages/recibos.py", "Recibos", "🧾"),
    ("pages/cardapio.py", "Cardápio", "🍽️"),
    ("pages/alocacao.py", "Alocação", "🛵"),
    ("pages/his_entregas.py", "Gestão de Entregas", "📦"),
    ("pages/produtos_crud.py", "Gestão de Produtos", "🍝"),
]

rotas_existentes = {
    caminho for caminho, _, _ in candidatos if (BASE_DIR / caminho).exists()
}
st.session_state["rotas_disponiveis"] = rotas_existentes

paginas = [
    st.Page(caminho, title=titulo, icon=icone)
    for caminho, titulo, icone in candidatos
    if caminho in rotas_existentes
]

nav = st.navigation(paginas, position="hidden")
nav.run()