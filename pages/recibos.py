from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st
from dados.sidebar import render_sidebar

DB_PATH = Path(__file__).resolve().parent.parent / "banco.db"
st.set_page_config(page_title="Recibos", layout="wide", initial_sidebar_state="expanded")

nome_restaurante, _ = render_sidebar("recibos")
st.subheader(f"🧾 Recibos — {nome_restaurante}")

c1, c2, c3 = st.columns(3)
f_data = c1.text_input("Data de emissão:", placeholder="Ex: 26/11/2026 ou 2026-11-26")
f_total = c2.number_input("Total mínimo (R$):", min_value=0.0, value=0.0, step=5.0)
f_status = c3.selectbox("Status:", ["Todos", "aprovado", "cancelado", "andamento"])

conn = sqlite3.connect(DB_PATH)
colunas_tickets = [col[1] for col in conn.execute("PRAGMA table_info(tickets)").fetchall()]
expr_forma = (
    "COALESCE(t.forma_pagamento, 'PIX')"
    if "forma_pagamento" in colunas_tickets
    else "'PIX'"
)

df = pd.read_sql_query(f"""
    SELECT
        t.id AS ticket_id,
        LOWER(SUBSTR(COALESCE(t.codigo, printf('%08x', t.id)), 1, 8)) AS ticket_hex,
        t.data_emissao AS data_raw,
        strftime('%d/%m/%Y %H:%M', t.data_emissao) AS data_fmt,
        COALESCE(SUM(hp.quantidade * hp.preco_unitario), 0.0) AS total,
        LOWER(COALESCE(t.status_pagamento, 'aprovado')) AS status_raw,
        {expr_forma} AS forma_pagamento
    FROM tickets t
    LEFT JOIN pedidos p ON p.ticket_id = t.id
    LEFT JOIN historico_pedidos hp ON hp.pedido_id = p.id
    GROUP BY t.id, t.codigo, t.data_emissao, t.status_pagamento
    ORDER BY t.data_emissao DESC, t.id DESC
""", conn)
conn.close()

mapa_st = {
    "aprovado": "aprovado",
    "entregue": "aprovado",
    "cancelado": "cancelado",
    "recusado": "cancelado",
    "andamento": "andamento",
    "em andamento": "andamento",
    "em rota": "andamento",
    "em entrega": "andamento",
    "pendente": "andamento",
}

mensagens_status = {
    "aprovado": "O pagamento foi processado com sucesso",
    "cancelado": "O pagamento foi cancelado ou não enviado",
    "andamento": "Em andamento...",
}

if not df.empty:
    df["status"] = df["status_raw"].apply(
        lambda s: mapa_st.get(str(s).strip().lower(), "andamento")
    )
    if f_data.strip():
        df = df[
            df["data_fmt"].str.contains(f_data.strip(), case=False, na=False)
            | df["data_raw"].str.contains(f_data.strip(), case=False, na=False)
        ]
    if f_total > 0:
        df = df[df["total"] >= f_total]
    if f_status != "Todos":
        df = df[df["status"] == f_status]

col_esq, col_dir = st.columns(2, gap="large")

with col_esq:
    if not df.empty:
        r = df.iloc[0]
        st_atual = str(r["status"]).strip().lower()
        msg_status = mensagens_status.get(st_atual, "Em andamento...")
        valor_fmt = f"R$ {float(r['total']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        with st.container(border=True):
            st.markdown(f"### {msg_status}")
            st.markdown(f"**Ticket:** `#{str(r['ticket_hex']).upper()}`")
            st.markdown(f"**Valor da transferência:** {valor_fmt}")
            st.markdown(f"**Forma de pagamento:** {r['forma_pagamento']}")
            st.markdown(f"**Data de emissão:** {r['data_fmt']}")
    else:
        with st.container(border=True):
            st.info("Nenhum recibo encontrado para o filtro selecionado.")

with col_dir:
    st.markdown("#### 📊 Tickets")
    if not df.empty:
        tabela = pd.DataFrame({
            "ID Ticket (Hex)": df["ticket_hex"].str.upper(),
            "Data de Emissão": df["data_fmt"],
            "Total da Compra": df["total"].apply(
                lambda v: f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ),
            "Status": df["status"],
        })
        st.dataframe(tabela, use_container_width=True, hide_index=True)
    else:
        st.info("Sem registros para o filtro.")