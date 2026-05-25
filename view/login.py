import streamlit as st
from storage.usuarios import tem_usuarios, autenticar, criar_primeiro_usuario, criar_usuario

def render_login():
    st.set_page_config(page_title="PSI-SI", layout="wide")

    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f4f7fb 0%, #e9eef6 100%);
    }

    .login-card {
        background: white;
        padding: 2.2rem 2rem;
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #e6ebf2;
    }

    .login-title {
        font-size: 2rem;
        font-weight: 700;
        color: #123;
        margin-bottom: 0.2rem;
        text-align: center;
    }

    .login-subtitle {
        font-size: 0.95rem;
        color: #5b6574;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .login-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        background: #e8f1ff;
        color: #1d4f91;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    div[data-testid="stForm"] {
        border: none !important;
    }

    .stTextInput > div > div > input {
        border-radius: 12px;
    }

    .stButton button, .stFormSubmitButton button {
        width: 100%;
        border-radius: 12px;
        height: 46px;
        font-weight: 600;
        background: #0f62fe;
        color: white;
        border: none;
    }

    .stButton button:hover, .stFormSubmitButton button:hover {
        background: #0043ce;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;"><span class="login-badge">Segurança • LGPD • Auditoria</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">PSI-SI</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Plataforma de avaliação de controles, auditoria e conformidade</div>', unsafe_allow_html=True)

        primeiro = not tem_usuarios()

        if primeiro:
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
        else:
            abas = st.tabs(["Entrar", "Criar conta"])

            with abas[0]:
                with st.form("form_login"):
                    usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
                    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
                    entrar = st.form_submit_button("Entrar")

                if entrar:
                    user = autenticar(usuario, senha)
                    if user:
                        st.session_state["autenticado"] = True
                        st.session_state["usuario"] = {
                            "nome": user.get("nome", usuario),
                            "usuario": user.get("usuario", usuario),
                            "perfil": user.get("perfil", "usuario")
                        }
                        st.success("Login realizado com sucesso.")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha inválidos.")

            with abas[1]:
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

        st.markdown('</div>', unsafe_allow_html=True)
