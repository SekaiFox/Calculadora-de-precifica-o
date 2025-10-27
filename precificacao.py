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
    use_markup: bool = False,
    ml_listing: str = None,
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

    # Determine percentual platform fee
    if plataforma == 'mercado_livre':
        # allow specifying listing type: 'classico' (14%) or 'premium' (19%)
        if ml_listing == 'classico':
            taxa_plataforma = 0.14
        elif ml_listing == 'premium':
            taxa_plataforma = 0.19
        else:
            taxa_plataforma = float(taxas_marketplaces.get(plataforma, 0.0))
    else:
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
    # NOTE: markup_produto não é uma "taxa" — é um parâmetro de markup/precificação.
    # Não o incluímos nas taxas aplicadas sobre o preço para evitar dupla contagem
    # e resultados negativos de margem. As taxas aplicadas são: plataforma, imposto e operacional.
    taxas_percentuais = taxa_plataforma + float(imposto or 0.0) + custo_operacional_percentual

    # calcula preco_venda
    # Para plataformas que possuem taxa fixa (ex: Shopee), devemos incluir a taxa fixa
    # no numerador (custos a recuperar) e considerar todas as taxas percentuais no denominador.
    if custo_produto == 0.0:
        preco_venda = 0.0
        warning = "Custo do produto não preenchido."
    else:
        # soma percentual que incide sobre o preço
        soma_percentual = taxa_plataforma + float(imposto or 0.0) + custo_operacional_percentual + float(difal or 0.0)
        plataforma_fixa_val = float(plataforma_fixa or 0.0)

        # For Mercado Livre the platform fixed fee depends on the product price range.
        def _ml_fixed_fee_by_price(price_value: float) -> float:
            # tiers (assumption: for price >=79 use the last tier)
            # Products below 12.50 pay half of the lowest fixed fee (6.25/2)
            if price_value < 12.50:
                return 6.25 / 2.0
            if price_value < 29.0:
                return 6.25
            if price_value < 50.0:
                return 6.50
            if price_value < 79.0:
                return 6.75
            return 6.75

        # If marketplace is mercado_livre, we need to determine plataforma_fixa from price tiers.
        if plataforma == 'mercado_livre':
            # We'll solve iteratively because plataforma_fixa depends on preco_venda
            # Start with a conservative upper-band fixed fee
            estimated_fixed = _ml_fixed_fee_by_price(custo_base)
            plataforma_fixa_val = float(estimated_fixed)
        else:
            plataforma_fixa_val = float(plataforma_fixa or 0.0)

        if use_markup:
            # Quando o usuário fornece um markup percentual desejado, calculamos o preço
            # que produz essa margem percentual (lucro/preço).
            target_margin = float(markup_produto or 0.0) / 100.0
            denom = 1.0 - soma_percentual - target_margin
            if plataforma == 'mercado_livre':
                # iterate to find consistent fixed fee based on resulting price
                preco_venda = (custo_base + plataforma_fixa_val) / denom if denom > 0 else (custo_base + plataforma_fixa_val)
                for _ in range(6):
                    new_fixed = _ml_fixed_fee_by_price(preco_venda)
                    if abs(new_fixed - plataforma_fixa_val) < 1e-6:
                        break
                    plataforma_fixa_val = new_fixed
                    preco_venda = (custo_base + plataforma_fixa_val) / denom if denom > 0 else (custo_base + plataforma_fixa_val)
                warning = None if denom > 0 else "Soma das taxas percentuais + markup >= 100%; precificação por soma direta."
            else:
                if denom > 0:
                    preco_venda = (custo_base + plataforma_fixa_val) / denom
                    warning = None
                else:
                    preco_venda = custo_base + plataforma_fixa_val
                    warning = "Soma das taxas percentuais + markup >= 100%; precificação por soma direta."
        else:
            # calcular preço a partir de lucro desejado em R$
            numerador = custo_base + plataforma_fixa_val + float(lucro_desejado or 0.0)
            if plataforma == 'mercado_livre':
                # iterate to ensure fixed fee bracket matches resulting price
                if soma_percentual < 1.0:
                    preco_venda = numerador / (1.0 - soma_percentual)
                else:
                    preco_venda = numerador
                for _ in range(6):
                    new_fixed = _ml_fixed_fee_by_price(preco_venda)
                    if abs(new_fixed - plataforma_fixa_val) < 1e-6:
                        break
                    plataforma_fixa_val = new_fixed
                    numerador = custo_base + plataforma_fixa_val + float(lucro_desejado or 0.0)
                    preco_venda = numerador / (1.0 - soma_percentual) if soma_percentual < 1.0 else numerador
                warning = None if soma_percentual < 1.0 else "Soma das taxas percentuais >= 100%; precificação por soma direta."
            else:
                if soma_percentual < 1.0:
                    preco_venda = numerador / (1.0 - soma_percentual)
                    warning = None
                else:
                    preco_venda = numerador
                    warning = "Soma das taxas percentuais >= 100%; precificação por soma direta."

    # valores em reais (taxas aplicadas sobre o preço)
    taxas_em_reais = preco_venda * (taxa_plataforma + float(imposto or 0.0))
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
        'markup_percentual': round(float(markup_produto or 0.0), 2),
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
