import streamlit as st

def render_filtro_nova_auditoria(norma, respostas, chave):
    opcoes_status = ["Conforme", "Não Conforme", "Não Aplica"]

    for grupo, lista in norma.items():
        conformes_g = sum(1 for c,_ in lista if respostas.get(c,{}).get("status")=="Conforme")
        with st.expander(f"**{grupo}** ({len(lista)} controles) | ✅ {conformes_g} conformes", expanded=False):
            for codigo, nome in lista:
                val = respostas.get(codigo, {})
                col_id, col_nome, col_status, col_and = st.columns([1, 4, 2, 2])
                with col_id:
                    st.markdown(f"`{codigo}`")
                with col_nome:
                    st.markdown(f"<small>{nome}</small>", unsafe_allow_html=True)
                with col_status:
                    status = st.selectbox("", opcoes_status,
                                          index=opcoes_status.index(val.get("status","Não Aplica")),
                                          key=f"s_{chave}_{codigo}", label_visibility="collapsed")
                with col_and:
                    em_and = False
                    if status == "Não Conforme":
                        em_and = st.checkbox("Em andamento?", value=val.get("em_andamento", False),
                                             key=f"a_{chave}_{codigo}")
                    else:
                        st.markdown("")
                respostas[codigo] = {"status": status, "em_andamento": em_and}

    return respostas
