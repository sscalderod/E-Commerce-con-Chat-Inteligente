from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class ProductDTO(BaseModel):
    """DTO para transferir datos de productos entre capas.

    Attributes:
        id (Optional[int]): Identificador del producto.
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoria del producto.
        size (str): Talla del producto.
        color (str): Color del producto.
        price (float): Precio del producto.
        stock (int): Unidades disponibles.
        description (str): Descripcion comercial.
    """

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    @validator("price")
    def price_must_be_positive(cls, value: float) -> float:
        """Valida que el precio sea mayor a 0.

        Args:
            value (float): Precio a validar.

        Returns:
            float: Precio validado.

        Raises:
            ValueError: Si el precio es menor o igual a 0.
        """
        if value <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return value

    @validator("stock")
    def stock_must_be_non_negative(cls, value: int) -> int:
        """Valida que el stock no sea negativo.

        Args:
            value (int): Stock a validar.

        Returns:
            int: Stock validado.

        Raises:
            ValueError: Si el stock es negativo.
        """
        if value < 0:
            raise ValueError("El stock no puede ser negativo")
        return value

    class Config:
        from_attributes = True


class ChatMessageRequestDTO(BaseModel):
    """DTO para recibir mensajes de entrada del usuario."""

    session_id: str
    message: str

    @validator("message")
    def message_not_empty(cls, value: str) -> str:
        """Valida que el mensaje no este vacio.

        Args:
            value (str): Texto del mensaje.

        Returns:
            str: Mensaje validado.

        Raises:
            ValueError: Si el mensaje esta vacio.
        """
        if not value or not value.strip():
            raise ValueError("El mensaje no puede estar vacio")
        return value

    @validator("session_id")
    def session_id_not_empty(cls, value: str) -> str:
        """Valida que el session_id no este vacio.

        Args:
            value (str): Identificador de sesion.

        Returns:
            str: Session ID validado.

        Raises:
            ValueError: Si el session_id esta vacio.
        """
        if not value or not value.strip():
            raise ValueError("El session_id no puede estar vacio")
        return value


class ChatMessageResponseDTO(BaseModel):
    """DTO de salida para respuestas del asistente conversacional."""

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """DTO para mostrar mensajes historicos de una sesion."""

    id: int
    role: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True
