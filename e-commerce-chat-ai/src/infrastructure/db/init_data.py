from sqlalchemy.exc import SQLAlchemyError

from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.models import ProductModel


def load_initial_data() -> None:
    """Carga productos de ejemplo solo si la tabla de productos esta vacia.

    Inserta un catalogo base de 10 productos con diferentes marcas,
    categorias y precios para facilitar pruebas iniciales.

    Raises:
        SQLAlchemyError: Si ocurre un error durante insercion o commit.
    """
    db = SessionLocal()
    try:
        existing_products = db.query(ProductModel).count()
        if existing_products > 0:
            return

        products = [
            ProductModel(
                name="Air Zoom Pegasus 40",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=120.0,
                stock=5,
                description="Zapato de running con amortiguacion reactiva.",
            ),
            ProductModel(
                name="Ultraboost 22",
                brand="Adidas",
                category="Running",
                size="41",
                color="Blanco",
                price=150.0,
                stock=3,
                description="Modelo premium para corredores de media distancia.",
            ),
            ProductModel(
                name="Suede Classic",
                brand="Puma",
                category="Casual",
                size="40",
                color="Azul",
                price=80.0,
                stock=10,
                description="Estilo retro ideal para uso diario.",
            ),
            ProductModel(
                name="Chuck Taylor All Star",
                brand="Converse",
                category="Casual",
                size="39",
                color="Rojo",
                price=65.0,
                stock=12,
                description="Clasico urbano de lona y suela de goma.",
            ),
            ProductModel(
                name="574 Core",
                brand="New Balance",
                category="Casual",
                size="42",
                color="Gris",
                price=95.0,
                stock=7,
                description="Silueta comoda con soporte para caminatas largas.",
            ),
            ProductModel(
                name="Classic Leather",
                brand="Reebok",
                category="Casual",
                size="41",
                color="Blanco",
                price=85.0,
                stock=8,
                description="Diseno minimalista con acabado de cuero.",
            ),
            ProductModel(
                name="Gel-Kayano 30",
                brand="ASICS",
                category="Running",
                size="43",
                color="Verde",
                price=170.0,
                stock=4,
                description="Soporte avanzado para corredores pronadores.",
            ),
            ProductModel(
                name="Cloudswift",
                brand="On",
                category="Running",
                size="42",
                color="Gris",
                price=180.0,
                stock=2,
                description="Tecnologia cloud para absorcion de impacto urbano.",
            ),
            ProductModel(
                name="Cap-Toe Oxford",
                brand="Clarks",
                category="Formal",
                size="42",
                color="Cafe",
                price=140.0,
                stock=6,
                description="Zapato formal de cuero para oficina y eventos.",
            ),
            ProductModel(
                name="Derby Leather",
                brand="Hush Puppies",
                category="Formal",
                size="41",
                color="Negro",
                price=130.0,
                stock=5,
                description="Modelo formal comodo con plantilla acolchada.",
            ),
        ]

        db.add_all(products)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()
