import json
import os
import io
import csv
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import os
from precificacao import compute_pricing, carregar_totais_custos, TAXAS_MARKETPLACES, TAXAS_FIXAS


st.set_page_config(page_title="Calculadora de Precificação", page_icon="🧮", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f1720; }
    .stSidebar { background-color: #1f1b2e; }
    h1, h2, h3, h4, h5, h6 { color: #8e44ad !important; }
    .stButton>button { background-color: #8e44ad; color: #fff; }
    .stNumberInput>div>div>input { background-color: #0f1720; color: #fff; border-radius: 6px; border: 1px solid #3b1850; }
    </style>
""", unsafe_allow_html=True)

st.title('🧮 Calculadora de Precificação — Organizada')

# Sidebar: configurações globais
# Dicionário de difal por estado (exemplo, ajuste os valores conforme necessário)
difal_estados = {
    "sp": 0.04,
    "rj": 0.02,
    "mg": 0.03,
    "es": 0.025,
    "pr": 0.035,
    "sc": 0.03,
    "rs": 0.04,
}

with st.sidebar.form(key='config_form'):
    st.header('Configurações')
    usar_markup = st.checkbox('Usar markup (%)', value=True, key='usar_markup')
    markup_produto = st.number_input("Markup do produto (%)", min_value=0.0, value=20.0, step=0.1, key='markup_produto', disabled=not usar_markup)
    plataforma = st.selectbox("Plataforma", list(TAXAS_MARKETPLACES.keys()), index=0, key='plataforma')
    ml_listing = None
    if plataforma == 'mercado_livre':
        ml_listing = st.selectbox('Tipo de anúncio (Mercado Livre)', ['classico', 'premium'], index=0, key='ml_listing')
    imposto = st.number_input("Alíquota de imposto (ex: 0.10 = 10%)", min_value=0.0, value=0.10, step=0.01, key='imposto')
    estado_destino = st.selectbox("Estado destino", ['0'] + list(difal_estados.keys()), key='estado_destino')
    faturamento_esperado = st.number_input("Faturamento mensal esperado (R$)", min_value=0.01, value=10000.0, step=0.01, key='faturamento_esperado')
    faturamento_meta = st.number_input("Faturamento mensal desejado (R$)", min_value=0.0, value=10000.0, step=0.01, key='faturamento_meta')
    submit_config = st.form_submit_button('Aplicar')

    if estado_destino != '0':
        difal = difal_estados.get(estado_destino, 0.0)
    else:
        difal = 0.0

# Load stored costs
totais = carregar_totais_custos()
total_variavel = totais.get('total_variavel', 0.0)
total_fixo = totais.get('total_fixo', 0.0)

st.write(f"Soma custos variáveis: R$ {total_variavel:.2f} — Fixos: R$ {total_fixo:.2f}")

# show logo if exists
logo_path = os.path.join(os.getcwd(), 'logo.png')
if os.path.exists(logo_path):
    st.image(logo_path, width=200)

# Main layout: 3 columns (Inputs | Custos detalhados | Resultado)
col1, col2, col3 = st.columns([3, 3, 4])

with col1:
    st.subheader('Dados do Produto')
    custo_produto = st.number_input("Custo do produto (R$)", min_value=0.0, value=0.0, step=0.01, key='custo_produto')
    custo_embalagem = st.number_input("Custo embalagem (R$)", min_value=0.0, value=0.0, step=0.01, key='custo_embalagem')
    custo_frete = st.number_input("Custo frete (R$)", min_value=0.0, value=0.0, step=0.01, key='custo_frete')
    adicional = st.number_input("Adicional (R$)", min_value=0.0, value=0.0, step=0.01, key='adicional')
    lucro_desejado = st.number_input("Lucro desejado (R$)", min_value=0.0, value=0.0, step=0.01, key='lucro_desejado', disabled=usar_markup)

    st.markdown('---')
    if st.button('Calcular preço'):
        # trigger calculation
        resultado = compute_pricing(
            markup_produto=markup_produto,
            plataforma=plataforma,
            imposto=imposto,
            difal=difal,
            faturamento_esperado=faturamento_esperado,
            custo_produto=custo_produto,
            custo_embalagem=custo_embalagem,
            custo_frete=custo_frete,
            adicional=adicional,
            lucro_desejado=lucro_desejado,
            ml_listing=ml_listing,
            use_markup=usar_markup,
            total_variavel=total_variavel,
            total_fixo=total_fixo,
        )
        st.session_state['resultado'] = resultado

with col2:
    st.subheader('Custos detalhados (editar)')
    with st.expander('Custos Variáveis'):
        # allow editing of loaded custos_variaveis.json via simple inputs
        try:
            with open('custos_variaveis.json', 'r', encoding='utf-8') as f:
                custos_var = json.load(f)
        except Exception:
            custos_var = {}
        for k, v in custos_var.items():
            novo = st.number_input(f"{k}", min_value=0.0, value=float(v or 0.0), step=0.01, key=f"var_{k}")
            custos_var[k] = novo
        if st.button('Salvar custos variáveis'):
            with open('custos_variaveis.json', 'w', encoding='utf-8') as f:
                json.dump(custos_var, f, ensure_ascii=False, indent=2)
            st.success('Custos variáveis salvos')

    with st.expander('Custos Fixos'):
        try:
            with open('custos_fixos.json', 'r', encoding='utf-8') as f:
                custos_fix = json.load(f)
        except Exception:
            custos_fix = {}
        for k, v in custos_fix.items():
            novo = st.number_input(f"{k}", min_value=0.0, value=float(v or 0.0), step=0.01, key=f"fix_{k}")
            custos_fix[k] = novo
        if st.button('Salvar custos fixos'):
            with open('custos_fixos.json', 'w', encoding='utf-8') as f:
                json.dump(custos_fix, f, ensure_ascii=False, indent=2)
            st.success('Custos fixos salvos')

with col3:
    st.subheader('Resultado')
    resultado = st.session_state.get('resultado')
    if resultado:
        st.metric('Preço sugerido', f"R$ {resultado['preco_venda']:.2f}")
        st.write(f"Valor faturamento: R$ {resultado['valor_faturamento']:.2f}")
        st.write(f"Valor lucro: R$ {resultado['valor_lucro']:.2f} — Margem: {resultado['margem_percentual']:.2f}%")
        # Opção: mostrar fluxo por pedido (faturamento - custos = lucro líquido)
        mostrar_fluxo = st.checkbox('Mostrar fluxo por pedido (Faturamento - Custos = Lucro líquido)', value=False)
        if mostrar_fluxo:
            # custos totais por venda = custos diretos por venda + taxas totais em reais
            custos_totais_por_venda = resultado.get('custos_diretos_por_venda', 0.0) + resultado.get('taxas_totais_em_reais', 0.0)
            faturamento = resultado.get('preco_venda', 0.0)
            lucro_liquido = resultado.get('valor_lucro', 0.0)
            st.markdown('**Fluxo por pedido**')
            st.write(f"Faturamento (preço de venda): R$ {faturamento:.2f}")
            st.write(f"Custos totais (diretos + taxas): R$ {custos_totais_por_venda:.2f}")
            st.write(f"Lucro líquido: R$ {lucro_liquido:.2f}")
            st.write(f"\nEquação: R$ {faturamento:.2f} - R$ {custos_totais_por_venda:.2f} = R$ {lucro_liquido:.2f}")
        # Visualização do Lucro Real (métrica + gráfico)
        custos_totais_por_venda = resultado.get('custos_diretos_por_venda', 0.0) + resultado.get('taxas_totais_em_reais', 0.0)
        faturamento = resultado.get('preco_venda', 0.0)
        lucro_liquido = resultado.get('valor_lucro', 0.0)
        st.markdown('---')
        st.subheader('Lucro real por pedido')
        # métrica destacada
        st.metric(label='Lucro líquido (R$)', value=f"R$ {lucro_liquido:.2f}", delta=f"{resultado.get('margem_percentual',0.0):.2f}%")
        # gráfico simples comparando faturamento / custos / lucro
        df = pd.DataFrame({'Valor': [faturamento, custos_totais_por_venda, lucro_liquido]}, index=['Faturamento', 'Custos', 'Lucro'])
        st.bar_chart(df)
        # Export buttons (CSV / PDF)
        col_a, col_b = st.columns(2)

        def build_csv_bytes(res):
            s = io.StringIO()
            writer = csv.writer(s, delimiter=',')
            writer.writerow(['campo', 'valor'])
            writer.writerow(['preco_venda', f"{res.get('preco_venda', 0.0):.2f}"])
            writer.writerow(['valor_faturamento', f"{res.get('valor_faturamento', 0.0):.2f}"])
            writer.writerow(['valor_lucro', f"{res.get('valor_lucro', 0.0):.2f}"])
            writer.writerow(['margem_percentual', f"{res.get('margem_percentual', 0.0):.2f}"])
            writer.writerow([])
            writer.writerow(['detalhamento', 'valor'])
            for k, v in res.get('breakdown', {}).items():
                writer.writerow([k, f"{v}"])
            return s.getvalue().encode('utf-8')

        csv_bytes = build_csv_bytes(resultado)
        col_a.download_button('Exportar resumo CSV', data=csv_bytes, file_name='resumo_precificacao.csv', mime='text/csv')

        # PDF export (optional - requires reportlab)
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            def build_pdf_bytes(res):
                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
                styles = getSampleStyleSheet()
                styles.add(ParagraphStyle(name='ReportTitle', parent=styles['Title'], fontSize=20, leading=24, spaceAfter=10))
                styles.add(ParagraphStyle(name='ReportSub', parent=styles['Normal'], fontSize=11, leading=14, spaceAfter=6))
                styles.add(ParagraphStyle(name='Metric', parent=styles['Normal'], fontSize=13, leading=15, spaceAfter=4))
                story = []

                # Header with optional logo and title
                logo_width = 80
                title = Paragraph('<b>Resumo de Precificação</b>', styles['ReportTitle'])
                header_cells = []
                logo_path_local = os.path.join(os.getcwd(), 'logo.png')
                if os.path.exists(logo_path_local):
                    try:
                        img = Image.open(logo_path_local)
                        aspect = img.height / img.width
                        img_w = logo_width
                        img_h = int(img_w * aspect)
                        img_buf = io.BytesIO()
                        img.resize((img_w, img_h)).save(img_buf, format='PNG')
                        img_buf.seek(0)
                        from reportlab.platypus import Image as RLImage
                        rl_img = RLImage(img_buf, width=img_w, height=img_h)
                        header_cells = [[rl_img, title]]
                    except Exception:
                        header_cells = [[Paragraph('', styles['Normal']), title]]
                else:
                    header_cells = [[Paragraph('', styles['Normal']), title]]

                header_table = Table(header_cells, colWidths=[logo_width, 420])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 6),
                    ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(header_table)
                story.append(Spacer(1, 8))

                # Key metrics highlighted
                preco = f"R$ {res.get('preco_venda', 0.0):.2f}"
                fatur = f"R$ {res.get('valor_faturamento', 0.0):.2f}"
                lucro = f"R$ {res.get('valor_lucro', 0.0):.2f}"
                margem = f"{res.get('margem_percentual', 0.0):.2f}%"
                metrics = [[Paragraph('<b>Preço sugerido</b>', styles['ReportSub']), Paragraph(preco, styles['Metric'])],
                           [Paragraph('<b>Faturamento</b>', styles['ReportSub']), Paragraph(fatur, styles['Metric'])],
                           [Paragraph('<b>Lucro líquido</b>', styles['ReportSub']), Paragraph(lucro, styles['Metric'])],
                           [Paragraph('<b>Margem</b>', styles['ReportSub']), Paragraph(margem, styles['Metric'])]]
                metrics_tbl = Table(metrics, colWidths=[300, 140])
                metrics_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(metrics_tbl)
                story.append(Spacer(1, 12))

                # Breakdown table with zebra striping and right-aligned numbers
                bd = [['Quebra', 'Valor']]
                for k, v in res.get('breakdown', {}).items():
                    bd.append([str(k), f"R$ {v}"])
                bd_tbl = Table(bd, colWidths=[320, 120])
                bd_style = TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d2d2d')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
                    ('LEFTPADDING', (0,0), (-1,-1), 6),
                    ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ])
                for i in range(1, len(bd)):
                    if i % 2 == 1:
                        bd_style.add('BACKGROUND', (0,i), (-1,i), colors.whitesmoke)
                bd_tbl.setStyle(bd_style)
                story.append(bd_tbl)

                # Add matplotlib charts: composition and units needed
                try:
                    custos = res.get('custos_diretos_por_venda', 0.0) + res.get('taxas_totais_em_reais', 0.0)
                    lucro_val = res.get('valor_lucro', 0.0)
                    labels = ['Custos', 'Lucro']
                    vals = [max(custos, 0.0), max(lucro_val, 0.0)]
                    fig1, ax1 = plt.subplots(figsize=(4, 3))
                    ax1.pie(vals, labels=labels, autopct='%1.1f%%', colors=['#4c72b0', '#dd8452'])
                    ax1.set_title('Composição por venda')
                    buf1 = io.BytesIO()
                    fig1.tight_layout()
                    fig1.savefig(buf1, format='png', dpi=150)
                    plt.close(fig1)
                    buf1.seek(0)
                    from reportlab.platypus import Image as RLImage
                    story.append(RLImage(buf1, width=360, height=270))

                    # units needed
                    try:
                        faturamento_meta_local = float(st.session_state.get('faturamento_meta', faturamento_esperado))
                        preco_unit = res.get('preco_venda', 0.0)
                        unidades = faturamento_meta_local / preco_unit if preco_unit > 0 else 0
                        fig2, ax2 = plt.subplots(figsize=(6, 2.5))
                        ax2.bar(['Unidades necessárias'], [unidades], color='#2ca02c')
                        ax2.set_ylabel('Unidades')
                        ax2.set_title('Unidades aproximadas por mês para meta de faturamento')
                        for i, v in enumerate([unidades]):
                            ax2.text(i, v + max(v * 0.01, 1), f"{v:.1f}", ha='center')
                        buf2 = io.BytesIO()
                        fig2.tight_layout()
                        fig2.savefig(buf2, format='png', dpi=150)
                        plt.close(fig2)
                        buf2.seek(0)
                        story.append(Spacer(1, 12))
                        story.append(RLImage(buf2, width=400, height=140))
                    except Exception:
                        pass
                except Exception:
                    pass

                doc.build(story)
                buf.seek(0)
                return buf.getvalue()

            pdf_bytes = build_pdf_bytes(resultado)
            col_b.download_button('Exportar resumo PDF', data=pdf_bytes, file_name='resumo_precificacao.pdf', mime='application/pdf')
        except Exception:
            col_b.info('Para habilitar exportação em PDF, instale: pip install reportlab')
        st.markdown('**Quebra de custos e taxas**')
        for k, v in resultado['breakdown'].items():
            st.write(f"{k}: R$ {v}")
    else:
        st.info('Preencha os dados na coluna "Dados do Produto" e clique em Calcular preço.')
