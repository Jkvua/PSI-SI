import streamlit as st
import pandas as pd
from storage.auditorias import buscar_todas_auditorias, buscar_auditoria_por_usuario_id
from components.header import render_header
from filters.usuario_auditoria import filtrar_auditorias_por_perfil
from logic.utils import calcular_stats_total, percentual_conformidade
from storage.auditorias import load_auditorias, delete_auditoria

def render_gerencias_auditoria():
    render_header(
        titulo="Gerenciar Auditorias",
        subtitulo="Visualize, edite ou exclua auditorias realizadas",
        emoji="🗂️"
    )

    usuario = st.session_state.get("usuario", {})
    auditorias = load_auditorias()
    auditorias_filtradas = filtrar_auditorias_por_perfil(auditorias, usuario)

    if not auditorias_filtradas:
         st.warning("Nenhuma auditoria encontrada. Realize uma nova auditoria para visualizar aqui.")
         st.stop()

    for aud in sorted(auditorias_filtradas, key=lambda x: x.get("data_auditoria",""), reverse=True):
        render_auditoria_linha(aud)

def calcular_pct(aud):
        stats = aud.get("stats_total") or calcular_stats_total(aud.get("respostas",{}))
        return percentual_conformidade(stats)

def render_auditoria_linha(aud):
        pct = calcular_pct(aud)
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1,1,1,1,1,1,1])

        col1.markdown(f"**{aud.get('empresa','—')}**")
        col2.markdown(f"{aud.get('norma','—')}")
        col3.markdown(f"{aud.get('data_auditoria','—')}")
        col4.markdown(f"*{aud.get('auditor','—')}*")
        col5.markdown(f"**{pct}%**")
        col6.markdown(f"`{aud.get('criado_em','—')}`")

        with col7:
            if st.button("Excluir", key=f"del_{aud.get('id')}"):
                delete_auditoria(aud.get("id"))
                st.success("Auditoria excluída!")
                st.rerun()
        st.markdown("---")