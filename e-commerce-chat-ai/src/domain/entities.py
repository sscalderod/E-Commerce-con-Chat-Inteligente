from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """Entidad que representa un producto en el e-commerce.

    Esta entidad encapsula reglas de negocio basicas sobre precio,
    disponibilidad y manejo de inventario.

    Attributes:
        id (Optional[int]): Identificador unico del producto.
        name (str): Nombre comercial del producto.
        brand (str): Marca del producto.
        category (str): Categoria funcional del producto.
        size (str): Talla disponible.
        color (str): Color principal del producto.
        price (float): Precio de venta en dolares.
        stock (int): Unidades disponibles en inventario.
        description (str): Descripcion corta del producto.
    """

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self) -> None:
        """Valida reglas minimas de consistencia al crear la entidad.

        Raises:
            ValueError: Si el nombre esta vacio, el precio es menor o igual a 0,
                o el stock es negativo.
        """
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacio")
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")

    def is_available(self) -> bool:
        """Indica si el producto se puede vender en este momento.

        Returns:
            bool: True cuando el stock es mayor que 0.
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """Reduce el inventario de acuerdo con una cantidad solicitada.

        Args:
            quantity (int): Cantidad a descontar del stock.

        Raises:
            ValueError: Si la cantidad no es positiva o supera el stock actual.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva")
        if quantity > self.stock:
            raise ValueError("No hay suficiente stock disponible")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """Incrementa el inventario del producto.

        Args:
            quantity (int): Cantidad a sumar al stock actual.

        Raises:
            ValueError: Si la cantidad no es positiva.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva")
        self.stock += quantity


@dataclass
class ChatMessage:
    """Entidad que representa un mensaje dentro de una conversacion.

    Attributes:
        id (Optional[int]): Identificador unico del mensaje.
        session_id (str): Identificador de sesion del usuario.
        role (str): Emisor del mensaje, solo "user" o "assistant".
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Momento de creacion del mensaje.
    """

    id: Optional[int]
    session_id: str
    role: str
    message: str
    timestamp: datetime

    def __post_init__(self) -> None:
        """Valida reglas de integridad para el mensaje conversacional.

        Raises:
            ValueError: Si el rol no es valido, o session_id/message estan vacios.
        """
        if self.role not in {"user", "assistant"}:
            raise ValueError("El rol debe ser 'user' o 'assistant'")
        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacio")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacio")

    def is_from_user(self) -> bool:
        """Indica si el emisor del mensaje es el usuario.

        Returns:
            bool: True cuando role es "user".
        """
        return self.role == "user"

    def is_from_assistant(self) -> bool:
        """Indica si el emisor del mensaje es el asistente.

        Returns:
            bool: True cuando role es "assistant".
        """
        return self.role == "assistant"


@dataclass
class ChatContext:
    """Value Object que encapsula el contexto conversacional reciente.

    Attributes:
        messages (list[ChatMessage]): Historial completo disponible.
        max_messages (int): Maximo de mensajes a incluir como contexto.
    """

    messages: list[ChatMessage]
    max_messages: int = 6

    def get_recent_messages(self) -> list[ChatMessage]:
        """Obtiene los ultimos mensajes para contexto de IA.

        Returns:
            list[ChatMessage]: Subconjunto mas reciente del historial.
        """
        return self.messages[-self.max_messages :]

    def format_for_prompt(self) -> str:
        """Convierte el historial reciente a texto legible para prompt.

        Returns:
            str: Conversacion formateada con prefijos de rol.
        """
        formatted_lines: list[str] = []
        for msg in self.get_recent_messages():
            prefix = "Usuario" if msg.is_from_user() else "Asistente"
            formatted_lines.append(f"{prefix}: {msg.message}")
        return "\n".join(formatted_lines)
