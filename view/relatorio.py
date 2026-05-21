import streamlit as st
import pandas as pd
from storage.auditorias import load_auditorias
from components.header import render_header
from filters.relatorio import render_filtro_relatorio
from components.metrics import render_metrics_status
from components.relatorio import render_graficos, render_nao_conformidades, render_header_relatorio, render_controles, render_mostra_comparativo
from data.controles_27001_27002 import CONTROLES_27001_27002
from data.controles_27701 import CONTROLES_27701
from logic.utils import calcular_stats_total, percentual_conformidade, calcular_stats_grupos

def render_relatorio():
    render_header(
        titulo="Relatorio de Conformidade",
        subtitulo="Relatório de conformidade das auditorias - exporte o PDF.",
        emoji="📄"
    )
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

    render_header_relatorio(aud, pct)

    tipo_rel, comparativo, grupo_sel = render_filtro_relatorio(controles)
    
    render_metrics_status(stats, pct)
    render_graficos(stats, grupos_stats)


    grupos_exibir = (
        {grupo_sel: controles[grupo_sel]}
        if tipo_rel == "Parcial por Grupo" and grupo_sel
        else controles
    )

    render_controles(grupos_exibir, grupos_stats, respostas)
    render_nao_conformidades(grupos_exibir, respostas)

    if comparativo:
        render_mostra_comparativo(aud, auditorias, [norma], grupos_stats)

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