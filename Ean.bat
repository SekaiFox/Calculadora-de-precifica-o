@echo off
title 🦐CALCULADORA🦐
color 0D

:: Caminho para ativar o Anaconda (ajuste se necessário)
call "%USERPROFILE%\anaconda3\Scripts\activate.bat"

:: (Opcional) Ativar ambiente específico, se você usa um
:: call conda activate meu_ambiente

:: Executa o Streamlit
streamlit run "C:\Users\Downloads\CALCULADORA.PY"

pause
