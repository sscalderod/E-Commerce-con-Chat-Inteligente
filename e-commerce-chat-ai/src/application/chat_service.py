from datetime import datetime
from typing import Any
import inspect

from src.application.dtos import ChatHistoryDTO, ChatMessageRequestDTO, ChatMessageResponseDTO
from src.domain.entities import ChatContext, ChatMessage
from src.domain.exceptions import ChatServiceError
from src.domain.repositories import IChatRepository, IProductRepository


class ChatService:
    """Servicio de aplicacion para gestionar el chat conversacional.

    Orquesta productos, historial y proveedor de IA para producir respuestas
    contextuales y persistir la conversacion de cada sesion.
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service: Any,
    ) -> None:
        """Inicializa el servicio con sus dependencias.

        Args:
            product_repository (IProductRepository): Fuente de productos.
            chat_repository (IChatRepository): Fuente de historial conversacional.
            ai_service (Any): Proveedor de IA con metodo generate_response.
        """
        self.product_repository = product_repository
        self.chat_repository = chat_repository
        self.ai_service = ai_service

    async def process_message(
        self, request: ChatMessageRequestDTO
    ) -> ChatMessageResponseDTO:
        """Procesa un mensaje de usuario y retorna una respuesta del asistente.

        Flujo:
            1. Obtiene catalogo de productos.
            2. Recupera historial reciente de la sesion.
            3. Genera respuesta con proveedor de IA.
            4. Guarda mensaje de usuario y respuesta.

        Args:
            request (ChatMessageRequestDTO): Mensaje entrante con session_id.

        Returns:
            ChatMessageResponseDTO: Respuesta final para el cliente.

        Raises:
            ChatServiceError: Si ocurre una falla en cualquier parte del flujo.
        """
        try:
            products = self.product_repository.get_all()
            recent_messages = self.chat_repository.get_recent_messages(
                request.session_id, count=6
            )
            context = ChatContext(messages=recent_messages, max_messages=6)

            ai_response = self.ai_service.generate_response(
                user_message=request.message,
                products=products,
                context=context,
            )
            if inspect.isawaitable(ai_response):
                ai_response = await ai_response

            timestamp = datetime.utcnow()
            user_msg = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=timestamp,
            )
            assistant_msg = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=ai_response,
                timestamp=timestamp,
            )

            self.chat_repository.save_message(user_msg)
            self.chat_repository.save_message(assistant_msg)

            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=ai_response,
                timestamp=timestamp,
            )
        except ChatServiceError:
            raise
        except Exception as error:
            raise ChatServiceError(str(error)) from error

    def get_session_history(
        self, session_id: str, limit: int | None = None
    ) -> list[ChatHistoryDTO]:
        """Obtiene el historial de una sesion en formato DTO.

        Args:
            session_id (str): Identificador de sesion.
            limit (int | None): Maximo de mensajes a retornar.

        Returns:
            list[ChatHistoryDTO]: Historial en orden cronologico.
        """
        messages = self.chat_repository.get_session_history(session_id, limit=limit)
        return [
            ChatHistoryDTO(
                id=message.id or 0,
                role=message.role,
                message=message.message,
                timestamp=message.timestamp,
            )
            for message in messages
        ]

    def clear_session_history(self, session_id: str) -> int:
        """Elimina todo el historial de una sesion y retorna el total eliminado.

        Args:
            session_id (str): Identificador de sesion.

        Returns:
            int: Numero de mensajes eliminados.
        """
        return self.chat_repository.delete_session_history(session_id)
