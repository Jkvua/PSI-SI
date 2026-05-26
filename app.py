import streamlit as st
import extra_streamlit_components as stx
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

cookie_manager = stx.CookieManager(key="psi_si_cookies_v1")


if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "just_logged_out" not in st.session_state:
    st.session_state["just_logged_out"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = {}

if not st.session_state.get("autenticado", False):
    render_login(cookie_manager)
    st.stop()

pagina_sidebar = render_sidebar(cookie_manager)


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
    pagina = pagina_sidebar if pagina_sidebar else "Página Inicial"

if pagina in routes:
    routes[pagina]()
else:
    routes["Página Inicial"]