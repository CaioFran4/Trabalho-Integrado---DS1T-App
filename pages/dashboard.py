import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Dashboard", initial_sidebar_state="expanded")

with st.sidebar:
    st.header('Teste')
    
    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")
        
    if st.button("Relatórios", use_container_width=True):
        st.switch_page("pages/relatorios.py")
        
    if st.button("Alocação", use_container_width=True):
        st.switch_page("pages/alocacao.py")

st.write('## Olá Gerente!')
