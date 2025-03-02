"""
Helper functions for common UI operations.
"""

def get_centered_geometry(root, window_width=1000, window_height=800):
    """Calculates centered window geometry for a given root Tk widget."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    return f"{window_width}x{window_height}+{x_position}+{y_position}"

def get_slider_ranges():
    """Returns the range definitions for various sliders."""
    return {
        'grados_rotacion': (-180, 180),
        'pixels_por_mm': (0.1, 50),
        'altura': (-500, 500),
        'horizontal': (-500, 500)
    }
