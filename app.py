import streamlit as st
from storage.auditorias import load_auditorias
from components.sidebar import render_sidebar

from view.home import render_home
from view.nova_auditoria import render_nova_auditoria
from view.dashboard import render_dashboard
from view.comparativo import render_comparativo
from view.relatorio import render_relatorio
from view.gerencias_auditoria import render_gerencias_auditoria

st.set_page_config(
    page_title="PSI-SI", 
    page_icon=":bar_chart:", 
    layout="wide",
    initial_sidebar_state="expanded"
)

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

auditorias = load_auditorias()

routes = {
    "Página Inicial": lambda: render_home(auditorias),
    "Nova Auditoria: 27001": lambda: render_nova_auditoria("Nova Auditoria: 27001"),
    "Nova Auditoria: 27701": lambda: render_nova_auditoria("Nova Auditoria: 27701"),
    "Dashboard": lambda: render_dashboard(),
    "Comparativo":lambda: render_comparativo(),
    "Relatórios": lambda: render_relatorio(),
    "Gerenciar Auditorias": lambda: render_gerencias_auditoria()
}

pagina = st.query_params.get("page", render_sidebar())
routes[pagina]()