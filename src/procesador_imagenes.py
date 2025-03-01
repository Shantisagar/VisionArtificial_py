class ProcesadorImagenes:
    # ...existing code...
    
    def update_parameters(self, grados_rotacion=None, pixels_por_mm=None, altura=None, horizontal=None):
        """
        Actualiza los parámetros de procesamiento.
        
        Args:
            grados_rotacion: Nuevos grados de rotación para la imagen
            pixels_por_mm: Nueva relación de píxeles por milímetro
            altura: Nuevo ajuste vertical para la imagen
            horizontal: Nuevo ajuste horizontal para la imagen
        """
        if grados_rotacion is not None:
            self.grados_rotacion = grados_rotacion
            
        if pixels_por_mm is not None:
            self.pixels_por_mm = pixels_por_mm
            
        if altura is not None:
            self.altura = altura
            
        if horizontal is not None:
            self.horizontal = horizontal
            
        # Actualizar cualquier estado interno que dependa de estos parámetros
        # Por ejemplo, recalcular matrices de transformación si las hay
        if hasattr(self, 'rotation_matrix'):
            # Recalcular la matriz de rotación si cambió el ángulo
            if grados_rotacion is not None:
                import cv2
                import numpy as np
                (h, w) = (0, 0)  # Estos valores se actualizarán con la primera imagen
                if hasattr(self, 'image_height') and hasattr(self, 'image_width'):
                    h, w = self.image_height, self.image_width
                if h > 0 and w > 0:
                    center = (w // 2, h // 2)
                    self.rotation_matrix = cv2.getRotationMatrix2D(center, self.grados_rotacion, 1.0)
