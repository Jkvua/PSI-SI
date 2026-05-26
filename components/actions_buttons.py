import json
import streamlit as st
from datetime import datetime
from data.controles_27001_27002 import CONTROLES_27001_27002
from data.controles_27701 import CONTROLES_27701
from logic.utils import calcular_stats_grupos
from storage.auditorias import save_auditoria

def _get_controles_por_norma(norma):
    return CONTROLES_27001_27002 if norma == "27001" else CONTROLES_27701


def _limpar_formulario(chave, controles):
    st.session_state[chave] = {}
    for grupo, lista in controles.items():
        for codigo, _ in lista:
            st.session_state.pop(f"s_{chave}_{grupo}_{codigo}", None)
            st.session_state.pop(f"a_{chave}_{grupo}_{codigo}", None)

    for key in (
        "nova_auditoria_empresa",
        "nova_auditoria_auditor",
        "nova_auditoria_cenario",
        "nova_auditoria_data",
    ):
        st.session_state.pop(key, None)


def _formulario_limpo(empresa, auditor, cenario, respostas):
    if empresa.strip() or auditor.strip() or cenario.strip():
        return False
    return all(v.get("status", "Não Aplica") == "Não Aplica" for v in respostas.values())


def _criar_hash_auditoria(empresa, auditor, cenario, respostas, norma):
    return json.dumps(
        {
            "norma": norma,
            "empresa": empresa.strip(),
            "auditor": auditor.strip(),
            "cenario": cenario.strip(),
            "respostas": respostas,
        },
        sort_keys=True,
        ensure_ascii=False,
    )

def render_auditoria_actions_buttons(empresa, auditor, data_auditoria, 
                                     cenario, respostas, stats, norma, chave, controles):
    
    col_salvar, _ ,col_limpar = st.columns([3, 6, 3])
    controles_por_norma = controles


    with col_salvar:
        if st.button("Salvar Auditoria", key="btn-salvar", type="primary"):
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not empresa.strip():
                st.error("Informe o nome da empresa!")
            elif not auditor.strip():
                st.error("Informe o nome do auditor!")
            elif _formulario_limpo(empresa, auditor, cenario, respostas):
                st.error("O formulário está vazio. Preencha os dados antes de salvar.")
            else:
                auditoria_hash = _criar_hash_auditoria(empresa, auditor, cenario, respostas, norma)
                if st.session_state.get("ultima_auditoria_hash") == auditoria_hash:
                    st.warning("Auditoria já foi salva. Modifique os dados antes de salvar novamente.")
                else:
                    grupos_stats = calcular_stats_grupos(respostas, norma)
                    usuario_logado = st.session_state.get("usuario", {})
                    aid = save_auditoria({
                        "norma": norma,
                        "empresa": empresa.strip(),
                        "auditor": auditor.strip(),
                        "data_auditoria": agora,
                        "cenario": cenario.strip(),
                        "respostas": respostas,
                        "stats_total": stats,
                        "stats_grupos": grupos_stats,
                        "usuario": usuario_logado.get("usuario", "desconhecido"),
                        "usuario_id": usuario_logado.get("id"),
                    })
                    st.session_state["ultima_auditoria_hash"] = auditoria_hash
                    _limpar_formulario(chave, controles_por_norma)
                    st.success(f"Auditoria salva! ID: `{aid}`")
                    st.rerun()

    with col_limpar:
        if st.button("Limpar Respostas", key="btn-limpar"):
            _limpar_formulario(chave, controles_por_norma)
            st.success("Formulário limpo.")
            st.rerun()