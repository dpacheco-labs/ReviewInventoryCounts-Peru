#!/bin/bash
# Script para ejecutar el sistema de revisión de inventarios

echo "🚀 Iniciando Sistema de Revisión de Inventarios - Perú"
echo "================================================"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "⚠️  No se encontró el entorno virtual. Creándolo..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
fi

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source venv/bin/activate

# Instalar/actualizar dependencias
echo "📥 Instalando dependencias..."
pip install -q -r requirements.txt

echo ""
echo "✅ Todo listo!"
echo ""
echo "🌐 Abriendo aplicación en el navegador..."
echo "   URL: http://localhost:8501"
echo ""
echo "   Para detener el servidor presiona Ctrl+C"
echo ""

# Ejecutar Streamlit
streamlit run app.py
