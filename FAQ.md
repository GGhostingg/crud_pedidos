# Preguntas Frecuentes y Respuestas Detalladas

## 🏗️ Arquitectura y Diseño

### ¿Por qué elegiste Django + FastAPI en lugar de solo uno?

**Respuesta detallada:**
- **Django**: Excelente para prototipos rápidos de interfaces web. Tiene autenticación integrada, ORM poderoso y templates. Ideal para el frontend administrativo.
- **FastAPI**: Superior en performance para APIs (3x más rápido que Django REST). Validación automática con Pydantic, documentación OpenAPI automática, mejor soporte para async.
- **Beneficios**: Separación clara de responsabilidades. Django maneja usuarios web, FastAPI la API móvil/desktop. Fácil escalar independientemente.

### ¿Por qué MySQL compartido en lugar de BDs separadas?

**Respuesta:**
- **Consistencia**: Evita problemas de sincronización entre servicios.
- **Simplicidad**: Un solo esquema, menos infraestructura.
- **Transacciones**: Operaciones complejas (crear pedido + reducir stock) necesitan ACID.
- **Alternativa**: Podría usar event-driven architecture con message queues, pero overkill para este scope.

## 🔐 Seguridad

### ¿Cómo funciona la autenticación dual?

**Django:**
- Sesiones basadas en cookies
- Autenticación estándar de Django
- Protección CSRF en formularios

**FastAPI:**
- JWT tokens stateless
- Refresh tokens para sesiones largas
- Bearer authentication en headers

**Flujo:** Usuario se loguea en Django, obtiene sesión. Para API calls, obtiene JWT separado.

### ¿Cómo implementaste los roles?

**Modelo:** Tabla `api_usuarios` con campo `role` ('admin'/'user')

**Dependencias FastAPI:**
```python
def get_current_admin(user: Usuario = Depends(get_current_user)):
    if user.role != 'admin':
        raise HTTPException(403, 'No autorizado')
    return user
```

**Uso:** Endpoints de productos/pedidos usan `get_current_admin` para operaciones write.

## 💾 Base de Datos

### ¿Cómo manejas la concurrencia en stock?

**Problema:** Dos usuarios creando pedidos simultáneamente pueden sobre-vender stock.

**Solución:**
- Transacciones SQL atómicas en `crear_pedido()`
- Check stock antes de reducir
- Rollback si insuficiente

**Código clave:**
```python
# Verificar stock
if prod.stock < det.cantidad:
    db.rollback()
    raise HTTPException(400, 'Stock insuficiente')

# Reducir stock
prod.stock -= det.cantidad
```

### ¿Por qué no usaste triggers o procedures en MySQL?

**Respuesta:** Quise mantener la lógica de negocio en Python para:
- Mejor testing
- Version control del código
- Facilidad de debugging
- Consistencia entre entornos

## 🚀 Performance y Escalabilidad

### ¿Cómo optimizaste las queries del dashboard?

**Dashboard queries:**
```python
# Usando agregaciones SQL eficientes
Pedido.objects.values('estado').annotate(count=Count('estado'))
Producto.objects.filter(stock__lt=5)
DetallePedido.objects.filter(pedido__estado='Entregado').aggregate(total=Sum(...))
```

**Optimizaciones:**
- `select_related()` para joins
- Índices en campos de búsqueda
- Paginación para listas grandes

### ¿Es escalable esta arquitectura?

**Ventajas:**
- FastAPI puede escalar horizontalmente (stateless)
- Django puede usar caching/CDN
- BD puede tener réplicas de lectura

**Limitaciones:**
- BD compartida es bottleneck potencial
- Monolito Django para UI

**Mejoras futuras:**
- Microservicios separados
- API Gateway
- Cache distribuido (Redis)

## 🧪 Testing y Calidad

### ¿Qué estrategia de testing usaste?

**Django:**
- Tests unitarios en `tests.py`
- Test de vistas y modelos
- Usando `TestCase` de Django

**FastAPI:**
- Tests con pytest (no implementados aún)
- Test de endpoints con `TestClient`
- Mock de BD para tests

**Integración:**
- Testing manual vía Swagger UI
- Validación de flujos completos

### ¿Cómo validaste la API?

**Herramientas:**
- Swagger UI (`/api/docs`) para testing interactivo
- Postman para flujos complejos
- Validación de responses con schemas Pydantic

## 🐛 Debugging y Troubleshooting

### ¿Qué problemas encontraste y cómo los solucionaste?

**Problema 1: CORS entre Django y FastAPI**
- **Solución:** Configurar CORS middleware en FastAPI
```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], ...)
```

**Problema 2: Serialización de modelos SQLAlchemy**
- **Solución:** Usar `from_attributes=True` en Pydantic Config

**Problema 3: Refresh tokens**
- **Solución:** Agregar campo 'type' al payload JWT para distinguir access/refresh

### ¿Cómo debuggeas requests entre servicios?

**Herramientas:**
- Logs detallados en ambos servicios
- `print()` statements durante desarrollo
- Postman para testing API
- Django debug toolbar

## 📦 Despliegue y DevOps

### ¿Cómo desplegarías en producción?

**Django:**
- Gunicorn + Nginx
- Static files servidos por Nginx
- Environment variables para secrets

**FastAPI:**
- Uvicorn workers
- Nginx como reverse proxy
- Docker containers

**Infraestructura:**
- MySQL en RDS/Aurora
- Load balancer para múltiples instancias
- SSL certificates

### ¿Consideraste Docker?

**Respuesta:** Sí, pero no implementado por simplicidad. Estructura sería:
- `Dockerfile` para cada servicio
- `docker-compose.yml` con Django, FastAPI, MySQL
- Volumes para persistencia

## 🔮 Decisiones de Diseño

### ¿Por qué Bootstrap en lugar de framework moderno?

**Razones:**
- Rápido de implementar
- No requiere build process
- Suficiente para demo/prototipo
- Bueno para universidad

**Alternativas consideradas:** React/Vue, pero overkill para CRUD simple.

### ¿Por qué no async/await en todas partes?

**FastAPI soporta async, pero:**
- MySQL driver no es fully async
- Complejidad adicional para poco beneficio
- Sync es suficiente para este caso de uso

## 💡 Mejoras y Lecciones Aprendidas

### ¿Qué cambiarías si lo hicieras de nuevo?

1. **Usar Docker desde el inicio**
2. **Implementar tests automatizados completos**
3. **Separar más responsabilidades (services layer)**
4. **Agregar monitoring (logs estructurados)**
5. **Usar environment-specific configs**

### ¿Qué aprendiste de este proyecto?

- **Arquitectura importa:** Pensar en escalabilidad desde el inicio
- **APIs first:** Diseñar API antes que UI
- **Testing temprano:** Bugs son más caros después
- **Documentación:** Vale la pena invertir tiempo
- **Simplicity:** No over-engineer para prototipos

## 🎯 Preguntas Específicas del Código

### ¿Por qué usaste CBV en Django?

**Respuesta:** Class-Based Views ofrecen:
- Reutilización de código
- Mixins para autenticación
- Mejor organización
- Menos boilerplate que FBV

### ¿Cómo funciona la paginación?

**Django:** `paginate_by = 10` en ListView
**FastAPI:** Query params `skip` y `limit` con validación

### ¿Por qué Pydantic en lugar de solo SQLAlchemy?

- Validación de input/output
- Serialización automática
- Documentación API
- Type hints para mejor DX

---

**Consejo:** Para cualquier pregunta, siempre relaciona con principios de arquitectura, trade-offs considerados, y alternativas evaluadas. Muestra pensamiento crítico y justificación técnica.