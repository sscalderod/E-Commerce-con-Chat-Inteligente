from datetime import datetime

import pytest

from src.domain.entities import ChatContext, ChatMessage, Product


def build_product(**kwargs) -> Product:
    data = {
        "id": None,
        "name": "Air Zoom",
        "brand": "Nike",
        "category": "Running",
        "size": "42",
        "color": "Negro",
        "price": 120.0,
        "stock": 5,
        "description": "Zapato de prueba",
    }
    data.update(kwargs)
    return Product(**data)


def test_product_valid_creation() -> None:
    product = build_product()
    assert product.name == "Air Zoom"
    assert product.stock == 5


def test_product_invalid_price_raises() -> None:
    with pytest.raises(ValueError, match="precio"):
        build_product(price=0)


def test_product_invalid_stock_raises() -> None:
    with pytest.raises(ValueError, match="stock"):
        build_product(stock=-1)


def test_product_empty_name_raises() -> None:
    with pytest.raises(ValueError, match="nombre"):
        build_product(name="")


def test_product_is_available() -> None:
    assert build_product(stock=2).is_available() is True
    assert build_product(stock=0).is_available() is False


def test_product_reduce_stock_success() -> None:
    product = build_product(stock=5)
    product.reduce_stock(2)
    assert product.stock == 3


def test_product_reduce_stock_invalid_quantity() -> None:
    product = build_product(stock=5)
    with pytest.raises(ValueError, match="cantidad"):
        product.reduce_stock(0)


def test_product_reduce_stock_not_enough() -> None:
    product = build_product(stock=3)
    with pytest.raises(ValueError, match="suficiente"):
        product.reduce_stock(4)


def test_product_increase_stock_success() -> None:
    product = build_product(stock=2)
    product.increase_stock(3)
    assert product.stock == 5


def test_product_increase_stock_invalid_quantity() -> None:
    product = build_product(stock=2)
    with pytest.raises(ValueError, match="cantidad"):
        product.increase_stock(-1)


def test_chat_message_valid_creation() -> None:
    message = ChatMessage(
        id=None,
        session_id="session-1",
        role="user",
        message="Hola",
        timestamp=datetime.utcnow(),
    )
    assert message.is_from_user() is True
    assert message.is_from_assistant() is False


def test_chat_message_invalid_role_raises() -> None:
    with pytest.raises(ValueError, match="rol"):
        ChatMessage(
            id=None,
            session_id="session-1",
            role="system",
            message="Hola",
            timestamp=datetime.utcnow(),
        )


def test_chat_context_format_for_prompt() -> None:
    messages = [
        ChatMessage(
            id=1,
            session_id="session-1",
            role="user",
            message="Hola",
            timestamp=datetime.utcnow(),
        ),
        ChatMessage(
            id=2,
            session_id="session-1",
            role="assistant",
            message="Hola, en que te ayudo?",
            timestamp=datetime.utcnow(),
        ),
    ]
    context = ChatContext(messages=messages, max_messages=6)
    text = context.format_for_prompt()

    assert "Usuario: Hola" in text
    assert "Asistente: Hola, en que te ayudo?" in text
