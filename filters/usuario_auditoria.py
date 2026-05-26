import streamlit as st

def filtrar_auditorias_por_perfil(auditorias, usuario):
    perfil = usuario.get("perfil", "usuario")
    usuario_id = str(usuario.get("id"))

    if perfil == "admin":
        return auditorias
    else:
        return [aud for aud in auditorias if str(aud.get("usuario_id")) == usuario_id]