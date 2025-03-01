"""
Path: utils/logging/info_error_filter.py
Filtro para permitir registros INFO y ERROR, filtrando otros niveles.
"""

import logging

class InfoErrorFilter(logging.Filter):
    """
    Filtro que permite solo registros con nivel INFO y ERROR.
    Útil para separar logs informativos y errores críticos.
    """
    
    def filter(self, record):
        """
        Filtra registros basados en su nivel.
        
        Args:
            record: Registro de log a evaluar
            
        Returns:
            True si el registro debe ser incluido, False en caso contrario
        """
        # Permitir INFO (20) y ERROR (40)
        return record.levelno == logging.INFO or record.levelno == logging.ERROR
