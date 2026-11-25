import streamlit as st
import sqlite3

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

def buscar_indicadores():
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE DATE(data_pedido) = DATE('now', 'localtime')")
    pedidos_hoje = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cadastro_motoboys")
    motoboys_disp = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(hp.quantidade * hp.preco_unitario), 0)
        FROM historico_pedidos hp
        JOIN pedidos p ON hp.pedido_id = p.id
        WHERE DATE(p.data_pedido) = DATE('now', 'localtime')
    """)
    faturamento_hoje = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(AVG(CAST(preparo_min AS REAL)), 0)
        FROM produtos
        WHERE status = 'Disponivel'
    """)
    tempo_medio = cursor.fetchone()[0]

    conexao.close()
    return pedidos_hoje, motoboys_disp, faturamento_hoje, tempo_medio

pedidos_hoje, motoboys_disp, faturamento_hoje, tempo_medio = buscar_indicadores()

faturamento_fmt = f"R$ {faturamento_hoje:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
tempo_fmt = f"{int(round(tempo_medio))} min"

st.write("## Olá Gerente!")
st.write("")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="quadrado-card">
            <span class="quadrado-titulo">Pedidos Hoje</span>
            <p class="quadrado-valor">{pedidos_hoje}</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="quadrado-card">
            <span class="quadrado-titulo">Motoboys Disponíveis</span>
            <p class="quadrado-valor">{motoboys_disp}</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="quadrado-card">
            <span class="quadrado-titulo">Faturamento Hoje</span>
            <p class="quadrado-valor">{faturamento_fmt}</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="quadrado-card">
            <span class="quadrado-titulo">Tempo Médio</span>
            <p class="quadrado-valor">{tempo_fmt}</p>
        </div>
    """, unsafe_allow_html=True)