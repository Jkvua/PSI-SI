import streamlit as st
from logic.utils import calcular_stats_grupos
from storage.auditorias import save_auditoria

def render_auditoria_actions_buttons(empresa, auditor, data_auditoria, 
                                     cenario, respostas, stats,norma, chave):
    
    col_salvar, _ ,col_limpar = st.columns([3, 6, 3])

    with col_salvar:
        if st.button("Salvar Auditoria", key="btn-salvar", type="primary"):
            if not empresa.strip():
                st.error("Informe o nome da empresa!")
            elif sum(stats.values()) == 0:
                st.error("Avalie pelo menos um controle!")
            else:
                grupos_stats = calcular_stats_grupos(respostas, norma)
                aid = save_auditoria({
                    "norma": norma, "empresa": empresa.strip(),
                    "auditor": auditor.strip(), 
                    "data_auditoria": str(data_auditoria),
                    "cenario": cenario.strip(), 
                    "respostas": respostas,
                    "stats_total": stats, 
                    "stats_grupos": grupos_stats,
                })
                st.success(f"Auditoria salva! ID: `{aid}`")
                st.session_state[chave] = {}
                st.rerun()

    with col_limpar:
        if st.button("Limpar Respostas", key="btn-limpar"):
            st.session_state[chave] = {}
            st.rerun()