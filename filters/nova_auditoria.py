import streamlit as st

OPECOES_STATUS = ["Conforme", "Não Conforme", "Não Aplica"]

def _render_controle(codigo, nome, val, chave, grupo):
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

def _render_grupo(grupo, lista, respostas, chave):
    conformes_g = sum(1 for c,_ in lista if respostas.get(c,{}).get("status")=="Conforme")

    exp_key = f"exp_{chave}_{grupo}"
    if exp_key not in st.session_state:
        st.session_state[exp_key] = False

    with st.expander(
        f"**{grupo}** ({len(lista)} controles) | ✅ {conformes_g} conformes",
        expanded=st.session_state[exp_key]    
    ):
        for codigo, nome in lista:
            val = respostas.get(codigo, {})
            respostas[codigo] = _render_controle(codigo, nome, val, chave, grupo)

    return respostas

def render_filtro_nova_auditoria(norma, respostas, chave):
    for grupo, lista in norma.items():
        respostas = _render_grupo(grupo, lista, respostas, chave)
    return respostas