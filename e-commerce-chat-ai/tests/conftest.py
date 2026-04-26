import pytest

from src.domain.entities import Product


@pytest.fixture
def sample_product() -> Product:
    return Product(
        id=1,
        name="Air Zoom",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="Producto de ejemplo",
    )
