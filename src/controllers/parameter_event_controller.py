class ParameterEventController:
    """
    Clase encargada de gestionar eventos y callbacks de la vista,
    delegando la validación y actualización en ParameterModel.
    """
    def __init__(self, logger, model, notifier=None):
        self.logger = logger
        self.model = model
        self.notifier = notifier
        self.parameters_update_callback = None

    def on_slider_change(self, param_name: str, value: float, view):
        """
        Maneja cambios en el slider, actualiza la vista y modelo.
        """
        view.update_parameter_text(param_name, str(value))
        self.model.update_parameter(param_name, value)
        if self.parameters_update_callback:
            self.parameters_update_callback({param_name: value})

    def on_update_parameters(self, view, parameters: dict = None):
        """
        Maneja el evento de actualizar parámetros:
        Obtiene los valores actuales y valida cada uno.
        """
        if parameters is None:
            string_values = view.get_current_values()
            parameters = {}
            for param_name, value_str in string_values.items():
                valid, error_msg = self.model.validate_value(param_name, value_str)
                if not valid:
                    if self.notifier:
                        self.notifier.notify_warning(f"Valor inválido en {param_name}: {error_msg}")
                    return
                parameters[param_name] = float(value_str)

        for param, val in parameters.items():
            self.model.update_parameter(param, val)
        if self.parameters_update_callback:
            self.parameters_update_callback(parameters)
        self.logger.info("Parámetros actualizados correctamente.")

    def set_parameters_update_callback(self, callback):
        self.parameters_update_callback = callback
