Gerar executável (Windows) usando PyInstaller

Passos rápidos:

1. Crie um ambiente virtual (opcional, recomendado):

   powershell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1

2. Instale dependências:

   pip install -r requirements.txt

3. Gerar executável da interface CLI (arquivo `cli_app.py`):

   pyinstaller --onefile --name CalculadoraCLI cli_app.py

   - O executável ficará em `dist\CalculadoraCLI.exe`.

4. (Opcional) Gerar executável para a versão Streamlit não é recomendado com PyInstaller —
   normalmente você distribui o app Streamlit como código Python e roda `streamlit run CALCULADORA.py`.

Notas:
- PyInstaller empacota o Python e dependências; confira alertas sobre antivírus.
- Para incluir arquivos JSON (custos JSON), adicione a opção `--add-data "custos_variaveis.json;." --add-data "custos_fixos.json;."` ao comando PyInstaller.
- Teste o executável em uma máquina limpa antes de distribuir.
