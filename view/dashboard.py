import streamlit as st
import pandas as pd
from components.header import render_header
from components.metrics import render_metrics_status
from components.charts import chart_pizza_total, chart_barras_grupos, chart_percentual_grupos
from filters.dashboard import render_dashboard_filtro
from logic.utils import calcular_stats_total, percentual_conformidade, calcular_stats_grupos
from storage.auditorias import load_auditorias

def render_dashboard():
    render_header(
        titulo="Dashboard - Auditorias",
        subtitulo="Visão geral das auditorias realizadas",
        emoji="📊"
    )
    
    auditorias = load_auditorias()
    if not auditorias:
        st.warning("Nenhuma auditoria encontrada. Realize uma auditoria primeiro.")
        st.stop()

    norma, empresa = render_dashboard_filtro(auditorias)

    auds = auditorias
    if norma != "Todas":
        auds = [a for a in auds if a.get("norma") == norma]
    if empresa != "Todas":
        auds = [a for a in auds if a.get("empresa") == empresa]

    if not auds:
        st.warning("Nenhuma auditoria para os filtros selecionados.")
        st.stop()
    
    aud = get_ultima_auditoria(auds)
    stats, grupos_stats, pct = calcular_stats(aud)
    render_grafico_dashboard(aud, stats, grupos_stats, pct)

def get_ultima_auditoria(auds):
    return sorted(auds, key=lambda x: x.get("data_auditoria",""), reverse=True)[0]

def calcular_stats(aud):
    stats = calcular_stats_total(aud.get("respostas", {}))
    grupos_stats = calcular_stats_grupos(aud.get("respostas", {}), aud.get("norma", "27001"))
    pct = percentual_conformidade(stats)
    return stats, grupos_stats, pct
    
def render_grafico_dashboard(aud, stats, grupos_stats, pct):
    st.info(f"**{aud.get('empresa')}** | {aud.get('data_auditoria')}"
            f" - Norma: {aud.get('norma')} - Auditor: {aud.get('auditor','—')}")
    st.markdown("---")

    render_metrics_status(stats, pct)
    st.markdown("---")

    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        st.plotly_chart(chart_pizza_total(stats), use_container_width=True)
    with col_g2:
        st.plotly_chart(chart_barras_grupos(grupos_stats), use_container_width=True)

    st.plotly_chart(chart_percentual_grupos(grupos_stats), use_container_width=True)

    st.markdown("### 📋 Detalhamento por Grupo")
    rows = []
    for grupo, gs in grupos_stats.items():
        avaliados = sum(gs.values()) - gs.get("Não Aplica",0)
        pct_g = round(gs.get("Conforme",0)/avaliados*100,1) if avaliados else 0
        rows.append({
            "Grupo": grupo, 
            "Conformes": gs.get("Conforme",0),
            "Não Conformes": gs.get("Não Conforme",0),
            # "Em Andamento": gs.get("Em Andamento",0),
            "Não Aplica": gs.get("Não Aplica",0),
            "% Conformidade": f"{pct_g}%"
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)