import io
import plotly.graph_objects as go
import traceback
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image, HRFlowable, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import PageBreak
from datetime import datetime
from components.charts import chart_barras_grupos, chart_comparativo, chart_percentual_grupos, chart_pizza_total, radar_bytes, gauge_bytes

AZUL       = colors.HexColor("#1a6fd4")
AZUL_ESC   = colors.HexColor("#0d4fa3")
AZUL_CLAR  = colors.HexColor("#dbeafe")
VERDE      = colors.HexColor("#22c55e")
VERDE_CLAR = colors.HexColor("#dcfce7")
VERM       = colors.HexColor("#ef4444")
VERM_CLAR  = colors.HexColor("#fee2e2")
AMAR       = colors.HexColor("#f59e0b")
AMAR_CLAR  = colors.HexColor("#fef3c7")
CINZA      = colors.HexColor("#64748b")
CINZA_CLAR = colors.HexColor("#f1f5f9")
CINZA_MED  = colors.HexColor("#e2e8f0")
PRETO      = colors.HexColor("#1e293b")
BRANCO     = colors.white


def _fig_para_bytes(fig):
    fig.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(color="#1e293b"),
        legend=dict(font=dict(color="#1e293b"), bgcolor="white"),
        title=dict(font=dict(color="#1e293b")),
    )
    for ax in ("xaxis","yaxis","xaxis2","yaxis2"):
        try: fig.update_layout({ax: dict(gridcolor="#e2e8f0", color="#1e293b")})
        except: pass
    return fig.to_image(format="png", width=700, height=320, scale=2)


def _estilos():
    base = getSampleStyleSheet()
    estilos = {
        "titulo": ParagraphStyle("titulo", parent=base["Title"],
            fontSize=22, textColor=BRANCO, alignment=TA_LEFT,
            fontName="Helvetica-Bold", spaceAfter=4),
        "subtitulo": ParagraphStyle("subtitulo", parent=base["Normal"],
            fontSize=10, textColor=colors.HexColor("#bfdbfe"), alignment=TA_LEFT,
            fontName="Helvetica", spaceAfter=0),
        "h2": ParagraphStyle("h2", parent=base["Heading2"],
            fontSize=13, textColor=AZUL_ESC, fontName="Helvetica-Bold",
            spaceBefore=14, spaceAfter=6,
            borderPad=4, leftIndent=0),
        "h3": ParagraphStyle("h3", parent=base["Heading3"],
            fontSize=11, textColor=PRETO, fontName="Helvetica-Bold",
            spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["Normal"],
            fontSize=9, textColor=PRETO, fontName="Helvetica",
            spaceAfter=3, leading=13),
        "caption": ParagraphStyle("caption", parent=base["Normal"],
            fontSize=8, textColor=CINZA, fontName="Helvetica",
            alignment=TA_CENTER, spaceAfter=6),
        "rodape": ParagraphStyle("rodape", parent=base["Normal"],
            fontSize=7, textColor=CINZA, fontName="Helvetica", alignment=TA_CENTER),
        "kpi_val": ParagraphStyle("kpi_val", parent=base["Normal"],
            fontSize=22, textColor=AZUL, fontName="Helvetica-Bold", alignment=TA_CENTER),
        "kpi_lbl": ParagraphStyle("kpi_lbl", parent=base["Normal"],
            fontSize=7.5, textColor=CINZA, fontName="Helvetica",
            alignment=TA_CENTER, spaceAfter=0),
        "badge_conf": ParagraphStyle("badge_conf", parent=base["Normal"],
            fontSize=8, textColor=colors.HexColor("#166534"),
            fontName="Helvetica-Bold", alignment=TA_CENTER),
        "badge_nc": ParagraphStyle("badge_nc", parent=base["Normal"],
            fontSize=8, textColor=colors.HexColor("#991b1b"),
            fontName="Helvetica-Bold", alignment=TA_CENTER),
        "badge_ea": ParagraphStyle("badge_ea", parent=base["Normal"],
            fontSize=8, textColor=colors.HexColor("#92400e"),
            fontName="Helvetica-Bold", alignment=TA_CENTER),
        "badge_na": ParagraphStyle("badge_na", parent=base["Normal"],
            fontSize=8, textColor=CINZA, fontName="Helvetica", alignment=TA_CENTER),
    }
    return estilos


def _status_style(status, em_and, estilos):
    if status == "Conforme":
        return Paragraph("Conforme", estilos["badge_conf"]), VERDE_CLAR
    elif status == "Não Conforme" and em_and:
        return Paragraph("⟳ Em Andamento", estilos["badge_ea"]), AMAR_CLAR
    elif status == "Não Conforme":
        return Paragraph("Não Conforme", estilos["badge_nc"]), VERM_CLAR
    else:
        return Paragraph("— Não Aplica", estilos["badge_na"]), CINZA_CLAR

def gerar_pdf(aud, stats, grupos_stats, controles_dict,
              grupos_exibir=None, aud_anterior=None, meta=95):
    
    buffer = io.BytesIO()
    norma = aud.get("norma","27001")
    pct = round(stats.get("Conforme",0) /
                max(sum(stats.values())-stats.get("Não Aplica",0),1) * 100, 1)

    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Relatório PSI-SI — {aud.get('empresa','')}",
        author=aud.get("auditor","PSI-SI"))

    W = A4[0] - 3.6*cm 
    es = _estilos()
    story = []

    capa_data = [[
        Table([[
            Paragraph(f"🛡️ PSI-SI", es["titulo"]),
            Paragraph("Relatório de Conformidade", es["subtitulo"]),
            Spacer(1,6),
            Paragraph(f"ISO/IEC {norma}", es["subtitulo"]),
        ]], colWidths=[W], rowHeights=None)
    ]]
    capa = Table(capa_data, colWidths=[W])
    capa.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), AZUL_ESC),
        ("TOPPADDING", (0,0),(-1,-1), 18),
        ("BOTTOMPADDING", (0,0),(-1,-1), 18),
        ("LEFTPADDING", (0,0),(-1,-1), 18),
        ("RIGHTPADDING", (0,0),(-1,-1), 18),
        ("ROUNDEDCORNERS", (0,0),(-1,-1), 8),
    ]))
    story.append(capa)
    story.append(Spacer(1, 0.5*cm))

    meta = [
        ["Empresa / Organização", aud.get("empresa","—"),
         "Data da Auditoria", aud.get("data_auditoria","—")],
        ["Auditor Responsável", aud.get("auditor","—"),
         "Norma Avaliada", f"ISO/IEC {norma}"],
        ["Cenário / Escopo", aud.get("cenario","—"), "Gerado em",
         datetime.now().strftime("%d/%m/%Y %H:%M")],
    ]
    t_meta = Table(meta, colWidths=[3.5*cm, W/2-3.5*cm, 3.2*cm, W/2-3.2*cm])
    t_meta.setStyle(TableStyle([
        ("FONTNAME",    (0,0),(-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0),(-1,-1), 8),
        ("FONTNAME",    (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",    (2,0),(2,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",   (0,0),(0,-1), AZUL),
        ("TEXTCOLOR",   (2,0),(2,-1), AZUL),
        ("BACKGROUND",  (0,0),(-1,-1), CINZA_CLAR),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[CINZA_CLAR, BRANCO]),
        ("GRID",        (0,0),(-1,-1), 0.3, CINZA_MED),
        ("TOPPADDING",  (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0),(-1,-1), 7),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Resumo Executivo", es["h2"]))
    story.append(HRFlowable(width=W, thickness=1, color=AZUL_CLAR, spaceAfter=8))

    kpi_items = [
        (f"{pct}%", "Conformidade Geral", AZUL, AZUL_CLAR),
        (str(stats.get("Conforme",0)), "Conformes", VERDE, VERDE_CLAR),
        (str(stats.get("Não Conforme",0)), "Não Conformes", VERM, VERM_CLAR),
        (str(stats.get("Em Andamento",0)), "Em Andamento", AMAR, AMAR_CLAR),
        (str(stats.get("Não Aplica",0)), "Não Aplica", CINZA, CINZA_MED),
    ]
    kpi_row = []
    for val, lbl, cor, bg in kpi_items:
        cell = Table([[Paragraph(val, ParagraphStyle("kv", fontSize=20,
                        textColor=cor, fontName="Helvetica-Bold", alignment=TA_CENTER))],
                      [Paragraph(lbl, es["kpi_lbl"])]],
                     colWidths=[W/5-0.3*cm])
        cell.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), bg),
            ("TOPPADDING",(0,0),(-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
            ("ROUNDEDCORNERS",(0,0),(-1,-1), 6),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ]))
        kpi_row.append(cell)
    t_kpi = Table([kpi_row], colWidths=[W/5]*5)
    t_kpi.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))
    story.append(t_kpi)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Dashboard de Conformidade", es["h2"]))
    story.append(HRFlowable(width=W, thickness=1, color=AZUL_CLAR, spaceAfter=8))

    # IMPORTANTE: Garanta que você importou essas funções no topo do arquivo:
    # from components.charts import chart_gauge, chart_pizza, chart_barras, chart_percentual_grupos, chart_radar

    try:
        # Chamando as funções reais do seu sistema e convertendo com fig_para_bytes
        img_gauge = Image(io.BytesIO(_fig_para_bytes(gauge_bytes(pct, meta=95))), width=W*0.45, height=5*cm)
        img_pizza = Image(io.BytesIO(_fig_para_bytes(chart_pizza_total(stats))), width=W*0.45, height=5*cm)
        
        row1 = Table([[img_gauge, img_pizza]], colWidths=[W*0.46, W*0.54])
        row1.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                   ("LEFTPADDING",(0,0),(-1,-1),2),
                                   ("RIGHTPADDING",(0,0),(-1,-1),2)]))
        story.append(row1)
        story.append(Spacer(1, 0.3*cm))
    except Exception as e:
        traceback.print_exc()
        story.append(Paragraph(f"[Gráfico Gauge/Pizza indisponível: {e}]", es["body"]))

    try:
        img_barras = Image(io.BytesIO(_fig_para_bytes(chart_barras_grupos(grupos_stats))), width=W, height=7*cm)
        story.append(img_barras)
        story.append(Paragraph("Controles avaliados por grupo e status", es["caption"]))
        story.append(Spacer(1, 0.2*cm))
    except Exception as e:
        story.append(Paragraph(f"[Gráfico Barras indisponível: {e}]", es["body"]))

    try:
        h_pct = max(5.5*cm, len(grupos_stats)*1.1*cm + 1.5*cm)
        # Note que aqui passamos a meta também
        img_pct = Image(io.BytesIO(_fig_para_bytes(chart_percentual_grupos(grupos_stats, meta=95))), width=W, height=h_pct)
        story.append(img_pct)
        story.append(Paragraph("Percentual de conformidade por grupo (linha vermelha = meta 95%)", es["caption"]))
        story.append(Spacer(1, 0.2*cm))
    except Exception as e:
        traceback.print_exc()
        story.append(Paragraph(f"[Gráfico Percentual indisponível: {e}]", es["body"]))

    if len(grupos_stats) >= 3:
        try:
            img_radar = Image(io.BytesIO(_fig_para_bytes(radar_bytes(grupos_stats))), width=W*0.7, height=7*cm)
            t_radar = Table([[img_radar]], colWidths=[W*0.7])
            t_radar.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")]))
            story.append(t_radar)
            story.append(Paragraph("Radar de conformidade por categoria de controles", es["caption"]))
        except Exception as e:
            traceback.print_exc()
            story.append(Paragraph(f"[Radar indisponível: {e}]", es["body"]))

    story.append(PageBreak())
    story.append(Paragraph("Resultados por Grupo de Controles", es["h2"]))
    story.append(HRFlowable(width=W, thickness=1, color=AZUL_CLAR, spaceAfter=8))

    cab = [Paragraph(c, ParagraphStyle("th", fontSize=8, fontName="Helvetica-Bold",
                     textColor=BRANCO, alignment=TA_CENTER))
           for c in ["Grupo","Conformes","Não Conformes","Em Andamento","Não Aplica","% Conformidade"]]
    rows_grupo = [cab]
    for g, s in grupos_stats.items():
        ap = sum(s.values()) - s.get("Não Aplica",0)
        pg = round(s.get("Conforme",0)/ap*100,1) if ap else 0
        cor_pg = VERDE if pg>=70 else AMAR if pg>=40 else VERM
        rows_grupo.append([
            Paragraph(g, ParagraphStyle("td", fontSize=7.5, fontName="Helvetica")),
            Paragraph(str(s.get("Conforme",0)), ParagraphStyle("tdc",fontSize=8,
                      fontName="Helvetica-Bold",textColor=VERDE,alignment=TA_CENTER)),
            Paragraph(str(s.get("Não Conforme",0)), ParagraphStyle("tdc",fontSize=8,
                      fontName="Helvetica-Bold",textColor=VERM,alignment=TA_CENTER)),
            Paragraph(str(s.get("Em Andamento",0)), ParagraphStyle("tdc",fontSize=8,
                      fontName="Helvetica-Bold",textColor=AMAR,alignment=TA_CENTER)),
            Paragraph(str(s.get("Não Aplica",0)), ParagraphStyle("tdc",fontSize=8,
                      fontName="Helvetica",textColor=CINZA,alignment=TA_CENTER)),
            Paragraph(f"{pg}%", ParagraphStyle("tdc",fontSize=9,
                      fontName="Helvetica-Bold",textColor=cor_pg,alignment=TA_CENTER)),
        ])
    cw = [W*0.32, W*0.12, W*0.15, W*0.14, W*0.12, W*0.15]
    t_grupo = Table(rows_grupo, colWidths=cw, repeatRows=1)
    t_grupo.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), AZUL_ESC),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[BRANCO, CINZA_CLAR]),
        ("GRID",          (0,0),(-1,-1), 0.3, CINZA_MED),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LINEBELOW",     (0,0),(-1,0), 1.5, AZUL),
    ]))
    story.append(t_grupo)
    story.append(Spacer(1, 0.6*cm))

    exibir = grupos_exibir if grupos_exibir else controles_dict
    respostas = aud.get("respostas", {})

    for grupo, lista in exibir.items():
        story.append(Paragraph(grupo, es["h3"]))
        gs = grupos_stats.get(grupo,{})
        ap = sum(gs.values()) - gs.get("Não Aplica",0)
        pg = round(gs.get("Conforme",0)/ap*100,1) if ap else 0
        story.append(Paragraph(
            f"Conformidade do grupo: <b>{pg}%</b>  |  "
            f"{gs.get('Conforme',0)} conformes de {ap} aplicáveis", es["body"]))

        cab2 = [Paragraph(c, ParagraphStyle("th2", fontSize=7.5, fontName="Helvetica-Bold",
                           textColor=BRANCO, alignment=TA_CENTER))
                for c in ["Código","Controle","Status"]]
        rows_ctrl = [cab2]
        for codigo, nome in lista:
            v = respostas.get(codigo, {})
            status = v.get("status","Não Aplica")
            em_and = v.get("em_andamento", False)
            badge, bg = _status_style(status, em_and, es)
            rows_ctrl.append([
                Paragraph(codigo, ParagraphStyle("cod",fontSize=7.5,
                           fontName="Helvetica-Bold",textColor=AZUL,alignment=TA_CENTER)),
                Paragraph(nome, ParagraphStyle("nm",fontSize=7.5,fontName="Helvetica")),
                badge,
            ])
        t_ctrl = Table(rows_ctrl, colWidths=[W*0.12, W*0.67, W*0.21], repeatRows=1)

        row_styles = [("BACKGROUND",(0,0),(-1,0), AZUL),
                      ("GRID",(0,0),(-1,-1), 0.3, CINZA_MED),
                      ("TOPPADDING",(0,0),(-1,-1), 4),
                      ("BOTTOMPADDING",(0,0),(-1,-1), 4),
                      ("LEFTPADDING",(0,0),(-1,-1), 5),
                      ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                      ("LINEBELOW",(0,0),(-1,0), 1, AZUL_ESC)]
        for i, (codigo, _) in enumerate(lista, 1):
            v = respostas.get(codigo, {})
            status = v.get("status","Não Aplica")
            em_and = v.get("em_andamento", False)
            if i % 2 == 0:
                row_styles.append(("BACKGROUND",(0,i),(-1,i), CINZA_CLAR))
            if status == "Conforme":
                row_styles.append(("BACKGROUND",(2,i),(2,i), VERDE_CLAR))
            elif status == "Não Conforme" and em_and:
                row_styles.append(("BACKGROUND",(2,i),(2,i), AMAR_CLAR))
            elif status == "Não Conforme":
                row_styles.append(("BACKGROUND",(2,i),(2,i), VERM_CLAR))
        t_ctrl.setStyle(TableStyle(row_styles))
        story.append(KeepTogether([t_ctrl]))
        story.append(Spacer(1, 0.4*cm))

    nc_list = []
    for grupo, lista in exibir.items():
        for codigo, nome in lista:
            v = respostas.get(codigo,{})
            if v.get("status") == "Não Conforme":
                nc_list.append((grupo.split(" - ")[0], codigo, nome, v.get("em_andamento",False)))

    if nc_list:
        story.append(PageBreak())
        story.append(Paragraph("⚠ Não Conformidades Identificadas", es["h2"]))
        story.append(HRFlowable(width=W, thickness=1, color=VERM, spaceAfter=8))
        story.append(Paragraph(
            f"Total de não conformidades: <b>{len(nc_list)}</b>  |  "
            f"Em andamento: <b>{sum(1 for x in nc_list if x[3])}</b>  |  "
            f"Pendentes: <b>{sum(1 for x in nc_list if not x[3])}</b>", es["body"]))
        story.append(Spacer(1,0.3*cm))

        cab_nc = [Paragraph(c, ParagraphStyle("th_nc",fontSize=7.5,fontName="Helvetica-Bold",
                              textColor=BRANCO,alignment=TA_CENTER))
                  for c in ["#","Grupo","Código","Controle","Em Andamento"]]
        rows_nc = [cab_nc]
        for i,(grp,cod,nm,ea) in enumerate(nc_list,1):
            rows_nc.append([
                Paragraph(str(i), ParagraphStyle("n",fontSize=7.5,alignment=TA_CENTER)),
                Paragraph(grp, ParagraphStyle("g",fontSize=7.5)),
                Paragraph(cod, ParagraphStyle("c",fontSize=7.5,fontName="Helvetica-Bold",textColor=AZUL,alignment=TA_CENTER)),
                Paragraph(nm, ParagraphStyle("nm",fontSize=7.5)),
                Paragraph("⟳ Sim" if ea else "✖ Não",
                          ParagraphStyle("ea",fontSize=8,fontName="Helvetica-Bold",
                          textColor=colors.HexColor("#92400e") if ea else VERM,
                          alignment=TA_CENTER)),
            ])
        t_nc = Table(rows_nc, colWidths=[W*0.05,W*0.18,W*0.10,W*0.55,W*0.12], repeatRows=1)
        nc_styles = [
            ("BACKGROUND",(0,0),(-1,0),VERM),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[BRANCO,VERM_CLAR]),
            ("GRID",(0,0),(-1,-1),0.3,CINZA_MED),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LEFTPADDING",(0,0),(-1,-1),5),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ]
        for i,(_,_,_,ea) in enumerate(nc_list,1):
            if ea:
                nc_styles.append(("BACKGROUND",(4,i),(4,i),AMAR_CLAR))
        t_nc.setStyle(TableStyle(nc_styles))
        story.append(t_nc)

    if aud_anterior:
        story.append(PageBreak())
        story.append(Paragraph("Comparativo com Auditoria Anterior", es["h2"]))
        story.append(HRFlowable(width=W, thickness=1, color=AZUL_CLAR, spaceAfter=8))

        gs_ant = aud_anterior.get("stats_grupos",{})
        rows_comp = [[
            Paragraph(c, ParagraphStyle("th",fontSize=7.5,fontName="Helvetica-Bold",
                       textColor=BRANCO,alignment=TA_CENTER))
            for c in ["Grupo", f"% {aud_anterior.get('data_auditoria','Anterior')}",
                      f"% {aud.get('data_auditoria','Atual')}", "Δ Evolução"]
        ]]
        for g in grupos_stats:
            s_cur = grupos_stats[g]; s_ant = gs_ant.get(g,{})
            a_c = sum(s_cur.values())-s_cur.get("Não Aplica",0)
            a_a = sum(s_ant.values())-s_ant.get("Não Aplica",0) if s_ant else 0
            p_c = round(s_cur.get("Conforme",0)/a_c*100,1) if a_c else 0
            p_a = round(s_ant.get("Conforme",0)/a_a*100,1) if a_a else 0
            delta = round(p_c - p_a, 1)
            cor_d = VERDE if delta>0 else VERM if delta<0 else CINZA
            rows_comp.append([
                Paragraph(g, ParagraphStyle("td",fontSize=7.5)),
                Paragraph(f"{p_a}%", ParagraphStyle("tc",fontSize=8,alignment=TA_CENTER)),
                Paragraph(f"{p_c}%", ParagraphStyle("tc",fontSize=8,
                           fontName="Helvetica-Bold",alignment=TA_CENTER)),
                Paragraph(f"{'+'if delta>=0 else ''}{delta}%",
                          ParagraphStyle("td",fontSize=9,fontName="Helvetica-Bold",
                          textColor=cor_d,alignment=TA_CENTER)),
            ])
        t_comp = Table(rows_comp, colWidths=[W*0.40,W*0.18,W*0.18,W*0.24], repeatRows=1)
        t_comp.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),AZUL_ESC),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[BRANCO,CINZA_CLAR]),
            ("GRID",(0,0),(-1,-1),0.3,CINZA_MED),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),6),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ]))
        story.append(t_comp)

    def _rodape(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(CINZA)
        canvas.drawString(1.8*cm, 1.3*cm,
            f"PSI-SI — {aud.get('empresa','')} | ISO/IEC {norma} | "
            f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(A4[0]-1.8*cm, 1.3*cm,
            f"Página {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=_rodape, onLaterPages=_rodape)
    buffer.seek(0)
    return buffer.read()