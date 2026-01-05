"""
Configuración del sistema de revisión de inventarios
"""
from datetime import datetime

# Lista de los 40 archivos Excel esperados cada día 9
# Modifica esta lista con los nombres reales de tus archivos
EXPECTED_FILES = [
    "Inventario_Almacen_Lima_Norte.xlsx",
    "Inventario_Almacen_Lima_Sur.xlsx",
    "Inventario_Almacen_Lima_Este.xlsx",
    "Inventario_Almacen_Lima_Oeste.xlsx",
    "Inventario_Almacen_Callao.xlsx",
    "Inventario_Almacen_Arequipa.xlsx",
    "Inventario_Almacen_Trujillo.xlsx",
    "Inventario_Almacen_Chiclayo.xlsx",
    "Inventario_Almacen_Piura.xlsx",
    "Inventario_Almacen_Cusco.xlsx",
    "Inventario_Almacen_Iquitos.xlsx",
    "Inventario_Almacen_Huancayo.xlsx",
    "Inventario_Almacen_Pucallpa.xlsx",
    "Inventario_Almacen_Tacna.xlsx",
    "Inventario_Almacen_Ica.xlsx",
    "Inventario_Almacen_Juliaca.xlsx",
    "Inventario_Almacen_Ayacucho.xlsx",
    "Inventario_Almacen_Cajamarca.xlsx",
    "Inventario_Almacen_Tarapoto.xlsx",
    "Inventario_Almacen_Chimbote.xlsx",
    # Agrega aquí los otros 20 archivos esperados
    "Inventario_Producto_A.xlsx",
    "Inventario_Producto_B.xlsx",
    "Inventario_Producto_C.xlsx",
    "Inventario_Producto_D.xlsx",
    "Inventario_Producto_E.xlsx",
    "Inventario_Producto_F.xlsx",
    "Inventario_Producto_G.xlsx",
    "Inventario_Producto_H.xlsx",
    "Inventario_Producto_I.xlsx",
    "Inventario_Producto_J.xlsx",
    "Inventario_Producto_K.xlsx",
    "Inventario_Producto_L.xlsx",
    "Inventario_Producto_M.xlsx",
    "Inventario_Producto_N.xlsx",
    "Inventario_Producto_O.xlsx",
    "Inventario_Producto_P.xlsx",
    "Inventario_Producto_Q.xlsx",
    "Inventario_Producto_R.xlsx",
    "Inventario_Producto_S.xlsx",
    "Inventario_Producto_T.xlsx",
]

# Columnas requeridas en cada archivo Excel
# Modifica según la estructura real de tus archivos
REQUIRED_COLUMNS = [
    "Código",
    "Descripción",
    "Cantidad",
    "Unidad",
    "Fecha",
]

# Validaciones
VALIDATIONS = {
    "cantidad_negativa": True,  # Validar que las cantidades no sean negativas
    "fecha_futura": True,  # Validar que las fechas no sean futuras
    "campos_vacios": True,  # Validar que no haya campos críticos vacíos
    "duplicados": True,  # Validar códigos duplicados
}

# Configuración de almacenamiento
DATA_DIR = "data"
UPLOADED_DIR = f"{DATA_DIR}/uploaded"
TRACKING_DIR = f"{DATA_DIR}/tracking"
REPORTS_DIR = f"{DATA_DIR}/reports"
