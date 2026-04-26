import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ecommerce_chat.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    """Provee una sesion de base de datos para dependencias de FastAPI.

    Yields:
        Generator: Sesion SQLAlchemy activa.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Inicializa esquema de base de datos y datos semilla.

    Esta funcion crea todas las tablas declaradas en ORM y luego invoca
    la carga de catalogo inicial si la tabla de productos esta vacia.
    """
    from src.infrastructure.db import models  # noqa: F401
    from src.infrastructure.db.init_data import load_initial_data

    Base.metadata.create_all(bind=engine)
    load_initial_data()
