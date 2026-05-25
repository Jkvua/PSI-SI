import streamlit as st
import sys, os
from streamlit_option_menu import option_menu
from storage.auditorias import load_auditorias

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🛡️ PSI-SI")
        st.markdown("*Sistema de Diagnóstico de Conformidade*")
        st.markdown("---")

        pagina = option_menu("Menu", [
            "Página Inicial",
            "Nova Auditoria: 27001",
            "Nova Auditoria: 27701",
            "Dashboard",
            "Comparativo",
            "Relatórios",
            "Gerenciar Auditorias",
            ],
            icons = ["house", "clipboard", "clipboard", "bar-chart", "graph-up", "file-earmark-text", "folder"],
            menu_icon = "cast",
            default_index = 0,
            styles={
                "nav-link-selected": {"background-color": "#b2bec7"}
            }
            
        )
        

        st.markdown("---")
        auditorias = load_auditorias()
        st.markdown(f"**{len(auditorias)}** auditoria(s) armazenada(s)")
        st.caption("PSI — IFC Araquari · 2026")

    return pagina