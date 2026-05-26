import streamlit as st
from datetime import date, datetime
from components.header import render_header
from components.metrics import render_metrics_status
from components.actions_buttons import render_auditoria_actions_buttons
from filters.nova_auditoria import render_filtro_nova_auditoria
from data.controles_27001_27002 import CONTROLES_27001_27002
from data.controles_27701 import CONTROLES_27701
from logic.utils import calcular_stats_total, percentual_conformidade


def render_identificar_autidoria():
    st.markdown("### Preencha os dados da auditoria")
    col1, col2 = st.columns(2)

    with col1:
        empresa = st.text_input(
            "Nome da Empresa / Organização",
            placeholder="Ex: IFC - Campus Araquari",
            key="nova_auditoria_empresa"
        )
        auditor = st.text_input(
            "Nome do Auditor",
            placeholder="Ex: Sidiclei Neckel",
            key="nova_auditoria_auditor"
        )

    with col2:
        data_input = st.date_input(
            "Data da Auditoria",
            value=st.session_state.get("nova_auditoria_data", date.today()),
            key="nova_auditoria_data"
        )
        agora = datetime.now().strftime("%H:%M:%S")
        data_auditoria = f"{data_input} {agora}"
        cenario = st.text_area(
            "Cenário / Escopo da Auditoria",
            height=68,
            placeholder="Ex: Avaliação do ambiente de TI do IFC",
            key="nova_auditoria_cenario"
        )
    
    return empresa, auditor, data_auditoria, cenario

def render_nova_auditoria(pagina:str):
    norma = "27001" if "27001" in pagina else "27701"
    titulo_norma = "ISO/IEC 27001 + 27002" if norma == "27001" else "ISO/IEC 27701"
    controles = CONTROLES_27001_27002 if norma == "27001" else CONTROLES_27701

    render_header(
        titulo="Nova Auditoria - " + titulo_norma,
        subtitulo="Preencha os dados e selecione os controles aplicáveis",
        emoji="📋"
    )
    empresa, auditor, data_auditoria, cenario = render_identificar_autidoria()
        
    st.markdown("---")
    st.markdown("### Seleção de Controles")
    
    chave = f"respostas_{norma}"
    if chave not in st.session_state:
        st.session_state[chave] = {}
    
    respostas = render_filtro_nova_auditoria(controles, st.session_state[chave], chave, norma)
    st.session_state[chave] = respostas


    st.markdown("---")
    st.markdown("### Resumo Parcial")
    
    stats = calcular_stats_total(respostas)
    pct = percentual_conformidade(stats)
    render_metrics_status(stats, pct)

    st.markdown("---")

    render_auditoria_actions_buttons(
        empresa, auditor, data_auditoria, cenario, 
        respostas, stats, norma, chave, controles)