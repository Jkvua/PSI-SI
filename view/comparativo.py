import streamlit as st
import pandas as pd
from datetime import date
from components.header import render_header
from components.charts import chart_evolucao, chart_comparativo
from logic.utils import calcular_stats_total, calcular_stats_grupos
from storage.auditorias import load_auditorias

def render_comparativo():
    render_header("📈 Comparativo de Auditorias"
                  "Evolução da conformidade ao longo do tempo", "📈")
    
    auditorias = load_auditorias()
    if not auditorias:
        st.warning("Nenhuma auditoria encontrada.")
        st.stop()


    norma_comp = st.selectbox("Norma para comparativo", ["27001", "27701"])
    auds_norma = [a for a in auditorias if a.get("norma") == norma_comp]

    if not auds_norma:
        st.warning(f"Nenhuma auditoria para a norma {norma_comp}.")
        st.stop()

    historico = []
    for a in sorted(auds_norma, key=lambda x: x.get("data_auditoria","")):
        s = a.get("stats_total") or calcular_stats_total(a.get("respostas",{}))
        historico.append({"data_auditoria": a["data_auditoria"], "stats_total": s,
                          "empresa": a.get("empresa",""), "id": a.get("id","")})

    st.plotly_chart(chart_evolucao(historico, norma_comp), use_container_width=True)

    if len(auds_norma) >= 2:
        st.markdown("---")
        st.markdown("### 🔀 Comparar Duas Auditorias")
        opcoes = {f"{a.get('empresa')} — {a.get('data_auditoria')} (ID:{a.get('id','')[:8]})": a
                  for a in auds_norma}
        labels = list(opcoes.keys())
        col1, col2 = st.columns(2)
        sel1 = col1.selectbox("Auditoria A (base)", labels, index=0)
        sel2 = col2.selectbox("Auditoria B (comparação)", labels, index=min(1, len(labels)-1))

        aud1 = opcoes[sel1]; aud2 = opcoes[sel2]
        gs1 = aud1.get("stats_grupos") or calcular_stats_grupos(aud1.get("respostas",{}), norma_comp)
        gs2 = aud2.get("stats_grupos") or calcular_stats_grupos(aud2.get("respostas",{}), norma_comp)
        st.plotly_chart(chart_comparativo(aud1, aud2, gs1, gs2), use_container_width=True)

        rows = []
        for grupo in gs1:
            s1 = gs1[grupo]; s2 = gs2.get(grupo, {})
            a1 = sum(s1.values()) - s1.get("Não Aplica",0)
            a2 = sum(s2.values()) - s2.get("Não Aplica",0)
            p1 = round(s1.get("Conforme",0)/a1*100,1) if a1 else 0
            p2 = round(s2.get("Conforme",0)/a2*100,1) if a2 else 0
            delta = round(p2 - p1, 1)
            rows.append({"Grupo": grupo,
                         f"% {aud1['data_auditoria']}": f"{p1}%",
                         f"% {aud2['data_auditoria']}": f"{p2}%",
                         "Δ Evolução": f"{'+'if delta>=0 else ''}{delta}%"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    
    else:
        st.info("Realize mais de uma auditoria para habilitar o comparativo detalhado.")
