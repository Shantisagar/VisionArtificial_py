"""
Path: src/config/constants.py
Central configuration module for application constants and magic numbers.
"""

# Window dimensions and properties
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 800
WINDOW_STATE_MAXIMIZED = 'zoomed'
WINDOW_MAXIMIZE_DELAY_MS = 2000

# Update intervals (milliseconds)
STATS_UPDATE_INTERVAL = 500

# UI Component properties
STATUS_LABEL_FONT = ('Helvetica', 11)
STATUS_LABEL_COLOR = 'blue'
STATUS_LABEL_WRAP_LENGTH = 250
STATS_LABEL_FONT = ('Helvetica', 10)

# Slider ranges
SLIDER_RANGE_GRADOS_ROTACION = (-180, 180)
SLIDER_RANGE_PIXELS_POR_MM = (0.1, 50)
SLIDER_RANGE_ALTURA = (-500, 500)
SLIDER_RANGE_HORIZONTAL = (-500, 500)
SLIDER_RANGE_ZOOM = (0.5, 3.0)

# Default values
DEFAULT_ZOOM = 1.0
DEFAULT_PAPER_COLOR = "Blanco"
DEFAULT_ZOOM_RESOLUTION = 0.1

# Paper colors
PAPER_COLOR_OPTIONS = ("Blanco", "Marrón")

# Format strings
ZOOM_FORMAT = ".1f"

# Constantes para formato de presentación de sliders
SLIDER_FORMAT = ".2f"  # Formato para mostrar valores con 2 decimales
SLIDER_RESOLUTION = 0.1  # Incremento de precisión para los sliders
