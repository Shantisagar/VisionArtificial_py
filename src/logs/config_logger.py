#src/logs/config_logger.py

import logging.config
import os
import json

def configurar_logging(default_path='config/logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """Configura el logging basado en un archivo JSON."""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
    
    return logging.getLogger(__name__)

class InfoErrorFilter(logging.Filter):
    def filter(self, record):
        # Permitir solo registros de nivel INFO y ERROR
        return record.levelno in (logging.INFO, logging.ERROR)


# Configurar el logger con un nivel específico
configurar_logging()
