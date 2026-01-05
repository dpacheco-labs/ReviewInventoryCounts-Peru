# 📊 Sistema de Revisión de Inventarios - Perú

Sistema automatizado para revisar los archivos de inventario WIP, PT, RM y Packaging cada WD9 del mes siguiente, en plantas, centros de distribución y transportadoras generados en cada inventario nacional mensual. 

## 🎯 Características

- ✅ **Carga masiva** de archivos Excel (drag & drop)
- ✅ **Validación automática** de KPI
- ✅ **Análisis masivo de archivos operativos** generados en el inventario
- ✅ **Envío de ratio de cumplimiento** de archivos recibidos/faltantes
- ✅ **Dashboard visual** con métricas en tiempo real
- ✅ **Reportes exportables** (Excel y CSV)
- ✅ **Validación de pantallas de integridad** de pendientes

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd ReviewInventoryCounts-Peru
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 📝 Configuración

### Personalizar archivos esperados

Edita el archivo `config.py` y modifica la lista `EXPECTED_FILES` con los 40 nombres reales de tus archivos:

```python
EXPECTED_FILES = [
    "Inventario_Almacen_Lima_Norte.xlsx",
    "Inventario_Almacen_Lima_Sur.xlsx",
    # ... agrega tus 40 archivos aquí
]
```

### Personalizar columnas requeridas

En `config.py`, ajusta las columnas que deben existir en cada Excel:

```python
REQUIRED_COLUMNS = [
    "Código",
    "Descripción",
    "Cantidad",
    "Unidad",
    "Fecha",
]
```

### Configurar validaciones

Activa/desactiva validaciones según necesites:

```python
VALIDATIONS = {
    "cantidad_negativa": True,    # Validar cantidades negativas
    "fecha_futura": True,         # Validar fechas futuras
    "campos_vacios": True,        # Validar campos vacíos
    "duplicados": True,           # Validar códigos duplicados
}
```

## 🖥️ Uso

### Iniciar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Flujo de trabajo - Día 9 del mes

1. **Crear sesión mensual**
   - En el sidebar, crea una nueva sesión con año y mes
   - Ejemplo: 2026-01 para enero 2026

2. **Cargar archivos**
   - Arrastra los archivos Excel a la zona de carga
   - O haz clic para seleccionarlos

3. **Validar**
   - Haz clic en "🔍 Validar Archivos"
   - Revisa los resultados de validación

4. **Revisar dashboard**
   - El dashboard muestra automáticamente:
     - Total de archivos recibidos vs esperados
     - Porcentaje de completitud
     - Lista de archivos faltantes

5. **Exportar reportes**
   - Descarga el reporte de validación
   - Descarga la lista de faltantes

### Flujo de trabajo - Archivos tardíos

Cuando lleguen archivos faltantes posteriormente:

1. **Seleccionar sesión existente**
   - En el sidebar, selecciona la sesión del mes correspondiente

2. **Cargar archivos faltantes**
   - Carga solo los archivos que llegaron tarde

3. **Validar y revisar**
   - El sistema actualizará automáticamente el tracking

## 📊 Funcionalidades del Dashboard

### Vista principal

- **Métricas**: Total esperados, recibidos, faltantes, % completado
- **Gráfico circular**: Visualización del estado
- **Barra de progreso**: Progreso de completitud
- **Historial de uploads**: Registro de todas las cargas

### Validación de datos

El sistema valida automáticamente:

- ✅ Columnas requeridas presentes
- ✅ Campos obligatorios sin valores vacíos
- ✅ Cantidades no negativas
- ✅ Fechas no futuras
- ✅ Códigos sin duplicados

### Archivos faltantes

- Lista completa de archivos pendientes
- Exportación a CSV
- Actualización automática al subir archivos

## 📁 Estructura del Proyecto

```
ReviewInventoryCounts-Peru/
├── app.py                  # Aplicación principal Streamlit
├── config.py              # Configuración (archivos esperados, validaciones)
├── validator.py           # Módulo de validación
├── tracker.py             # Módulo de seguimiento
├── requirements.txt       # Dependencias
├── README.md             # Este archivo
├── data/
│   ├── uploaded/         # Archivos subidos
│   ├── tracking/         # Base de datos de seguimiento
│   └── reports/          # Reportes generados
└── .gitignore
```

## 🔧 Personalización Avanzada

### Agregar nuevas validaciones

Edita `validator.py` y agrega métodos en la clase `InventoryValidator`:

```python
def _validate_custom(self, df: pd.DataFrame, filename: str):
    """Tu validación personalizada"""
    # Tu código aquí
    pass
```

### Modificar el dashboard

Edita `app.py` para personalizar:
- Métricas mostradas
- Gráficos
- Colores
- Layout

## 📦 Exportaciones

El sistema genera:

1. **Reporte de validación** (Excel):
   - Hoja "Resumen": Métricas generales
   - Hoja "Detalle": Errores y warnings por archivo

2. **Lista de faltantes** (CSV):
   - Nombres de archivos pendientes

## 🐛 Solución de Problemas

### Error al leer archivos Excel

Si obtienes errores al leer archivos:
- Verifica que sean archivos `.xlsx` o `.xls` válidos
- Asegúrate de que no estén corruptos
- Verifica que tengan las columnas requeridas

### Archivos no se marcan como recibidos

- Verifica que el nombre del archivo coincida EXACTAMENTE con `EXPECTED_FILES`
- Los nombres son case-sensitive

### La aplicación no inicia

```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

## 📚 Soporte

Para reportar problemas o solicitar funcionalidades:
1. Abre un issue en el repositorio
2. Describe el problema/solicitud
3. Incluye capturas de pantalla si aplica

## 📄 Licencia

Este proyecto es de uso interno para la gestión de inventarios.

## 🔄 Actualizaciones Futuras

Posibles mejoras:
- [ ] Notificaciones automáticas de archivos faltantes
- [ ] Integración con email
- [ ] Validaciones más complejas
- [ ] Dashboard con histórico de meses anteriores
- [ ] Comparación mes a mes
- [ ] Alertas automáticas de inconsistencias

---

**Versión:** 1.0
**Última actualización:** Enero 2026
