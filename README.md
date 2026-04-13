# CRUD Pedidos — Sistema de Gestión de Pedidos

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Django](https://img.shields.io/badge/Django-6.0.4-092E20.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135.3-009688.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green.svg)

Sistema híbrido de gestión de pedidos con **interfaz web en Django** y **API REST en FastAPI**, compartiendo una base de datos **MySQL**. Incluye autenticación, control de acceso por roles, dashboard de estadísticas y exportación a PDF/Excel.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Ejecución](#-ejecución)
- [Uso](#-uso)
- [Endpoints de la API](#-endpoints-de-la-api-fastapi)
- [Modelo de Datos](#-modelo-de-datos)
- [Seguridad](#-seguridad)
- [Exportación](#-exportación)
- [Variables de Entorno](#-variables-de-entorno)
- [Testing](#-testing)
- [Despliegue](#-despliegue)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## ✨ Características

### 🌐 App Web (Django)
- Autenticación por sesiones con registro e inicio de sesión
- CRUD completo de **clientes**, **productos** y **pedidos**
- Dashboard con estadísticas en tiempo real
- Búsqueda y filtros avanzados
- Exportación a **PDF** y **Excel**
- Interfaz moderna con **Bootstrap 5**
- Validaciones de formularios en el servidor

### 🔌 API REST (FastAPI)
- Autenticación **JWT** con access y refresh tokens
- Control de acceso por roles (**admin** / **user**)
- Documentación automática con **Swagger UI** y **ReDoc**
- Validación automática con **Pydantic**
- CRUD completo para clientes, productos y pedidos
- Validación de stock en transacciones atómicas

### 🗄️ Base de Datos
- **MySQL** compartido entre Django y FastAPI
- Consistencia de datos garantizada
- Transacciones ACID para operaciones críticas

---

## 🏗️ Arquitectura

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│   Django App     │       │   FastAPI App    │       │   MySQL Database │
│   (Web UI)       │◄─────►│   (REST API)     │◄─────►│   (Compartida)   │
│                  │       │                  │       │                  │
│ • Sesiones       │       │ • JWT Auth       │       │ • clientes       │
│ • Templates      │       │ • Roles          │       │ • productos      │
│ • Formularios    │       │ • CRUD           │       │ • pedidos        │
│ • Dashboard      │       │ • Swagger UI     │       │ • detalles_pedido│
│ • PDF/Excel      │       │ • Pydantic       │       │ • api_usuarios   │
└──────────────────┘       └──────────────────┘       └──────────────────┘
```

> [!NOTE]
> Ambos servicios comparten la misma base de datos MySQL, lo que garantiza consistencia de datos sin necesidad de sincronización.

---

## 📦 Requisitos

| Software | Versión | Propósito |
|----------|---------|-----------|
| Python | 3.12+ | Entorno de ejecución |
| MySQL | 8.0+ | Base de datos relacional |
| pip | 23.0+ | Gestor de paquetes |
| venv | Incluido | Entorno virtual |

> [!TIP]
> Se recomienda usar **MySQL 8.0** o superior para mejor rendimiento y compatibilidad con SQLAlchemy 2.0.

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/crud-pedidos.git
cd crud-pedidos
```

### 2. Crear y activar entorno virtual

```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

> [!IMPORTANT]
> Asegúrate de tener instalado **mysqlclient** previamente. En sistemas Debian/Ubuntu:
> ```bash
> sudo apt install default-libmysqlclient-dev build-essential pkg-config
> ```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales de MySQL y secretos de seguridad:

```env
# Base de datos
DB_NAME=crud_pedidos_db
DB_USER=root
DB_PASSWORD=tu_password_aqui
DB_HOST=localhost
DB_PORT=3306

# Django
DJANGO_SECRET_KEY=cambia-esto-por-una-clave-segura-y-unica
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# FastAPI - JWT
JWT_SECRET=tu_jwt_secret_aqui
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# FastAPI - CORS
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### 5. Crear la base de datos

```sql
CREATE DATABASE crud_pedidos_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Ejecutar migraciones de Django

```bash
cd django_app
python manage.py migrate
```

> [!NOTE]
> FastAPI crea su tabla `api_usuarios` automáticamente al iniciar. No requiere migraciones.

---

## 🖥️ Ejecución

### Servidor Django (Interfaz Web)

```bash
cd django_app
python manage.py runserver
```

Accede en: **http://localhost:8000**

### Servidor FastAPI (API REST)

```bash
cd fastapi_app
uvicorn main:app --reload
```

- API base: **http://localhost:8000**
- Swagger UI: **http://localhost:8000/api/docs**
- ReDoc: **http://localhost:8000/redoc**

> [!TIP]
> Ejecuta ambos servicios en terminales separadas para usar la aplicación completa.

---

## 📖 Uso

### Primeros pasos

1. Abre **http://localhost:8000** en tu navegador
2. Regístrate con el botón **"Crear cuenta"**
3. Inicia sesión con tus credenciales
4. Explora el **dashboard** con estadísticas
5. Crea clientes, productos y pedidos desde el menú lateral

### Roles de usuario

| Rol | Permisos |
|-----|----------|
| **User** | Crear pedidos, ver sus pedidos, editar pedidos pendientes |
| **Admin** | CRUD completo de clientes, productos y pedidos, cambiar estados |

> [!CAUTION]
> La sesión de Django expira en **120 segundos** por defecto. Para producción, aumenta este valor en `settings.py`.

---

## 🔌 Endpoints de la API (FastAPI)

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Registrar nuevo usuario |
| `POST` | `/api/auth/token` | Login (OAuth2 password flow) |
| `POST` | `/api/auth/refresh` | Refrescar access token |

### Clientes

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| `GET` | `/api/clientes/` | Listar clientes (paginado) | Auth |
| `POST` | `/api/clientes/` | Crear cliente | Auth |
| `GET` | `/api/clientes/{id}` | Obtener cliente | Auth |
| `PUT` | `/api/clientes/{id}` | Actualizar cliente | Auth |
| `DELETE` | `/api/clientes/{id}` | Eliminar cliente | Auth |

### Productos

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| `GET` | `/api/productos/` | Listar productos | Auth |
| `POST` | `/api/productos/` | Crear producto | **Admin** |
| `PUT` | `/api/productos/{id}` | Actualizar producto | **Admin** |
| `DELETE` | `/api/productos/{id}` | Eliminar producto | **Admin** |

### Pedidos

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| `GET` | `/api/pedidos/` | Listar pedidos | Auth |
| `POST` | `/api/pedidos/` | Crear pedido | Auth |
| `PUT` | `/api/pedidos/{id}` | Actualizar pedido | **Admin** |
| `DELETE` | `/api/pedidos/{id}` | Eliminar pedido | **Admin** |

> [!TIP]
> Usa **Swagger UI** en `/api/docs` para probar los endpoints interactivamente.

---

## 💾 Modelo de Datos

```
Cliente (1) ──── (N) Pedido (1) ──── (N) DetallePedido (N) ──── (1) Producto
                                              └── usuario (N) ──── (1) User
```

### Tablas principales

| Tabla | Campos clave |
|-------|-------------|
| **clientes** | id, nombre, correo, dirección, teléfono |
| **productos** | id, nombre, precio, stock |
| **pedidos** | id, cliente_id, usuario_id, fecha, estado |
| **detalles_pedido** | id, pedido_id, producto_id, cantidad |
| **api_usuarios** | id, username, email, hashed_password, role |

### Estados del pedido

```
Pendiente → Enviado → Entregado
                 ↓
               Anulado
```

> [!IMPORTANT]
> Las transiciones de estado son validadas. Por ejemplo, no se puede pasar de `Pendiente` a `Entregado` directamente.

---

## 🔐 Seguridad

### Django
- ✅ Protección **CSRF** en todos los formularios POST
- ✅ Autenticación por **sesiones** seguras
- ✅ Protección contra **SQL injection** vía ORM
- ✅ Validación de contraseñas con Django validators
- ✅ **EmailBackend** personalizado para login por correo

### FastAPI
- ✅ Tokens **JWT** con expiración configurable
- ✅ Hash de contraseñas con **bcrypt**
- ✅ Dependencias de roles (`get_current_user`, `get_current_admin`)
- ✅ Validación automática con **Pydantic**
- ✅ **CORS** restrictivo configurable

### Validaciones de formularios
- ✅ Nombres sin números ni caracteres especiales
- ✅ Teléfonos con formato válido (7-15 dígitos)
- ✅ Correos electrónicos únicos
- ✅ Stock suficiente antes de crear pedidos
- ✅ Transiciones de estado válidas

---

## 📄 Exportación

El sistema permite exportar datos a:

| Formato | Biblioteca | Uso |
|---------|-----------|-----|
| **PDF** | reportlab | Reportes de pedidos |
| **Excel** | openpyxl | Listados de clientes, productos |

> [!TIP]
> Los botones de exportación están disponibles en las vistas de lista de cada recurso.

---

## ⚙️ Variables de Entorno

### Base de datos

| Variable | Tipo | Valor por defecto |
|----------|------|-------------------|
| `DB_NAME` | string | `crud_pedidos_db` |
| `DB_USER` | string | `root` |
| `DB_PASSWORD` | string | — |
| `DB_HOST` | string | `localhost` |
| `DB_PORT` | string | `3306` |

### Django

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `DJANGO_SECRET_KEY` | string | Clave de seguridad de Django |
| `DJANGO_ALLOWED_HOSTS` | string | Hosts permitidos (separados por coma) |

### FastAPI

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `JWT_SECRET` | string | Clave secreta para firmar tokens JWT |
| `JWT_ALGORITHM` | string | Algoritmo de firma (default: `HS256`) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | int | Tiempo de vida del access token (default: `60`) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | int | Tiempo de vida del refresh token (default: `7`) |
| `CORS_ALLOWED_ORIGINS` | string | Orígenes permitidos para CORS |

> [!CAUTION]
> **Nunca** subas el archivo `.env` al repositorio. Usa `.env.example` como plantilla.

---

## 🧪 Testing

### Django

```bash
cd django_app
python manage.py test
```

> [!NOTE]
> Los tests unitarios están en `pedidos/tests.py`.

### FastAPI

- Testing manual vía **Swagger UI** (`/api/docs`)
- Tests automáticos con pytest: *pendiente de implementación*

---

## 🚀 Despliegue

### Desarrollo

```bash
# Django
cd django_app && python manage.py runserver

# FastAPI
cd fastapi_app && uvicorn main:app --reload
```

### Producción (recomendado)

| Servicio | Configuración |
|----------|--------------|
| **Django** | Gunicorn + Nginx |
| **FastAPI** | Uvicorn workers + Nginx (reverse proxy) |
| **MySQL** | Servidor dedicado o RDS |
| **Static files** | Servidos por Nginx o CDN |
| **Secrets** | Variables de entorno o vault |

> [!IMPORTANT]
> Para producción:
> - Establece `DEBUG = False` en Django
> - Usa claves secretas seguras y únicas
> - Configura HTTPS con certificados SSL/TLS
> - Aumenta el timeout de sesión (`SESSION_COOKIE_AGE`)

---

## 📁 Estructura del Proyecto

```
crud-pedidos/
├── django_app/                     # Aplicación web Django
│   ├── config/                     # Configuración principal
│   │   ├── settings.py             # Settings, BD, sesiones, auth
│   │   ├── urls.py                 # Rutas principales
│   │   └── wsgi.py                 # WSGI para producción
│   ├── pedidos/                    # App principal
│   │   ├── models.py               # Modelos de datos
│   │   ├── views.py                # Vistas CBV + dashboard
│   │   ├── forms.py                # Formularios con validaciones
│   │   ├── urls.py                 # Rutas de la app
│   │   ├── exports.py              # Exportación PDF/Excel
│   │   ├── auth_backends.py        # Backend de autenticación por email
│   │   └── templates/              # Templates Bootstrap 5
│   └── manage.py                   # CLI de Django
├── fastapi_app/                    # API REST FastAPI
│   ├── main.py                     # Punto de entrada, CORS, routers
│   ├── auth.py                     # Creación/verificación JWT
│   ├── database.py                 # Engine SQLAlchemy + sesión
│   ├── models_fa.py                # Modelos SQLAlchemy
│   ├── schemas.py                  # Esquemas Pydantic
│   └── routers/                    # Endpoints por recurso
│       ├── auth.py                 # Login/registro/refresh
│       ├── clientes.py             # CRUD Clientes
│       ├── productos.py            # CRUD Productos
│       └── pedidos.py              # CRUD Pedidos
├── .env.example                    # Plantilla de variables de entorno
├── .gitignore                      # Archivos ignorados por Git
├── requirements.txt                # Dependencias Python
├── README.md                       # Este archivo
├── DOCUMENTATION.md                # Documentación técnica completa
├── ARCHITECTURE.md                 # Diagramas y arquitectura
├── FAQ.md                          # Preguntas frecuentes
└── PRESENTATION_GUIDE.md           # Guía de presentación
```

---

## 🤝 Contribuir

1. Haz un **fork** del proyecto
2. Crea una rama para tu funcionalidad: `git checkout -b feature/nueva-funcionalidad`
3. Haz commit de tus cambios: `git commit -m 'Agrega nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un **Pull Request**

> [!TIP]
> Revisa [CONTRIBUTING.md](CONTRIBUTING.md) para guías detalladas de contribución.

---

## 📝 Licencia

Este proyecto está bajo la Licencia **MIT**. Ver el archivo `LICENSE` para más detalles.

---

> [!NOTE]
> Proyecto desarrollado con fines educativos y de demostración.
