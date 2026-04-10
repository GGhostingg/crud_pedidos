# CRUD Pedidos - Django + FastAPI

Proyecto de gestión de pedidos con interfaz web en Django y API REST en FastAPI, compartiendo base de datos MySQL.

## Características

- **Django**: Interfaz web con login, CRUD de clientes, productos y pedidos, dashboard con estadísticas, búsqueda y filtros.
- **FastAPI**: API REST con JWT, roles (admin/user), refresh tokens.
- **Base de datos**: MySQL compartida.
- **Estilos**: Bootstrap 5.

## Instalación

1. Clona el repositorio.
2. Crea un entorno virtual y activa.
3. Instala dependencias: `pip install -r requirements.txt`
4. Configura MySQL y crea la base de datos.
5. Crea `.env` en la raíz con:
   ```
   DJANGO_SECRET_KEY=tu_clave
   DB_NAME=tu_db
   DB_USER=tu_user
   DB_PASSWORD=tu_pass
   DB_HOST=localhost
   DB_PORT=3306
   SECRET_KEY=tu_secret_fastapi
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_MINUTES=1440
   ```
6. Para Django: `cd django_app && python manage.py migrate`
7. Para FastAPI: Las tablas se crean automáticamente al iniciar.

## Ejecución

- Django: `cd django_app && python manage.py runserver`
- FastAPI: `cd fastapi_app && uvicorn main:app --reload`

## Uso

- Accede a Django en http://localhost:8000
- Regístrate o inicia sesión.
- API en http://localhost:8000/api/docs

## Sugerencias Implementadas

- Búsqueda en clientes.
- Dashboard con estadísticas.
- Refresh tokens en FastAPI.
- Roles en FastAPI (admin para CRUD productos/pedidos, user para leer y crear pedidos).