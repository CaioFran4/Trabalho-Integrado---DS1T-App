import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

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

st.write("")

col_grafico, col_lateral = st.columns([3, 1])

with col_grafico:
    with st.container(border=True):
        st.markdown("#### Vendas Registradas do Dia")

        conexao = sqlite3.connect('banco.db')
        df_vendas = pd.read_sql_query("""
            SELECT 
                strftime('%H:00', p.data_pedido) AS Horário,
                COALESCE(SUM(hp.quantidade * hp.preco_unitario), 0) AS Vendas
            FROM pedidos p
            JOIN historico_pedidos hp ON p.id = hp.pedido_id
            WHERE DATE(p.data_pedido) = DATE('now', 'localtime')
            GROUP BY Horário
            ORDER BY Horário
        """, conexao)
        conexao.close()

        if not df_vendas.empty:
            grafico = alt.Chart(df_vendas).mark_line(
                point=True,
                interpolate="monotone",
                color="#111827",
                strokeWidth=3
            ).encode(
                x=alt.X("Horário:N", title="Horário do Dia"),
                y=alt.Y("Vendas:Q", title="Faturamento (R$)"),
                tooltip=["Horário", alt.Tooltip("Vendas:Q", format="$.2f")]
            ).properties(height=280)

            st.altair_chart(grafico, use_container_width=True)
        else:
            st.info("Nenhuma venda registrada hoje.")

with col_lateral:
    with st.container(border=True):
        st.markdown("#### Pedidos recentes")

        conexao = sqlite3.connect('banco.db')
        df_recentes = pd.read_sql_query("""
            SELECT 
                COALESCE(t.codigo, CAST(p.ticket_id AS TEXT)) AS ticket,
                p.status AS status,
                strftime('%H:%M', p.data_pedido) AS hora
            FROM pedidos p
            LEFT JOIN tickets t ON p.ticket_id = t.id
            ORDER BY p.data_pedido DESC
            LIMIT 6
        """, conexao)
        conexao.close()

        if not df_recentes.empty:
            for _, row in df_recentes.iterrows():
                status_texto = str(row["status"]).strip()
                status_lower = status_texto.lower()

                if status_lower == "entregue":
                    cor_bolinha = "#22c55e"
                elif status_lower in ["em entrega", "em rota"]:
                    cor_bolinha = "#f97316"
                elif status_lower == "cancelado":
                    cor_bolinha = "#ef4444"
                else:
                    cor_bolinha = "#9ca3af"

                st.markdown(f"""
                    <div class="pedido-item">
                        <span class="ticket-tag">#{row['ticket']}</span>
                        <span><strong>{status_texto}</strong></span>
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <span style="width: 10px; height: 10px; border-radius: 50%; background-color: {cor_bolinha}; display: inline-block;"></span>
                            {row['hora']}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum pedido recente.")