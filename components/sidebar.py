import streamlit as st
import extra_streamlit_components as stx
from storage.auth import revogar_token
from streamlit_option_menu import option_menu

def render_sidebar(cookie_manager):
    usuario = st.session_state.get("usuario", {})

    with st.sidebar:
        st.markdown("### 🛡️ PSI-SI")
        st.markdown("*Sistema de Diagnóstico de Conformidade*")
    
        st.divider()

        selecao = option_menu (
            "Menu",
            ["Página Inicial", 
             "Nova Auditoria: 27001", 
             "Nova Auditoria: 27701",
             "Dashboard", 
             "Comparativo", 
             "Relatórios", 
             "Gerenciar Auditorias"
            ],
            
            icons=["house", "clipboard", "clipboard", "bar-chart", "graph-up", "file-earmark-text", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "nav-link-selected": {"background-color": "#e8f1ff", "color": "black"},
            }
        )

        st.divider()
        
        if st.button("Sair", use_container_width=True):
            try:
                token_cookie = cookie_manager.get("auth_token")
                if token_cookie:
                    revogar_token(token_cookie)
                cookie_manager.delete("auth_token")
            except Exception as erro_logout:
                print(f"Aviso: Limpeza de token/cookie falhou de forma segura: {erro_logout}")
            
            st.session_state["autenticado"] = False
            st.session_state["usuario"] = {}
            st.session_state["just_logged_out"] = True

            st.rerun()

        st.divider()

        st.markdown(f"👤 Usuario: **{usuario.get('usuario','Usuário')}**")   
    return selecao