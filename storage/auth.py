import uuid
import datetime
from storage.db import get_db

def gerar_token(usuario):
    token = str(uuid.uuid4())
    expira_em = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    doc = {"usuario": usuario, "token": token, "expira_em": expira_em}
    get_db()["tokens"].insert_one(doc)
    return token

def validar_token(token):
    doc =  get_db()["tokens"].find_one({"token": token})
    if doc and doc["expira_em"] > datetime.datetime.utcnow():
        return doc["usuario"]
    return None

def revogar_token(token):
    get_db()["tokens"].delete_one({"token": token})