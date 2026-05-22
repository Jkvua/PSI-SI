import streamlit as st

OPECOES_STATUS = ["Conforme", "Não Conforme", "Não Aplica"]

def _render_controle(codigo, nome, val, chave, grupo, norma):
    col_id, col_nome, col_status, col_and = st.columns([1, 4, 2, 2])

    with col_id:
        st.markdown(f"`{codigo}`")
    with col_nome:
        st.markdown(f"<small>{nome}</small>", unsafe_allow_html=True)
    with col_status:
        status = st.selectbox(
            "Status", 
            OPECOES_STATUS,
            index=OPECOES_STATUS.index(val.get("status","Não Aplica")),
            key=f"s_{chave}_{grupo}_{codigo}", 
            label_visibility="collapsed")
        
    with col_and:
        em_and = False
        if status == "Não Conforme":
            em_and = st.checkbox("Em andamento?", 
            value=val.get("em_andamento", False),
            key=f"a_{chave}_{grupo}_{codigo}")
        else:
            st.markdown("")

    return {"status": status, "em_andamento": em_and}

def render_filtro_nova_auditoria(norma, respostas, chave):
    grupo = list(norma.keys())
    tabs = st.tabs(grupo)

    for i, grupo in enumerate(grupo):
        lista = norma[grupo]
        with tabs[i]:
            conformes_g = sum(1 for c,_ in lista if respostas.get(c, {}).get("status")=="Conforme")
            st.markdown(f"{grupo} ({len(lista)} controles) | {conformes_g} conformes")

            for codigo, nome in lista:
                val = respostas.get(codigo, {})
                respostas[codigo] = _render_controle(codigo, nome, val, chave, grupo, norma)
    
    return respostas