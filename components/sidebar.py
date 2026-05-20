import streamlit as st
from storage.auditorias import load_auditorias
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🛡️ PSI-SI")
        st.markdown("*Sistema de Diagnóstico de Conformidade*")
        st.markdown("---")
        pagina = st.radio("Navegação", [
            "🏠 Home",
            "📋 Nova Auditoria — 27001",
            "📋 Nova Auditoria — 27701",
            "📊 Dashboard",
            "📈 Comparativo",
            "📄 Relatórios",
            "🗑️ Gerenciar Auditorias",
        ])

        st.markdown("---")
        auditorias = load_auditorias()
        st.markdown(f"**{len(auditorias)}** auditoria(s) armazenada(s)")
        st.caption("PSI — IFC Araquari · 2026")

    return pagina