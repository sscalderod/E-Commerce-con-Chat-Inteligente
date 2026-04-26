# E-commerce con Chat IA

## Descripcion
API REST para una tienda de zapatos con asistente conversacional usando Clean Architecture.

## Caracteristicas principales
- Catalogo de productos con filtros por marca y categoria.
- Chat con IA usando Google Gemini.
- Memoria conversacional por session_id.
- Persistencia con SQLite y SQLAlchemy.
- Arquitectura en capas: Domain, Application, Infrastructure.

## Arquitectura
El proyecto sigue Clean Architecture:
- Domain: entidades, contratos de repositorio, excepciones de negocio.
- Application: DTOs y casos de uso (servicios).
- Infrastructure: FastAPI, ORM, repositorios SQL y proveedor Gemini.

## Tecnologias
- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic
- Google Gemini API
- Docker y Docker Compose
- Pytest

## Estructura del proyecto
```text
src/
  domain/
  application/
  infrastructure/
tests/
data/
```

## Instalacion
### Requisitos previos
- Python 3.10 o superior
- Docker (opcional)
- API Key de Google Gemini

### Pasos
1. Clonar repositorio
```bash
git clone <tu-repo>
cd e-commerce-chat-ai
```

2. Crear y activar entorno virtual
```bash
python -m venv venv
source venv/bin/activate
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con GEMINI_API_KEY real
```

## Ejecucion local
```bash
uvicorn src.infrastructure.api.main:app --reload
```

## Ejecucion con Docker
```bash
docker compose up --build
```

## Documentacion de la API
- Swagger UI: http://localhost:8000/docs

## Endpoints principales
- `GET /products`: Lista todos los productos.
- `GET /products/{id}`: Obtiene un producto por ID.
- `POST /chat`: Procesa mensaje y retorna respuesta IA.
- `GET /chat/history/{session_id}`: Recupera historial de una sesion.
- `DELETE /chat/history/{session_id}`: Limpia historial de una sesion.
- `GET /health`: Estado del servicio.

### Ejemplo de request al chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"user123","message":"Busco zapatos para correr"}'
```

## Testing
Ejecutar pruebas unitarias:
```bash
pytest -q
```

## Notas
- La base de datos se crea automaticamente en `data/ecommerce_chat.db`.
- En startup se inicializan tablas y datos semilla.
- Para eliminar datos de prueba, borra el archivo `.db` y reinicia la API.

