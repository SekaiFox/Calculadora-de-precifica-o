import json
import os
import pandas as pd
import streamlit as st
import openpyxl

st.set_page_config(page_title="Calculadora de Precificação", page_icon="🧮", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #18181b;
    }
    .stButton>button {
        background-color: #8e44ad;
        color: #fff;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #6c3483;
        color: #fff;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #8e44ad !important;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #18181b;
        color: #fff;
        border-radius: 6px;
        border: 1px solid #8e44ad;
    }
    .stAlert {
        border-radius: 8px;
    }
    /* Expander */
    .st-expanderHeader {
        color: #8e44ad !important;
    }
    /* Caixa dos widgets */
    section[data-testid="stSidebar"] {
        background-color: #2d033b !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title('🧮 Calculadora de Precificação para E-commerce')

# Dicionário de taxas base por marketplace
taxas_marketplaces = {
    'shopee': 0.15,
    'mercado_livre': 0.19,
    'olx': 0.12,
    'magalu': 0.15,
    'mercado_pago': 0.05,
    'shein': 0.16,
    'b2w': 0.19,
    'olist': 0.23
}
taxas_fixas = {
    'shopee': 4.00
}

imposto = 0.10

# Dicionário de difal por estado (exemplo, ajuste os valores conforme necessário)
difal_estados = {
    "sp": 0.04,
    "rj": 0.02,
    "mg": 0.03,
    "es": 0.025,
    "pr": 0.035,
    "sc": 0.03,
    "rs": 0.04,
    # Adicione outros estados conforme necessário
}

# Corrija a entrada do markup para garantir que seja float
markup_produto = st.number_input("Digite o markup do produto (ex: 20 para 20%): ", min_value=0.0, step=0.1, key="markup_produto")

# Seleção da plataforma
plataforma = st.selectbox("Escolha a plataforma:", list(taxas_marketplaces.keys()), key="plataforma")
taxa_plataforma = taxas_marketplaces[plataforma]
st.write(f"Taxa da plataforma {plataforma}: {taxa_plataforma * 100:.1f}%")

# Seleção do estado de destino
estado_destino = st.selectbox("Escolha o estado de destino:", ["0"] + list(difal_estados.keys()), key="estado_destino")
if estado_destino != "0":
    difal = difal_estados[estado_destino]
    st.write(f"Difal para {estado_destino.upper()}: {difal * 100:.2f}%")
else:
    difal = 0.0
    st.write("Estado não cadastrado. Difal considerado 0%.")

# Listas de custos
custos_variaveis = [
    "ALIMENTAÇÃO", "GASOLINA", "TRANSPORTE", "PRODUTOS DE LIMPEZA", "MARKETING",
    "MANUTENÇÃO", "GASTOS CORPORATIVOS", "EMBALAGEM", "ICMS", "RETIRADA MENSAL",
    "LOGISTICA", "MATERIAIS", "OUTROS"
 ]

custos_fixos = [
    "AGUA", "LUZ", "INTERNET", "TELEFONE", "ESPAÇO FISICO ALUGUEL",
    "MATERIAL ADMINISTRATIVO", "SIMPLES NACIONAL", "CONTABILIDADE", "FGTS",
    "FOLHA DE PAGAMENTO FUNCIONARIOS", "OUTROS"
 ]

# Função para carregar custos de arquivo
def carregar_custos(nome_arquivo, lista_itens):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        custos = {}
        for item in lista_itens:
            custos[item] = 0.0
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(custos, f, ensure_ascii=False, indent=2)
        return custos

# Função para editar custos via Streamlit
def editar_custos_streamlit(nome_arquivo, custos):
    st.write(f"### Editar valores de {nome_arquivo.replace('.json','')}")
    for item in custos.keys():
        novo_valor = st.number_input(f"{item}", min_value=0.0, value=float(custos[item]), step=0.01, key=f"{nome_arquivo}_{item}")
        custos[item] = novo_valor
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(custos, f, ensure_ascii=False, indent=2)
    return custos

# Carregar ou criar custos variáveis e fixos
valores_variaveis = carregar_custos('custos_variaveis.json', custos_variaveis)
valores_fixos = carregar_custos('custos_fixos.json', custos_fixos)

# Permitir edição se desejar
with st.expander("Editar Custos Variáveis"):
    valores_variaveis = editar_custos_streamlit('custos_variaveis.json', valores_variaveis)
with st.expander("Editar Custos Fixos"):
    valores_fixos = editar_custos_streamlit('custos_fixos.json', valores_fixos)

# Soma total dos custos
total_variavel = sum(valores_variaveis.values())
total_fixo = sum(valores_fixos.values())

st.write(f"Soma total dos custos variáveis: R$ {total_variavel:.2f}")
st.write(f"Soma total dos custos fixos: R$ {total_fixo:.2f}")
st.write(f'Soma total dos custos: R$ {total_variavel + total_fixo:.2f}')

# Novo cálculo: custo operacional como percentual do faturamento
# Exemplo: se custos totais = 1000 e faturamento esperado = 10000, percentual = 10%
# Aqui, você pode pedir ao usuário o faturamento mensal esperado:
faturamento_esperado = st.number_input("Digite o faturamento mensal esperado: R$ ", min_value=0.01, step=0.01, key="faturamento_esperado")
custo_operacional_percentual = (total_variavel + total_fixo) / faturamento_esperado

porcentagem_operacional = min(custo_operacional_percentual * 100, 500)
st.write(f'Porcentagem convertida custo operacional: {porcentagem_operacional:.0f}%')

# Novo: valor simbólico baseado nos 3 primeiros dígitos da porcentagem
porcentagem_str = f"{int(porcentagem_operacional):03d}"  # Garante pelo menos 3 dígitos
valor_simbolico = float(porcentagem_str[:3]) / 100
st.write(f"Valor simbólico do custo operacional: {valor_simbolico:.2f}")

# Use valor_simbolico como custo operacional
custo_operacional = valor_simbolico

custo_produto = st.number_input("Digite o custo do produto: R$ ", min_value=0.0, step=0.01, key="custo_produto")
custo_embalagem = st.number_input("Digite o custo de embalagem: R$ ", min_value=0.0, step=0.01, key="custo_embalagem")
custo_frete = st.number_input("Digite o custo do frete: R$ ", min_value=0.0, step=0.01, key="custo_frete")
adicional = st.number_input("Digite o valor adicional: R$ ", min_value=0.0, step=0.01, key="adicional")

# Cálculo do custo total do produto
custo_base = custo_produto + custo_frete + custo_embalagem + adicional
custo_total = custo_base + custo_operacional + difal

# Soma das taxas percentuais (agora incluindo custo operacional percentual)
taxas_percentuais = taxa_plataforma + imposto + (markup_produto / 100) + custo_operacional_percentual

# Preço de venda sugerido
if custo_produto == 0.0:
    preco_venda = 0.0
    st.warning("Custo do produto não preenchido. Preço sugerido de venda: R$ 0,00")
elif taxas_percentuais < 1:
    preco_venda = custo_total / (1 - taxas_percentuais)
    st.success(f"Preço sugerido de venda: R$ {preco_venda:.2f}")
else:
    preco_venda = custo_total  # Apenas a soma real dos custos
    st.warning("A soma das taxas percentuais é igual ou maior que 100%. O preço sugerido será apenas a soma dos custos.")
    st.success(f"Preço sugerido de venda: R$ {preco_venda:.2f}")

lucro_desejado = st.number_input("Digite o lucro desejado: R$ ", min_value=0.0, step=0.01, key="lucro_desejado")