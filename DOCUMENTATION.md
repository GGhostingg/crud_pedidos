# Documentación Técnica — CRUD Pedidos

> Documentación completa del sistema de gestión de pedidos con Django + FastAPI + MySQL.

---

## 📋 Tabla de Contenidos

- [Arquitectura General](#arquitectura-general)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Modelos de Datos](#modelos-de-datos)
- [Autenticación y Autorización](#autenticación-y-autorización)
- [Endpoints de la API](#endpoints-de-la-api)
- [Flujos de Trabajo](#flujos-de-trabajo)
- [Seguridad](#seguridad)
- [Validaciones de Formularios](#validaciones-de-formularios)
- [Exportación](#exportación)
- [Configuraciones Importantes](#configuraciones-importantes)
- [Despliegue](#despliegue)
- [Testing](#testing)
- [Solución de Problemas](#solución-de-problemas)

---

## Arquitectura General

Este proyecto implementa un sistema de gestión de pedidos con una **arquitectura híbrida** que combina:

1. **Django** — Aplicación web completa con autenticación por sesiones, interfaz de usuario con Bootstrap 5, y gestión de pedidos.
2. **FastAPI** — API REST moderna con autenticación JWT, documentación automática Swagger/OpenAPI y validación con Pydantic.
3. **MySQL** — Base de datos relacional compartida entre ambos servicios.

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
> Ambos servicios comparten la misma base de datos MySQL, lo que garantiza consistencia de datos sin necesidad de sincronización compleja.

### ¿Por qué dos servicios?

| Servicio | Propósito | Ventajas |
|----------|-----------|----------|
| **Django** | Interfaz web para usuarios finales | Autenticación integrada, templates, admin |
| **FastAPI** | API REST para integraciones externas | Alto rendimiento, documentación automática, tipado |

> [!TIP]
> Esta separación permite escalar cada servicio de forma independiente y facilita la integración con aplicaciones móviles o de escritorio.

---

## Tecnologías

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| **Framework Web** | Django | 6.0.4 |
| **Framework API** | FastAPI | 0.135.3 |
| **Base de Datos** | MySQL | 8.0+ |
| **ORM (Django)** | Django ORM | Integrado |
| **ORM (FastAPI)** | SQLAlchemy | 2.0.49 |
| **Validación** | Pydantic | 2.12.5 |
| **Autenticación (FastAPI)** | JWT (python-jose) + bcrypt | 3.5.0 / 4.0.1 |
| **Autenticación (Django)** | Sesiones + EmailBackend | Integrado |
| **UI** | Bootstrap 5 | CDN |
| **Exportación** | reportlab, openpyxl | 4.4.10 / 3.1.5 |
| **Servidor** | Uvicorn, Django dev | 0.44.0 |

---

## Estructura del Proyecto

```
crud-pedidos/
├── django_app/                         # Aplicación web Django
│   ├── config/                         # Configuración principal
│   │   ├── settings.py                 # Settings, BD, sesiones, auth
│   │   ├── urls.py                     # Rutas principales + auth
│   │   ├── wsgi.py                     # WSGI para producción
│   │   └── asgi.py                     # ASGI para async
│   ├── pedidos/                        # App principal
│   │   ├── models.py                   # Modelos: Cliente, Producto, Pedido
│   │   ├── views.py                    # Vistas CBV + dashboard
│   │   ├── forms.py                    # Formularios con validaciones
│   │   ├── urls.py                     # Rutas de la app
│   │   ├── exports.py                  # Exportación PDF/Excel
│   │   ├── auth_backends.py            # Backend de autenticación por email
│   │   ├── tests.py                    # Tests unitarios
│   │   └── templates/                  # Templates Bootstrap 5
│   │       ├── pedidos/
│   │       │   ├── base.html           # Layout base con sidebar
│   │       │   ├── login.html          # Formulario de login
│   │       │   ├── registro.html       # Formulario de registro
│   │       │   ├── dashboard.html      # Panel de estadísticas
│   │       │   ├── clientes/           # CRUD Clientes
│   │       │   ├── productos/          # CRUD Productos
│   │       │   └── pedidos/            # CRUD Pedidos
│   │       ├── 403.html                # Página de error 403
│   │       └── protected_error.html    # Página de error genérica
│   └── manage.py                       # CLI de Django
├── fastapi_app/                        # API REST FastAPI
│   ├── main.py                         # Punto de entrada, CORS, routers
│   ├── auth.py                         # Creación/verificación JWT
│   ├── database.py                     # Engine SQLAlchemy + sesión
│   ├── models_fa.py                    # Modelos SQLAlchemy
│   ├── schemas.py                      # Esquemas Pydantic
│   └── routers/                        # Endpoints por recurso
│       ├── auth.py                     # Login/registro/refresh
│       ├── clientes.py                 # CRUD Clientes
│       ├── productos.py                # CRUD Productos (admin-only write)
│       └── pedidos.py                  # CRUD Pedidos (stock validation)
├── .env.example                        # Plantilla de variables de entorno
├── .gitignore                          # Archivos ignorados por Git
├── requirements.txt                    # Dependencias Python
├── README.md                           # Guía principal
├── DOCUMENTATION.md                    # Este archivo
├── ARCHITECTURE.md                     # Diagramas y arquitectura
├── FAQ.md                              # Preguntas frecuentes
└── PRESENTATION_GUIDE.md               # Guía de presentación
```

> [!NOTE]
> FastAPI crea su tabla `api_usuarios` automáticamente al iniciar mediante `Base.metadata.create_all()`. Django requiere migraciones explícitas con `python manage.py migrate`.

---

## Modelos de Datos

### Diagrama de Relaciones

```
Cliente (1) ──── (N) Pedido (1) ──── (N) DetallePedido (N) ──── (1) Producto
                                              └── usuario (N) ──── (1) User
```

### Cliente

```python
class Cliente(models.Model):
    usuario    = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre     = models.CharField(max_length=100)
    correo     = models.EmailField(unique=True)
    direccion  = models.CharField(max_length=200, blank=True)
    telefono   = models.CharField(max_length=20, blank=True)
```

| Campo | Tipo | Restricciones |
|-------|------|--------------|
| `nombre` | CharField(100) | **Obligatorio**, sin números, sin caracteres especiales |
| `correo` | EmailField | **Único**, obligatorio |
| `direccion` | CharField(200) | Opcional |
| `telefono` | CharField(20) | Opcional, 7-15 dígitos |

### Producto

```python
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock  = models.IntegerField(default=0)
```

| Campo | Tipo | Restricciones |
|-------|------|--------------|
| `nombre` | CharField(100) | **Obligatorio**, mínimo 3 caracteres |
| `precio` | DecimalField | **Obligatorio**, mayor que cero |
| `stock` | IntegerField | Obligatorio, no negativo |

### Pedido

```python
class Pedido(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Enviado',   'Enviado'),
        ('Entregado', 'Entregado'),
        ('Anulado',   'Anulado'),
    ]
    cliente  = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    usuario  = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fecha    = models.DateTimeField(auto_now_add=True)
    estado   = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
```

| Campo | Tipo | Restricciones |
|-------|------|--------------|
| `cliente` | ForeignKey | **Obligatorio**, PROTECT (no se puede eliminar si tiene pedidos) |
| `usuario` | ForeignKey | Opcional, CASCADE |
| `fecha` | DateTimeField | Automática (solo lectura) |
| `estado` | CharField | Ver [Transiciones de Estado](#transiciones-de-estado) |

### DetallePedido

```python
class DetallePedido(models.Model):
    pedido    = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto  = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad  = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.cantidad * self.producto.precio
```

### Transiciones de Estado

| Estado Actual | Estados Válidos |
|--------------|----------------|
| `Pendiente` | `Pendiente`, `Enviado`, `Anulado` |
| `Enviado` | `Enviado`, `Entregado`, `Anulado` |
| `Entregado` | `Entregado`, `Anulado` |
| `Anulado` | `Anulado` (final) |

> [!CAUTION]
> Las transiciones de estado son validadas en el servidor. Intentar una transición inválida genera un error y no guarda cambios.

### Tabla de API (FastAPI)

```python
class Usuario(Base):
    __tablename__ = 'api_usuarios'
    id             = Column(Integer, primary_key=True)
    username       = Column(String, unique=True)
    email          = Column(String, unique=True)
    hashed_password = Column(String)
    role           = Column(String, default='user')  # 'admin' o 'user'
```

> [!IMPORTANT]
> Esta tabla es creada automáticamente por FastAPI al iniciar. No requiere migraciones de Django.

---

## Autenticación y Autorización

### Django — Sesiones

| Aspecto | Configuración |
|---------|--------------|
| **Tipo** | Basada en sesiones (cookies) |
| **Backend** | `pedidos.auth_backends.EmailBackend` (login por correo) |
| **Expiración** | 120 segundos (configurable en `SESSION_COOKIE_AGE`) |
| **Protección** | CSRF token en todos los formularios POST |

#### Flujo de Autenticación

```
1. Usuario visita /login/
2. Ingresa correo y contraseña
3. EmailBackend busca usuario por email
4. Si válido, se crea sesión
5. Redirect a / (dashboard)
```

#### Registro

```
1. Usuario visita /registro/
2. Completa formulario (nombre, email, password)
3. Validaciones de formulario verifican:
   - Nombre sin números ni caracteres especiales
   - Email único
   - Password segura
4. Crea User + Cliente vinculado
5. Login automático
6. Redirect a / (dashboard)
```

> [!NOTE]
> El nombre completo se valida para que solo contenga letras, espacios, acentos, ñ y guiones. Cada palabra debe tener al menos 2 caracteres.

### FastAPI — JWT

| Aspecto | Configuración |
|---------|--------------|
| **Tipo** | Tokens JWT stateless |
| **Algoritmo** | HS256 |
| **Access Token TTL** | 60 minutos (configurable) |
| **Refresh Token TTL** | 7 días (configurable) |
| **Hash** | bcrypt |

#### Flujo de Autenticación

```
1. POST /api/auth/token con username/password
2. API valida credenciales contra api_usuarios
3. Retorna access_token + refresh_token
4. Cliente incluye "Authorization: Bearer <token>" en headers
5. API verifica token en cada request protegido
6. Cuando expira, usar POST /api/auth/refresh
```

#### Roles

| Rol | Permisos |
|-----|----------|
| **user** | Leer recursos, crear pedidos |
| **admin** | CRUD completo de todos los recursos |

> [!TIP]
> Las dependencias `get_current_user` y `get_current_admin` de FastAPI manejan la autorización automáticamente.

---

## Endpoints de la API

### Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/auth/register` | Registrar usuario | No |
| `POST` | `/api/auth/token` | Login (OAuth2) | No |
| `POST` | `/api/auth/refresh` | Refrescar token | Sí (refresh token) |

### Clientes

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/clientes/` | Listar (paginado) | Sí |
| `POST` | `/api/clientes/` | Crear | Sí |
| `GET` | `/api/clientes/{id}` | Obtener | Sí |
| `PUT` | `/api/clientes/{id}` | Actualizar | Sí |
| `DELETE` | `/api/clientes/{id}` | Eliminar | Sí |

### Productos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/productos/` | Listar | Sí |
| `POST` | `/api/productos/` | Crear | **Admin** |
| `PUT` | `/api/productos/{id}` | Actualizar | **Admin** |
| `DELETE` | `/api/productos/{id}` | Eliminar | **Admin** |

### Pedidos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/pedidos/` | Listar | Sí |
| `POST` | `/api/pedidos/` | Crear | Sí |
| `PUT` | `/api/pedidos/{id}` | Actualizar | **Admin** |
| `DELETE` | `/api/pedidos/{id}` | Eliminar | **Admin** |

> [!TIP]
> La documentación interactiva está disponible en **http://localhost:8000/api/docs** (Swagger UI).

---

## Flujos de Trabajo

### Creación de Pedido

```
1. Usuario autenticado accede a "Nuevo Pedido"
2. Si es user normal:
   - Cliente se asigna automáticamente
   - Solo puede crear en estado "Pendiente"
3. Si es admin:
   - Selecciona cliente de lista despleable
   - Puede elegir estado inicial
4. Agrega productos con cantidades
5. Formulario valida stock disponible
6. Al guardar:
   a. Transacción atómica inicia
   b. Verifica stock de cada producto
   c. Crea Pedido
   d. Crea DetallePedido
   e. Reduce stock
   f. Commit
7. Redirect a lista de pedidos con mensaje de éxito
```

> [!CAUTION]
> Si el stock es insuficiente, la transacción se revierte completamente (rollback) y se muestra un error.

### Actualización de Pedido (Admin)

```
1. Admin abre pedido existente
2. Si estado es "Entregado" o "Anulado": bloqueado
3. Si estado es "Pendiente": puede editar productos
4. Si estado es "Enviado": solo puede cambiar estado
5. Al cambiar estado:
   a. Validar transición permitida
   b. Si es "Anulado": devolver stock automáticamente
   c. Guardar nuevos cambios
```

### Anulación de Pedido

```
1. Admin selecciona "Anular" en pedido
2. Confirmación de anulación
3. Al confirmar:
   a. devolver_stock(pedido) — restaura cantidades
   b. Cambia estado a "Anulado"
   c. Guarda pedido
4. Mensaje de éxito con confirmación
```

> [!IMPORTANT]
> La función `devolver_stock()` se ejecuta dentro de una transacción atómica para garantizar consistencia.

---

## Seguridad

### Django

| Medida | Implementación |
|--------|---------------|
| **CSRF** | Token en todos los formularios POST |
| **SQL Injection** | Protegido por ORM de Django |
| **XSS** | Templates con escape automático |
| **Clickjacking** | X-Frame-Options middleware |
| **Sesiones** | Cookies seguras con expiración |
| **Contraseñas** | Django password validators |
| **Auth por email** | EmailBackend personalizado |

### FastAPI

| Medida | Implementación |
|--------|---------------|
| **JWT** | Tokens firmados con HS256 |
| **Password Hash** | bcrypt |
| **Input Validation** | Pydantic schemas |
| **CORS** | Whitelist configurable |
| **Roles** | Dependencias `get_current_user` / `get_current_admin` |

### Validaciones de Formularios

#### Registro de Usuario

| Campo | Validaciones |
|-------|-------------|
| **nombre_completo** | Mín. 3 chars, sin números, sin caracteres especiales, cada palabra mín. 2 chars |
| **email** | Formato válido, único |
| **telefono** | Solo dígitos/espacios/guiones/paréntesis/+, 7-15 dígitos |
| **direccion** | Máx. 200 chars, sin caracteres peligrosos (`<>"';/`) |

#### Cliente

| Campo | Validaciones |
|-------|-------------|
| **nombre** | Misma que nombre_completo en registro |
| **correo** | Formato válido, único |
| **telefono** | Misma que en registro |
| **direccion** | Misma que en registro |

#### Producto

| Campo | Validaciones |
|-------|-------------|
| **nombre** | Mín. 3 chars, máx. 100, sin caracteres peligrosos |
| **precio** | Mayor que cero |
| **stock** | No negativo |

> [!NOTE]
> Las validaciones se ejecutan en el servidor. Los errores se muestran en rojo debajo de cada campo en la interfaz.

---

## Exportación

### PDF (reportlab)

- Reporte de pedido individual con detalles
- Encabezado con logo y datos del pedido
- Tabla de productos con subtotales

### Excel (openpyxl)

- Listado completo de clientes
- Listado completo de productos
- Listado de pedidos con filtros

> [!TIP]
> Los botones de exportación están en las vistas de lista de cada recurso.

---

## Configuraciones Importantes

### Django Settings

| Configuración | Valor | Descripción |
|--------------|-------|-------------|
| `SESSION_COOKIE_AGE` | 120 | Expiración de sesión en segundos |
| `SESSION_EXPIRE_AT_BROWSER_CLOSE` | False | La sesión persiste tras cerrar navegador |
| `SESSION_SAVE_EVERY_REQUEST` | False | No resetea timer en cada request |
| `LOGIN_URL` | `/login/` | URL de login |
| `LOGIN_REDIRECT_URL` | `/` | Redirect tras login exitoso |
| `LANGUAGE_CODE` | `es` | Idioma español |
| `DEBUG` | True | Modo desarrollo (False en producción) |

### FastAPI

| Configuración | Valor | Descripción |
|--------------|-------|-------------|
| `CORS_ALLOWED_ORIGINS` | `http://localhost:8000` | Orígenes permitidos |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | TTL del access token |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | 7 | TTL del refresh token |

---

## Despliegue

### Desarrollo

```bash
# Terminal 1 — Django
cd django_app && python manage.py runserver

# Terminal 2 — FastAPI
cd fastapi_app && uvicorn main:app --reload
```

### Producción

| Componente | Configuración Recomendada |
|-----------|-------------------------|
| **Django** | Gunicorn + Nginx, `DEBUG=False` |
| **FastAPI** | Uvicorn workers + Nginx (reverse proxy) |
| **MySQL** | Servidor dedicado o AWS RDS |
| **Static Files** | Nginx o CDN (Cloudflare) |
| **Secrets** | Variables de entorno o vault (AWS Secrets Manager) |
| **SSL/TLS** | Certificados Let's Encrypt |

> [!CAUTION]
> En producción:
> - `DEBUG = False` en Django
> - Claves secretas seguras y únicas
> - HTTPS obligatorio
> - Aumentar `SESSION_COOKIE_AGE` a 3600 (1 hora) o más
> - Configurar `ALLOWED_HOSTS` correctamente

---

## Testing

### Django

```bash
cd django_app
python manage.py test
```

> [!NOTE]
> Tests unitarios están en `pedidos/tests.py`. Cubren modelos y vistas básicas.

### FastAPI

- Testing manual vía **Swagger UI** (`/api/docs`)
- Tests automatizados con pytest: **pendiente de implementación**

---

## Solución de Problemas

### Error 403 CSRF en logout

**Causa:** Sesión expirada (120 segundos).

**Solución:** Aumenta `SESSION_COOKIE_AGE` en `settings.py` o habilita `SESSION_SAVE_EVERY_REQUEST = True`.

### FastAPI no crea tabla api_usuarios

**Causa:** Error de conexión a MySQL.

**Solución:** Verifica que las variables de entorno en `.env` sean correctas.

### Stock negativo tras crear pedido

**Causa:** Bug en validación de stock (ya corregido con `db_estado` directo de BD).

**Solución:** Asegúrate de tener la última versión del código.

### Error de importación de mysqlclient

**Causa:** Faltan dependencias del sistema.

**Solución:**
```bash
# Debian/Ubuntu
sudo apt install default-libmysqlclient-dev build-essential pkg-config

# macOS
brew install mysql-client
```

### Migraciones de Django fallan

**Causa:** Base de datos no existe o credenciales incorrectas.

**Solución:**
```sql
CREATE DATABASE crud_pedidos_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

> [!NOTE]
> Para más detalles, consulta [FAQ.md](FAQ.md) y [ARCHITECTURE.md](ARCHITECTURE.md).
