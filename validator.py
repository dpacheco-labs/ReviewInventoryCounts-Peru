"""
Módulo de validación de archivos Excel de inventario
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
import config


class InventoryValidator:
    """Valida archivos Excel de inventario"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_file(self, df: pd.DataFrame, filename: str) -> Dict:
        """
        Valida un archivo de inventario

        Args:
            df: DataFrame con los datos del Excel
            filename: Nombre del archivo

        Returns:
            Dict con resultados de validación
        """
        self.errors = []
        self.warnings = []

        # Validar columnas requeridas
        self._validate_columns(df, filename)

        # Validar datos
        if config.VALIDATIONS.get("campos_vacios"):
            self._validate_empty_fields(df, filename)

        if config.VALIDATIONS.get("cantidad_negativa"):
            self._validate_negative_quantities(df, filename)

        if config.VALIDATIONS.get("fecha_futura"):
            self._validate_future_dates(df, filename)

        if config.VALIDATIONS.get("duplicados"):
            self._validate_duplicates(df, filename)

        return {
            "filename": filename,
            "total_rows": len(df),
            "errors": self.errors,
            "warnings": self.warnings,
            "is_valid": len(self.errors) == 0
        }

    def _validate_columns(self, df: pd.DataFrame, filename: str):
        """Valida que existan todas las columnas requeridas"""
        missing_cols = set(config.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            self.errors.append(
                f"Columnas faltantes: {', '.join(missing_cols)}"
            )

    def _validate_empty_fields(self, df: pd.DataFrame, filename: str):
        """Valida que no haya campos críticos vacíos"""
        for col in config.REQUIRED_COLUMNS:
            if col in df.columns:
                empty_count = df[col].isna().sum()
                if empty_count > 0:
                    self.errors.append(
                        f"Campo '{col}' tiene {empty_count} valores vacíos"
                    )

    def _validate_negative_quantities(self, df: pd.DataFrame, filename: str):
        """Valida que las cantidades no sean negativas"""
        if "Cantidad" in df.columns:
            negative = df[df["Cantidad"] < 0]
            if len(negative) > 0:
                self.errors.append(
                    f"Se encontraron {len(negative)} cantidades negativas en filas: "
                    f"{negative.index.tolist()[:10]}"
                )

    def _validate_future_dates(self, df: pd.DataFrame, filename: str):
        """Valida que las fechas no sean futuras"""
        if "Fecha" in df.columns:
            try:
                df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
                future = df[df["Fecha"] > datetime.now()]
                if len(future) > 0:
                    self.warnings.append(
                        f"Se encontraron {len(future)} fechas futuras"
                    )
            except Exception as e:
                self.errors.append(f"Error al validar fechas: {str(e)}")

    def _validate_duplicates(self, df: pd.DataFrame, filename: str):
        """Valida códigos duplicados"""
        if "Código" in df.columns:
            duplicates = df[df.duplicated(subset=["Código"], keep=False)]
            if len(duplicates) > 0:
                self.warnings.append(
                    f"Se encontraron {len(duplicates)} códigos duplicados"
                )


def validate_multiple_files(files_dict: Dict[str, pd.DataFrame]) -> Dict:
    """
    Valida múltiples archivos

    Args:
        files_dict: Dict {filename: DataFrame}

    Returns:
        Dict con resumen de validaciones
    """
    validator = InventoryValidator()
    results = []

    for filename, df in files_dict.items():
        result = validator.validate_file(df, filename)
        results.append(result)

    # Resumen general
    total_files = len(results)
    valid_files = sum(1 for r in results if r["is_valid"])
    total_errors = sum(len(r["errors"]) for r in results)
    total_warnings = sum(len(r["warnings"]) for r in results)

    return {
        "results": results,
        "summary": {
            "total_files": total_files,
            "valid_files": valid_files,
            "invalid_files": total_files - valid_files,
            "total_errors": total_errors,
            "total_warnings": total_warnings
        }
    }
