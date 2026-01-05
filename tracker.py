"""
Módulo de seguimiento de archivos recibidos y faltantes
"""
import json
import os
from datetime import datetime
from typing import List, Dict
import config


class FileTracker:
    """Gestiona el seguimiento de archivos esperados vs recibidos"""

    def __init__(self):
        self._ensure_directories()
        self.tracking_file = f"{config.TRACKING_DIR}/tracking.json"
        self.history = self._load_history()

    def _ensure_directories(self):
        """Crea directorios necesarios si no existen"""
        for directory in [config.DATA_DIR, config.UPLOADED_DIR,
                         config.TRACKING_DIR, config.REPORTS_DIR]:
            os.makedirs(directory, exist_ok=True)

    def _load_history(self) -> Dict:
        """Carga el historial de seguimiento"""
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_history(self):
        """Guarda el historial de seguimiento"""
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def create_session(self, year: int, month: int) -> str:
        """
        Crea una nueva sesión de revisión

        Args:
            year: Año
            month: Mes

        Returns:
            Session ID
        """
        session_id = f"{year}-{month:02d}"

        if session_id not in self.history:
            self.history[session_id] = {
                "created_at": datetime.now().isoformat(),
                "expected_files": config.EXPECTED_FILES.copy(),
                "received_files": [],
                "missing_files": config.EXPECTED_FILES.copy(),
                "uploads": []
            }
            self._save_history()

        return session_id

    def register_upload(self, session_id: str, uploaded_files: List[str]):
        """
        Registra archivos subidos

        Args:
            session_id: ID de la sesión
            uploaded_files: Lista de nombres de archivos subidos
        """
        if session_id not in self.history:
            raise ValueError(f"Sesión {session_id} no existe")

        session = self.history[session_id]

        # Registrar upload
        upload_record = {
            "timestamp": datetime.now().isoformat(),
            "files": uploaded_files
        }
        session["uploads"].append(upload_record)

        # Actualizar archivos recibidos
        for filename in uploaded_files:
            if filename not in session["received_files"]:
                session["received_files"].append(filename)

            # Remover de faltantes si está ahí
            if filename in session["missing_files"]:
                session["missing_files"].remove(filename)

        self._save_history()

    def get_session_status(self, session_id: str) -> Dict:
        """
        Obtiene el estado de una sesión

        Args:
            session_id: ID de la sesión

        Returns:
            Dict con estado de la sesión
        """
        if session_id not in self.history:
            return None

        session = self.history[session_id]
        total_expected = len(session["expected_files"])
        total_received = len(session["received_files"])
        total_missing = len(session["missing_files"])

        return {
            "session_id": session_id,
            "created_at": session["created_at"],
            "total_expected": total_expected,
            "total_received": total_received,
            "total_missing": total_missing,
            "completion_percentage": (total_received / total_expected * 100) if total_expected > 0 else 0,
            "expected_files": session["expected_files"],
            "received_files": session["received_files"],
            "missing_files": session["missing_files"],
            "uploads": session["uploads"]
        }

    def get_all_sessions(self) -> List[str]:
        """Retorna todas las sesiones disponibles"""
        return sorted(self.history.keys(), reverse=True)

    def get_missing_files(self, session_id: str) -> List[str]:
        """
        Obtiene archivos faltantes de una sesión

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de archivos faltantes
        """
        if session_id not in self.history:
            return []
        return self.history[session_id]["missing_files"]

    def check_file_expected(self, filename: str) -> bool:
        """
        Verifica si un archivo está en la lista de esperados

        Args:
            filename: Nombre del archivo

        Returns:
            True si está en la lista de esperados
        """
        return filename in config.EXPECTED_FILES
