import streamlit as st

def render_header(titulo: str, subtitulo: str, emoji: str = "🛡️") -> None:
    st.markdown(f"""
    <div class='main-header'>
        <h1>{emoji} {titulo}</h1>
        <p>{subtitulo}</p>
    </div>
    """, unsafe_allow_html=True)
                
