import streamlit as st

def render_dashboard_filtro(auditorias):
    col_f1, col_f2 = st.columns(2)

    norma = col_f1.selectbox("Norma", ["Todas", "27001", "27701"])
    empresas = ["Todas"] + sorted(set(a.get("empresa", "") for a in auditorias))
    empresa = col_f2.selectbox("Empresa", empresas)

    return norma, empresa