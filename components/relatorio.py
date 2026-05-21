import streamlit as st
import pandas as pd
from charts import chart_pizza_total, chart_percentual_grupos, chart_comparativo
from logic.utils import calcular_stats_grupos

def render_header_relatorio(aud, pct):
    dados = {
        "Empresa": aud.get("empresa", "-"),
        "Auditor": aud.get("auditor", "-"),
        "Data": aud.get("data_auditoria", "-"),
        "cenario": aud.get("cenario", "-"),
        "Norma": aud.get("norma", "-"),
        "Conformidade": f"{pct}%"
    }
    
    df = pd.DataFrame([dados])
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_graficos(stats, grupos_stats):
    col_v1, col_v2 = st.columns([1, 2])
    with col_v1:
        st.plotly_chart(chart_pizza_total(stats), use_container_width=True)
    with col_v2:
        st.plotly_chart(chart_percentual_grupos(grupos_stats), use_container_width=True)

def render_controles(grupos_exibir, grupos_stats, respostas):
    status_map = {
        "Conforme": "✅ Conforme",
        "Não Conforme": "❌ Não Conforme",
        "Em Andamento": "🔄 Em Andamento"
    }

    for grupo, lista in grupos_exibir.items():
        gs = grupos_stats.get(grupo, {})
        aplicaveis = sum(gs.values()) - gs.get("Não Aplica",0)
        pct_grupo = round(gs.get("Conforme",0)/aplicaveis*100,1) if aplicaveis else 0
        
        st.markdown(f"### {grupo}")
        st.caption(f"Conformidade: **{pct_grupo}%** | {gs.get('Conforme',0)} conformes / {aplicaveis} aplicáveis")
        
        rows = []
        for codigo, nome in lista:
            v = respostas.get(codigo, {})
            status = v.get("status", "Não Aplica")
            em_and = v.get("em_andamento", False)

            if status == "Não Conforme" and em_and:
                icone = "🔄 Em Andamento"
            else:
                icone = status_map.get(status, "🙅 Não Aplica")
                
            rows.append({"Código": codigo, "Controle": nome, "Status": icone})

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

def render_nao_conformidades(controles, respostas):
    st.markdown("### ⚠️ Não Conformidades Identificadas")
    nc_rows = []
    for grupo, lista in controles.items():
        for codigo, nome in lista:
            v = respostas.get(codigo, {})
            if v.get("status") == "Não Conforme":
                nc_rows.append({
                    "Grupo": grupo,
                    "Código": codigo,
                    "Controle": nome,
                    "Em Andamento": "Sim" if v.get("em_andamento") else "❌ Não"
                })
    if nc_rows:
        st.dataframe(pd.DataFrame(nc_rows), use_container_width=True, hide_index=True)
    else:
        st.info("🎉 Nenhuma não conformidade identificada.")

def render_mostra_comparativo(aud_atual, auditorias, normas, grupo_stats):
    auds_ant_lista = sorted(
        [a for a in auditorias if a.get("norma") in normas and a.get("id") != aud_atual.get("id")],
        key=lambda x: x.get("data_auditoria",""), reverse=True
    )
    if auds_ant_lista:
        aud_ant = auds_ant_lista[0]
        st.markdown("---")
        st.markdown(f"### 📈 Comparativo com auditoria de {aud_ant.get('data_auditoria')}")
        gs_ant = aud_ant.get("stats_grupos") or calcular_stats_grupos(aud_ant.get("respostas",{}), aud_ant.get("norma"))
        st.plotly_chart(chart_comparativo(aud_ant, aud_atual, gs_ant, grupo_stats), use_container_width=True)
    else:
        st.info("Nenhuma auditoria anterior disponível para comparação.")

