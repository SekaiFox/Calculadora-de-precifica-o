import json
from precificacao import carregar_totais_custos, compute_pricing


def ask_float(prompt: str, default: float = 0.0):
    try:
        val = input(f"{prompt} [{default}]: ")
        if val.strip() == "":
            return float(default)
        return float(val.replace(',', '.'))
    except Exception:
        print("Entrada inválida, usando valor padrão.")
        return float(default)


def main():
    print("Calculadora de Precificação - CLI")
    totals = carregar_totais_custos()
    print(f"Total custos variáveis: R$ {totals['total_variavel']:.2f}")
    print(f"Total custos fixos: R$ {totals['total_fixo']:.2f}")

    markup = ask_float("Digite o markup do produto (ex: 20 para 20%): ", 20.0)
    plataforma = input("Escolha a plataforma (shopee/mercado_livre/olx/magalu/mercado_pago/shein/b2w/olist) [shopee]: ") or 'shopee'
    imposto = ask_float("Digite a alíquota de imposto (ex: 0.10 para 10%): ", 0.10)
    estado = input("Estado destino (sigla, ex: sp) [nenhum]: ") or '0'
    difal = 0.0
    if estado != '0':
        # try to read from precificacao defaults if the file exists
        try:
            from precificacao import TAXAS_MARKETPLACES, TAXAS_FIXAS
            # If user asked an estado not present, keep zero
            # We'll keep difal 0.0 here for simplicity
        except Exception:
            pass

    faturamento_esperado = ask_float("Digite o faturamento mensal esperado: R$ ", 10000.0)
    custo_produto = ask_float("Digite o custo do produto: R$ ", 10.0)
    custo_embalagem = ask_float("Digite o custo da embalagem: R$ ", 1.0)
    custo_frete = ask_float("Digite o custo do frete: R$ ", 5.0)
    adicional = ask_float("Digite o valor adicional: R$ ", 0.0)
    lucro_desejado = ask_float("Digite o lucro desejado: R$ ", 2.0)

    result = compute_pricing(
        markup_produto=markup,
        plataforma=plataforma,
        imposto=imposto,
        difal=difal,
        faturamento_esperado=faturamento_esperado,
        custo_produto=custo_produto,
        custo_embalagem=custo_embalagem,
        custo_frete=custo_frete,
        adicional=adicional,
        lucro_desejado=lucro_desejado,
        total_variavel=totals['total_variavel'],
        total_fixo=totals['total_fixo'],
    )

    print('\nResultado:')
    print(f"Preço sugerido: R$ {result['preco_venda']:.2f}")
    print(f"Valor faturamento: R$ {result['valor_faturamento']:.2f}")
    print(f"Valor lucro: R$ {result['valor_lucro']:.2f} — Margem: {result['margem_percentual']:.2f}%")
    print('Detalhamento:')
    for k, v in result['breakdown'].items():
        print(f"  {k}: R$ {v}")


if __name__ == '__main__':
    main()
