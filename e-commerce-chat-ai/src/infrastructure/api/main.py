from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.application.chat_service import ChatService
from src.application.dtos import (
    ChatHistoryDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ProductDTO,
)
from src.application.product_service import ProductService
from src.domain.exceptions import ChatServiceError, ProductNotFoundError
from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.repositories.product_repository import SQLProductRepository

app = FastAPI(
    title="E-commerce Chat AI API",
    description="API REST para e-commerce de zapatos con asistente conversacional.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Inicializa recursos de infraestructura al arrancar la aplicacion.

    Crea tablas faltantes y carga datos semilla para facilitar uso inicial.
    """
    init_db()


@app.get("/")
def root() -> dict:
    """Retorna metadatos de la API.

    Returns:
        dict: Informacion de version y rutas disponibles.
    """
    return {
        "name": "E-commerce Chat AI API",
        "version": "1.0.0",
        "description": "API de productos y chat inteligente para tienda de zapatos",
        "endpoints": [
            "GET /products",
            "GET /products/{product_id}",
            "POST /chat",
            "GET /chat/history/{session_id}",
            "DELETE /chat/history/{session_id}",
            "GET /health",
        ],
    }


@app.get("/products", response_model=list[ProductDTO])
def get_products(db: Session = Depends(get_db)) -> list[ProductDTO]:
    """Obtiene el listado completo de productos.

    Args:
        db (Session): Sesion de base de datos inyectada por FastAPI.

    Returns:
        list[ProductDTO]: Catalogo completo de productos.
    """
    product_repository = SQLProductRepository(db)
    product_service = ProductService(product_repository)
    return product_service.get_all_products()


@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
    """Obtiene un producto por ID y responde 404 si no existe.

    Args:
        product_id (int): Identificador del producto.
        db (Session): Sesion de base de datos inyectada.

    Returns:
        ProductDTO: Producto encontrado.

    Raises:
        HTTPException: Con codigo 404 cuando el producto no existe.
    """
    product_repository = SQLProductRepository(db)
    product_service = ProductService(product_repository)
    try:
        return product_service.get_product_by_id(product_id)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/chat", response_model=ChatMessageResponseDTO)
async def process_chat_message(
    request: ChatMessageRequestDTO,
    db: Session = Depends(get_db),
) -> ChatMessageResponseDTO:
    """Procesa un mensaje de usuario y retorna respuesta del asistente IA.

    Args:
        request (ChatMessageRequestDTO): Payload con session_id y mensaje.
        db (Session): Sesion de base de datos inyectada.

    Returns:
        ChatMessageResponseDTO: Interaccion completa usuario-asistente.

    Raises:
        HTTPException: Con codigo 500 cuando ocurre un error interno.
    """
    product_repository = SQLProductRepository(db)
    chat_repository = SQLChatRepository(db)

    try:
        ai_service = GeminiService()
        chat_service = ChatService(product_repository, chat_repository, ai_service)
        return await chat_service.process_message(request)
    except ChatServiceError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno procesando el chat: {error}",
        ) from error


@app.get("/chat/history/{session_id}", response_model=list[ChatHistoryDTO])
def get_chat_history(
    session_id: str,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ChatHistoryDTO]:
    """Obtiene el historial de una sesion de chat.

    Args:
        session_id (str): Identificador de sesion.
        limit (int): Maximo de mensajes a retornar.
        db (Session): Sesion de base de datos inyectada.

    Returns:
        list[ChatHistoryDTO]: Historial de conversacion.
    """
    product_repository = SQLProductRepository(db)
    chat_repository = SQLChatRepository(db)
    chat_service = ChatService(product_repository, chat_repository, ai_service=None)
    return chat_service.get_session_history(session_id=session_id, limit=limit)


@app.delete("/chat/history/{session_id}")
def delete_chat_history(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Elimina todo el historial de una sesion y retorna cantidad eliminada.

    Args:
        session_id (str): Identificador de sesion.
        db (Session): Sesion de base de datos inyectada.

    Returns:
        dict: Resumen con session_id y mensajes eliminados.
    """
    product_repository = SQLProductRepository(db)
    chat_repository = SQLChatRepository(db)
    chat_service = ChatService(product_repository, chat_repository, ai_service=None)

    deleted_count = chat_service.clear_session_history(session_id=session_id)
    return {
        "session_id": session_id,
        "deleted_messages": deleted_count,
    }


@app.get("/health")
def health_check() -> dict:
    """Endpoint de verificacion de salud de la API.

    Returns:
        dict: Estado actual del servicio y timestamp UTC.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }
