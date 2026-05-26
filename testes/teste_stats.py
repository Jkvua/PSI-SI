from storage.auditorias import load_auditorias
from logic.utils import calcular_stats_total, percentual_conformidade

def validar_percentuais(aud):
    respostas = aud.get("respostas", {})
    stats = calcular_stats_total(respostas)
    pct = percentual_conformidade(stats)

    print("=== Auditoria ===")
    print(f"Empresa: {aud.get('empresa')}")
    print(f"Data: {aud.get('data_auditoria')}")
    print(f"Norma: {aud.get('norma')}")
    print(f"Auditor: {aud.get('auditor')}")
    print(f"Stats:", stats )
    print(f"Percentual de Conformidade:", pct, "%")
    print("-" * 40)

if __name__ == "__main__":
    auditorias = load_auditorias()
    if not auditorias:
        print("Nenhuma auditoria encontrada.")
    else:
        aud = sorted(auditorias, key=lambda x: x.get("id", ""), reverse=True)[0]
        validar_percentuais(aud)