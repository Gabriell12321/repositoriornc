@echo off
echo ========================================
echo APLICANDO CORRECAO ABA ENGENHARIA
echo ========================================
echo.

echo [1/3] Testando correcoes...
python test_endpoint_engenharia_fixed.py
if errorlevel 1 (
    echo.
    echo ERRO: Testes falharam!
    echo Verifique o arquivo de log acima.
    pause
    exit /b 1
)

echo.
echo [2/3] Correcoes validadas com sucesso!
echo.
echo [3/3] Proximo passo: Reiniciar o servidor
echo.
echo ========================================
echo INSTRUCOES:
echo ========================================
echo.
echo 1. PARE o servidor Flask atual (Ctrl+C)
echo.
echo 2. REINICIE o servidor:
echo    python server_form.py
echo.
echo 3. ACESSE o dashboard:
echo    http://192.168.0.157:5001/dashboard
echo.
echo 4. CLIQUE na aba "Engenharia"
echo.
echo 5. Se ainda mostrar zero:
echo    - Pressione Ctrl+Shift+R para forcar reload
echo    - Ou limpe o cache do navegador
echo.
echo ========================================
echo RESULTADO ESPERADO:
echo ========================================
echo.
echo - Contador: 2763 RNCs
echo - Graficos: Preenchidos com dados
echo - Tendencias mensais: Visiveis
echo.
echo ========================================
echo.
pause
