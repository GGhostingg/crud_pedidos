# Preguntas Frecuentes — CRUD Pedidos

> Respuestas detalladas a las preguntas más comunes sobre el proyecto.

---

## 📋 Tabla de Contenidos

- [Arquitectura y Diseño](#arquitectura-y-diseño)
- [Autenticación y Seguridad](#autenticación-y-seguridad)
- [Base de Datos](#base-de-datos)
- [Pedidos y Stock](#pedidos-y-stock)
- [Performance y Escalabilidad](#performance-y-escalabilidad)
- [Testing y Calidad](#testing-y-calidad)
- [Despliegue y DevOps](#despliegue-y-devops)
- [Decisiones de Diseño](#decisiones-de-diseño)
- [Solución de Problemas](#solución-de-problemas)
- [Mejoras y Lecciones Aprendidas](#mejoras-y-lecciones-aprendidas)

---

## 🏗️ Arquitectura y Diseño

### ¿Por qué elegiste Django + FastAPI en lugar de solo uno?

**Respuesta:**

| Framework | Fortalezas | Uso en este proyecto |
|-----------|-----------|---------------------|
| **Django** | Autenticación integrada, ORM potente, templates, admin, rápido prototipado | Interfaz web completa con login, CRUD, dashboard |
| **FastAPI** | Alto rendimiento (3x Django REST), validación automática con Pydantic, documentación Swagger/OpenAPI, tipado completo | API REST para integraciones externas |

**Beneficios de la separación:**
- ✅ Separación clara de responsabilidades
- ✅ Escalar independientemente cada servicio
- ✅ Fácil integración con apps móviles/desktop vía API
- ✅ Documentación automática para la API

> [!TIP]
> Si solo necesitas una interfaz web, Django es suficiente. Si necesitas API para otros servicios, FastAPI es ideal.

### ¿Por qué no usaste Django REST Framework (DRF)?

**Respuesta:**

DRF es excelente, pero FastAPI ofrece:
- **Performance superior**: FastAPI es hasta 3x más rápido que DRF
- **Documentación automática**: Swagger UI y ReDoc se generan automáticamente
- **Tipado completo**: Pydantic valida y documenta los schemas
- **Async nativo**: Soporte completo para async/await (útil para futuro)

> [!NOTE]
> DRF sigue siendo una excelente opción para proyectos Django-only. La elección depende de los requisitos específicos.

### ¿Por qué MySQL y no PostgreSQL o SQLite?

**Respuesta:**

| Base de Datos | Ventajas | Desventajas |
|--------------|----------|-------------|
| **MySQL** | Amplio soporte, rápido, compatible con ambos ORMs | Menos features avanzadas que PostgreSQL |
| **PostgreSQL** | Más features (JSONB, full-text search, etc.) | Configuración más compleja |
| **SQLite** | Sin configuración, portable | No soporta concurrencia alta |

> [!CAUTION]
> Para producción con carga alta, **PostgreSQL** es recomendado por su robustez y features avanzadas.

---

## 🔐 Autenticación y Seguridad

### ¿Cómo funciona la autenticación dual?

El sistema usa **dos mecanismos independientes**:

| Servicio | Mecanismo | Almacenamiento |
|----------|----------|---------------|
| **Django** | Sesiones basadas en cookies | Tabla `django_session` en MySQL |
| **FastAPI** | JWT tokens stateless | No se almacenan (verificados criptográficamente) |

**Flujo:**
```
1. Usuario se registra en Django → Session creada
2. Usuario hace login en Django → Session actualizada
3. Para API (FastAPI) → Login separado con JWT
4. Sesión y JWT son independientes
```

> [!IMPORTANT]
> Las cuentas de Django (`auth_user`) y FastAPI (`api_usuarios`) son **tablas separadas**. No están sincronizadas automáticamente.

### ¿Cómo implementaste los roles en FastAPI?

**Modelo:** Tabla `api_usuarios` con campo `role` (`'admin'` o `'user'`).

**Dependencias:**
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Decodifica JWT, busca usuario, retorna
    ...

def get_current_admin(user: Usuario = Depends(get_current_user)):
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='No autorizado')
    return user
```

**Uso en endpoints:**
```python
@router.post('/api/productos/')
def create_producto(producto: ProductoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_admin)):
    # Solo admin puede crear productos
    ...
```

> [!TIP]
> Este patrón de dependencias es reutilizable y fácil de testear.

### ¿Qué es CSRF y cómo lo proteges?

**CSRF (Cross-Site Request Forgery)** es un ataque donde un sitio malicioso envía requests a otro sitio en nombre del usuario autenticado.

**Protección en Django:**
- ✅ Middleware CSRF habilitado por defecto
- ✅ Token `{% csrf_token %}` en todos los formularios POST
- ✅ Verificación automática en cada request POST

> [!CAUTION]
> Si un formulario POST no tiene `{% csrf_token %}`, Django retornará **Error 403 Forbidden**.

### ¿Los tokens JWT se pueden revocar?

**No directamente.** Los JWT son **stateless** — una vez emitidos, son válidos hasta su expiración.

**Soluciones posibles:**
- ⏰ Expiración corta (60 minutos para access token)
- 🔄 Refresh tokens con expiración más larga (7 días)
- 📋 Lista de revocación en base de datos (no implementado)

> [!NOTE]
> Para producción, considera implementar una lista de tokens revocados (blacklist) en Redis o base de datos.

---

## 💾 Base de Datos

### ¿Cómo manejas la concurrencia en stock?

**Problema:** Dos usuarios creando pedidos simultáneamente pueden sobre-vender stock.

**Solución:**
```python
@transaction.atomic
def form_valid(self, form):
    # 1. Verificar stock
    if producto.stock < cantidad:
        messages.error(...)
        return self.form_invalid(form)

    # 2. Crear pedido y detalles
    # 3. Reducir stock
    producto.stock -= cantidad
    producto.save()
    # 4. COMMIT automático al salir del bloque
```

> [!IMPORTANT]
> El decorador `@transaction.atomic` garantiza que si **cualquier** paso falla, se revierten **todos** los cambios (rollback).

### ¿Por qué no usaste triggers o procedures en MySQL?

**Respuesta:**

| Enfoque | Ventajas | Desventajas |
|---------|----------|-------------|
| **Python (actual)** | Testing fácil, version control, debugging simple | Lógica en aplicación |
| **Triggers/Procedures** | Ejecución en BD, independiente de app | Difícil testear, versionar, debuggear |

**Decisión:** Mantener la lógica en Python para:
- ✅ Facilidad de testing
- ✅ Control de versiones del código
- ✅ Debugging sencillo
- ✅ Consistencia entre entornos (dev/staging/prod)

### ¿Qué pasa si la conexión a MySQL falla?

**Django:**
- Retorna error 500
- Sesión se pierde (si no hay reconnect)

**FastAPI:**
- Retorna error 500 con detalle
- Transacción se revierte automáticamente

> [!TIP]
> Para producción, configura **connection pooling** y **retries automáticos**.

---

## 📦 Pedidos y Stock

### ¿Cómo funcionan las transiciones de estado?

Las transiciones están validadas para evitar cambios inválidos:

```
Pendiente ──► Enviado ──► Entregado
    │            │            │
    │            │            ▼
    │            └────────► Anulado
    ▼
  Anulado
```

**Reglas:**
| Estado Actual | Estados Válidos |
|--------------|----------------|
| `Pendiente` | `Pendiente`, `Enviado`, `Anulado` |
| `Enviado` | `Enviado`, `Entregado`, `Anulado` |
| `Entregado` | `Entregado`, `Anulado` |
| `Anulado` | `Anulado` (estado final) |

> [!CAUTION]
> No se puede pasar de `Pendiente` a `Entregado` directamente. Debe pasar por `Enviado` primero.

### ¿Qué pasa con el stock al anular un pedido?

**Se restaura automáticamente:**

```python
def devolver_stock(pedido):
    for detalle in pedido.detalles.all():
        detalle.producto.stock += detalle.cantidad
        detalle.producto.save()
    pedido.estado = 'Anulado'
    pedido.save()
```

> [!IMPORTANT]
> Esta operación ocurre dentro de una transacción atómica para garantizar consistencia.

### ¿Por qué el campo `cliente` se oculta para usuarios normales?

**Razón de seguridad:** Los usuarios normales solo pueden crear pedidos para **su propio cliente**. Mostrar el selector permitiría asignar pedidos a otros clientes.

**Implementación:**
```python
if not request.user.is_staff:
    cliente = self.get_cliente_for_user(request.user)
    form.fields['cliente'].initial = cliente.pk
    form.fields['cliente'].widget = forms.HiddenInput()
```

> [!NOTE]
> Los administradores ven el selector completo para asignar pedidos a cualquier cliente.

### ¿Por qué `db_estado` se lee directo de la BD en `form_valid()`?

**Problema descubierto:** Django's `UpdateView` actualiza `self.object` con los datos del formulario **antes** de llamar `form_valid()`, lo que significa que `self.object.estado` ya tiene el valor nuevo en vez del valor guardado en BD.

**Solución:**
```python
def form_valid(self, form):
    db_estado = Pedido.objects.get(pk=self.object.pk).estado  # Lee de BD
    submitted_estado = self.request.POST.get('estado') or db_estado
    # Validar transición con el estado REAL de BD
```

> [!CAUTION]
> Este es un bug sutil que puede causar transiciones de estado inválidas. Siempre lee el estado original de BD cuando necesites validar cambios.

---

## 🚀 Performance y Escalabilidad

### ¿Cómo optimizaste las queries del dashboard?

**Técnicas usadas:**

```python
# ✅ Usando agregaciones SQL eficientes
Pedido.objects.values('estado').annotate(count=Count('estado'))

# ✅ select_related para evitar N+1 queries
Pedido.objects.select_related('cliente').all()

# ✅ Filtros específicos
Producto.objects.filter(stock__lt=5)

# ✅ Anotaciones para cálculos
DetallePedido.objects.filter(pedido__estado='Entregado').aggregate(total=Sum('cantidad'))
```

> [!TIP]
> Usa `django-debug-toolbar` para identificar queries N+1 y optimizarlas.

### ¿Es escalable esta arquitectura?

**Ventajas:**
- ✅ FastAPI puede escalar horizontalmente (stateless)
- ✅ Django puede usar caching/CDN
- ✅ BD puede tener réplicas de lectura
- ✅ Servicios independientes

**Limitaciones:**
- ⚠️ BD compartida es bottleneck potencial
- ⚠️ Monolito Django para UI

**Mejoras futuras:**
- 🔧 Microservicios separados
- 🔧 API Gateway
- 🔧 Cache distribuido (Redis)
- 🔧 Message queue para tareas async (Celery)

### ¿Cuál es el límite de usuarios concurrentes?

**Depende de:**
- RAM/CPU del servidor
- Configuración de MySQL (max_connections)
- Número de workers de Django/FastAPI

**Estimación保守 (servidor modesto):**
- Django: ~50-100 usuarios concurrentes
- FastAPI: ~500-1000 requests/segundo
- MySQL: ~150 conexiones simultáneas

> [!NOTE]
> Para producción con carga alta, usa **load testing** con herramientas como Apache JMeter o Locust.

---

## 🧪 Testing y Calidad

### ¿Qué estrategia de testing usaste?

**Django:**
```bash
cd django_app
python manage.py test
```

- Tests unitarios en `pedidos/tests.py`
- Tests de modelos y vistas básicas
- Usando `TestCase` de Django

**FastAPI:**
- Testing manual vía **Swagger UI** (`/api/docs`)
- Tests automáticos con pytest: **pendiente de implementación**

> [!TIP]
> Para producción, implementa tests de integración completos con cobertura > 80%.

### ¿Cómo validaste la API?

**Herramientas:**
- ✅ Swagger UI (`/api/docs`) para testing interactivo
- ✅ Validación de responses con schemas Pydantic
- ⏰ Postman para flujos complejos (pendiente)
- ⏰ Tests automatizados con pytest (pendiente)

### ¿Qué cobertura de tests tienes actualmente?

**Estado actual:**
- Django: Tests básicos (~30% cobertura estimada)
- FastAPI: Sin tests automatizados (0%)

> [!CAUTION]
> Para producción, necesitas tests unitarios, de integración y E2E con cobertura mínima del 80%.

---

## 🚀 Despliegue y DevOps

### ¿Cómo desplegarías en producción?

**Arquitectura recomendada:**

```
                    ┌──────────────┐
                    │   Nginx      │
                    │ (SSL + LB)   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Gunicorn │ │ Uvicorn  │ │ Uvicorn  │
        │ (Django) │ │ (FastAPI)│ │ (FastAPI)│
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             └────────────┼────────────┘
                          ▼
                    ┌──────────┐
                    │  MySQL   │
                    │  (RDS)   │
                    └──────────┘
```

**Configuración:**
| Servicio | Herramienta |
|----------|-----------|
| **Django** | Gunicorn + Nginx, `DEBUG=False` |
| **FastAPI** | Uvicorn workers (4+) + Nginx |
| **MySQL** | AWS RDS o servidor dedicado |
| **Static Files** | Nginx o CDN (Cloudflare) |
| **Secrets** | Variables de entorno o vault |
| **SSL/TLS** | Let's Encrypt (certbot) |

> [!IMPORTANT]
> En producción:
> - `DEBUG = False` en Django
> - Claves secretas seguras y únicas
> - HTTPS obligatorio
> - Aumentar `SESSION_COOKIE_AGE` a 3600+ segundos

### ¿Consideraste Docker?

**Respuesta:** Sí, pero no implementado por simplicidad del desarrollo.

**Estructura propuesta:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
    volumes:
      - mysql_data:/var/lib/mysql

  django:
    build: ./django_app
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    environment:
      - DB_HOST=db
      - DB_NAME=${DB_NAME}
      ...
    depends_on:
      - db

  fastapi:
    build: ./fastapi_app
    command: uvicorn main:app --host 0.0.0.0 --port 8001
    environment:
      - DB_HOST=db
      ...
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - django
      - fastapi

volumes:
  mysql_data:
```

> [!TIP]
> Docker facilita el despliegue consistente entre entornos (dev/staging/prod).

---

## 🎯 Decisiones de Diseño

### ¿Por qué Bootstrap en lugar de un framework moderno?

**Razones:**
- ✅ Rápido de implementar (sin build process)
- ✅ Suficiente para demo/prototipo
- ✅ No requiere Node.js/npm
- ✅ Bueno para universidad/proyecto académico

**Alternativas consideradas:**
- React/Vue con componentes separados (overkill para CRUD simple)
- Tailwind CSS (requiere build process)

> [!NOTE]
> Para producción con requisitos de UX avanzados, considera **React** o **Vue.js**.

### ¿Por qué no async/await en todas partes?

**FastAPI soporta async, pero:**
- ⚠️ mysqlclient (driver MySQL de Django) no es fully async
- ⚠️ PyMySQL (usado por SQLAlchemy) tiene soporte async limitado
- ⚠️ Complejidad adicional para poco beneficio en este caso
- ✅ Sync es suficiente para el volumen actual

> [!TIP]
> Para alta concurrencia, considera **asyncpg** (PostgreSQL) o **aiomysql** (MySQL).

### ¿Por qué CBV en Django?

**Class-Based Views ofrecen:**
- ✅ Reutilización de código con mixins
- ✅ Mejor organización de responsabilidades
- ✅ Menos boilerplate que Function-Based Views
- ✅ Testing más sencillo
- ✅ herencia clara

**Ejemplo:**
```python
class PedidoUpdateView(LoginRequiredMixin, UpdateView):
    # LoginRequiredMixin asegura autenticación
    # UpdateView maneja GET/POST automáticamente
    ...
```

### ¿Por qué Pydantic en lugar de solo SQLAlchemy?

**Pydantic agrega:**
- ✅ Validación automática de input/output
- ✅ Serialización a JSON automática
- ✅ Documentación API (Swagger)
- ✅ Type hints para mejor developer experience
- ✅ Manejo de errores consistente

---

## 🐛 Solución de Problemas

### Error 403 CSRF en logout

**Causa más común:** Sesión expirada (120 segundos por defecto).

**Solución:**
1. Aumenta `SESSION_COOKIE_AGE` en `settings.py`:
   ```python
   SESSION_COOKIE_AGE = 3600  # 1 hora
   ```
2. O habilita `SESSION_SAVE_EVERY_REQUEST = True` para resetear timer en cada request.

### FastAPI no crea tabla `api_usuarios`

**Causa:** Error de conexión a MySQL.

**Solución:**
1. Verifica `.env`:
   ```env
   DB_NAME=crud_pedidos_db
   DB_USER=root
   DB_PASSWORD=tu_password_aqui
   DB_HOST=localhost
   DB_PORT=3306
   ```
2. Verifica que MySQL esté corriendo:
   ```bash
   mysql -u root -p -e "SHOW DATABASES;"
   ```

### Stock negativo tras crear pedido

**Causa:** Bug ya corregido — `db_estado` se leía de `self.object.estado` en vez de BD.

**Solución:** Actualiza a la última versión del código.

### Error de importación de mysqlclient

**Causa:** Faltan dependencias del sistema.

**Solución:**
```bash
# Debian/Ubuntu
sudo apt install default-libmysqlclient-dev build-essential pkg-config

# macOS
brew install mysql-client
export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"
pip install mysqlclient
```

### Migraciones de Django fallan

**Causa:** Base de datos no existe o credenciales incorrectas.

**Solución:**
```sql
CREATE DATABASE crud_pedidos_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Error "NoReverseMatch" en templates

**Causa:** Nombre de URL no existe en `urls.py`.

**Solución:** Verifica que el `name=` en `urls.py` coincida con `{% url 'nombre' %}` en el template.

---

## 💡 Mejoras y Lecciones Aprendidas

### ¿Qué cambiarías si lo hicieras de nuevo?

1. **🐳 Docker desde el inicio** — Despliegue consistente, fácil escalar
2. **🧪 Tests automatizados completos** — Bugs son más caros después
3. **📦 Separar más responsabilidades** — Capa de servicios (service layer)
4. **📊 Monitoring y logging estructurados** — Sentry, ELK stack
5. **🔑 Environment-specific configs** — Diferentes configs para dev/staging/prod
6. **🔄 Sincronización de usuarios Django/FastAPI** — Mismo sistema de auth
7. **⚡ Cache con Redis** — Dashboard queries, sesiones

### ¿Qué aprendiste de este proyecto?

| Lección | Descripción |
|---------|-------------|
| **Arquitectura importa** | Pensar en escalabilidad desde el inicio evita rework |
| **APIs first** | Diseñar API antes que UI facilita integraciones |
| **Testing temprano** | Bugs detectados temprano son 10x más baratos |
| **Documentación** | Vale la pena invertir tiempo desde el inicio |
| **Simplicidad** | No over-engineer para prototipos |
| **Transacciones** | Siempre usa `@transaction.atomic` para operaciones críticas |
| **Validación** | Valida en cliente Y servidor, nunca confíes solo en cliente |

### ¿Qué features agregarías en el futuro?

- [ ] **Notificaciones** por email al cambiar estado de pedido
- [ ] **Búsqueda avanzada** con filtros múltiples
- [ ] **Gráficos interactivos** en dashboard (Chart.js)
- [ ] **Exportación masiva** a PDF/Excel con filtros
- [ ] **Histórico de cambios** (audit log)
- [ ] **API versioning** (`/api/v1/...`)
- [ ] **Rate limiting** en API
- [ ] **WebSocket** para actualizaciones en tiempo real
- [ ] **Docker** para despliegue consistente
- [ ] **CI/CD** con GitHub Actions

---

> [!TIP]
> Para más detalles técnicos, consulta [DOCUMENTATION.md](DOCUMENTATION.md) y [ARCHITECTURE.md](ARCHITECTURE.md).
