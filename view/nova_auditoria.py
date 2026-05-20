import streamlit as st
import pandas as pd
from datetime import date
from components.header import render_header
from data.controles_27001_27002 import CONTROLES_27001_27002
from data.controles_27701 import CONTROLES_27701
from logic.utils import calcular_stats_total, percentual_conformidade, calcular_stats_grupos
from storage.auditorias import save_auditoria, delete_auditoria
from components.metrics import render_metrics_auditoria

def render_nova_auditoria(pagina:str):
    norma = "27001" if "27001" in pagina else "27701"
    titulo_norma = "ISO/IEC 27001 + 27002" if norma == "27001" else "ISO/IEC 27701"
    controles = CONTROLES_27001_27002 if norma == "27001" else CONTROLES_27701

    render_header(f"Nova Auditoria - {titulo_norma}",
                  "Preencha os detalhes e selecione os controles aplicáveis", "📋"
    )

    st.markdown("### Identificação da Auditoria")
    col1, col2 = st.columns(2)
    with col1:
        empresa = st.text_input("Nome da Empresa / Organização",
                                placeholder="Ex: IFC - Campus Araquari")
        auditor = st.text_input("Nome do Auditor",
                                placeholder="Ex: Sidiclei Neckel")
    with col2:
        data_auditoria = st.date_input("Data da Auditoria", value=date.today())
        cenario = st.text_area("Cenário / Escopo da Auditoria", height=68,
                               placeholder="Ex: Avaliação do ambiente de TI do IFC")
        
    st.markdown("---")
    st.markdown("### Seleção de Controles")
    
    chave = chave = f"respostas_{norma}"
    if chave not in st.session_state:
        st.session_state[chave] = {}

    respostas = st.session_state[chave]
    opcoes_status = ["Conforme", "Não Conforme", "Não Aplica"]

    for grupo, lista in controles.items():
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
                                          key=f"s_{norma}_{codigo}", label_visibility="collapsed")
                with col_and:
                    em_and = False
                    if status == "Não Conforme":
                        em_and = st.checkbox("Em andamento?", value=val.get("em_andamento", False),
                                             key=f"a_{norma}_{codigo}")
                    else:
                        st.markdown("")
                respostas[codigo] = {"status": status, "em_andamento": em_and}

    st.session_state[chave] = respostas

    st.markdown("---")
    st.markdown("### 📊 Resumo Parcial")
    
    stats = calcular_stats_total(respostas)
    pct = percentual_conformidade(stats)

    render_metrics_auditoria(stats, pct)

    st.markdown("---")
    col_salvar, col_limpar, _ = st.columns([1, 1, 4])
    with col_salvar:
        if st.button("💾 Salvar Auditoria", type="primary"):
            if not empresa.strip():
                st.error("⚠️ Informe o nome da empresa!")
            elif sum(stats.values()) == 0:
                st.error("⚠️ Avalie pelo menos um controle!")
            else:
                grupos_stats = calcular_stats_grupos(respostas, norma)
                aid = save_auditoria({
                    "norma": norma, "empresa": empresa.strip(),
                    "auditor": auditor.strip(), "data_auditoria": str(data_auditoria),
                    "cenario": cenario.strip(), "respostas": respostas,
                    "stats_total": stats, "stats_grupos": grupos_stats,
                })
                st.success(f"✅ Auditoria salva! ID: `{aid}`")
                st.session_state[chave] = {}
                st.rerun()
    with col_limpar:
        if st.button("🗑️ Limpar Formulário"):
            st.session_state[chave] = {}
            st.rerun()



