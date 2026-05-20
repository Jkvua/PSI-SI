import streamlit as st
from logic.utils import total_controles, percentual_conformidade, calcular_stats_total, calcular_stats_grupos

def render_metrics(auditorias):
    col1, col2, col3, col4 = st.columns(4)
    n27001 = len([a for a in auditorias if a.get("norma") == "27001"])
    n27701 = len([a for a in auditorias if a.get("norma") == "27701"])
    col1.metric("📋 Auditorias 27001", n27001)
    col2.metric("📋 Auditorias 27701", n27701)
    col3.metric("📝 Controles 27001/27002", total_controles("27001"))
    col4.metric("📝 Controles 27701", total_controles("27701"))

def render_metrics_auditoria(stats: dict, pct: int):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("✅ Conformes", stats.get("Conforme", 0))
    c2.metric("❌ Não Conformes", stats.get("Não Conforme", 0))
    c3.metric("🔄 Em Andamento", stats.get("Em Andamento", 0))
    c4.metric("⬜ Não Aplica", stats.get("Não Aplica", 0))
    c5.metric("🎯 % Conformidade", f"{pct}%")
    st.progress(min(pct / 100, 1.0))

def render_metrics_dashboard(stats: dict, pct: int):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("✅ Conformes", stats.get("Conforme", 0))
    c2.metric("❌ Não Conformes", stats.get("Não Conforme", 0))
    c3.metric("🔄 Em Andamento", stats.get("Em Andamento", 0))
    c4.metric("⬜ Não Aplica", stats.get("Não Aplica", 0))
    c5.metric("🎯 % Conformidade", f"{pct}%")
    st.progress(min(pct / 100, 1.0))