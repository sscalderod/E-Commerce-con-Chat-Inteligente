from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """Implementacion SQLAlchemy del repositorio de mensajes de chat."""

    def __init__(self, db: Session) -> None:
        """Inicializa el repositorio con sesion activa.

        Args:
            db (Session): Sesion SQLAlchemy.
        """
        self.db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje individual en la tabla de memoria."""
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(self, session_id: str, limit: int | None = None) -> list[ChatMessage]:
        """Obtiene historial de sesion en orden cronologico.

        Si se especifica un limite, retorna solo los ultimos N mensajes.
        """
        if limit is not None:
            models = (
                self.db.query(ChatMemoryModel)
                .filter(ChatMemoryModel.session_id == session_id)
                .order_by(ChatMemoryModel.timestamp.desc())
                .limit(limit)
                .all()
            )
            models.reverse()
        else:
            models = (
                self.db.query(ChatMemoryModel)
                .filter(ChatMemoryModel.session_id == session_id)
                .order_by(ChatMemoryModel.timestamp.asc())
                .all()
            )
        return [self._model_to_entity(model) for model in models]

    def delete_session_history(self, session_id: str) -> int:
        """Elimina todos los mensajes asociados a una sesion."""
        deleted_count = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted_count

    def get_recent_messages(self, session_id: str, count: int) -> list[ChatMessage]:
        """Obtiene los ultimos N mensajes en orden cronologico."""
        models_desc = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(count)
            .all()
        )
        models_desc.reverse()
        return [self._model_to_entity(model) for model in models_desc]

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """Convierte un modelo ORM de chat a entidad de dominio."""
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """Convierte una entidad de dominio a modelo ORM de chat."""
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp,
        )
