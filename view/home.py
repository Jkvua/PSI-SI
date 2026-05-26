import streamlit as st
import pandas as pd
from datetime import date
from components.header import render_header
from components.metrics import render_metrics
from filters.usuario_auditoria import filtrar_auditorias_por_perfil
from components.cards import render_norma_card
from storage.auditorias import load_auditorias
from logic.utils import calcular_stats_total, percentual_conformidade

def render_home(auditorias):
    usuario = st.session_state.get("usuario")
    auditorias = load_auditorias()
    auditorias_filtradas = filtrar_auditorias_por_perfil(auditorias, usuario)
    
    render_header(
        titulo="PSI-SI - Diagnóstico de Conformidade",
        subtitulo="Sistema de avaliação ISO/IEC 27001 + 27002 · 27701",
        emoji="🛡️",
        auditorias=auditorias_filtradas
    )

    render_normas_info()
    if auditorias_filtradas:
        render_auditorias_table(auditorias_filtradas)


def render_normas_info():
    col_a, col_b = st.columns(2)
    with col_a:
        render_norma_card(
            titulo="ISO/IEC 27001 + 27002",
            descricao="Avaliação do Sistema de Gestão de Segurança da Informação (SGSI) com 93 controles da ISO 27002:2022.",
            rota="📋 Nova Auditoria — 27001",
            detalhes_esquerda=["Organizacionais (37)", "Pessoas (8)"],
            detalhes_direita=["Físicos (14)", "Tecnológicos (34)"]
        )
    with col_b: 
        render_norma_card(
            titulo="ISO/IEC 27701",
            descricao="Avaliação do Sistema de Gestão de Informações de Privacidade (SGPI), para controladores e operadores de Dados Pessoais",
            rota="📋 Nova Auditoria — 27701",
            detalhes_esquerda=[],
            detalhes_direita=[]
        )
            
def render_auditorias_table(auditorias):
    st.markdown("---")
    st.markdown("### Últimas Auditorias")

    rows = []
    for a in sorted(auditorias, key=lambda x: x.get("criado_em",""), reverse=True)[:5]:
        s = a.get("stats_total") or calcular_stats_total(a.get("respostas",{}))
        rows.append({
            "Empresa": a.get("empresa","—"),
            "Norma": a.get("norma","—"),
            "Data Auditoria": a.get("data_auditoria","—"),
            "Auditor": a.get("auditor","—"),
            "Conformidade": f"{percentual_conformidade(s)}%",
            "Controles": sum(s.values()),
        })
        
    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)