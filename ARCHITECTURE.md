# Arquitectura del Proyecto — CRUD Pedidos

> Diagramas, patrones de diseño y decisiones arquitectónicas del sistema.

---

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura Híbrida](#arquitectura-híbrida)
- [Diagrama de Componentes](#diagrama-de-componentes)
- [Diagrama de Flujo de Datos](#diagrama-de-flujo-de-datos)
- [Diagrama de Base de Datos](#diagrama-de-base-de-datos)
- [Patrones de Diseño](#patrones-de-diseño)
- [Flujo de Autenticación](#flujo-de-autenticación)
- [Flujo de Pedidos](#flujo-de-pedidos)
- [Flujo de Stock](#flujo-de-stock)
- [Seguridad por Capas](#seguridad-por-capas)
- [Escalabilidad](#escalabilidad)
- [Decisiones Arquitectónicas](#decisiones-arquitectónicas)

---

## Descripción General

El sistema **CRUD Pedidos** implementa una arquitectura híbrida que combina **Django** para la interfaz web y **FastAPI** para la API REST, ambos compartiendo una base de datos **MySQL**.

### Principios de Diseño

| Principio | Implementación |
|-----------|---------------|
| **Separación de responsabilidades** | Django maneja UI, FastAPI maneja API |
| **Consistencia de datos** | Base de datos compartida |
| **Escalabilidad horizontal** | Servicios independientes |
| **Seguridad por capas** | CSRF + JWT + RBAC + Validaciones |

---

## Arquitectura Híbrida

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Navegador)                      │
│                                                                 │
│   http://localhost:8000/          http://localhost:8000/api/docs│
│   (Interfaz Web Django)           (Swagger UI FastAPI)          │
└────────────┬──────────────────────────────┬─────────────────────┘
             │                              │
             │ HTTP Request                 │ HTTP + Bearer Token
             ▼                              ▼
┌────────────────────────┐    ┌────────────────────────────────┐
│     DJANGO APP         │    │        FASTAPI APP             │
│   (Web Interface)      │    │       (REST API)               │
│                        │    │                                │
│  ┌──────────────────┐  │    │  ┌──────────────────────────┐  │
│  │ Sessions Auth    │  │    │  │ JWT Auth (python-jose)   │  │
│  │ EmailBackend     │  │    │  │ bcrypt password hash     │  │
│  └──────────────────┘  │    │  └──────────────────────────┘  │
│  ┌──────────────────┐  │    │  ┌──────────────────────────┐  │
│  │ CBV Views        │  │    │  │ Routers:                 │  │
│  │ Dashboard        │  │    │  │  • auth.py               │  │
│  │ Forms + Valid.   │  │    │  │  • clientes.py           │  │
│  │ Templates BS5    │  │    │  │  • productos.py          │  │
│  │ Exports PDF/XLS  │  │    │  │  • pedidos.py            │  │
│  └──────────────────┘  │    │  └──────────────────────────┘  │
│  ┌──────────────────┐  │    │  ┌──────────────────────────┐  │
│  │ Django ORM       │  │    │  │ SQLAlchemy 2.0 ORM       │  │
│  │ migrations       │  │    │  │ Pydantic validation      │  │
│  └──────────────────┘  │    │  └──────────────────────────┘  │
└────────────┬─────────────┘    └───────────────┬────────────────┘
             │                                   │
             │         MySQL Protocol            │
             └──────────────┬────────────────────┘
                            ▼
              ┌─────────────────────────┐
              │     MySQL DATABASE      │
              │                         │
              │  • clientes             │
              │  • productos            │
              │  • pedidos              │
              │  • detalles_pedido      │
              │  • auth_user (Django)   │
              │  • api_usuarios (Fast)  │
              │  • django_session       │
              └─────────────────────────┘
```

> [!NOTE]
> Ambos servicios se comunican con la **misma base de datos MySQL**, lo que elimina la necesidad de sincronización entre servicios.

---

## Diagrama de Componentes

```
┌──────────────────────────────────────────────────────────────────┐
│                        Capa de Presentación                      │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│
│  │  Templates   │  │  Dashboard  │  │  Formularios│  │ Swagger ││
│  │  HTML/BS5    │  │  Estadísticas│  │  Validados  │  │  UI     ││
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────┬────┘│
└─────────┼────────────────┼────────────────┼───────────────┼─────┘
          │                │                │               │
┌─────────┼────────────────┼────────────────┼───────────────┼─────┐
│         ▼                ▼                ▼               ▼     │
│                    Capa de Servicio                             │
│                                                                 │
│  ┌─────────────────────────┐   ┌─────────────────────────────┐  │
│  │  Django Views (CBV)     │   │  FastAPI Routers            │  │
│  │  • ClienteListView      │   │  • POST /api/auth/token     │  │
│  │  • PedidoCreateView     │   │  • GET  /api/clientes/      │  │
│  │  • PedidoUpdateView     │   │  • POST /api/pedidos/       │  │
│  │  • DashboardView        │   │  • PUT  /api/pedidos/{id}   │  │
│  └───────────┬─────────────┘   └──────────────┬──────────────┘  │
│              │                                 │                 │
│  ┌───────────▼─────────────┐   ┌──────────────▼──────────────┐  │
│  │  Django Forms           │   │  Pydantic Schemas           │  │
│  │  • CustomUserCreation   │   │  • Token, UserCreate        │  │
│  │  • ClienteForm          │   │  • ClienteResponse          │  │
│  │  • PedidoCreateForm     │   │  • PedidoCreate             │  │
│  │  • DetallePedidoFormSet │   │  • ProductoResponse         │  │
│  └───────────┬─────────────┘   └──────────────┬──────────────┘  │
│              │                                 │                 │
│  ┌───────────▼─────────────┐   ┌──────────────▼──────────────┐  │
│  │  Business Logic         │   │  Business Logic             │  │
│  │  • devolver_stock()     │   │  • crear_pedido()           │  │
│  │  • validación transición│   │  • validar_stock()          │  │
│  │  • get_cliente_for_user │   │  • get_current_admin        │  │
│  └───────────┬─────────────┘   └──────────────┬──────────────┘  │
└──────────────┼────────────────────────────────┼─────────────────┘
               │                                │
┌──────────────┼────────────────────────────────┼─────────────────┐
│              ▼            Capa de Datos       ▼                 │
│                                                                 │
│  ┌────────────────────────┐    ┌─────────────────────────────┐  │
│  │  Django ORM            │    │  SQLAlchemy 2.0 ORM         │  │
│  │  • models.py           │    │  • models_fa.py             │  │
│  │  • migrations/         │    │  • database.py              │  │
│  └───────────┬────────────┘    └──────────────┬──────────────┘  │
│              │                                 │                 │
│              └────────────┬────────────────────┘                 │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    MySQL Database                           ││
│  │  clientes │ productos │ pedidos │ detalles_pedido │ ...    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Diagrama de Flujo de Datos

### Creación de Pedido

```
Usuario (Navegador)
       │
       │ 1. GET /pedidos/nuevo/
       ▼
┌─────────────────┐
│  Django View    │
│  PedidoCreate   │
└────────┬────────┘
         │ 2. Render template con formset vacío
         ▼
Usuario completa formulario
         │
         │ 3. POST /pedidos/nuevo/ (form + csrf)
         ▼
┌─────────────────────────────────────┐
│  Django View.form_valid()           │
│  ┌───────────────────────────────┐  │
│  │ 1. Validar formulario         │  │
│  │ 2. Validar formset detalles   │  │
│  │ 3. Verificar stock            │  │
│  │ 4. @transaction.atomic        │  │
│  │    a. Crear Pedido            │  │
│  │    b. Crear DetallePedido     │  │
│  │    c. Reducir stock           │  │
│  │    d. Commit                  │  │
│  └───────────────────────────────┘  │
└────────┬────────────────────────────┘
         │ 4. Redirect /pedidos/
         ▼
Lista de pedidos con mensaje de éxito
```

> [!CAUTION]
> Toda la operación de creación de pedido ocurre dentro de una transacción atómica (`@transaction.atomic`). Si cualquier paso falla, se revierten **todos** los cambios.

### Actualización de Estado de Pedido

```
Admin (Navegador)
       │
       │ 1. GET /pedidos/{id}/editar/
       ▼
┌──────────────────┐
│ PedidoUpdateView │
│ get_context_data │
└────────┬─────────┘
         │ 2. Render con estado actual + opciones
         ▼
Admin cambia estado y envía form
         │
         │ 3. POST /pedidos/{id}/editar/
         ▼
┌────────────────────────────────────────────┐
│  PedidoUpdateView.form_valid()             │
│  ┌──────────────────────────────────────┐  │
│  │ 1. Leer estado DIRECTO de BD         │  │
│  │    db_estado = Pedido.objects.get()  │  │
│  │ 2. Validar transición                │  │
│  │ 3. Si es "Anulado":                  │  │
│  │    a. devolver_stock()               │  │
│  │    b. form.instance.estado = Anulado │  │
│  │    c. super().form_valid()           │  │
│  │ 4. Si es "Pendiente":                │  │
│  │    a. Validar formset                │  │
│  │    b. Restaurar stock anterior       │  │
│  │    c. Eliminar detalles anteriores   │  │
│  │    d. Crear nuevos detalles          │  │
│  │    e. Descontar nuevo stock          │  │
│  └──────────────────────────────────────┘  │
└────────┬───────────────────────────────────┘
         │ 4. Redirect /pedidos/
         ▼
Detalle del pedido actualizado
```

> [!IMPORTANT]
> El estado se lee **directamente de la base de datos** (`Pedido.objects.get(pk=self.object.pk).estado`) para evitar inconsistencias causadas por el formulario que modifica `self.object.estado` antes de `form_valid()`.

---

## Diagrama de Base de Datos

```
┌─────────────────────────┐
│      auth_user          │  (Django User)
│                         │
│  id       INT PK        │
│  username VARCHAR(150)  │
│  email    VARCHAR(254)  │
│  password VARCHAR(128)  │
│  is_staff BOOLEAN       │
│  is_active BOOLEAN      │
└────────┬────────────────┘
         │
         │ 1:1 (usuario → cliente)
         │
┌────────▼────────────────┐         ┌─────────────────────────┐
│      clientes           │         │     api_usuarios        │
│                         │         │  (FastAPI auth)         │
│  id       INT PK        │         │                         │
│  usuario  INT FK (User) │         │  id       INT PK        │
│  nombre   VARCHAR(100)  │         │  username VARCHAR       │
│  correo   VARCHAR(254)  │◄────────│  email    VARCHAR       │
│  direccion VARCHAR(200) │  share  │  hashed_pw VARCHAR      │
│  telefono VARCHAR(20)   │  email  │  role     VARCHAR       │
└────────┬────────────────┘         └─────────────────────────┘
         │
         │ 1:N (cliente → pedidos)
         │
┌────────▼────────────────┐
│       pedidos           │
│                         │
│  id        INT PK       │
│  cliente   INT FK       │──► clientes.id
│  usuario   INT FK       │──► auth_user.id
│  fecha     DATETIME     │
│  estado    VARCHAR(20)  │  ← Pendiente, Enviado,
│                          │    Entregado, Anulado
└────────┬────────────────┘
         │
         │ 1:N (pedido → detalles)
         │
┌────────▼──────────────────┐       ┌─────────────────────────┐
│    detalles_pedido        │       │      productos          │
│                           │       │                         │
│  id          INT PK       │  N:1  │  id       INT PK        │
│  pedido      INT FK       │──────►│  nombre   VARCHAR(100)  │
│  producto    INT FK       │       │  precio   DECIMAL(10,2) │
│  cantidad    INT          │       │  stock    INT           │
└───────────────────────────┘       └─────────────────────────┘
```

> [!NOTE]
> La tabla `api_usuarios` es creada automáticamente por FastAPI mediante `Base.metadata.create_all(bind=engine)`. No requiere migraciones de Django.

---

## Patrones de Diseño

### Django — Class-Based Views (CBV)

```python
class PedidoCreateView(LoginRequiredMixin, CreateView):
    model = Pedido
    form_class = PedidoCreateForm
    template_name = 'pedidos/pedidos/formulario.html'
    success_url = reverse_lazy('pedido-list')

    def get_context_data(self, **kwargs):
        # Agregar datos adicionales al contexto
        ...

    def form_valid(self, form):
        # Lógica de negocio al validar
        ...
```

> [!TIP]
> Los CBV permiten reutilización de código mediante mixins (`LoginRequiredMixin`, `StaffRequiredMixin`) y organización clara de responsabilidades.

### FastAPI — Router Pattern

```python
# routers/clientes.py
router = APIRouter(prefix='/api/clientes', tags=['Clientes'])

@router.get('/')
def list_clientes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    ...

@router.post('/')
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    ...
```

```python
# main.py
from routers import clientes
app.include_router(clientes.router)
```

> [!TIP]
> Los routers permiten organizar endpoints por recurso, facilitando el mantenimiento y la escalabilidad.

### Repository Pattern (FastAPI)

```python
def get_cliente_by_id(db: Session, cliente_id: int):
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()
```

> [!NOTE]
> Las queries de base de datos se encapsulan en funciones separadas, facilitando testing y reutilización.

---

## Flujo de Autenticación

### Django (Sesiones)

```
┌──────────┐     ┌───────────┐     ┌──────────────┐     ┌───────────┐
│ Usuario  │────►│ /login/   │────►│ EmailBackend │────►│ Sesión    │
│          │     │ POST form │     │ validate     │     │ creada    │
└──────────┘     └───────────┘     └──────────────┘     └───────────┘
                                                              │
                                                              ▼
                                                       ┌───────────────┐
                                                       │ django_session│
                                                       │ table (MySQL) │
                                                       └───────────────┘
```

### FastAPI (JWT)

```
┌──────────┐     ┌──────────────────┐     ┌──────────────┐     ┌───────────┐
│ Cliente  │────►│ POST /api/auth/  │────►│ Verificar    │────►│ JWT Token │
│          │     │ token            │     │ credenciales │     │ firmado   │
└──────────┘     └──────────────────┘     └──────────────┘     └───────────┘
                                                                   │
                 ┌─────────────────────────────────────────────────┘
                 ▼
┌──────────┐     ┌──────────────────┐     ┌──────────────┐
│ Endpoint │◄────│ Authorization:   │◄────│ Incluir token│
│ Protegido│     │ Bearer <token>   │     │ en header    │
└──────────┘     └──────────────────┘     └──────────────┘
```

> [!CAUTION]
> Los tokens JWT son **stateless**. Una vez emitidos, no se pueden revocar hasta su expiración. Para producción, considera implementar una lista de revocación.

---

## Flujo de Pedidos

```
                    ┌─────────────┐
                    │  Pendiente  │◄──── Creación inicial
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌─────────┐ ┌─────────┐
        │Pendiente │ │ Enviado │ │ Anulado │
        │(editar)  │ │         │ │(final)  │
        └──────────┘ └────┬────┘ └─────────┘
                          │
               ┌──────────┼──────────┐
               │          │          │
               ▼          ▼          ▼
         ┌─────────┐ ┌─────────┐ ┌─────────┐
         │ Enviado │ │Entregado│ │ Anulado │
         │         │ │(final)  │ │(final)  │
         └─────────┘ └─────────┘ └─────────┘
```

### Reglas de Transición

| De → A | Permitido | Acción |
|--------|-----------|--------|
| `Pendiente` → `Pendiente` | ✅ | Editar productos |
| `Pendiente` → `Enviado` | ✅ | Cambiar estado |
| `Pendiente` → `Anulado` | ✅ | Devolver stock |
| `Enviado` → `Enviado` | ✅ | Sin cambios |
| `Enviado` → `Entregado` | ✅ | Finalizar |
| `Enviado` → `Anulado` | ✅ | Devolver stock |
| `Entregado` → `Entregado` | ✅ | Sin cambios |
| `Entregado` → `Anulado` | ✅ | Devolver stock |
| `Anulado` → `Anulado` | ✅ | Estado final |
| `Pendiente` → `Entregado` | ❌ | **No permitido** |
| `Enviado` → `Pendiente` | ❌ | **No permitido** |

---

## Flujo de Stock

### Crear Pedido

```
┌─────────────────────────────────────────────────────┐
│                 Transacción Atómica                  │
│                                                      │
│  1. Verificar stock de cada producto                 │
│     IF producto.stock < cantidad → ERROR, rollback   │
│                                                      │
│  2. Crear Pedido                                     │
│                                                      │
│  3. Crear DetallePedido para cada producto           │
│                                                      │
│  4. producto.stock -= cantidad (para cada producto)  │
│                                                      │
│  5. COMMIT                                           │
└─────────────────────────────────────────────────────┘
```

### Anular Pedido

```
┌─────────────────────────────────────────────────────┐
│                 Transacción Atómica                  │
│                                                      │
│  1. Obtener todos los DetallePedido del pedido       │
│                                                      │
│  2. For each detalle:                                │
│     producto.stock += detalle.cantidad               │
│     producto.save()                                  │
│                                                      │
│  3. pedido.estado = 'Anulado'                        │
│                                                      │
│  4. COMMIT                                           │
└─────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> La función `devolver_stock()` se llama **antes** de guardar cambios para garantizar que el stock se restaura correctamente incluso si la operación falla.

### Editar Pedido (Pendiente)

```
┌─────────────────────────────────────────────────────┐
│                 Transacción Atómica                  │
│                                                      │
│  1. devolver_stock(pedido) — Restaurar stock anterior│
│                                                      │
│  2. Eliminar detalles anteriores                     │
│                                                      │
│  3. Verificar stock de nuevos productos              │
│                                                      │
│  4. Crear nuevos detalles                            │
│                                                      │
│  5. Descontar nuevo stock                            │
│                                                      │
│  6. COMMIT                                           │
└─────────────────────────────────────────────────────┘
```

> [!CAUTION]
> El stock se restaur **antes** de crear nuevos detalles para evitar inconsistencias si hay errores de validación.

---

## Seguridad por Capas

```
┌─────────────────────────────────────────────────────┐
│                    Capa 1: Red                       │
│  • CORS restrictivo (FastAPI)                        │
│  • ALLOWED_HOSTS (Django)                            │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                 Capa 2: Autenticación                │
│  • Sesiones seguras (Django)                         │
│  • JWT con expiración (FastAPI)                      │
│  • EmailBackend personalizado                        │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                 Capa 3: Autorización                 │
│  • LoginRequiredMixin (Django)                       │
│  • get_current_user / get_current_admin (FastAPI)    │
│  • Roles: admin / user                               │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                Capa 4: Validación                    │
│  • Django Forms con validaciones                     │
│  • Pydantic schemas (FastAPI)                        │
│  • Validación de stock                               │
│  • Transiciones de estado                            │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                Capa 5: Base de Datos                 │
│  • ORM (protección SQL injection)                    │
│  • Transacciones atómicas                            │
│  • Foreign keys con PROTECT/CASCADE                  │
│  • Unique constraints                                │
└─────────────────────────────────────────────────────┘
```

---

## Escalabilidad

### Horizontal

| Servicio | Estrategia |
|----------|-----------|
| **Django** | Múltiples workers + load balancer |
| **FastAPI** | Uvicorn workers + load balancer |
| **MySQL** | Read replicas + connection pooling |

### Mejoras Futuras

| Mejora | Beneficio |
|--------|----------|
| **Docker** | Despliegue consistente, fácil escalar |
| **Redis** | Cache de sesiones, dashboard queries |
| **API Gateway** | Rate limiting, autenticación centralizada |
| **Message Queue** | Tareas asíncronas (exportar PDF/Excel) |
| **CDN** | Servir static files eficientemente |
| **Microservicios** | Separar responsabilidades completamente |

> [!TIP]
> Para producción, considera usar **Gunicorn** para Django y **Uvicorn con múltiples workers** para FastAPI.

---

## Decisiones Arquitectónicas

### ¿Por qué Django + FastAPI?

| Criterio | Django | FastAPI |
|----------|--------|---------|
| **Prototipado web** | ✅ Excelente | ❌ No es su propósito |
| **API performance** | Bueno | ✅ Excelente (3x más rápido) |
| **Auth integrada** | ✅ Sessions | ✅ JWT |
| **Documentación API** | Manual (DRF) | ✅ Automática (Swagger) |
| **Tipado** | Parcial | ✅ Completo (Pydantic) |

> [!NOTE]
> Esta combinación permite aprovechar lo mejor de cada framework sin compromisos significativos.

### ¿Por qué MySQL compartido?

**Ventajas:**
- ✅ Consistencia de datos garantizada
- ✅ Sin sincronización compleja
- ✅ Transacciones ACID entre servicios
- ✅ Simplicidad de infraestructura

**Desventajas:**
- ⚠️ Single point of failure
- ⚠️ Bottleneck potencial bajo carga alta

**Alternativas consideradas:**
- Event-driven architecture con message queues (overkill para este scope)
- Bases de datos separadas con sincronización (complejidad innecesaria)

### ¿Por qué CBV en Django?

- ✅ Reutilización de código con mixins
- ✅ Organización clara de responsabilidades
- ✅ Menos boilerplate que Function-Based Views
- ✅ Testing más sencillo

### ¿Por qué SQLAlchemy en FastAPI?

- ✅ Mejor integración con Pydantic
- ✅ Soporte completo para async (futuro)
- ✅ Control fino sobre queries
- ✅ Compatible con múltiples motores de BD

---

> [!NOTE]
> Para más detalles, consulta [DOCUMENTATION.md](DOCUMENTATION.md) y [FAQ.md](FAQ.md).
