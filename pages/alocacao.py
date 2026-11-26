import streamlit as st
import sqlite3
import pandas as pd
from dados.sidebar import render_sidebar

st.set_page_config(page_title="Alocação de Entregadores", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .disp-badge-sim {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-block;
    }
    .disp-badge-nao {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

nome_restaurante, _ = render_sidebar("alocacao")

col_titulo, col_novo = st.columns([4, 1], vertical_alignment="center")
with col_titulo:
    st.write(f"## 🛵 Alocação de Entregadores — {nome_restaurante}")
with col_novo:
    with st.popover("➕ Novo Entregador", use_container_width=True):
        with st.form("form_novo_motoboy", clear_on_submit=True):
            m_nome = st.text_input("Nome do Entregador:")
            m_tel = st.text_input("Telefone:", placeholder="(11) 99999-9999")
            m_placa = st.text_input("Placa do Veículo:", placeholder="ABC1D23", max_chars=8)
            m_disp = st.selectbox("Disponibilidade:", ["Disponível", "Indisponível"])
            if st.form_submit_button("Cadastrar Entregador", type="primary", use_container_width=True):
                if m_nome.strip() and m_tel.strip() and m_placa.strip():
                    try:
                        conn = sqlite3.connect('banco.db')
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO cadastro_motoboys (nome_motoboy, telefone, placa, disponivel)
                            VALUES (?, ?, ?, ?)
                        """, (m_nome.strip(), m_tel.strip(), m_placa.strip().upper(), 1 if m_disp == "Disponível" else 0))
                        conn.commit()
                        conn.close()
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Já existe um entregador cadastrado com esta placa.")
                else:
                    st.warning("Preencha todos os campos obrigatórios.")

st.write("")

conexao = sqlite3.connect('banco.db')
df_alocacao = pd.read_sql_query("""
    SELECT 
        m.id AS motoboy_id,
        m.nome_motoboy AS nome_entregador,
        COALESCE(
            (SELECT GROUP_CONCAT('#' || p.id, ', ')
             FROM pedidos p 
             WHERE p.motoboy_id = m.id AND LOWER(p.status) IN ('em rota', 'em entrega', 'pendente')),
            'Sem pedido ativo'
        ) AS id_pedido,
        m.placa AS placa,
        m.telefone AS telefone,
        m.disponivel AS disponivel
    FROM cadastro_motoboys m
    ORDER BY m.disponivel DESC, m.nome_motoboy ASC
""", conexao)

df_pedidos_abertos = pd.read_sql_query("""
    SELECT p.id, p.nome_cliente, p.bairro, p.status, COALESCE(m.nome_motoboy, 'Sem entregador') AS entregador_atual
    FROM pedidos p
    LEFT JOIN cadastro_motoboys m ON p.motoboy_id = m.id
    WHERE LOWER(p.status) NOT IN ('entregue', 'cancelado')
    ORDER BY p.id DESC
""", conexao)
conexao.close()

total_entregadores = len(df_alocacao)
total_disponiveis = int((df_alocacao["disponivel"] == 1).sum()) if not df_alocacao.empty else 0
total_ocupados = total_entregadores - total_disponiveis

k1, k2, k3 = st.columns(3)
k1.metric("Total de Entregadores", total_entregadores)
k2.metric("Disponíveis Agora", total_disponiveis)
k3.metric("Em Rota / Indisponíveis", total_ocupados)

st.write("")

with st.container(border=True):
    st.markdown("#### 🔄 Vincular / Alocar Pedido a Entregador")
    if not df_pedidos_abertos.empty and not df_alocacao.empty:
        c_p, c_m, c_b = st.columns([2.5, 2.5, 1], vertical_alignment="bottom")
        opcoes_pedidos = {
            f"Pedido #{row['id']} — {row['nome_cliente']} ({row['bairro']}) [{row['status']}]": int(row["id"])
            for _, row in df_pedidos_abertos.iterrows()
        }
        opcoes_motoboys = {
            f"{row['nome_entregador']} — Placa {row['placa']} ({'Disponível' if row['disponivel'] == 1 else 'Indisponível'})": int(row["motoboy_id"])
            for _, row in df_alocacao.iterrows()
        }
        ped_escolhido = c_p.selectbox("Selecione o Pedido:", list(opcoes_pedidos.keys()))
        moto_escolhido = c_m.selectbox("Selecione o Entregador:", list(opcoes_motoboys.keys()))
        if c_b.button("Alocar", type="primary", use_container_width=True):
            ped_id = opcoes_pedidos[ped_escolhido]
            moto_id = opcoes_motoboys[moto_escolhido]
            conn = sqlite3.connect('banco.db')
            cur = conn.cursor()
            cur.execute("UPDATE pedidos SET motoboy_id = ?, status = 'Em rota' WHERE id = ?", (moto_id, ped_id))
            cur.execute("UPDATE cadastro_motoboys SET disponivel = 0 WHERE id = ?", (moto_id,))
            conn.commit()
            conn.close()
            st.success(f"Pedido #{ped_id} alocado com sucesso!")
            st.rerun()
    else:
        st.info("Não há pedidos pendentes/em rota para alocar no momento.")

st.write("")

f_busca, f_disp = st.columns([3, 1])
busca_nome = f_busca.text_input("🔍 Buscar por nome do entregador ou placa:", placeholder="Digite nome ou placa...")
filtro_disp = f_disp.selectbox("Disponibilidade:", ["Todos", "Disponível", "Indisponível"])

df_view = df_alocacao.copy()
if busca_nome.strip():
    termo = busca_nome.strip()
    df_view = df_view[
        df_view["nome_entregador"].str.contains(termo, case=False, na=False) |
        df_view["placa"].str.contains(termo, case=False, na=False)
    ]
if filtro_disp == "Disponível":
    df_view = df_view[df_view["disponivel"] == 1]
elif filtro_disp == "Indisponível":
    df_view = df_view[df_view["disponivel"] == 0]

st.markdown("### 📋 Quadro de Alocação")

if not df_view.empty:
    h1, h2, h3, h4, h5, h6 = st.columns([2.2, 1.5, 1.3, 1.8, 1.5, 1.2])
    h1.markdown("**Nome do Entregador**")
    h2.markdown("**ID do Pedido**")
    h3.markdown("**Placa**")
    h4.markdown("**Telefone**")
    h5.markdown("**Disponibilidade**")
    h6.markdown("**Ação**")
    st.divider()

    for _, row in df_view.iterrows():
        m_id = int(row["motoboy_id"])
        esta_disp = int(row["disponivel"]) == 1
        badge = '<span class="disp-badge-sim">Disponível</span>' if esta_disp else '<span class="disp-badge-nao">Indisponível</span>'

        with st.container(border=True):
            c1, c2, c3, c4, c5, c6 = st.columns([2.2, 1.5, 1.3, 1.8, 1.5, 1.2], vertical_alignment="center")
            c1.markdown(f"**{row['nome_entregador']}**")
            c2.markdown(f"`{row['id_pedido']}`")
            c3.write(row["placa"])
            c4.write(row["telefone"])
            c5.markdown(badge, unsafe_allow_html=True)

            novo_estado = 0 if esta_disp else 1
            texto_btn = "Pausar" if esta_disp else "Liberar"
            if c6.button(texto_btn, key=f"toggle_disp_{m_id}", use_container_width=True):
                conn = sqlite3.connect('banco.db')
                cur = conn.cursor()
                cur.execute("UPDATE cadastro_motoboys SET disponivel = ? WHERE id = ?", (novo_estado, m_id))
                conn.commit()
                conn.close()
                st.rerun()
else:
    st.info("Nenhum entregador encontrado.")