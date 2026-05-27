import streamlit as st
from logic.gerar_pdf import gerar_pdf

def render_exportar_pdf(aud, auditorias, norma, stats, grupos_stats, controles, grupo_sel, ):
    st.markdown("---")
    st.markdown("### Exportar Relatório em PDF")

    col_pdf1, col_pdf2 = st.columns(2)
    with col_pdf1:
        incluir_comp_pdf = st.checkbox("Incluir comparativo no PDF", value=False, key="pdf_comp")
    with col_pdf2:
        tipo_rel_pdf = st.radio(
            "Escopo do PDF",
            ["Completo", "Somente grupo selecionado"],
            key="pdf_escopo", horizontal=True
        )

    aud_ant_pdf = None
    if incluir_comp_pdf:
        auds_ant_pdf = sorted(
            [a for a in auditorias
             if a.get("norma") == norma 
             and a.get("empresa") == aud.get("empresa")
             and a.get("id")!=aud.get("id")],
            key=lambda x: x.get("data_auditoria",""), reverse=True
        )
        if auds_ant_pdf:
            aud_ant_pdf = auds_ant_pdf[0]
            st.info(f"Comparativo com auditoria de **{aud_ant_pdf.get('data_auditoria')}** "
                    f"({aud_ant_pdf.get('empresa','')})")
        else:
            st.warning("Nenhuma auditoria anterior disponível para comparativo.")

    grupos_pdf = None
    if tipo_rel_pdf == "Somente grupo selecionado" and grupo_sel:
        grupos_pdf = {grupo_sel: controles[grupo_sel]}

    if st.button("Gerar PDF", type="primary", key="btn_pdf"):
        with st.spinner("Gerando PDF com gráficos... aguarde."):
            try:
                pdf_bytes = gerar_pdf(
                    aud=aud,
                    stats=stats,
                    grupos_stats=grupos_stats,
                    controles_dict=controles,
                    grupos_exibir=grupos_pdf,
                    aud_anterior=aud_ant_pdf,
                )
                nome_arq = (
                    f"relatorio_PSI-SI_{aud.get('norma','')}_"
                    f"{aud.get('empresa','').replace(' ','_')}_"
                    f"{aud.get('data_auditoria','')}.pdf"
                )
                st.download_button(
                    label="Clique aqui para baixar o PDF",
                    data=pdf_bytes,
                    file_name=nome_arq,
                    mime="application/pdf",
                    key="download_pdf",
                )
                st.success("PDF gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")
                st.exception(e)