import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
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
    .pedido-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #f3f4f6;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #1f2937;
    }
    .ticket-tag {
        background-color: #6b7280;
        color: #ffffff;
        padding: 2px 8px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.78rem;
        font-family: monospace;
    }
    .alerta-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #991b1b;
    }
    </style>
""", unsafe_allow_html=True)

def preparar_config_logo():
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()
    cursor.execute("PRAGMA table_info(configuracoes)")
    colunas = [col[1] for col in cursor.fetchall()]
    if "logo_url" not in colunas:
        cursor.execute("ALTER TABLE configuracoes ADD COLUMN logo_url TEXT DEFAULT ''")
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

preparar_config_logo()
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
        if st.button("Salvar", type="primary", use_container_width=True):
            if novo_nome.strip():
                salvar_configuracoes(novo_nome.strip(), nova_url.strip())
                st.rerun()

    st.divider()
    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")
    if st.button("Relatórios", use_container_width=True):
        st.switch_page("pages/relatorios.py")
    if st.button("Alocação", use_container_width=True):
        st.switch_page("pages/alocacao.py")

    st.divider()
    if st.button("Sair", use_container_width=True):
        if "usuario_logado" in st.session_state:
            del st.session_state.usuario_logado
        st.switch_page("la_pasta_login.py")

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
    faturamento_hoje = float(cursor.fetchone()[0])

    cursor.execute("""
        SELECT COALESCE(AVG(CAST(preparo_min AS REAL)), 0)
        FROM produtos
        WHERE status = 'Disponivel'
    """)
    tempo_medio = float(cursor.fetchone()[0])

    conexao.close()
    return pedidos_hoje, motoboys_disp, faturamento_hoje, tempo_medio

pedidos_hoje, motoboys_disp, faturamento_hoje, tempo_medio = buscar_indicadores()

faturamento_fmt = f"R$ {faturamento_hoje:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
tempo_fmt = f"{int(round(tempo_medio))} min"

st.write(f"## Olá, {nome_restaurante}!")
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

st.write("")

col_mais_vendidos, col_alertas = st.columns([3, 1])

with col_mais_vendidos:
    with st.container(border=True):
        st.markdown("#### Top 3 Produtos Mais Vendidos")

        conexao = sqlite3.connect('banco.db')
        df_top_produtos = pd.read_sql_query("""
            SELECT 
                pr.nome_prod AS produto,
                SUM(hp.quantidade) AS total_vendido
            FROM historico_pedidos hp
            JOIN produtos pr ON hp.produto_id = pr.id
            GROUP BY pr.id, pr.nome_prod
            ORDER BY total_vendido DESC
            LIMIT 3
        """, conexao)
        conexao.close()

        if not df_top_produtos.empty:
            maior_venda = df_top_produtos["total_vendido"].max()

            for index, row in df_top_produtos.iterrows():
                posicao = index + 1
                nome_prod = row["produto"]
                qtd = int(row["total_vendido"])
                progresso = float(qtd / maior_venda) if maior_venda > 0 else 0.0

                c_pos, c_nome, c_barra, c_qtd = st.columns([0.5, 2.5, 4, 1], vertical_alignment="center")
                c_pos.markdown(f"**{posicao}º**")
                c_nome.write(nome_prod)
                c_barra.progress(progresso)
                c_qtd.markdown(f"**{qtd} un.**")
        else:
            st.info("Nenhuma venda de produto registrada ainda.")

with col_alertas:
    with st.container(border=True):
        st.markdown("#### Alertas de Estoque")

        conexao = sqlite3.connect('banco.db')
        df_indisponiveis = pd.read_sql_query("""
            SELECT nome_prod, categoria
            FROM produtos
            WHERE status = 'Indisponivel'
            LIMIT 5
        """, conexao)
        conexao.close()

        if not df_indisponiveis.empty:
            for _, row in df_indisponiveis.iterrows():
                st.markdown(f"""
                    <div class="alerta-item">
                        <span><strong>{row['nome_prod']}</strong></span>
                        <span style="font-size: 0.75rem; opacity: 0.85;">{row['categoria']}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("Estoque completo.")