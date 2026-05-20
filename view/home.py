import streamlit as st
import pandas as pd
from datetime import date
from components.header import render_header
from components.metrics import render_metrics
from logic.utils import calcular_stats_total, calcular_stats_grupos, percentual_conformidade, total_controles

def render_home(auditorias):
    render_header("PSI-SI — Diagnóstico de Conformidade",
                  "Sistema de avaliação ISO/IEC 27001 · 27002 · 27701", "🛡️")
    
    render_metrics(auditorias)
    
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📌 ISO/IEC 27001 + 27002")
        st.info("Avaliação do Sistema de Gestão de Segurança da Informação (SGSI).\n\n"
                "Utiliza os **93 controles** da ISO 27002:2022 agrupados em 4 categorias:\n"
                "- Organizacionais (37)\n- Pessoas (8)\n- Físicos (14)\n- Tecnológicos (34)")
    with col_b:
        st.markdown("### 🔒 ISO/IEC 27701")
        st.info("Avaliação do Sistema de Gestão de Informações de Privacidade (SGPI).\n\n"
                "Controles para **controladores** e **operadores** de Dados Pessoais (DP),\n"
                "alinhado à LGPD e ao RGPD.")
    
    if auditorias:
        st.markdown("---")
        st.markdown("### 📅 Últimas Auditorias")
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
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)