import streamlit as st
from datetime import datetime
from logic.utils import calcular_stats_grupos
from storage.auditorias import save_auditoria

def render_auditoria_actions_buttons(empresa, auditor, data_auditoria, 
                                     cenario, respostas, stats,norma, chave):
    
    if "auditoria_salva" not in st.session_state:
        st.session_state["auditoria_salva"] = False
    
    if st.session_state["auditoria_salva"]:
        st.success("Auditoria salva com sucesso!")

    col_salvar, _ ,col_limpar = st.columns([3, 6, 3])

    with col_salvar:
        if st.button("Salvar Auditoria", key="btn-salvar", type="primary"):
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not empresa.strip():
                st.error("Informe o nome da empresa!")
            elif sum(stats.values()) == 0:
                st.error("Avalie pelo menos um controle!")
            else:
                grupos_stats = calcular_stats_grupos(respostas, norma)
                usuario_logado = st.session_state.get("usuario", {})
                aid = save_auditoria({
                    "norma": norma, "empresa": empresa.strip(),
                    "auditor": auditor.strip(), 
                    "data_auditoria": agora,
                    "cenario": cenario.strip(), 
                    "respostas": respostas,
                    "stats_total": stats, 
                    "stats_grupos": grupos_stats,
                    "usuario": usuario_logado.get("usuario", "desconhecido"),
                    "usuario_id": usuario_logado.get("id")
                })
                st.session_state["auditoria_salva"] = True
                st.success(f"Auditoria salva! ID: `{aid}`")
                st.session_state[chave] = {}
                st.rerun()

    with col_limpar:
        if st.button("Limpar Respostas", key="btn-limpar"):
            st.session_state[chave] = {}
            st.rerun()