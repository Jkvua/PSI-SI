import streamlit as st

def render_norma_card(titulo, icone, descricao, rota, detalhes_esquerda=None, detalhes_direita=None):
    esquerda = "<br>".join(detalhes_esquerda) if detalhes_esquerda else ""
    direita = "<br>".join(detalhes_direita) if detalhes_direita else ""
    
    st.markdown(
        f"""
        <a href="?page={rota}" style="text-decoration: none; color: inherit;">
        <div class="norma-card">
            <h3>{icone} {titulo}</h3>
            <p>{descricao}</p>
            <div class="norma-card-cols">
                <div>{esquerda}</div>
                <div>{direita}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
