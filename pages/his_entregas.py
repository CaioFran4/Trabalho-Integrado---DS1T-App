import streamlit as st
import sqlite3
import pandas as pd
from dados.sidebar import render_sidebar

st.set_page_config(page_title="Gestão de Entregas", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .motoboy-cell {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .motoboy-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #dee2e6;
        flex-shrink: 0;
    }
    </style>
""", unsafe_allow_html=True)

FOTOS_MOTOS_FALLBACK = [
    "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=200",
    "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=200",
    "https://images.unsplash.com/photo-1591637333184-19aa84b3e01f?w=200"
]

nome_restaurante, _ = render_sidebar("his_entregas")

col_tit, col_nova = st.columns([4, 1.3], vertical_alignment="center")
with col_tit:
    st.write(f"## 📦 Gestão de Entregas — {nome_restaurante}")
with col_nova:
    with st.popover("➕ Nova Entrega", use_container_width=True):
        conexao = sqlite3.connect('banco.db')
        df_motos_form = pd.read_sql_query("SELECT id, nome_motoboy, placa FROM cadastro_motoboys", conexao)
        df_prods_form = pd.read_sql_query("SELECT id, nome_prod, preco FROM produtos WHERE status = 'Disponivel'", conexao)
        conexao.close()

        with st.form("form_nova_entrega", clear_on_submit=True):
            e_cliente = st.text_input("Nome do Cliente:", value="Cliente Delivery")
            e_tel = st.text_input("Telefone do Cliente:", placeholder="(11) 99999-9999")
            e_rua = st.text_input("Rua / Avenida:")
            c_num, c_bai = st.columns(2)
            e_num = c_num.text_input("Número:")
            e_bai = c_bai.text_input("Bairro:")
            c_cid, c_comp = st.columns(2)
            e_cid = c_cid.text_input("Cidade:", value="Jandira")
            e_comp = c_comp.text_input("Complemento:")

            op_motos = {f"{r['nome_motoboy']} ({r['placa']})": int(r['id']) for _, r in df_motos_form.iterrows()}
            e_moto = st.selectbox("Entregador Responsável:", list(op_motos.keys()) if op_motos else ["Sem entregador"])

            op_prods = {f"{r['nome_prod']} (R$ {float(r['preco']):.2f})": (int(r['id']), float(r['preco'])) for _, r in df_prods_form.iterrows()}
            c_pr, c_qt = st.columns([3, 1])
            e_prod = c_pr.selectbox("Prato Principal:", list(op_prods.keys()) if op_prods else ["Sem produto"])
            e_qtd = c_qt.number_input("Qtd:", min_value=1, value=1, step=1)

            if st.form_submit_button("Registrar Entrega", type="primary", use_container_width=True):
                if e_rua.strip() and e_num.strip() and e_bai.strip() and op_motos and op_prods:
                    conn = sqlite3.connect('banco.db')
                    cur = conn.cursor()
                    cur.execute("INSERT INTO tickets (status_pagamento) VALUES ('em andamento')")
                    t_id = cur.lastrowid

                    m_id = op_motos[e_moto]
                    p_id, p_preco = op_prods[e_prod]

                    cur.execute("""
                        INSERT INTO pedidos (ticket_id, motoboy_id, rua, numero, bairro, cidade, complemento, status, nome_cliente, telefone_cliente)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendente', ?, ?)
                    """, (t_id, m_id, e_rua.strip(), e_num.strip(), e_bai.strip(), e_cid.strip(), e_comp.strip(), e_cliente.strip(), e_tel.strip()))
                    ped_id = cur.lastrowid

                    cur.execute("""
                        INSERT INTO historico_pedidos (pedido_id, produto_id, quantidade, preco_unitario)
                        VALUES (?, ?, ?, ?)
                    """, (ped_id, p_id, int(e_qtd), p_preco))

                    conn.commit()
                    conn.close()
                    st.rerun()
                else:
                    st.warning("Preencha endereço, entregador e produto.")

st.write("")

conexao = sqlite3.connect('banco.db')
df_entregas = pd.read_sql_query("""
    SELECT 
        p.id AS pedido_id,
        LOWER(SUBSTR(COALESCE(t.codigo, printf('%08x', p.ticket_id)), 1, 8)) AS ticket_hex,
        p.motoboy_id AS motoboy_id,
        strftime('%d/%m/%Y %H:%M', p.data_pedido) AS data_hora,
        COALESCE(m.nome_motoboy, 'Não atribuído') AS motoboy,
        COALESCE(m.placa, '-') AS placa,
        m.foto AS motoboy_foto,
        COALESCE(p.nome_cliente, 'Cliente') AS cliente,
        COALESCE(p.telefone_cliente, '') AS telefone_cliente,
        p.rua || ', ' || p.numero || ' - ' || p.bairro || ', ' || p.cidade ||
            CASE WHEN p.complemento IS NOT NULL AND p.complemento != '' THEN ' (' || p.complemento || ')' ELSE '' END AS endereco_completo,
        p.bairro AS bairro,
        COALESCE(GROUP_CONCAT(hp.quantidade || 'x ' || pr.nome_prod, ', '), 'Sem itens') AS pedido_itens,
        COALESCE(SUM(hp.quantidade * hp.preco_unitario), 0.0) AS valor_total,
        p.status AS status
    FROM pedidos p
    LEFT JOIN tickets t ON p.ticket_id = t.id
    LEFT JOIN cadastro_motoboys m ON p.motoboy_id = m.id
    LEFT JOIN historico_pedidos hp ON p.id = hp.pedido_id
    LEFT JOIN produtos pr ON hp.produto_id = pr.id
    GROUP BY p.id
    ORDER BY p.data_pedido DESC, p.id DESC
""", conexao)

df_motoboys_lista = pd.read_sql_query("SELECT id, nome_motoboy, placa FROM cadastro_motoboys ORDER BY nome_motoboy", conexao)
conexao.close()

total_ent = len(df_entregas)
pendentes = int(df_entregas["status"].str.lower().isin(["pendente"]).sum()) if not df_entregas.empty else 0
em_rota = int(df_entregas["status"].str.lower().isin(["em rota", "em entrega"]).sum()) if not df_entregas.empty else 0
entregues = int(df_entregas["status"].str.lower().isin(["entregue"]).sum()) if not df_entregas.empty else 0
cancelados = int(df_entregas["status"].str.lower().isin(["cancelado"]).sum()) if not df_entregas.empty else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total de Pedidos", total_ent)
k2.metric("⏳ Pendentes", pendentes)
k3.metric("🛵 Em Rota", em_rota)
k4.metric("✅ Entregues", entregues)
k5.metric("❌ Cancelados", cancelados)

st.write("")

col_b1, col_b2, col_b3 = st.columns([2, 1.5, 1.2])
busca_geral = col_b1.text_input("🔍 Buscar por entregador, cliente ou ticket:", placeholder="Digite nome, cliente ou código hex...")
filtro_bairro = col_b2.text_input("📍 Filtrar por bairro:", placeholder="Ex: Centro, Alphaville...")
filtro_status = col_b3.selectbox("📌 Status da Entrega:", ["Todos", "Pendente", "Em rota", "Em entrega", "Entregue", "Cancelado"])

st.write("")

df_filtrado = df_entregas.copy()
if busca_geral.strip():
    termo = busca_geral.strip()
    df_filtrado = df_filtrado[
        df_filtrado["motoboy"].str.contains(termo, case=False, na=False) |
        df_filtrado["cliente"].str.contains(termo, case=False, na=False) |
        df_filtrado["ticket_hex"].str.contains(termo, case=False, na=False)
    ]

if filtro_bairro.strip():
    df_filtrado = df_filtrado[df_filtrado["bairro"].str.contains(filtro_bairro.strip(), case=False, na=False)]

if filtro_status != "Todos":
    df_filtrado = df_filtrado[df_filtrado["status"].str.strip().str.lower() == filtro_status.lower()]

if not df_filtrado.empty:
    for idx, row in df_filtrado.iterrows():
        ped_id = int(row["pedido_id"])
        status_txt = str(row["status"]).strip()
        status_low = status_txt.lower()

        if status_low == "entregue":
            cor = "#22c55e"
        elif status_low in ["em entrega", "em rota"]:
            cor = "#f97316"
        elif status_low == "cancelado":
            cor = "#ef4444"
        else:
            cor = "#eab308"

        foto_db = str(row["motoboy_foto"]).strip() if row["motoboy_foto"] else ""
        if foto_db.startswith("http"):
            foto_url = foto_db
        else:
            indice_foto = int(row["motoboy_id"] or idx) % len(FOTOS_MOTOS_FALLBACK)
            foto_url = FOTOS_MOTOS_FALLBACK[indice_foto]

        valor_fmt = f"R$ {float(row['valor_total']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([1.4, 2.0, 2.4, 2.2, 1.5], vertical_alignment="center")

            with c1:
                st.markdown(f"**Pedido #{ped_id}** · `#{str(row['ticket_hex']).upper()}`")
                st.caption(f"🕒 {row['data_hora']}")
                st.markdown(f"**{valor_fmt}**")

            with c2:
                st.markdown(f"""
                    <div class="motoboy-cell">
                        <img src="{foto_url}" class="motoboy-avatar">
                        <div>
                            <strong>{row['motoboy']}</strong><br>
                            <small style="color:#6b7280;">Placa: {row['placa']}</small>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with c3:
                st.markdown(f"**👤 {row['cliente']}**")
                st.caption(f"📍 {row['endereco_completo']}")

            with c4:
                st.write(row["pedido_itens"])

            with c5:
                st.markdown(
                    f"<div style='margin-bottom:6px; display:inline-flex; align-items:center; gap:6px; font-weight:700;'>"
                    f"<span style='width:10px; height:10px; border-radius:50%; background-color:{cor}; display:inline-block;'></span>"
                    f"{status_txt}</div>",
                    unsafe_allow_html=True
                )
                with st.popover("⚙️ Gerenciar", use_container_width=True):
                    status_opcoes = ["Pendente", "Em rota", "Entregue", "Cancelado"]
                    idx_st = next((i for i, s in enumerate(status_opcoes) if s.lower() == status_low), 0)
                    novo_st = st.selectbox("Status:", status_opcoes, index=idx_st, key=f"st_ped_{ped_id}")

                    op_motos_edit = {f"{r['nome_motoboy']} ({r['placa']})": int(r['id']) for _, r in df_motoboys_lista.iterrows()}
                    lista_nomes_m = list(op_motos_edit.keys())
                    idx_m = next((i for i, k in enumerate(lista_nomes_m) if op_motos_edit[k] == row["motoboy_id"]), 0)
                    novo_m_label = st.selectbox("Entregador:", lista_nomes_m, index=idx_m, key=f"mt_ped_{ped_id}")

                    if st.button("Salvar Alterações", key=f"save_ped_{ped_id}", type="primary", use_container_width=True):
                        novo_m_id = op_motos_edit[novo_m_label]
                        conn = sqlite3.connect('banco.db')
                        cur = conn.cursor()
                        cur.execute(
                            "UPDATE pedidos SET status = ?, motoboy_id = ? WHERE id = ?",
                            (novo_st, novo_m_id, ped_id)
                        )
                        if novo_st.lower() == "entregue":
                            cur.execute("UPDATE cadastro_motoboys SET disponivel = 1 WHERE id = ?", (novo_m_id,))
                            cur.execute("UPDATE tickets SET status_pagamento = 'aprovado' WHERE id = (SELECT ticket_id FROM pedidos WHERE id = ?)", (ped_id,))
                        elif novo_st.lower() == "cancelado":
                            cur.execute("UPDATE cadastro_motoboys SET disponivel = 1 WHERE id = ?", (novo_m_id,))
                            cur.execute("UPDATE tickets SET status_pagamento = 'recusado' WHERE id = (SELECT ticket_id FROM pedidos WHERE id = ?)", (ped_id,))
                        elif novo_st.lower() == "em rota":
                            cur.execute("UPDATE cadastro_motoboys SET disponivel = 0 WHERE id = ?", (novo_m_id,))
                        conn.commit()
                        conn.close()
                        st.rerun()
else:
    st.info("Nenhuma entrega encontrada com os filtros selecionados.")