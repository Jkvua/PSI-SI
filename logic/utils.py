from data import CONTROLES_27001_27002, CONTROLES_27701

def novo_stats() -> dict:
    return {"Conforme": 0, "Não Conforme": 0, "Em Andamento": 0, "Não Aplica": 0}

def calcular_stats_total(respostas: dict) -> dict:  
    stats = novo_stats()
    
    for v in respostas.values():
        status = v.get("status", "Não Aplica")
        if status == "Conforme":
            stats["Conforme"] += 1
        elif status == "Não Aplica":
            stats["Não Aplica"] += 1
        elif status == "Não Conforme":
            stats["Não Conforme"] += 1
            if v.get("em_andamento", False):
                stats["Em Andamento"] += 1

    return stats

def calcular_stats_grupos(respostas: dict, norma: str) -> dict:   
    controles = CONTROLES_27001_27002 if norma == "27001" else CONTROLES_27701
    grupos_stats = {}
    
    for grupo, lista in controles.items():
        stats = novo_stats()
        for codigo, _unused in lista:
            v = respostas.get(codigo, {})
            status = v.get("status", "Não Aplica")
            if status == "Conforme":
                stats["Conforme"] += 1
            elif status == "Não Aplica":
                stats["Não Aplica"] += 1
            elif status == "Não Conforme":
                stats["Não Conforme"] += 1
                if v.get("em_andamento", False):
                    stats["Em Andamento"] += 1
        grupos_stats[grupo] = stats
        
    return grupos_stats

def percentual_conformidade(stats: dict) -> float: 
    aplicaveis = sum(stats.values()) - stats.get("Não Aplica", 0)
    
    if aplicaveis == 0:
        return 0.0
    return round(stats.get("Conforme", 0) / aplicaveis * 100, 1)

def total_controles(norma: str) -> int:
    controles = CONTROLES_27001_27002 if norma == "27001" else CONTROLES_27701
    return sum(len(v) for v in controles.values())