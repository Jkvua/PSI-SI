import plotly.graph_objects as go
import plotly.express as px
import re

def load_css_vars(path="assets/style.css"):
    with open(path) as f:
        css = f.read()
    return dict(re.findall(r"--([\w-]+):\s*([^;]+);", css))

STYLE = load_css_vars()

COLORS = {
    "Conforme": STYLE.get("color-conforme"),
    "Não Conforme": STYLE.get("color-nao-conforme"),
    "Não Aplica": STYLE.get("color-nao-aplica"),
    # "Em Andamento": STYLE.get("color-em-andamento"),
}
DARK_BG = STYLE["bg-dark"]
CARD_BG = STYLE["dg-card"]
TEXT = STYLE["text-color"]
GRID = STYLE["grid-color"]

def _layout(fig, title, height=None, margin=None):
    
    h = height or int(STYLE.get("chart-height", 320))
    m = margin or dict(
        t=int(STYLE.get("chart-margin-top", 50)),
        b=int(STYLE.get("chart-margin-bottom", 20)),
        l=int(STYLE.get("chart-margin-left", 20)),
        r=int(STYLE.get("chart-margin-right", 20))
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=16,color=TEXT)),
        paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG, font=dict(color=TEXT),
        legend=dict(font=dict(color=TEXT), bgcolor=CARD_BG, 
                    bordercolor="rgba(100,180,255,0.15)"),
        margin=m, height=height,
    )
    return fig

def chart_pizza_total(stats, title="Conformidade Total"):
    conformes = stats.get("Conforme", 0)
    nao_conformes = stats.get("Não Conforme", 0)
    nao_aplica = stats.get("Não Aplica", 0)

    aplicaveis = conformes + nao_conformes

    pct_conforme = round(conformes / aplicaveis * 100, 1) if aplicaveis else 0
    pct_nao_conforme = round(nao_conformes / aplicaveis * 100, 1) if aplicaveis else 0 
    pct_nao_aplica = round(nao_aplica / (aplicaveis + nao_aplica) * 100, 1) if (aplicaveis + nao_aplica) else 0

    labels = ["Conforme", "Não Conforme", "Não Aplica"]
    values = [pct_conforme, pct_nao_conforme, pct_nao_aplica]
    colors = [COLORS.get(l,"#888") for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels, 
        values=values,
        marker=dict(colors=colors, line=dict(color=DARK_BG,width=2)),
        hole=0.55, 
        textinfo="percent+label",
        textposition="outside",
        showlegend=True,
        automargin=True,
        pull=[0.05 if v/sum(values) < 0.1 else 0 for v in values],
        hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>",
    ))
    
    return _layout(fig, title, height=400, margin=dict(t=60,b=40,l=40,r=40))

def chart_barras_grupos(grupos_stats, title="Conformidade por Grupo de Controles"):
    nomes, conf, nc, ea, na = [], [], [], [], []
    for g,s in grupos_stats.items():
        nomes.append(g.split(" - ")[0])
        conf.append(s.get("Conforme",0)); 
        nc.append(s.get("Não Conforme",0))
        na.append(s.get("Não Aplica",0))
    
    fig = go.Figure()
    for label, vals, color in [
        ("Conforme", conf, COLORS["Conforme"]),
        ("Não Conforme", nc, COLORS["Não Conforme"]),
        ("Não Aplica", na, COLORS["Não Aplica"])
    ]:
        
        fig.add_trace(go.Bar(
            name=label, x=nomes, y=vals,
            marker_color=color,
            text=vals, textposition="inside",
            hovertemplate="<b>%{x}</b><br>%{y} "+label+"<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        xaxis=dict(gridcolor=GRID,color=TEXT),
        yaxis=dict(gridcolor=GRID,color=TEXT),
        height = int(STYLE.get("chart-height", 320)),
        margin = dict(t=50, b=90, l=40, r=10)
    )
    return _layout(fig, title)

def chart_percentual_grupos(grupos_stats, title="% Conformidade por Grupo", ordenar=True, meta=95):
    nomes, pcts, absolutos =[], [], []
    for g,s in grupos_stats.items():
        total = sum(s.values()) 
        ap = total - s.get("Não Aplica",0)
        conformes = s.get("Conforme", 0)
        pct = round(conformes/ap*100, 1) if ap else 0
        nomes.append(g.split(" - ")[0])
        pcts.append(pct)
        absolutos.append(f"{conformes}/{ap}")

    dados = [{"nome": n, "pct": p, "abs": a} for n, p, a in zip(nomes, pcts, absolutos)] 

    if ordenar:
        dados = sorted(dados, key=lambda x: x["pct"], reverse=True)
    
    nomes = [d["nome"] for d in dados]
    pcts = [d["pct"] for d in dados]
    absolutos = [d["abs"] for d in dados]

    paleta = px.colors.qualitative.Plotly
    cores = [paleta[i % len(paleta)] for i in range(len(nomes))]


    fig=go.Figure(go.Bar(
        x=pcts,
        y=nomes,
        orientation='h',
        marker=dict(color=cores,line=dict(color=DARK_BG,width=1)),
        text=[f"{n} - {p}% ({a})" for n, p, a in zip(nomes, pcts, absolutos)],
        textposition='inside',
        textfont=dict(color="white",size=12),
        hovertemplate="<b>%{y}</b><br>%{x}%<extra></extra>"
    ))
    
    fig.add_vline(x=95,line_dash="dash",line_color="rgba(255,255,255,0.3)",
                  annotation_text="Meta +{meta}",annotation_font_color=TEXT)
    
    fig.update_layout(
        xaxis=dict(gridcolor=GRID,color=TEXT,range=[0,105]),
        yaxis=dict(gridcolor=GRID,color=TEXT),
        height = max(300, len(nomes)*42+80),
        margin = dict(t=50, b=20, l=10, r=70)
    )
    
    return _layout(fig, title)

def chart_evolucao(historico, norma, ordenar=True):
    if ordenar:
        historico = sorted(historico, key=lambda x: x["data_auditoria"])

    datas, pcts, absolutos = [], [], []    
    for h in historico:
        s = h["stats_total"]
        total = sum(s.values()) 
        conformes = s.get("Conforme", 0)
        pct = round(conformes/total*100,1) if total else 0
        datas.append(h["data_auditoria"])
        pcts.append(pct)
        absolutos.append(f"{conformes}/{total}")    
    
    fig=go.Figure(go.Scatter(
        x=datas, y=pcts, mode="lines+markers+text",
        line=dict(color=COLORS["Conforme"], width=3),
        marker=dict(color="#64b4ff", size=10, line=dict(color=COLORS["Conforme"], width=2)),
        text=[f"{p}% ({a})" for p, a in zip(pcts, absolutos)],
        textposition="top center",
        textfont=dict(color=TEXT,size=12),
        fill="tozeroy",fillcolor="rgba(26,111,212,0.15)",
        hovertemplate="<b>%{x}</b><br>%{y}%<extra></extra>"))
    
    fig.add_hline(y=70,line_dash="dash",line_color="rgba(255,255,255,0.3)",
                  annotation_text="Meta 70%",annotation_font_color=TEXT)
    
    fig.update_layout(xaxis=dict(gridcolor=GRID,color=TEXT),
                      yaxis=dict(gridcolor=GRID,color=TEXT,range=[0,105]),
                      height=int(STYLE.get("chart-height", 320)),
                      margin=dict(t=50,b=30,l=50,r=20)
    )

    return _layout(fig, f"Evolução da Conformidade — {norma}")

def chart_comparativo(auditorias, stats_list, ordenar=True):
    dados = []
    for g in stats_list[0].keys():
        nome = g.split(" - ")[0]
        grupo_dados = {"nome": nome}

        for aud, gs in zip(auditorias, stats_list):
            s = gs.get(g, {})
            aplicaveis = sum(s.values()) - s.get("Não aplica", 0)
            pct = round(s.get("Conforme", 0) / aplicaveis * 100, 1) if aplicaveis else 0
            grupo_dados[aud["data_auditoria"]] = {
                "pct": pct,
                "abs": f"{s.get('Conforme', 0)}/{aplicaveis}"
            }
        
        dados.append(grupo_dados)

    if ordenar:
        dados = sorted(dados, 
                       key=lambda d: max([v["pct"] for k, v in d.items() if k!="nome"]) - min([v["pct"] for k, v in d.items() if k!="nome"]),
                       reverse=True
        )

    nomes = [d["nome"] for d in dados]

    cor_grafico = ["#1f77b4", "#ff7f0e", "#9467bd", "#2ca02c", "#d62728"]
    fig=go.Figure()

    for i, aud in enumerate(auditorias):
        y = [d[aud["data_auditoria"]]["pct"] for d in dados]
        abs_valor = [d[aud["data_auditoria"]]["abs"] for d in dados]
        fig.add_trace(go.Bar(
            name = aud["data_auditoria"],
            x = nomes,
            y = y,
            marker_color = cor_grafico[i % len(cor_grafico)],
            opacity=0.9,
            text=[f"{p}%" for p, a in zip(y, abs_valor)],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y} (%{text})<extra></extra>"
        ))

    fig.update_layout(
        barmode="group",
        xaxis=dict(gridcolor="#ccc", color="#ccc"),
        yaxis=dict(gridcolor="#ccc", color="#ccc",range=[0,105], title="% Conformidade"),
        height = 400,
        margin = dict(t=50, b=90, l=50, r=10)
    )
    
    return fig

def radar_bytes(grupos_stats):
    cats = [g.split(" - ")[0] for g in grupos_stats]
    vals = []
    for s in grupos_stats.values():
        ap = sum(s.values()) - s.get("Não Aplica",0)
        vals.append(round(s.get("Conforme",0)/ap*100,1) if ap else 0)
    cats_closed = cats + [cats[0]]
    vals_closed = vals + [vals[0]]

    fig = go.Figure(go.Scatterpolar(
        r=vals_closed, theta=cats_closed,
        fill='toself', fillcolor='rgba(26,111,212,0.2)',
        line=dict(color='#1a6fd4', width=2),
        marker=dict(color='#1a6fd4', size=6),
    ))
    fig.update_layout(
        title="Radar de Conformidade por Grupo",
        polar=dict(radialaxis=dict(visible=True, range=[0,100],
                                   gridcolor="#e2e8f0", tickfont=dict(size=9)),
                   angularaxis=dict(gridcolor="#e2e8f0")),
        height=320, margin=dict(t=50,b=20,l=20,r=20)
    )
    return fig


def gauge_bytes(pct, meta=95):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        number=dict(suffix="%", font=dict(size=36, color="#1e293b")),
        title=dict(text="Índice de Conformidade", font=dict(size=14, color="#1e293b")),
        gauge=dict(
            axis=dict(range=[0,100], tickwidth=1, tickcolor="#64748b"),
            bar=dict(color="#1a6fd4"),
            bgcolor="white",
            borderwidth=2, bordercolor="#e2e8f0",
            steps=[
                dict(range=[0,40], color="#fee2e2"),
                dict(range=[40,70], color="#fef3c7"),
                dict(range=[70,100], color="#dcfce7"),
            ],
            threshold=dict(line=dict(color="#ef4444",width=4), thickness=0.75, value=meta),
        )
    ))
    fig.update_layout(height=260, margin=dict(t=50,b=20,l=30,r=30),
                      paper_bgcolor="white")
    
    return fig