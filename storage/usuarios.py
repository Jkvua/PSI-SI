from werkzeug.security import generate_password_hash, check_password_hash
from storage.db import get_db

def tem_usuarios():
    return get_db()["usuarios"].count_documents({}) > 0

def criar_primeiro_usuario(nome, usuario, senha):
    colecao = get_db()["usuarios"]

    if colecao.count_documents({}) > 0:
        raise ValueError("Já existe usuário cadastrado.")

    doc = {
        "nome": nome,
        "usuario": usuario,
        "senha": generate_password_hash(senha),
        "perfil": "admin"
    }
    colecao.insert_one(doc)

def criar_usuario(nome, usuario, senha, perfil="usuario"):
    colecao = get_db()["usuarios"]

    if colecao.find_one({"usuario": usuario}):
        raise ValueError("Já existe um usuário com esse login.")

    doc = {
        "nome": nome,
        "usuario": usuario,
        "senha": generate_password_hash(senha),
        "perfil": perfil
    }
    colecao.insert_one(doc)

def autenticar(usuario, senha):
    colecao = get_db()["usuarios"]
    user = colecao.find_one({"usuario": usuario})

    if not user:
        return False

    if check_password_hash(user["senha"], senha):
        return user

    return False

def listar_usuarios():
    colecao = get_db()["usuarios"]
    return list(colecao.find({}, {"senha": 0}))

def excluir_usuario(usuario):
    colecao = get_db()["usuarios"]
    colecao.delete_one({"usuario": usuario})