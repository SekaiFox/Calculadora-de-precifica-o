import json
import os
import PySimpleGUI as sg
from precificacao import compute_pricing, carregar_totais_custos, TAXAS_MARKETPLACES, TAXAS_FIXAS

# Layout
sg.theme('DarkPurple')

def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

custos_variaveis = load_json('custos_variaveis.json')
custos_fixos = load_json('custos_fixos.json')

layout = [
    [sg.Text('Calculadora de Precificação - Offline', font=('Any', 16))],
    [sg.Frame('Configurações', [[
        sg.Text('Plataforma'), sg.Combo(list(TAXAS_MARKETPLACES.keys()), default_value='shopee', key='plataforma'),
        sg.Text('Markup (%)'), sg.Input('20', key='markup', size=(6,1)),
        sg.Text('Imposto (ex: 0.10)'), sg.Input('0.10', key='imposto', size=(6,1)),
    ]])],
    [sg.Frame('Produto', [[
        sg.Text('Custo produto (R$)'), sg.Input('0.00', key='custo_produto', size=(10,1)),
        sg.Text('Embalagem'), sg.Input('0.00', key='embalagem', size=(10,1)),
        sg.Text('Frete'), sg.Input('0.00', key='frete', size=(10,1)),
        sg.Text('Adicional'), sg.Input('0.00', key='adicional', size=(10,1)),
        sg.Text('Lucro desejado'), sg.Input('0.00', key='lucro', size=(10,1)),
    ]])],
    [sg.Frame('Resultados', [[
        sg.Multiline('', key='result', size=(80, 15), disabled=True)
    ]])],
    [sg.Button('Calcular'), sg.Button('Salvar custos'), sg.Button('Exportar CSV'), sg.Button('Sair')]
]

window = sg.Window('Calculadora de Precificacao', layout, finalize=True)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Sair'):
        break
    if event == 'Calcular':
        try:
            markup = float(values.get('markup', 0))
            plataforma = values.get('plataforma', 'shopee')
            imposto = float(values.get('imposto', 0))
            custo_produto = float(values.get('custo_produto', 0))
            embalagem = float(values.get('embalagem', 0))
            frete = float(values.get('frete', 0))
            adicional = float(values.get('adicional', 0))
            lucro = float(values.get('lucro', 0))

            totais = carregar_totais_custos()
            resultado = compute_pricing(
                markup_produto=markup,
                plataforma=plataforma,
                imposto=imposto,
                difal=0.0,
                faturamento_esperado=10000.0,
                custo_produto=custo_produto,
                custo_embalagem=embalagem,
                custo_frete=frete,
                adicional=adicional,
                lucro_desejado=lucro,
                total_variavel=totais.get('total_variavel', 0.0),
                total_fixo=totais.get('total_fixo', 0.0),
            )

            out = []
            out.append(f"Preço sugerido: R$ {resultado['preco_venda']:.2f}")
            out.append(f"Valor faturamento: R$ {resultado['valor_faturamento']:.2f}")
            out.append(f"Valor lucro: R$ {resultado['valor_lucro']:.2f} — Margem: {resultado['margem_percentual']:.2f}%")
            out.append('\nQuebra de custos:')
            for k, v in resultado['breakdown'].items():
                out.append(f"{k}: R$ {v}")
            window['result'].update('\n'.join(out))
        except Exception as e:
            window['result'].update(f"Erro: {e}")
    if event == 'Salvar custos':
        # For simplicity, save current loaded custos to files (no editor in this simple GUI)
        with open('custos_variaveis.json', 'w', encoding='utf-8') as f:
            json.dump(custos_variaveis, f, ensure_ascii=False, indent=2)
        with open('custos_fixos.json', 'w', encoding='utf-8') as f:
            json.dump(custos_fixos, f, ensure_ascii=False, indent=2)
        sg.popup('Custos salvos')
    if event == 'Exportar CSV':
        sg.popup('Funcionalidade a implementar')

window.close()
