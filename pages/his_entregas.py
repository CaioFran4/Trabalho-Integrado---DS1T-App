import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Histórico de Entregas", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    .motoboy-cell {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .motoboy-avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #dee2e6;
        flex-shrink: 0;
    }
    </style>
""", unsafe_allow_html=True)

FOTOS_MOTOS_FALLBACK = [
    "https://unsplash.com",
    "https://unsplash.com",
    "https://unsplash.com",
    "https://unsplash.com",
    "https://unsplash.com"
]

def preparar_tabelas():
    conexao = sqlite3.connect('banco.db')
    cursor = conexao.cursor()
    
    cursor.execute("PRAGMA table_info(configuracoes)")
    colunas_cfg = [col[1] for col in cursor.fetchall()]
    if "logo_url" not in colunas_cfg:
        cursor.execute("ALTER TABLE configuracoes ADD COLUMN logo_url TEXT DEFAULT ''")

    cursor.execute("PRAGMA table_info(pedidos)")
    colunas_ped = [col[1] for col in cursor.fetchall()]
    if "nome_cliente" not in colunas_ped:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN nome_cliente TEXT NOT NULL DEFAULT 'Cliente Balcão'")

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
        if st.button("Salvar", key="btn_salvar_his", type="primary", use_container_width=True):
            if novo_nome.strip():
                salvar_configuracoes(novo_nome.strip(), nova_url.strip())
                st.rerun()

        st.divider()
    if st.button("Dashboard", key="btn_dash_his", use_container_width=True):
        st.switch_page("pages/dashboard.py")
    if st.button("Relatórios", key="btn_rel_his", use_container_width=True):
        st.switch_page("pages/his_entregas.py")
    if st.button("Gestão de Produtos", key="btn_prod_his", use_container_width=True):
        st.switch_page("pages/produtos_crud.py")
    if st.button("Alocação", key="btn_aloc_his", use_container_width=True):
        st.switch_page("pages/alocacao.py")

    st.divider()
    if st.button("Sair", key="btn_sair_his", use_container_width=True):
        if "usuario_logado" in st.session_state:
            del st.session_state.usuario_logado
        st.switch_page("la_pasta_login.py")

st.write(f"## 📦 Histórico de Entregas — {nome_restaurante}")
st.write("")

col_busca, col_filtro = st.columns([2, 1])

with col_busca:
    busca_entregador = st.text_input(
        "🔍 Buscar por nome do entregador:",
        placeholder="Digite o nome do motoboy..."
    )

with col_filtro:
    filtro_status = st.selectbox(
        "Filtrar por status:",
        options=["Todos", "Entregue", "Em entrega", "Cancelado"]
    )

st.write("")

conexao = sqlite3.connect('banco.db')
df_entregas = pd.read_sql_query("""
    SELECT 
        p.id AS pedido_id,
        p.motoboy_id AS motoboy_id,
        strftime('%d/%m/%Y %H:%M', p.data_pedido) AS data_hora,
        COALESCE(m.nome_motoboy, 'Não atribuído') AS motoboy,
        m.foto AS motoboy_foto,
        COALESCE(p.nome_cliente, 'Cliente') AS cliente,
        COALESCE(GROUP_CONCAT(hp.quantidade || 'x ' || pr.nome_prod, ', '), 'Sem itens') AS pedido_itens,
        p.status AS status
    FROM pedidos p
    LEFT JOIN cadastro_motoboys m ON p.motoboy_id = m.id
    LEFT JOIN historico_pedidos hp ON p.id = hp.pedido_id
    LEFT JOIN produtos pr ON hp.produto_id = pr.id
    GROUP BY p.id
    ORDER BY p.data_pedido DESC
""", conexao)
conexao.close()

if busca_entregador.strip():
    df_entregas = df_entregas[
        df_entregas["motoboy"].str.contains(busca_entregador.strip(), case=False, na=False)
    ]

if filtro_status != "Todos":
    df_entregas = df_entregas[
        df_entregas["status"].str.strip().str.lower() == filtro_status.lower()
    ]

if not df_entregas.empty:
    h_data, h_moto, h_cli, h_ped, h_stat = st.columns([1.4, 2.3, 1.8, 3.2, 1.5])
    h_data.markdown("**Data / Hora**")
    h_moto.markdown("**Entregador**")
    h_cli.markdown("**Cliente**")
    h_ped.markdown("**Pedido**")
    h_stat.markdown("**Status**")
    st.divider()

    for idx, row in df_entregas.iterrows():
        status_txt = str(row["status"]).strip()
        status_low = status_txt.lower()

        if status_low == "entregue":
            cor = "#22c55e"
        elif status_low in ["em entrega", "em rota"]:
            cor = "#f97316"
        elif status_low == "cancelado":
            cor = "#ef4444"
        else:
            cor = "#9ca3af"

        foto_db = str(row["motoboy_foto"]).strip() if row["motoboy_foto"] else ""
        if foto_db.startswith("http"):
            foto_url = foto_db
        else:
            indice_foto = int(row["motoboy_id"] or idx) % len(FOTOS_MOTOS_FALLBACK)
            foto_url = FOTOS_MOTOS_FALLBACK[indice_foto]

        with st.container(border=True):
            c_data, c_moto, c_cli, c_ped, c_stat = st.columns([1.4, 2.3, 1.8, 3.2, 1.5], vertical_alignment="center")
            c_data.write(row["data_hora"])
            c_moto.markdown(f"""
                <div class="motoboy-cell">
                    <img src="{foto_url}" class="motoboy-avatar">
                    <span><strong>{row['motoboy']}</strong></span>
                </div>
            """, unsafe_allow_html=True)
            c_cli.write(row["cliente"])
            c_ped.write(row["pedido_itens"])
            c_stat.markdown(
                f"<span style='display:inline-flex; align-items:center; gap:6px; font-weight:600;'>"
                f"<span style='width:10px; height:10px; border-radius:50%; background-color:{cor}; display:inline-block;'></span>"
                f"{status_txt}</span>",
                unsafe_allow_html=True
            )
else:
    st.info("Nenhuma entrega encontrada com os filtros selecionados.")