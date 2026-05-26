import streamlit as st
from storage.auditorias import load_auditorias
from components.sidebar import render_sidebar
from view.login import render_login
from view.home import render_home
from view.nova_auditoria import render_nova_auditoria
from view.dashboard import render_dashboard
from view.comparativo import render_comparativo
from view.relatorio import render_relatorio
from view.gerencias_auditoria import render_gerencias_auditoria

st.set_page_config(page_title="PSI-SI", page_icon=":bar_chart:",    
                   layout="wide", initial_sidebar_state="expanded")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "just_logged_out" not in st.session_state:
    st.session_state["just_logged_out"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = {}

if not st.session_state.get("autenticado", False):
    render_login()
    st.stop()

pagina_sidebar = render_sidebar()

if not st.session_state.get("autenticado", False):
    render_login()
    st.stop()

auditorias = load_auditorias()
routes = {
    "Página Inicial":        lambda: render_home(auditorias),
    "Nova Auditoria: 27001": lambda: render_nova_auditoria("Nova Auditoria: 27001"),
    "Nova Auditoria: 27701": lambda: render_nova_auditoria("Nova Auditoria: 27701"),
    "Dashboard":             lambda: render_dashboard(),
    "Comparativo":           lambda: render_comparativo(),
    "Relatórios":            lambda: render_relatorio(),
    "Gerenciar Auditorias":  lambda: render_gerencias_auditoria(),
}

pagina = st.query_params.get("page")
if not pagina:
    # Se a URL não tiver parâmetro, usa a sidebar. Se a sidebar for None, assume a Página Inicial.
    pagina = pagina_sidebar if pagina_sidebar else "Página Inicial"

if pagina in routes:
    routes[pagina]()
else:
    routes["Página Inicial"]