import json
import os
from typing import Dict, Any

# Keep marketplace and default values here for reuse
TAXAS_MARKETPLACES = {
    'shopee': 0.15,
    'mercado_livre': 0.19,
    'olx': 0.12,
    'magalu': 0.15,
    'mercado_pago': 0.05,
    'shein': 0.16,
    'b2w': 0.19,
    'olist': 0.23
}
TAXAS_FIXAS = {
    'shopee': 6.00
}
IMPSTO_DEFAULT = 0.10


def carregar_totais_custos(custos_variaveis_file: str = 'custos_variaveis.json', custos_fixos_file: str = 'custos_fixos.json') -> Dict[str, float]:
    """Tenta carregar os arquivos JSON de custos e retorna os totais (variavel, fixo).
    Se os arquivos não existirem ou tiverem erro, retorna zeros.
    """
    total_variavel = 0.0
    total_fixo = 0.0
    try:
        if os.path.exists(custos_variaveis_file):
            with open(custos_variaveis_file, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                if isinstance(dados, dict):
                    total_variavel = sum(float(v or 0) for v in dados.values())
    except Exception:
        total_variavel = 0.0
    try:
        if os.path.exists(custos_fixos_file):
            with open(custos_fixos_file, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                if isinstance(dados, dict):
                    total_fixo = sum(float(v or 0) for v in dados.values())
    except Exception:
        total_fixo = 0.0
    return {"total_variavel": total_variavel, "total_fixo": total_fixo}


def compute_pricing(
    markup_produto: float,
    plataforma: str,
    imposto: float,
    difal: float,
    faturamento_esperado: float,
    custo_produto: float,
    custo_embalagem: float,
    custo_frete: float,
    adicional: float,
    lucro_desejado: float,
    total_variavel: float = 0.0,
    total_fixo: float = 0.0,
    taxas_marketplaces: Dict[str, float] = None,
    taxas_fixas: Dict[str, float] = None,
) -> Dict[str, Any]:
    """Calcula preço sugerido e detalhamento em R$ e %.

    Retorna um dicionário com chaves:
      preco_venda, valor_faturamento, valor_lucro, margem_percentual,
      operacional_em_reais, difal_em_reais, plataforma_fixa_em_reais,
      taxas_em_reais, taxas_totais_em_reais, custos_diretos_por_venda, breakdown (dict)
    """
    if taxas_marketplaces is None:
        taxas_marketplaces = TAXAS_MARKETPLACES
    if taxas_fixas is None:
        taxas_fixas = TAXAS_FIXAS

    taxa_plataforma = float(taxas_marketplaces.get(plataforma, 0.0))
    plataforma_fixa = float(taxas_fixas.get(plataforma, 0.0))

    # base costs
    custo_base = float(custo_produto or 0.0) + float(custo_frete or 0.0) + float(custo_embalagem or 0.0) + float(adicional or 0.0)

    # percentual operacional baseado no faturamento esperado
    if faturamento_esperado and faturamento_esperado > 0:
        custo_operacional_percentual = (float(total_variavel or 0.0) + float(total_fixo or 0.0)) / float(faturamento_esperado)
    else:
        custo_operacional_percentual = 0.0

    # taxa percentuais agregadas (são aplicadas sobre preco_venda)
    taxas_percentuais = taxa_plataforma + float(imposto or 0.0) + (float(markup_produto or 0.0) / 100.0) + custo_operacional_percentual

    # calcula preco_venda
    if custo_produto == 0.0:
        preco_venda = 0.0
        warning = "Custo do produto não preenchido."
    elif taxas_percentuais < 1.0:
        preco_venda = (custo_base + float(lucro_desejado or 0.0)) / (1.0 - taxas_percentuais)
        warning = None
    else:
        preco_venda = custo_base + float(lucro_desejado or 0.0) + plataforma_fixa
        warning = "Soma das taxas >= 100%; precificação por soma direta."

    # valores em reais
    taxas_em_reais = preco_venda * (taxa_plataforma + float(imposto or 0.0) + (float(markup_produto or 0.0) / 100.0))
    operacional_em_reais = preco_venda * custo_operacional_percentual
    difal_em_reais = preco_venda * float(difal or 0.0)
    plataforma_fixa_em_reais = plataforma_fixa

    taxas_totais_em_reais = taxas_em_reais + plataforma_fixa_em_reais + difal_em_reais

    custos_diretos_por_venda = custo_base + operacional_em_reais

    valor_lucro = preco_venda - (custos_diretos_por_venda + taxas_totais_em_reais)

    margem_percentual = (valor_lucro / preco_venda * 100.0) if preco_venda else 0.0

    breakdown = {
        'custo_base': round(custo_base, 2),
        'operacional_em_reais': round(operacional_em_reais, 2),
        'difal_em_reais': round(difal_em_reais, 2),
        'taxa_plataforma_em_reais': round(preco_venda * taxa_plataforma, 2),
        'imposto_em_reais': round(preco_venda * float(imposto or 0.0), 2),
        'markup_em_reais': round(preco_venda * (float(markup_produto or 0.0) / 100.0), 2),
        'plataforma_fixa_em_reais': round(plataforma_fixa_em_reais, 2),
        'taxas_totais_em_reais': round(taxas_totais_em_reais, 2),
    }

    return {
        'preco_venda': round(preco_venda, 2),
        'valor_faturamento': round(preco_venda, 2),
        'valor_lucro': round(valor_lucro, 2),
        'margem_percentual': round(margem_percentual, 2),
        'operacional_em_reais': round(operacional_em_reais, 2),
        'difal_em_reais': round(difal_em_reais, 2),
        'plataforma_fixa_em_reais': round(plataforma_fixa_em_reais, 2),
        'taxas_em_reais': round(taxas_em_reais, 2),
        'taxas_totais_em_reais': round(taxas_totais_em_reais, 2),
        'custos_diretos_por_venda': round(custos_diretos_por_venda, 2),
        'breakdown': breakdown,
        'warning': warning,
    }
