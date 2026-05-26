import json, os
from datetime import datetime

STORAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auditorias.json")

def load_auditorias():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_auditoria(auditoria: dict):
    auditorias = load_auditorias()
    auditoria["id"] = datetime.now().strftime("%Y%m%d%H%M%S")
    auditoria["criado_em"] = datetime.now().isoformat()
    auditorias.append(auditoria)
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(auditorias, f, ensure_ascii=False, indent=2)
    return auditoria["id"]

def delete_auditoria(auditoria_id: str):
    auditorias = [a for a in load_auditorias() if a.get("id") != auditoria_id]
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(auditorias, f, ensure_ascii=False, indent=2)

def buscar_todas_auditorias():
    return load_auditorias()

def buscar_auditoria_por_usuario_id(usuario_id):
    todas = load_auditorias()
    return [a for a in todas if a.get("usuario_id") == usuario_id]