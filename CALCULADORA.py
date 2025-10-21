import json
import os
import streamlit as st
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
    markup_produto = st.number_input("Markup do produto (%)", min_value=0.0, value=20.0, step=0.1, key='markup_produto')
    plataforma = st.selectbox("Plataforma", list(TAXAS_MARKETPLACES.keys()), index=0, key='plataforma')
    imposto = st.number_input("Alíquota de imposto (ex: 0.10 = 10%)", min_value=0.0, value=0.10, step=0.01, key='imposto')
    estado_destino = st.selectbox("Estado destino", ['0'] + list(difal_estados.keys()), key='estado_destino')
    faturamento_esperado = st.number_input("Faturamento mensal esperado (R$)", min_value=0.01, value=10000.0, step=0.01, key='faturamento_esperado')
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

# Main layout: 3 columns (Inputs | Custos detalhados | Resultado)
col1, col2, col3 = st.columns([3, 3, 4])

with col1:
    st.subheader('Dados do Produto')
    custo_produto = st.number_input("Custo do produto (R$)", min_value=0.0, value=0.0, step=0.01, key='custo_produto')
    custo_embalagem = st.number_input("Custo embalagem (R$)", min_value=0.0, value=0.0, step=0.01, key='custo_embalagem')
    custo_frete = st.number_input("Custo frete (R$)", min_value=0.0, value=0.0, step=0.01, key='custo_frete')
    adicional = st.number_input("Adicional (R$)", min_value=0.0, value=0.0, step=0.01, key='adicional')
    lucro_desejado = st.number_input("Lucro desejado (R$)", min_value=0.0, value=0.0, step=0.01, key='lucro_desejado')

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
        st.markdown('**Quebra de custos e taxas**')
        for k, v in resultado['breakdown'].items():
            st.write(f"{k}: R$ {v}")
    else:
        st.info('Preencha os dados na coluna "Dados do Produto" e clique em Calcular preço.')
