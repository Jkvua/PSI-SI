import streamlit as st
import pandas as pd
from datetime import date
from components.header import render_header
from components.metrics import render_metrics_dashboard
from components.charts import chart_pizza_total, chart_barras_grupos, chart_percentual_grupos
from logic.utils import calcular_stats_total, percentual_conformidade, calcular_stats_grupos
from storage.auditorias import load_auditorias

def render_dashboard():
    render_header("Dashboard de Auditorias", 
                  "Visão geral das auditorias realizadas", "📊")
    
    auditorias = load_auditorias()
    if not auditorias:
        st.warning("Nenhuma auditoria encontrada. Realize uma auditoria primeiro.")
        st.stop()

    col_f1, col_f2 = st.columns(2)
    norma_filter = col_f1.selectbox("Norma", ["Todas", "27001", "27701"])
    empresas = ["Todas"] + sorted(set(a.get("empresa","") for a in auditorias))
    empresa_filter = col_f2.selectbox("Empresa", empresas)

    auds = auditorias
    if norma_filter != "Todas":
        auds = [a for a in auds if a.get("norma") == norma_filter]
    if empresa_filter != "Todas":
        auds = [a for a in auds if a.get("empresa") == empresa_filter]

    if not auds:
        st.warning("Nenhuma auditoria para os filtros selecionados.")
        st.stop()

    aud = sorted(auds, key=lambda x: x.get("data_auditoria",""), reverse=True)[0]
    stats = aud.get("stats_total") or calcular_stats_total(aud.get("respostas",{}))
    grupos_stats = aud.get("stats_grupos") or calcular_stats_grupos(aud.get("respostas",{}), aud.get("norma","27001"))
    pct = percentual_conformidade(stats)

    st.info(f"**{aud.get('empresa')}** | {aud.get('data_auditoria')} | Norma: {aud.get('norma')} | Auditor: {aud.get('auditor','—')}")
    st.markdown("---")

    render_metrics_dashboard(stats, pct)
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
        ap = sum(gs.values()) - gs.get("Não Aplica",0)
        pct_g = round(gs.get("Conforme",0)/ap*100,1) if ap else 0
        rows.append({
            "Grupo": grupo, "✅ Conformes": gs.get("Conforme",0),
            "❌ Não Conformes": gs.get("Não Conforme",0),
            "🔄 Em Andamento": gs.get("Em Andamento",0),
            "⬜ Não Aplica": gs.get("Não Aplica",0),
            "% Conformidade": f"{pct_g}%"
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)