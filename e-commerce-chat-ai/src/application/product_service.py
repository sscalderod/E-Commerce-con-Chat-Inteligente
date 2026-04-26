from typing import Any

from src.application.dtos import ProductDTO
from src.domain.entities import Product
from src.domain.exceptions import InvalidProductDataError, ProductNotFoundError
from src.domain.repositories import IProductRepository


class ProductService:
    """Servicio de aplicacion para casos de uso de productos.

    Coordina validaciones de dominio y operaciones del repositorio para exponer
    flujos de consulta y administracion de productos.
    """

    def __init__(self, product_repository: IProductRepository) -> None:
        """Inicializa el servicio con su dependencia de persistencia.

        Args:
            product_repository (IProductRepository): Repositorio de productos.
        """
        self.product_repository = product_repository

    def get_all_products(self) -> list[ProductDTO]:
        """Retorna todos los productos registrados.

        Returns:
            list[ProductDTO]: Lista completa de productos.
        """
        products = self.product_repository.get_all()
        return [self._to_dto(product) for product in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """Busca un producto por ID y falla si no existe.

        Args:
            product_id (int): Identificador de producto.

        Returns:
            ProductDTO: Producto encontrado.

        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return self._to_dto(product)

    def search_products(self, filters: dict[str, Any]) -> list[ProductDTO]:
        """Filtra productos por marca, categoria y disponibilidad.

        Args:
            filters (dict[str, Any]): Diccionario con filtros opcionales.

        Returns:
            list[ProductDTO]: Productos que cumplen filtros.
        """
        brand = filters.get("brand")
        category = filters.get("category")
        only_available = filters.get("available")

        if brand:
            products = self.product_repository.get_by_brand(brand)
        elif category:
            products = self.product_repository.get_by_category(category)
        else:
            products = self.product_repository.get_all()

        if only_available:
            products = [product for product in products if product.is_available()]

        return [self._to_dto(product) for product in products]

    def create_product(self, product_dto: ProductDTO) -> ProductDTO:
        """Crea un producto nuevo a partir de un DTO.

        Args:
            product_dto (ProductDTO): Datos de entrada del producto.

        Returns:
            ProductDTO: Producto persistido.

        Raises:
            InvalidProductDataError: Si la informacion de entrada es invalida.
        """
        try:
            product = self._to_entity(product_dto, keep_id=False)
        except ValueError as error:
            raise InvalidProductDataError(str(error)) from error

        saved_product = self.product_repository.save(product)
        return self._to_dto(saved_product)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """Actualiza un producto existente por su ID.

        Args:
            product_id (int): ID del producto a actualizar.
            product_dto (ProductDTO): Datos nuevos del producto.

        Returns:
            ProductDTO: Producto actualizado.

        Raises:
            ProductNotFoundError: Si el producto no existe.
            InvalidProductDataError: Si los datos nuevos no son validos.
        """
        existing_product = self.product_repository.get_by_id(product_id)
        if existing_product is None:
            raise ProductNotFoundError(product_id)

        try:
            updated_entity = self._to_entity(product_dto, keep_id=True)
            updated_entity.id = product_id
        except ValueError as error:
            raise InvalidProductDataError(str(error)) from error

        saved_product = self.product_repository.save(updated_entity)
        return self._to_dto(saved_product)

    def delete_product(self, product_id: int) -> bool:
        """Elimina un producto por ID y retorna True si fue eliminado.

        Args:
            product_id (int): ID del producto objetivo.

        Returns:
            bool: True si se elimino correctamente.

        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        existing_product = self.product_repository.get_by_id(product_id)
        if existing_product is None:
            raise ProductNotFoundError(product_id)
        return self.product_repository.delete(product_id)

    def get_available_products(self) -> list[ProductDTO]:
        """Retorna productos con stock disponible.

        Returns:
            list[ProductDTO]: Productos cuyo stock es mayor que cero.
        """
        products = self.product_repository.get_all()
        available_products = [product for product in products if product.is_available()]
        return [self._to_dto(product) for product in available_products]

    def _to_dto(self, product: Product) -> ProductDTO:
        """Convierte entidad de dominio a DTO.

        Args:
            product (Product): Entidad de dominio.

        Returns:
            ProductDTO: DTO serializable.
        """
        return ProductDTO(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description,
        )

    def _to_entity(self, product_dto: ProductDTO, keep_id: bool) -> Product:
        """Convierte DTO a entidad de dominio.

        Args:
            product_dto (ProductDTO): DTO de entrada.
            keep_id (bool): Indica si debe conservarse el ID recibido.

        Returns:
            Product: Entidad de dominio para persistencia.
        """
        return Product(
            id=product_dto.id if keep_id else None,
            name=product_dto.name,
            brand=product_dto.brand,
            category=product_dto.category,
            size=product_dto.size,
            color=product_dto.color,
            price=product_dto.price,
            stock=product_dto.stock,
            description=product_dto.description,
        )
