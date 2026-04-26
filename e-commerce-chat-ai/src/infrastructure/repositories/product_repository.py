from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """Implementacion SQLAlchemy del repositorio de productos."""

    def __init__(self, db: Session) -> None:
        """Inicializa el repositorio con sesion activa.

        Args:
            db (Session): Sesion SQLAlchemy.
        """
        self.db = db

    def get_all(self) -> list[Product]:
        """Recupera todos los productos desde la base de datos."""
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_id(self, product_id: int) -> Product | None:
        """Busca un producto por ID.

        Args:
            product_id (int): ID de producto.

        Returns:
            Product | None: Entidad encontrada o None.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return self._model_to_entity(model) if model else None

    def get_by_brand(self, brand: str) -> list[Product]:
        """Filtra productos por marca."""
        models = self.db.query(ProductModel).filter(ProductModel.brand == brand).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_category(self, category: str) -> list[Product]:
        """Filtra productos por categoria."""
        models = self.db.query(ProductModel).filter(ProductModel.category == category).all()
        return [self._model_to_entity(model) for model in models]

    def save(self, product: Product) -> Product:
        """Crea o actualiza un producto en persistencia.

        Args:
            product (Product): Entidad de dominio.

        Returns:
            Product: Entidad persistida y refrescada.
        """
        if product.id is None:
            model = self._entity_to_model(product)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._model_to_entity(model)

        existing_model = self.db.query(ProductModel).filter(ProductModel.id == product.id).first()
        if existing_model is None:
            model = self._entity_to_model(product)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._model_to_entity(model)

        existing_model.name = product.name
        existing_model.brand = product.brand
        existing_model.category = product.category
        existing_model.size = product.size
        existing_model.color = product.color
        existing_model.price = product.price
        existing_model.stock = product.stock
        existing_model.description = product.description

        self.db.commit()
        self.db.refresh(existing_model)
        return self._model_to_entity(existing_model)

    def delete(self, product_id: int) -> bool:
        """Elimina un producto por su identificador.

        Args:
            product_id (int): ID objetivo.

        Returns:
            bool: True si se elimina, False si no existe.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model is None:
            return False

        self.db.delete(model)
        self.db.commit()
        return True

    def _model_to_entity(self, model: ProductModel) -> Product:
        """Convierte un modelo ORM a entidad de dominio."""
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """Convierte una entidad de dominio a modelo ORM."""
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description,
        )
