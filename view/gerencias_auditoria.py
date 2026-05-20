import streamlit as st
import pandas as pd
from components.header import render_header
from logic.utils import calcular_stats_total, percentual_conformidade
from storage.auditorias import load_auditorias, delete_auditoria

def render_gerencias_auditoria():
    render_header("Gerenciar Auditorias", 
                  "Visualize, compare ou exclua auditorias armazenadas", "⚙️")

    auditorias = load_auditorias()
    if not auditorias:
        st.warning("Nenhuma auditoria armazenada.")
        st.stop()

    for a in sorted(auditorias, key=lambda x: x.get("data_auditoria",""), reverse=True):
        s = a.get("stats_total") or calcular_stats_total(a.get("respostas",{}))
        pct = percentual_conformidade(s)
        col1, col2, col3, col4, col5 = st.columns([3,1,1,1,1])
        col1.markdown(f"**{a.get('empresa','—')}** — {a.get('norma')} — {a.get('data_auditoria')}")
        col2.markdown(f"*{a.get('auditor','—')}*")
        col3.markdown(f"🎯 **{pct}%**")
        col4.markdown(f"`{a.get('id','')[:8]}`")
        with col5:
            if st.button("🗑️ Excluir", key=f"del_{a.get('id')}"):
                delete_auditoria(a.get("id"))
                st.success("Auditoria excluída!")
                st.rerun()
        st.markdown("---")