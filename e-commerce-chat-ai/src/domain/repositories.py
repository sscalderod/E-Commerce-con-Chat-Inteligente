from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import ChatMessage, Product


class IProductRepository(ABC):
    """Contrato para operaciones de persistencia de productos.

    Define la interfaz que debe implementar cualquier repositorio concreto,
    independientemente de la tecnologia de almacenamiento.
    """

    @abstractmethod
    def get_all(self) -> List[Product]:
        """Obtiene todos los productos registrados.

        Returns:
            List[Product]: Coleccion completa de productos.
        """
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Obtiene un producto por su identificador unico.

        Args:
            product_id (int): ID del producto buscado.

        Returns:
            Optional[Product]: Entidad encontrada o None.
        """
        pass

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """Obtiene productos que pertenecen a una marca especifica.

        Args:
            brand (str): Nombre de marca a consultar.

        Returns:
            List[Product]: Productos que cumplen el filtro.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """Obtiene productos de una categoria especifica.

        Args:
            category (str): Categoria de negocio.

        Returns:
            List[Product]: Productos de la categoria solicitada.
        """
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Guarda o actualiza un producto y retorna la entidad persistida.

        Args:
            product (Product): Entidad a persistir.

        Returns:
            Product: Entidad guardada, idealmente con ID asignado.
        """
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Elimina un producto por ID y retorna si la operacion fue exitosa.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            bool: True si se elimino, False si no existia.
        """
        pass


class IChatRepository(ABC):
    """Contrato para persistir y consultar mensajes de chat."""

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje de chat y retorna la entidad persistida.

        Args:
            message (ChatMessage): Mensaje a registrar.

        Returns:
            ChatMessage: Mensaje persistido.
        """
        pass

    @abstractmethod
    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Obtiene historial de una sesion en orden cronologico.

        Args:
            session_id (str): Identificador de sesion.
            limit (Optional[int]): Maximo de mensajes a recuperar.

        Returns:
            List[ChatMessage]: Historial ordenado de mas antiguo a mas reciente.
        """
        pass

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """Elimina historial de una sesion y retorna cuantos mensajes borro.

        Args:
            session_id (str): Sesion objetivo.

        Returns:
            int: Cantidad de registros eliminados.
        """
        pass

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """Obtiene los ultimos N mensajes de una sesion en orden cronologico.

        Args:
            session_id (str): Sesion objetivo.
            count (int): Numero maximo de mensajes.

        Returns:
            List[ChatMessage]: Mensajes recientes ordenados cronologicamente.
        """
        pass
