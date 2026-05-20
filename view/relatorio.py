import streamlit as st
import pandas as pd
from storage.auditorias import load_auditorias
from components.header import render_header
from components.charts import chart_pizza_total, chart_percentual_grupos, chart_comparativo
from data.controles_27001_27002 import CONTROLES_27001_27002
from data.controles_27701 import CONTROLES_27701
from logic.utils import calcular_stats_total, percentual_conformidade, calcular_stats_grupos

def render_relatorio():
    auditorias = load_auditorias()
    if not auditorias:
        st.warning("Nenhuma auditoria encontrada.")
        st.stop()
    
    opcoes_aud = {
        f"{a.get('empresa')} — {a.get('norma')} — {a.get('data_auditoria')} (ID:{a.get('id','')[:8]})": a
        for a in sorted(auditorias, key=lambda x: x.get("data_auditoria",""), reverse=True)
    }

    sel = st.selectbox("Selecione a auditoria", list(opcoes_aud.keys()))
    aud = opcoes_aud[sel]
    norma = aud.get("norma","27001")
    controles = CONTROLES_27001_27002 if norma == "27001" else CONTROLES_27701
    respostas = aud.get("respostas", {})
    stats = aud.get("stats_total") or calcular_stats_total(respostas)
    grupos_stats = aud.get("stats_grupos") or calcular_stats_grupos(respostas, norma)
    pct = percentual_conformidade(stats)

    render_header(f"Relatório de Conformidade - {aud.get('empresa','')} ({aud.get('data_auditoria','')})",
                    "Preencha os detalhes e selecione os controles aplicáveis", "📄"
                )


    col_t1, col_t2 = st.columns(2)
    tipo_rel = col_t1.radio("Tipo de Relatório", ["Completo", "Parcial por Grupo"])
    comparativo = col_t2.checkbox("Incluir comparativo com auditoria anterior")

    grupo_sel = None
    if tipo_rel == "Parcial por Grupo":
        grupo_sel = st.selectbox("Selecione o grupo", list(controles.keys()))

    st.markdown("---")

    # ── Cabeçalho do relatório na tela ────────────────────────────────────────
    st.markdown(f"""
## 📋 Relatório de Conformidade — {aud.get('norma')}
| Campo | Valor |
|---|---|
| **Empresa** | {aud.get('empresa','—')} |
| **Auditor** | {aud.get('auditor','—')} |
| **Data** | {aud.get('data_auditoria','—')} |
| **Cenário** | {aud.get('cenario','—')} |
| **Conformidade Geral** | **{pct}%** |
""")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("✅ Conformes", stats.get("Conforme",0))
    c2.metric("❌ Não Conformes", stats.get("Não Conforme",0))
    c3.metric("🔄 Em Andamento", stats.get("Em Andamento",0))
    c4.metric("⬜ Não Aplica", stats.get("Não Aplica",0))
    st.progress(min(pct / 100, 1.0))

    col_v1, col_v2 = st.columns([1, 2])
    with col_v1:
        st.plotly_chart(chart_pizza_total(stats), use_container_width=True)
    with col_v2:
        st.plotly_chart(chart_percentual_grupos(grupos_stats), use_container_width=True)

    # ── Controles na tela ─────────────────────────────────────────────────────
    grupos_exibir = (
        {grupo_sel: controles[grupo_sel]}
        if tipo_rel == "Parcial por Grupo" and grupo_sel
        else controles
    )

    for grupo, lista in grupos_exibir.items():
        gs = grupos_stats.get(grupo, {})
        ap = sum(gs.values()) - gs.get("Não Aplica",0)
        pg = round(gs.get("Conforme",0)/ap*100,1) if ap else 0
        st.markdown(f"### {grupo}")
        st.caption(f"Conformidade: **{pg}%** | {gs.get('Conforme',0)} conformes / {ap} aplicáveis")
        rows = []
        for codigo, nome in lista:
            v = respostas.get(codigo, {})
            status = v.get("status", "Não Aplica")
            em_and = v.get("em_andamento", False)
            if status == "Conforme":
                icone = "✅ Conforme"
            elif status == "Não Conforme" and em_and:
                icone = "🔄 Em Andamento"
            elif status == "Não Conforme":
                icone = "❌ Não Conforme"
            else:
                icone = "⬜ Não Aplica"
            rows.append({"Código": codigo, "Controle": nome, "Status": icone})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Não conformidades na tela ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚠️ Não Conformidades Identificadas")
    nc_rows = []
    for grupo, lista in grupos_exibir.items():
        for codigo, nome in lista:
            v = respostas.get(codigo, {})
            if v.get("status") == "Não Conforme":
                nc_rows.append({
                    "Grupo": grupo.split(" - ")[0],
                    "Código": codigo,
                    "Controle": nome,
                    "Em Andamento": "🔄 Sim" if v.get("em_andamento") else "❌ Não"
                })
    if nc_rows:
        st.dataframe(pd.DataFrame(nc_rows), use_container_width=True, hide_index=True)
    else:
        st.success("🎉 Nenhuma não conformidade no escopo selecionado!")

    # ── Comparativo na tela ───────────────────────────────────────────────────
    if comparativo:
        auds_ant_lista = sorted(
            [a for a in auditorias if a.get("norma")==norma and a.get("id")!=aud.get("id")],
            key=lambda x: x.get("data_auditoria",""), reverse=True
        )
        if auds_ant_lista:
            aud_ant = auds_ant_lista[0]
            st.markdown("---")
            st.markdown(f"### 📈 Comparativo com auditoria de {aud_ant.get('data_auditoria')}")
            gs_ant = aud_ant.get("stats_grupos") or calcular_stats_grupos(aud_ant.get("respostas",{}), norma)
            st.plotly_chart(chart_comparativo(aud_ant, aud, gs_ant, grupos_stats), use_container_width=True)
        else:
            st.info("Nenhuma auditoria anterior disponível para comparação.")

    # # ── EXPORTAR PDF ──────────────────────────────────────────────────────────
    # st.markdown("---")
    # st.markdown("### 📥 Exportar Relatório em PDF")

    # col_pdf1, col_pdf2 = st.columns(2)
    # with col_pdf1:
    #     incluir_comp_pdf = st.checkbox("📈 Incluir comparativo no PDF", value=False, key="pdf_comp")
    # with col_pdf2:
    #     tipo_rel_pdf = st.radio(
    #         "Escopo do PDF",
    #         ["Completo", "Somente grupo selecionado"],
    #         key="pdf_escopo", horizontal=True
    #     )

    # aud_ant_pdf = None
    # if incluir_comp_pdf:
    #     auds_ant_pdf = sorted(
    #         [a for a in auditorias if a.get("norma")==norma and a.get("id")!=aud.get("id")],
    #         key=lambda x: x.get("data_auditoria",""), reverse=True
    #     )
    #     if auds_ant_pdf:
    #         aud_ant_pdf = auds_ant_pdf[0]
    #         st.info(f"📊 Comparativo com auditoria de **{aud_ant_pdf.get('data_auditoria')}** "
    #                 f"({aud_ant_pdf.get('empresa','')})")
    #     else:
    #         st.warning("Nenhuma auditoria anterior disponível para comparativo.")

    # grupos_pdf = None
    # if tipo_rel_pdf == "Somente grupo selecionado" and grupo_sel:
    #     grupos_pdf = {grupo_sel: controles[grupo_sel]}

    # if st.button("📄 Gerar e Baixar PDF", type="primary", key="btn_pdf"):
    #     with st.spinner("Gerando PDF com gráficos... aguarde."):
    #         try:
    #             pdf_bytes = gerar_pdf(
    #                 aud=aud,
    #                 stats=stats,
    #                 grupos_stats=grupos_stats,
    #                 controles_dict=controles,
    #                 grupos_exibir=grupos_pdf,
    #                 aud_anterior=aud_ant_pdf,
    #             )
    #             nome_arq = (
    #                 f"relatorio_PSI-SI_{aud.get('norma','')}_"
    #                 f"{aud.get('empresa','').replace(' ','_')}_"
    #                 f"{aud.get('data_auditoria','')}.pdf"
    #             )
    #             st.download_button(
    #                 label="⬇️ Clique aqui para baixar o PDF",
    #                 data=pdf_bytes,
    #                 file_name=nome_arq,
    #                 mime="application/pdf",
    #                 key="download_pdf",
    #             )
    #             st.success("✅ PDF gerado com sucesso!")
    #         except Exception as e:
    #             st.error(f"❌ Erro ao gerar PDF: {e}")
    #             st.exception(e)