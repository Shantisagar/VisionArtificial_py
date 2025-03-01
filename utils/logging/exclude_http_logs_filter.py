"""
Path: utils/logging/exclude_http_logs_filter.py
Filtro para excluir logs relacionados con peticiones HTTP.
"""

import logging

class ExcludeHTTPLogsFilter(logging.Filter):
    """
    Filtro que excluye mensajes de log relacionados con peticiones HTTP.
    Útil para reducir el ruido en los logs cuando se utilizan clientes HTTP.
    """
    
    def filter(self, record):
        """
        Filtra registros basados en su contenido.
        
        Args:
            record: Registro de log a evaluar
            
        Returns:
            True si el registro debe ser incluido, False en caso contrario
        """
        # Excluir mensajes que contengan palabras clave relacionadas con HTTP
        keywords = ['http://', 'https://', 'GET ', 'POST ', 'urllib3', 'requests', 'HTTP']
        for keyword in keywords:
            if keyword in record.getMessage():
                return False
        return True
