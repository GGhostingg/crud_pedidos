# QWEN.md - Project Context: CRUD Pedidos

## Project Overview

**CRUD Pedidos** is a hybrid order management system that combines **Django** for the web interface and **FastAPI** for a REST API, both sharing a **MySQL** database. The project implements complete CRUD operations for clients, products, and orders with authentication, role-based access control, and a statistics dashboard.

### Key Features
- **Django Web App**: Session-based authentication, CRUD operations, dashboard with real-time statistics, search/filtering, Bootstrap 5 UI
- **FastAPI REST API**: JWT authentication with refresh tokens, role-based access control (admin/user), Pydantic validation, automatic Swagger/OpenAPI documentation
- **Shared MySQL Database**: Ensures data consistency between both services
- **Export Capabilities**: PDF and Excel export functionality

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | Django 6.0.4 |
| API Framework | FastAPI 0.135.3 |
| Database | MySQL (via mysqlclient/PyMySQL) |
| ORM (Django) | Django ORM |
| ORM (FastAPI) | SQLAlchemy 2.0 |
| Validation | Pydantic 2.12 |
| Auth (FastAPI) | JWT (python-jose) + bcrypt |
| Auth (Django) | Session-based + custom EmailBackend |
| UI | Bootstrap 5 |
| Export | reportlab (PDF), openpyxl (Excel) |
| Server | Uvicorn (FastAPI), Django dev server |

## Project Structure

```
crud_pedidos/
├── django_app/                 # Django web application
│   ├── config/                 # Django configuration, URLs, WSGI
│   │   ├── settings.py         # MySQL config, sessions, auth backends
│   │   └── urls.py
│   ├── pedidos/                # Main Django app
│   │   ├── models.py           # Models: Cliente, Producto, Pedido, DetallePedido
│   │   ├── views.py            # CBV views + dashboard
│   │   ├── forms.py            # Custom forms
│   │   ├── urls.py
│   │   ├── exports.py          # PDF/Excel export
│   │   ├── tests.py
│   │   └── templates/          # Bootstrap 5 templates
│   └── manage.py
├── fastapi_app/                # FastAPI REST API
│   ├── main.py                 # Entry point, CORS, router registration
│   ├── auth.py                 # JWT token creation/verification
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models_fa.py            # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   └── routers/                # Endpoints organized by resource
│       ├── auth.py             # Login/register/refresh
│       ├── clientes.py         # Clients CRUD
│       ├── productos.py        # Products CRUD (admin-only for writes)
│       └── pedidos.py          # Orders CRUD (with stock validation)
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
├── README.md
├── ARCHITECTURE.md             # Architecture diagrams
├── DOCUMENTATION.md            # Complete documentation
├── FAQ.md                      # Technical Q&A
└── PRESENTATION_GUIDE.md       # Presentation script
```

## Building and Running

### Prerequisites
- Python 3.8+
- MySQL 8.0+ running locally

### Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your MySQL credentials and secrets
   ```

3. **Create MySQL database:**
   ```sql
   CREATE DATABASE crud_pedidos_db;
   ```

4. **Run Django migrations:**
   ```bash
   cd django_app
   python manage.py migrate
   ```

### Running Services

**Django (Web Interface):**
```bash
cd django_app
python manage.py runserver
# Access at http://localhost:8000
```

**FastAPI (REST API):**
```bash
cd fastapi_app
uvicorn main:app --reload
# Access at http://localhost:8000 (or different port if configured)
# Swagger UI at http://localhost:8000/api/docs
```

> **Note:** Both services share the same MySQL database. FastAPI creates its `api_usuarios` table automatically on startup via `Base.metadata.create_all()`.

## Key Configuration

### Environment Variables (.env)

| Variable | Purpose |
|----------|---------|
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | MySQL connection |
| `DJANGO_SECRET_KEY` | Django security key |
| `DJANGO_ALLOWED_HOSTS` | Django allowed hosts |
| `JWT_SECRET`, `JWT_ALGORITHM` | FastAPI JWT config |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL (default: 60) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL (default: 7) |
| `CORS_ALLOWED_ORIGINS` | FastAPI CORS whitelist |

### Session Configuration
- Django sessions expire in **120 seconds** (configurable in `settings.py`)
- Session does NOT refresh on each request (`SESSION_SAVE_EVERY_REQUEST = False`)

## Data Model

```
Cliente (1) ──── (N) Pedido (1) ──── (N) DetallePedido (N) ──── (1) Producto
                                              └── usuario (N) ──── (1) User
```

### Main Tables
- **clientes**: id, nombre, correo, dirección, teléfono
- **productos**: id, nombre, precio, stock
- **pedidos**: id, cliente_id, usuario_id, fecha, estado
- **detalles_pedido**: id, pedido_id, producto_id, cantidad, precio_unitario
- **api_usuarios**: id, username, email, hashed_password, role (for FastAPI auth)

### Order States
`Pendiente` → `Enviado` → `Entregado` (or `Anulado`)

## API Endpoints (FastAPI)

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/token` - Login (OAuth2 password flow)
- `POST /api/auth/refresh` - Refresh access token

### Clients
- `GET /api/clientes/` - List (paginated)
- `POST /api/clientes/` - Create
- `GET /api/clientes/{id}` - Get
- `PUT /api/clientes/{id}` - Update
- `DELETE /api/clientes/{id}` - Delete

### Products (Admin-only for writes)
- `GET /api/productos/` - List
- `POST /api/productos/` - Create (admin)
- `PUT /api/productos/{id}` - Update (admin)
- `DELETE /api/productos/{id}` - Delete (admin)

### Orders
- `GET /api/pedidos/` - List
- `POST /api/pedidos/` - Create (user)
- `PUT /api/pedidos/{id}` - Update (admin)
- `DELETE /api/pedidos/{id}` - Delete (admin)

## Development Conventions

### Code Style
- Django uses **Class-Based Views** (CBV) with `LoginRequiredMixin`
- FastAPI uses **router organization** with separate modules per resource
- Pydantic schemas for all API request/response validation
- SQLAlchemy models use `declarative_base`

### Security
- **Django**: CSRF protection, session auth, SQL injection protection via ORM
- **FastAPI**: JWT tokens, bcrypt password hashing, role-based dependencies (`get_current_user`, `get_current_admin`)
- **Database**: Stock validation with atomic transactions to prevent overselling

### Testing
- Django: Unit tests in `pedidos/tests.py`
- FastAPI: Manual testing via Swagger UI (`/api/docs`); automated tests not yet implemented

## Common Tasks

### Run Tests
```bash
cd django_app
python manage.py test
```

### Create Migrations (Django)
```bash
cd django_app
python manage.py makemigrations
python manage.py migrate
```

### Add New FastAPI Endpoint
1. Create/edit router in `fastapi_app/routers/`
2. Register in `fastapi_app/main.py` with `app.include_router()`

## Important Notes

- Both services use the **same `.env` file** in the project root for database configuration
- FastAPI tables are created automatically; Django requires explicit migrations
- Session timeout is short (2 minutes) — designed for demo purposes
- The context processor `pedidos.views.nombre_visible` is registered in Django's TEMPLATES

## Useful Links

- **Django Admin**: http://localhost:8000/admin/ (if configured)
- **FastAPI Swagger UI**: http://localhost:8000/api/docs
- **FastAPI ReDoc**: http://localhost:8000/redoc
