import asyncio
from datetime import datetime

import pytest

from src.application.chat_service import ChatService
from src.application.dtos import ChatMessageRequestDTO, ProductDTO
from src.application.product_service import ProductService
from src.domain.entities import ChatMessage, Product
from src.domain.exceptions import ProductNotFoundError


class FakeProductRepository:
    def __init__(self, products: list[Product] | None = None) -> None:
        self.products = products or []

    def get_all(self) -> list[Product]:
        return list(self.products)

    def get_by_id(self, product_id: int) -> Product | None:
        for product in self.products:
            if product.id == product_id:
                return product
        return None

    def get_by_brand(self, brand: str) -> list[Product]:
        return [p for p in self.products if p.brand == brand]

    def get_by_category(self, category: str) -> list[Product]:
        return [p for p in self.products if p.category == category]

    def save(self, product: Product) -> Product:
        if product.id is None:
            next_id = max((p.id or 0 for p in self.products), default=0) + 1
            product.id = next_id
            self.products.append(product)
            return product

        for index, existing in enumerate(self.products):
            if existing.id == product.id:
                self.products[index] = product
                return product

        self.products.append(product)
        return product

    def delete(self, product_id: int) -> bool:
        initial_len = len(self.products)
        self.products = [p for p in self.products if p.id != product_id]
        return len(self.products) < initial_len


class FakeChatRepository:
    def __init__(self) -> None:
        self.messages: list[ChatMessage] = []

    def save_message(self, message: ChatMessage) -> ChatMessage:
        message.id = len(self.messages) + 1
        self.messages.append(message)
        return message

    def get_session_history(self, session_id: str, limit: int | None = None) -> list[ChatMessage]:
        session_messages = [m for m in self.messages if m.session_id == session_id]
        if limit is not None:
            return session_messages[-limit:]
        return session_messages

    def delete_session_history(self, session_id: str) -> int:
        before = len(self.messages)
        self.messages = [m for m in self.messages if m.session_id != session_id]
        return before - len(self.messages)

    def get_recent_messages(self, session_id: str, count: int) -> list[ChatMessage]:
        session_messages = [m for m in self.messages if m.session_id == session_id]
        return session_messages[-count:]


class FakeAIService:
    async def generate_response(self, user_message: str, products: list[Product], context) -> str:
        return f"Respuesta IA para: {user_message}"


def build_product(product_id: int = 1, stock: int = 5) -> Product:
    return Product(
        id=product_id,
        name="Air Zoom",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=stock,
        description="Producto de prueba",
    )


def test_product_service_get_product_by_id_ok() -> None:
    repo = FakeProductRepository([build_product(1)])
    service = ProductService(repo)

    result = service.get_product_by_id(1)
    assert result.id == 1


def test_product_service_get_product_by_id_not_found() -> None:
    repo = FakeProductRepository([])
    service = ProductService(repo)

    with pytest.raises(ProductNotFoundError):
        service.get_product_by_id(999)


def test_product_service_create_product() -> None:
    repo = FakeProductRepository([])
    service = ProductService(repo)
    dto = ProductDTO(
        name="Ultraboost",
        brand="Adidas",
        category="Running",
        size="41",
        color="Blanco",
        price=150.0,
        stock=3,
        description="Nuevo producto",
    )

    saved = service.create_product(dto)
    assert saved.id is not None
    assert saved.name == "Ultraboost"


def test_product_service_get_available_products() -> None:
    repo = FakeProductRepository([build_product(1, stock=3), build_product(2, stock=0)])
    service = ProductService(repo)

    result = service.get_available_products()
    assert len(result) == 1
    assert result[0].id == 1


def test_chat_service_process_message() -> None:
    product_repo = FakeProductRepository([build_product(1)])
    chat_repo = FakeChatRepository()
    ai_service = FakeAIService()
    service = ChatService(product_repo, chat_repo, ai_service)

    request = ChatMessageRequestDTO(session_id="user-123", message="Busco running")
    response = asyncio.run(service.process_message(request))

    assert response.session_id == "user-123"
    assert response.user_message == "Busco running"
    assert "Respuesta IA" in response.assistant_message
    assert len(chat_repo.messages) == 2


def test_chat_service_history_and_clear() -> None:
    product_repo = FakeProductRepository([build_product(1)])
    chat_repo = FakeChatRepository()
    ai_service = FakeAIService()
    service = ChatService(product_repo, chat_repo, ai_service)

    chat_repo.save_message(
        ChatMessage(
            id=None,
            session_id="user-abc",
            role="user",
            message="Hola",
            timestamp=datetime.utcnow(),
        )
    )
    chat_repo.save_message(
        ChatMessage(
            id=None,
            session_id="user-abc",
            role="assistant",
            message="Hola, te ayudo",
            timestamp=datetime.utcnow(),
        )
    )

    history = service.get_session_history("user-abc", limit=10)
    assert len(history) == 2

    deleted = service.clear_session_history("user-abc")
    assert deleted == 2
