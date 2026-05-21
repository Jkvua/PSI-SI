import streamlit as st
import pandas as pd
from cProfile import label
from datetime import date
from components.header import render_header
from components.charts import chart_evolucao, chart_comparativo
from logic.utils import calcular_stats_total, calcular_stats_grupos
from storage.auditorias import load_auditorias

def render_comparativo():
    render_header(
        titulo="Comparativo - Auditorias",
        subtitulo="Compare as auditorias realizadas.",
        emoji="📈"
    )
    
    auditorias = load_auditorias()
    if not auditorias:
        st.warning("Nenhuma auditoria encontrada.")
        st.stop()


    norma_comp = st.selectbox("Norma para comparativo", ["27001", "27701"])
    auds_norma = filtrar_por_norma(auditorias, norma_comp)

    if not auds_norma:
        st.warning(f"Nenhuma auditoria para a norma {norma_comp}.")
        st.stop()

    historico = monstar_historico(auds_norma)
    st.plotly_chart(chart_evolucao(historico, norma_comp), use_container_width=True)

    if len(auds_norma) >= 2:
        render_comparativo_auditorias(auds_norma, norma_comp)
    else:
        st.info("Realize mais de uma auditoria para habilitar o comparativo detalhado.")


def filtrar_por_norma(auditorias, norma):
    return [a for a in auditorias if a.get("norma") == norma]

def monstar_historico(auds_norma):
    historico = []
    for a in sorted(auds_norma, key=lambda x: x.get("data_auditoria","")):
        s = a.get("stats_total") or calcular_stats_total(a.get("respostas",{}))
        historico.append({
            "data_auditoria": a["data_auditoria"], 
            "stats_total": s,
            "empresa": a.get("empresa",""), 
            "id": a.get("id","")
        })

    return historico

def render_comparativo_auditorias(auds_norma, norma_comp):
    st.markdown("---")
    st.markdown("### 🔀 Comparar Auditorias")
    
    opcoes = {f"{a.get('empresa')} — {a.get('data_auditoria')} (ID:{a.get('id','')[:8]})": a
              for a in auds_norma}
    labels = list(opcoes.keys())

    selecionadas = st.multiselect(
        "Selecione as auditorias para comparação",
        labels,
        default=labels[:2]
    )

    if len(selecionadas) < 2:
        st.info("Selecione pelo menos duas auditorias para comparação.")
        return

    auditoria_sel = [opcoes[l] for l in selecionadas]
    grupo_stats = [
        aud.get("stats_grupos") or calcular_stats_grupos(aud.get("respostas",{}), norma_comp)
        for aud in auditoria_sel
    ]

    fig = chart_comparativo(auditoria_sel, grupo_stats)
    st.plotly_chart(fig, use_container_width=True)
    
    rows = []
    for grupo in grupo_stats[0]:
        linha = {"Grupo": grupo}
        for aud, gs in zip(auditoria_sel, grupo_stats):
            s = gs.get(grupo, {})
            aplicaveis = sum(s.values()) - s.get("Não Aplica",0)
            pct = round(s.get("Conforme",0)/aplicaveis*100,1) if aplicaveis else 0
            linha[f"% {aud['data_auditoria']}"] = f"{pct}%"
        
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    
