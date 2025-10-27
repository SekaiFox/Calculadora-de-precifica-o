
# 💰 Calculadora de Precificação para Marketplaces

Uma ferramenta de análise e precificação para vendedores de e-commerce, construída com Python e Streamlit, baseada na minha experiência como gerente de e-commerce.

### [COLE AQUI UM GIF DO SEU APP FUNCIONANDO]

## 🎯 O Problema (Contexto de E-commerce)

Definir o preço de venda em marketplaces é uma das tarefas mais complexas para um seller. Um erro de cálculo pode zerar a margem de lucro. O preço final precisa absorver:
* Custo do produto
* Impostos (Ex: ICMS, Simples Nacional)
* Comissão da plataforma (que varia de 12% a 20%+)
* Taxas de frete (muitas vezes subsidiadas pelo vendedor)
* A margem de lucro líquida desejada.

Fazer essa "engenharia reversa" manualmente em uma planilha é demorado e suscetível a erros.

## 💡 A Solução (Habilidade de Analytics)

Esta aplicação funciona como um assistente para o seller. O usuário informa o **custo do produto**, as **taxas da plataforma** (ex: Shopee 14% + R$ 3,00) e a **margem de lucro líquida** que deseja obter.

A calculadora processa esses inputs e retorna o **preço de venda ideal** que deve ser anunciado no marketplace para garantir que, após todas as deduções, o lucro líquido desejado seja alcançado.

## 🛠️ Tecnologias Utilizadas
* **Python**
* **Streamlit** (para a interface web e sliders de input)

## 🏁 Como Executar o Projeto

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/SekaiFox/Calculadora-de-precificacao.git](https://github.com/SekaiFox/Calculadora-de-precificacao.git)
    cd Calculadora-de-precificacao
    ```
2.  Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```
3.  Instale as dependências (crie um arquivo `requirements.txt`):
    ```bash
    pip install -r requirements.txt
    ```
4.  Execute o app Streamlit:
    ```bash
    streamlit run seu_script.py
    ```

**Arquivo `requirements.txt`:**
