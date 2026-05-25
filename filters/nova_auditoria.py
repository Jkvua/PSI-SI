from data.descricao_controles import DESCRICOES_CONTROLES, DESCRICOES_CONTROLES_27701
import streamlit as st

OPECOES_STATUS = ["Conforme", "Não Conforme", "Não Aplica"]


def _render_controle(codigo, nome, val, chave, grupo, tipo_norma):
    col_id, col_nome, col_status, col_and = st.columns([1, 4, 2, 2])

    with col_id:
        st.markdown(f"`{codigo}`")

    with col_nome:
        st.markdown(f"**{nome}**")

        descricoes = (
            DESCRICOES_CONTROLES
            if tipo_norma == "27001"
            else DESCRICOES_CONTROLES_27701
        )

        st.caption(descricoes.get(codigo, "Descrição não disponível"))

    with col_status:
        status = st.selectbox(
            "Status",
            OPECOES_STATUS,
            index=OPECOES_STATUS.index(val.get("status", "Não Aplica")),
            key=f"s_{chave}_{grupo}_{codigo}",
            label_visibility="collapsed"
        )

    with col_and:
        em_and = False
        if status == "Não Conforme":
            em_and = st.checkbox(
                "Em andamento?",
                value=val.get("em_andamento", False),
                key=f"a_{chave}_{grupo}_{codigo}"
            )
        else:
            st.markdown("")

    return {"status": status, "em_andamento": em_and}


def render_filtro_nova_auditoria(controles, respostas, chave, tipo_norma):
    grupos = list(controles.keys())
    tabs = st.tabs(grupos)

    for i, grupo in enumerate(grupos):
        lista = controles[grupo]

        with tabs[i]:
            conformes_g = sum(
                1 for c, _ in lista
                if respostas.get(c, {}).get("status") == "Conforme"
            )

            st.markdown(f"{grupo} ({len(lista)} controles) | {conformes_g} conformes")

            for codigo, nome in lista:
                val = respostas.get(codigo, {})
                respostas[codigo] = _render_controle(
                    codigo, nome, val, chave, grupo, tipo_norma
                )

    return respostas