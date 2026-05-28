import json
import streamlit as st
from datetime import datetime

from data.controles_27001_27002 import CONTROLES_27001_27002
from data.controles_27701 import CONTROLES_27701

from logic.utils import calcular_stats_grupos
from storage.auditorias import save_auditoria


def _get_controles_por_norma(norma):
    return (
        CONTROLES_27001_27002
        if norma == "27001"
        else CONTROLES_27701
    )


def _formulario_limpo(
    empresa,
    auditor,
    cenario,
    respostas
):
    if (
        empresa.strip()
        or auditor.strip()
        or cenario.strip()
    ):
        return False

    return all(
        v.get("status", "Não Aplica")
        == "Não Aplica"
        for v in respostas.values()
    )


def _criar_hash_auditoria(
    empresa,
    auditor,
    cenario,
    respostas,
    norma
):
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


def render_auditoria_actions_buttons(
    empresa,
    auditor,
    data_auditoria,
    cenario,
    respostas,
    stats,
    norma,
    chave,
    controles
):

    col_salvar = st.columns([1])[0]

    with col_salvar:

        if st.button(
            "Salvar Auditoria",
            key="btn-salvar",
            type="primary"
        ):

            agora = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            if not empresa.strip():

                st.error(
                    "Informe o nome da empresa!"
                )

            elif not auditor.strip():

                st.error(
                    "Informe o nome do auditor!"
                )

            elif _formulario_limpo(
                empresa,
                auditor,
                cenario,
                respostas
            ):

                st.error(
                    "O formulário está vazio. "
                    "Preencha os dados antes de salvar."
                )

            else:

                auditoria_hash = (
                    _criar_hash_auditoria(
                        empresa,
                        auditor,
                        cenario,
                        respostas,
                        norma
                    )
                )

                ultimo_hash = st.session_state.get(
                    "ultima_auditoria_hash"
                )

                if ultimo_hash == auditoria_hash:

                    st.warning(
                        "Auditoria já foi salva. "
                        "Modifique os dados antes "
                        "de salvar novamente."
                    )

                else:

                    hash_respostas = json.dumps(
                        respostas,
                        sort_keys=True
                    )

                    if (
                        st.session_state.get(
                            "stats_hash"
                        ) != hash_respostas
                    ):

                        st.session_state[
                            "stats_cache"
                        ] = calcular_stats_grupos(
                            respostas,
                            norma
                        )

                        st.session_state[
                            "stats_hash"
                        ] = hash_respostas

                    grupos_stats = st.session_state[
                        "stats_cache"
                    ]

                    usuario_logado = (
                        st.session_state.get(
                            "usuario",
                            {}
                        )
                    )

                    aid = save_auditoria({

                        "norma": norma,

                        "empresa": empresa.strip(),

                        "auditor": auditor.strip(),

                        "data_auditoria": agora,

                        "cenario": cenario.strip(),

                        "respostas": respostas,

                        "stats_total": stats,

                        "stats_grupos": grupos_stats,

                        "usuario": (
                            usuario_logado.get(
                                "usuario",
                                "desconhecido"
                            )
                        ),

                        "usuario_id": (
                            usuario_logado.get("id")
                        ),
                    })

                    st.session_state[
                        "ultima_auditoria_hash"
                    ] = auditoria_hash

                    st.success(
                        f"Auditoria salva com "
                        f"sucesso! ID: {aid}"
                    )

                    st.session_state[chave] = {}