@echo off
REM Script para ejecutar el sistema de revisión de inventarios en Windows

echo.
echo ========================================
echo Sistema de Revisión de Inventarios - Perú
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    echo Entorno virtual creado
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar/actualizar dependencias
echo Instalando dependencias...
pip install -q -r requirements.txt

echo.
echo Todo listo!
echo.
echo Abriendo aplicación en el navegador...
echo URL: http://localhost:8501
echo.
echo Para detener el servidor presiona Ctrl+C
echo.

REM Ejecutar Streamlit
streamlit run app.py
