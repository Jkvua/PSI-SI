import streamlit as st
from storage.auditorias import load_auditorias
from components.header import render_header
from filters.relatorio import render_filtro_relatorio
from components.metrics import render_metrics_status
from components.relatorio import render_graficos, render_nao_conformidades, render_header_relatorio, render_controles, render_mostra_comparativo
from data.controles_27001_27002 import CONTROLES_27001_27002
from data.controles_27701 import CONTROLES_27701
from logic.utils import calcular_stats_total, percentual_conformidade, calcular_stats_grupos
from components.pdf import render_exportar_pdf

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

    render_exportar_pdf(aud, auditorias, norma, stats, grupos_stats, controles, grupo_sel)