import streamlit as st


def render_sidebar():
    usuario = st.session_state.get("usuario", {})
    with st.sidebar:
        st.markdown("### 🛡️ PSI-SI")
        st.markdown(f"👤 **{usuario.get('usuario','Usuário')}**")
        st.divider()
        paginas = ["Página Inicial", "Nova Auditoria: 27001", "Nova Auditoria: 27701",
                   "Dashboard", "Comparativo", "Relatórios", "Gerenciar Auditorias"]
        selecao = st.radio("Navegação", paginas, label_visibility="collapsed")
        st.divider()
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    return selecao