import streamlit as st
import pandas as pd
import sqlite3

st.markdown("""
    <style>
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    </style>
""", unsafe_allow_html=True)

_, col_centro, _ = st.columns([1,2,1])

with col_centro:
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)

        id_user = st.text_input(label='Coloque seu id:')
        senha_user = st.text_input(label='Coloque sua senha:', type='password')

        st.write("")

        with st.container(horizontal=True, horizontal_alignment="center"):
            st.button("Cadastre-se")
            st.button("Entrar", type="primary")
