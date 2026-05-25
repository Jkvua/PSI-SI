import streamlit as st
from storage.usuarios import criar_usuario, listar_usuarios, excluir_usuario

def render_gerenciar_usuarios():
    st.title("Gerenciar usuários")

    usuario_logado = st.session_state.get("usuario", {})
    if usuario_logado.get("perfil") != "admin":
        st.error("Apenas administradores podem acessar esta página.")
        return

    with st.form("form_novo_usuario"):
        nome = st.text_input("Nome completo")
        usuario = st.text_input("Login")
        senha = st.text_input("Senha", type="password")
        perfil = st.selectbox("Perfil", ["usuario", "admin"])

        salvar = st.form_submit_button("Cadastrar usuário")

        if salvar:
            try:
                if not nome or not usuario or not senha:
                    st.warning("Preencha todos os campos.")
                else:
                    criar_usuario(nome, usuario, senha, perfil)
                    st.success("Usuário cadastrado com sucesso.")
                    st.rerun()
            except Exception as e:
                st.error(str(e))

    st.subheader("Usuários cadastrados")

    usuarios = listar_usuarios()

    for u in usuarios:
        col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
        col1.write(u.get("nome", "-"))
        col2.write(u.get("usuario", "-"))
        col3.write(u.get("perfil", "usuario"))

        if col4.button("Excluir", key=f"exc_{u.get('usuario')}"):
            excluir_usuario(u.get("usuario"))
            st.success("Usuário excluído.")
            st.rerun()