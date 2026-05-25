import streamlit as st

def filtrar_por_norma(auditorias, norma):
    return [a for a in auditorias if a.get("norma") == norma]

def filtrar_auditoria_anterior(auditorias, norma, id_atual):
    return sorted(
        [a for a in auditorias if a.get("norma") == norma and a.get("id") != id_atual],
        key=lambda x: x.get("data_auditoria",""),
    )

def render_filtro_relatorio(controles):
    col_t1, col_t2 = st.columns(2)
    tipo_rel = col_t1.radio("Tipo de Relatório", ["Completo", "Parcial por Grupo"])
    comparativo = col_t2.checkbox("Incluir comparativo com auditoria anterior")

    grupo_sel = None
    if tipo_rel == "Parcial por Grupo":
        grupo_sel = st.selectbox("Selecione o grupo", list(controles.keys()))
    st.markdown("---")
    return tipo_rel, comparativo, grupo_sel