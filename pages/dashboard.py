import streamlit as st

st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .quadrado-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 16px;
        padding: 24px;
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
        color: #1f2937;
    }
    .quadrado-titulo {
        font-size: 0.95rem;
        color: #6b7280;
        margin-bottom: 6px;
    }
    .quadrado-valor {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

st.write("## Olá Gerente!")
st.write("")


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="quadrado-card">
            <span class="quadrado-titulo">Pedidos Hoje</span>
            <p class="quadrado-valor">Texto 1</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="quadrado-card">
            <span class="quadrado-titulo">Motoboys</span>
            <p class="quadrado-valor">Texto 2</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="quadrado-card">
            <span class="quadrado-titulo">Faturamento</span>
            <p class="quadrado-valor">Texto 3</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="quadrado-card">
            <span class="quadrado-titulo">Tempo Médio</span>
            <p class="quadrado-valor">Texto 4</p>
        </div>
    """, unsafe_allow_html=True)
