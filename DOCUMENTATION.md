# Documentación Completa del Proyecto CRUD Pedidos

## Arquitectura General

Este proyecto implementa un sistema de gestión de pedidos con dos implementaciones principales:

1. **Django App**: Aplicación web completa con autenticación por sesiones, interfaz de usuario y gestión de pedidos.
2. **FastAPI App**: API REST moderna con autenticación JWT, documentación automática Swagger/OpenAPI.

### Tecnologías Principales

- **Django 6.0**: Framework web full-stack con ORM, templates y sesiones.
- **FastAPI**: Framework API moderno para Python con validación automática.
- **JWT (JSON Web Tokens)**: Sistema de autenticación stateless en FastAPI.
- **Swagger/OpenAPI**: Documentación automática de APIs generada por FastAPI.
- **MySQL**: Base de datos relacional.
- **Bootstrap 5**: Framework CSS para la interfaz de Django.

## Estructura del Proyecto

```
crud_pedidos/
├── ARCHITECTURE.md          # Documentación de arquitectura
├── README.md               # Información básica del proyecto
├── requirements.txt        # Dependencias Python
├── debug_username_regex.py # Script de debug para validación de usernames
├── django_app/             # Aplicación Django
│   ├── manage.py
│   ├── config/             # Configuración Django
│   │   ├── settings.py     # Configuración principal
│   │   ├── urls.py         # URLs principales
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── pedidos/            # App principal de Django
│   │   ├── models.py       # Modelos de datos (Cliente, Producto, Pedido)
│   │   ├── forms.py        # Formularios personalizados
│   │   ├── views.py        # Vistas y lógica de negocio
│   │   ├── urls.py         # URLs de la app
│   │   ├── admin.py        # Configuración del admin
│   │   ├── apps.py
│   │   ├── tests.py
│   │   └── templates/      # Plantillas HTML
│   │       ├── pedidos/    # Templates base y de autenticación
│   │       └── pedidos/    # Templates específicos de pedidos
│   └── templates/          # Templates globales
│       └── pedidos/
└── fastapi_app/            # Aplicación FastAPI
    ├── main.py             # Punto de entrada FastAPI
    ├── database.py         # Configuración de base de datos
    ├── auth.py             # Autenticación JWT
    ├── models_fa.py        # Modelos Pydantic
    ├── schemas.py          # Esquemas de respuesta
    ├── pedidos.py          # Lógica de negocio para pedidos
    └── routers/            # Endpoints organizados
        ├── __init__.py
        ├── auth.py         # Endpoints de autenticación
        ├── clientes.py     # CRUD Clientes
        ├── productos.py    # CRUD Productos
        └── pedidos.py      # CRUD Pedidos
```

## Modelos de Datos

### Django Models

#### Cliente
```python
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
```

#### Producto
```python
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
```

#### Pedido
```python
class Pedido(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Entregado', 'Entregado'),
        ('Cancelado', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos_usuario')
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    detalles = models.ManyToManyField(Producto, through='DetallePedido')
```

#### DetallePedido
```python
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
```

### FastAPI Models (Pydantic)

Los modelos de FastAPI están definidos en `models_fa.py` y `schemas.py`, usando Pydantic para validación automática.

## Autenticación y Autorización

### Django Authentication

#### Sesiones
- Django utiliza autenticación basada en sesiones por defecto.
- Configuración en `settings.py`:
  ```python
  SESSION_COOKIE_AGE = 60  # 1 minuto para demo
  SESSION_EXPIRE_AT_BROWSER_CLOSE = False
  ```

#### Formularios Personalizados
- `CustomUserCreationForm`: Permite usernames con espacios y caracteres especiales.
- `CustomAuthenticationForm`: Para login con validación personalizada.

#### Flujo de Autenticación Django
1. **Registro**: Usuario crea cuenta con username, email, password.
2. **Login**: Usuario ingresa credenciales, se valida contra User model.
3. **Sesión**: Se crea sesión en base de datos.
4. **Logout**: POST request con CSRF token para cerrar sesión.

### FastAPI Authentication (JWT)

#### JWT Implementation
- **auth.py**: Contiene lógica de creación y verificación de tokens JWT.
- **Dependencias**: `fastapi.security` para OAuth2PasswordBearer.

#### Token Creation
```python
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

#### Flujo de Autenticación JWT
1. **Login**: Usuario envía username/password.
2. **Verificación**: Se valida contra base de datos.
3. **Token Generation**: Se crea JWT con expiración.
4. **Token Usage**: Cliente incluye `Authorization: Bearer <token>` en headers.
5. **Token Validation**: Cada request valida el token.

## Endpoints API

### FastAPI Endpoints

#### Autenticación
- `POST /auth/login`: Login y obtención de token JWT
- `GET /auth/me`: Información del usuario actual (requiere token)

#### Clientes
- `GET /clientes/`: Listar clientes
- `POST /clientes/`: Crear cliente
- `GET /clientes/{id}`: Obtener cliente específico
- `PUT /clientes/{id}`: Actualizar cliente
- `DELETE /clientes/{id}`: Eliminar cliente

#### Productos
- `GET /productos/`: Listar productos
- `POST /productos/`: Crear producto
- `GET /productos/{id}`: Obtener producto específico
- `PUT /productos/{id}`: Actualizar producto
- `DELETE /productos/{id}`: Eliminar producto

#### Pedidos
- `GET /pedidos/`: Listar pedidos del usuario
- `POST /pedidos/`: Crear pedido
- `GET /pedidos/{id}`: Obtener pedido específico
- `PUT /pedidos/{id}`: Actualizar pedido
- `DELETE /pedidos/{id}`: Eliminar pedido

### Django URLs

#### Autenticación
- `/login/`: Login view
- `/logout/`: Logout view (POST only)
- `/registro/`: Registro de usuarios

#### Gestión
- `/`: Dashboard
- `/clientes/`: CRUD Clientes
- `/productos/`: CRUD Productos
- `/pedidos/`: CRUD Pedidos

## Swagger/OpenAPI Documentation

FastAPI genera automáticamente documentación Swagger en:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Características de la Documentación
- **Interfaz Interactiva**: Prueba endpoints directamente desde el navegador.
- **Esquemas Automáticos**: Muestra modelos Pydantic como JSON schemas.
- **Autenticación**: Soporte para incluir Bearer tokens.
- **Ejemplos**: Valores de ejemplo para requests/responses.

## Flujos de Trabajo

### Flujo de Pedidos (Django)

1. **Usuario autenticado** accede al sistema.
2. **Selecciona "Nuevo Pedido"** desde el menú.
3. **Elige cliente** de la lista existente o crea uno nuevo.
4. **Selecciona productos** y cantidades.
5. **Confirma el pedido** con estado inicial "Pendiente".
6. **Puede actualizar estado** a "En Proceso", "Entregado" o "Cancelado".

### Flujo de Pedidos (FastAPI)

1. **Cliente obtiene token JWT** mediante login.
2. **Incluye token** en header `Authorization: Bearer <token>`.
3. **Crea pedido** enviando datos JSON con cliente y productos.
4. **API valida** stock disponible y crea pedido.
5. **Cliente puede consultar** pedidos propios mediante token.

## Configuraciones Importantes

### Django Settings
- **Base de datos**: MySQL configurada en `settings.py`
- **Sesiones**: Configuradas para expirar en 1 minuto (demo)
- **Templates**: Ubicados en `templates/` y `pedidos/templates/`
- **Static Files**: Servidos automáticamente en desarrollo

### FastAPI Settings
- **CORS**: Configurado para permitir requests desde diferentes orígenes
- **JWT**: SECRET_KEY y ALGORITHM definidos
- **Database**: Conexión SQLAlchemy a MySQL
- **Routers**: Endpoints organizados por funcionalidad

## Seguridad

### Django Security
- **CSRF Protection**: Habilitado para forms POST
- **Session Security**: Sesiones seguras con expiración
- **Password Validation**: Validadores de Django aplicados
- **SQL Injection**: Protegido por ORM

### FastAPI Security
- **JWT Tokens**: Autenticación stateless
- **Password Hashing**: Usando `passlib` con bcrypt
- **Input Validation**: Pydantic valida automáticamente
- **CORS**: Configurado apropiadamente

## Despliegue y Desarrollo

### Requisitos
- Python 3.8+
- MySQL 8.0+
- Dependencias en `requirements.txt`

### Ejecución

#### Django
```bash
cd django_app
python manage.py runserver
```

#### FastAPI
```bash
cd fastapi_app
uvicorn main:app --reload
```

### Variables de Entorno
- `DJANGO_SECRET_KEY`: Clave secreta de Django
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Configuración MySQL

## Preguntas Frecuentes

### ¿Por qué dos implementaciones?
- **Django**: Para usuarios finales con interfaz web completa.
- **FastAPI**: Para integraciones API, móviles, otros sistemas.

### ¿Cómo funciona la autenticación?
- **Django**: Sesiones del lado servidor.
- **FastAPI**: Tokens JWT stateless.

### ¿Qué es Swagger?
- Interfaz web automática para probar y documentar APIs REST.

### ¿Por qué usernames con espacios?
- Para permitir nombres completos como "Daniel Meza" en el registro.

### ¿Cómo se manejan los pedidos?
- Pedidos tienen cliente, usuario creador, productos con cantidades, y estados de progreso.

Esta documentación cubre todos los aspectos principales del proyecto. Para detalles específicos, consulta los archivos fuente comentados.</content>
<parameter name="filePath">c:\Users\Gabriel Mesa\crud_pedidos\DOCUMENTATION.md