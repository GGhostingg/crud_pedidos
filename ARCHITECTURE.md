# Arquitectura y Flujo del Proyecto CRUD Pedidos

## 📋 Descripción General

Este proyecto implementa un sistema de gestión de pedidos con una arquitectura híbrida que combina Django para la interfaz web y FastAPI para la API REST, compartiendo una base de datos MySQL. Está diseñado para ser escalable, seguro y fácil de mantener.

## 🏗️ Arquitectura General

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Base de       │
│   (Django)      │◄──►│   (FastAPI)     │◄──►│   Datos         │
│                 │    │                 │    │   (MySQL)       │
│ - Templates     │    │ - Endpoints     │    │                 │
│ - Vistas        │    │ - JWT Auth      │    │ - Clientes      │
│ - Formularios   │    │ - Roles         │    │ - Productos     │
│ - Dashboard     │    │ - CRUD Ops      │    │ - Pedidos       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componentes Principales

1. **Django App** (`django_app/`)
   - Interfaz de usuario web
   - Autenticación de usuarios
   - Gestión de sesiones
   - Templates con Bootstrap

2. **FastAPI App** (`fastapi_app/`)
   - API RESTful
   - Autenticación JWT con refresh tokens
   - Control de acceso basado en roles
   - Operaciones CRUD

3. **Base de Datos** (MySQL)
   - Esquema compartido
   - Tablas: clientes, productos, pedidos, detalles_pedido, api_usuarios

## 🔄 Flujo de Datos

### 1. Autenticación y Autorización

#### Django (Web Interface)
```
Usuario → Login Form → Django Auth → Sesión → Acceso a vistas
```

#### FastAPI (API)
```
Cliente → POST /api/auth/token → JWT Token → Bearer Auth → Endpoints protegidos
```

### 2. Operaciones CRUD

#### Creación de Pedido (Ejemplo Completo)
```
1. Usuario autenticado en Django
2. Selecciona cliente y productos
3. Django valida y envía datos
4. FastAPI recibe request con JWT
5. Valida token y permisos
6. Verifica stock de productos
7. Crea pedido y detalles
8. Actualiza stock
9. Retorna respuesta
10. Django muestra confirmación
```

### 3. Dashboard y Estadísticas
```
Django View → Queries a MySQL → Agregaciones → Render Template → Usuario
```

## 📁 Estructura de Archivos Detallada

### Django App (`django_app/`)

```
config/
├── settings.py          # Configuración Django + BD MySQL
├── urls.py              # Rutas principales + auth
└── wsgi.py

pedidos/
├── models.py            # Modelos Django (Clientes, Productos, Pedidos)
├── views.py             # Vistas CBV + Dashboard
├── urls.py              # URLs de la app
├── admin.py             # Config Admin
├── apps.py              # Config App
├── exports.py           # Export PDF/Excel
├── tests.py             # Tests
└── templates/pedidos/   # Templates Bootstrap
    ├── base.html        # Layout base
    ├── login.html       # Login form
    ├── registro.html    # Registro form
    ├── dashboard.html   # Estadísticas
    ├── clientes/        # CRUD Clientes
    ├── productos/       # CRUD Productos
    └── pedidos/         # CRUD Pedidos

migrations/              # Migraciones BD
manage.py                # CLI Django
```

### FastAPI App (`fastapi_app/`)

```
auth.py                  # JWT utils + dependencias
database.py              # SQLAlchemy engine + session
main.py                  # App FastAPI + CORS
models_fa.py             # Modelos SQLAlchemy
schemas.py               # Pydantic schemas
pedidos.py               # Lógica pedidos (no en routers)

routers/
├── auth.py              # Endpoints auth (login/register/refresh)
├── clientes.py          # CRUD Clientes
├── productos.py         # CRUD Productos (con roles)
└── pedidos.py           # CRUD Pedidos (con roles)
```

## 🔐 Seguridad

### Autenticación
- **Django**: Sesiones basadas en cookies
- **FastAPI**: JWT tokens con expiración + refresh tokens

### Autorización
- **Django**: LoginRequiredMixin en vistas
- **FastAPI**: Dependencias `get_current_user` y `get_current_admin`

### Validaciones
- Pydantic schemas en FastAPI
- Django forms con validaciones
- Constraints de BD (unique, foreign keys)

## 🚀 Endpoints API (FastAPI)

### Autenticación
- `POST /api/auth/register` - Registro usuario
- `POST /api/auth/token` - Login (OAuth2)
- `POST /api/auth/refresh` - Refresh token

### Clientes
- `GET /api/clientes/` - Listar (paginado)
- `POST /api/clientes/` - Crear
- `GET /api/clientes/{id}` - Obtener
- `PUT /api/clientes/{id}` - Actualizar
- `DELETE /api/clientes/{id}` - Eliminar

### Productos (Admin only para write)
- `GET /api/productos/` - Listar
- `POST /api/productos/` - Crear (admin)
- `PUT /api/productos/{id}` - Actualizar (admin)
- `DELETE /api/productos/{id}` - Eliminar (admin)

### Pedidos (Admin only para update/delete)
- `GET /api/pedidos/` - Listar
- `POST /api/pedidos/` - Crear (user)
- `PUT /api/pedidos/{id}` - Actualizar (admin)
- `DELETE /api/pedidos/{id}` - Eliminar (admin)

## 💾 Modelo de Datos

### Relaciones
```
Cliente (1) ──── (N) Pedido (1) ──── (N) DetallePedido (N) ──── (1) Producto
```

### Tablas Principales
- **clientes**: id, nombre, correo, direccion, telefono
- **productos**: id, nombre, precio, stock
- **pedidos**: id, cliente_id, fecha, estado
- **detalles_pedido**: id, pedido_id, producto_id, cantidad
- **api_usuarios**: id, username, email, hashed_password, role

## 🔄 Ciclo de Vida de un Pedido

1. **Creación**: Usuario selecciona cliente y productos
2. **Validación**: Verifica stock disponible
3. **Transacción**: Crea pedido + detalles, reduce stock
4. **Estados**: Pendiente → Enviado → Entregado
5. **Ingresos**: Calcula total al marcar como Entregado

## 📊 Dashboard

Muestra métricas en tiempo real:
- Conteos totales
- Distribuciones por estado
- Alertas de stock bajo
- Ingresos acumulados

## 🧪 Testing

- Django: Tests unitarios en `tests.py`
- FastAPI: Tests con pytest (no implementados aún)
- Validación manual vía Swagger UI (`/api/docs`)

## 🚀 Despliegue

### Desarrollo
```bash
# Django
cd django_app && python manage.py runserver

# FastAPI
cd fastapi_app && uvicorn main:app --reload
```

### Producción
- Django: Gunicorn + Nginx
- FastAPI: Uvicorn + Nginx
- BD: MySQL en servidor separado
- Docker: Contenedores para cada servicio

## ❓ Preguntas Frecuentes

### ¿Por qué Django + FastAPI?
- Django: Rápido para prototipos web
- FastAPI: Alto rendimiento para APIs, mejor typing

### ¿Por qué MySQL compartido?
- Consistencia de datos
- Evita sincronización compleja

### ¿Cómo manejar concurrencia?
- Transacciones SQL para operaciones críticas
- Locks optimistas en stock

### ¿Escalabilidad?
- FastAPI puede escalar horizontalmente
- Django puede usar caching/CDN