import streamlit as st
from components.metrics import render_metrics

def render_header(
        titulo: str, 
        subtitulo: str, 
        emoji: str = "🛡️",
        auditorias = None,
        mostrar_divisor: bool = True
    ) -> None:

    st.markdown(f"""
    <div class='main-header'>
        <h1>{emoji} {titulo}</h1>
        <p>{subtitulo}</p>
    </div>
    """, 
    unsafe_allow_html=True
    )

    if auditorias is not None:
        render_metrics(auditorias)
    if mostrar_divisor:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
                
