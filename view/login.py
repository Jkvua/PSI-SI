import streamlit as st
from storage.usuarios import tem_usuarios, autenticar, criar_primeiro_usuario, criar_usuario
from storage.auth import gerar_token, validar_token, revogar_token

def render_login(cookie_manager):
    st.set_page_config(page_title="PSI-SI", layout="wide")
    
    if "just_logged_out" not in st.session_state:
        st.session_state["just_logged_out"] = False
    
    token_cookie = cookie_manager.get("auth_token")

    if st.session_state["just_logged_out"]:
        if token_cookie is None:
            st.session_state["just_logged_out"] = False
        else:
            token_cookie = None

    usuario_cookie = validar_token(token_cookie) if token_cookie else None

    if usuario_cookie and not st.session_state.get("autenticado"):
        st.session_state["autenticado"] = True
        st.session_state["usuario"] = usuario_cookie
        st.rerun()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: 
       
       with st.container(): 
            st.markdown('<div class="login-title">PSI-SI</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle">Plataforma de auditoria</div>', unsafe_allow_html=True)
            
            if not tem_usuarios():
                _render_admin_form()
            else:
                abas = st.tabs(["Entrar", "Criar conta"])
                with abas[0]:
                    _render_login_form(cookie_manager)
                with abas[1]:
                    _render_signup_form()

def _render_admin_form():
    with st.form("form_admin"):
        nome = st.text_input("Nome", placeholder="Seu nome completo")
        usuario = st.text_input("Usuário", placeholder="Login de acesso")
        senha = st.text_input("Senha", type="password", placeholder="Digite uma senha")
        confirmar = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha")
        enviar = st.form_submit_button("Criar administrador")

        if enviar:
            if not nome or not usuario or not senha or not confirmar:
                st.warning("Preencha todos os campos.")
            elif senha != confirmar:
                        st.error("As senhas não coincidem.")
            else:
                criar_primeiro_usuario(nome.strip(), usuario.strip(), senha)
                st.success("Administrador criado com sucesso. Faça login.")
                st.rerun()

def _render_login_form(cookie_manager):
    with st.form("form_login"):
        usuario = st.text_input("Usuário", placeholder="Nome do usuário")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        entrar = st.form_submit_button("Entrar")

    if entrar:
        if not usuario or not senha:
            st.warning("Informe usuário e senha")
            return

        user = autenticar(usuario, senha)
        if user:
            dados_usuario = {
                "id": str(user.get("_id")),
                "nome": user.get("nome", usuario),
                "usuario": user.get("usuario", usuario),
                "perfil": user.get("perfil", "usuario")
            }
            st.session_state["usuario"] = dados_usuario
            st.session_state["autenticado"] = True
            
            token = gerar_token(dados_usuario)
            cookie_manager.set("auth_token", token, key="cookie_set_login")
            st.success("Login realizado com sucesso.")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

def _render_signup_form():
    with st.form("form_cadastro", clear_on_submit=True):
        nome = st.text_input("Nome completo", placeholder="Seu nome completo")
        usuario = st.text_input("Usuário", placeholder="Login de acesso")
        senha = st.text_input("Senha", type="password", placeholder="Digite uma senha")
        confirmar = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha")
        criar = st.form_submit_button("Criar conta")

        if criar:
            if not nome or not usuario or not senha or not confirmar:
                st.warning("Preencha todos os campos.")
            elif senha != confirmar:
                st.error("As senhas não coincidem.")
            else:
                try:
                    criar_usuario(nome.strip(), usuario.strip(), senha)
                    st.success("Conta criada com sucesso. Faça login.")
                except ValueError as err:
                    st.error(str(err))

def logout(cookie_manager):
    st.session_state.clear()
    cookie_manager.delete("auth_token")
    st.success("Você saiu da conta")
    st.rerun()
