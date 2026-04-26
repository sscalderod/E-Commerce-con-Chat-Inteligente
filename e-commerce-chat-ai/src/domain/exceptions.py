"""Excepciones especificas del dominio para reglas de negocio."""


class ProductNotFoundError(Exception):
    """Excepcion para consultas de producto inexistente.

    Args:
        product_id (int | None): ID que se intento consultar.
    """

    def __init__(self, product_id: int | None = None):
        if product_id is not None:
            message = f"Producto con ID {product_id} no encontrado"
        else:
            message = "Producto no encontrado"
        super().__init__(message)


class InvalidProductDataError(Exception):
    """Excepcion para errores de validacion de datos de producto.

    Args:
        message (str): Descripcion del error de validacion.
    """

    def __init__(self, message: str = "Datos de producto invalidos"):
        super().__init__(message)


class ChatServiceError(Exception):
    """Excepcion de alto nivel para fallas en el flujo de chat.

    Args:
        message (str): Descripcion detallada del problema.
    """

    def __init__(self, message: str = "Error en el servicio de chat"):
        super().__init__(message)
