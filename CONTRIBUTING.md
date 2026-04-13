# Guía de Contribución — CRUD Pedidos

> Gracias por tu interés en contribuir a este proyecto. Esta guía te ayudará a empezar.

---

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo Puedo Contribuir?](#cómo-puedo-contribuir)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Mejoras](#sugerir-mejoras)
- [Desarrollo Local](#desarrollo-local)
- [Estándares de Código](#estándares-de-código)
- [Commits y Pull Requests](#commits-y-pull-requests)
- [Testing](#testing)
- [Documentación](#documentación)
- [Licencia](#licencia)

---

## 🤝 Código de Conducta

Este proyecto se rige por los siguientes principios:

- ✅ **Respeto**: Tratar a todos los contribuyentes con cortesía y profesionalismo.
- ✅ **Inclusión**: Fomentar un ambiente acogedor para todos, sin importar su experiencia.
- ✅ **Colaboración**: Trabajar juntos para lograr los mejores resultados.
- ✅ **Constructividad**: Dar y recibir feedback de manera constructiva.

> [!IMPORTANT]
> Comportamiento abusivo, acosador o discriminatorio no será tolerado.

---

## 🛠️ ¿Cómo Puedo Contribuir?

### 1. Reportar Bugs

Si encuentras un error, por favor:

1. Busca en [Issues](../../issues) para verificar que no se haya reportado.
2. Si no existe, abre un **nuevo issue** con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs. actual
   - Capturas de pantalla (si aplica)
   - Versión de Python, Django y FastAPI

### 2. Sugerir Mejoras

Para nuevas features o mejoras:

1. Abre un **issue** describiendo la mejora.
2. Explica el **por qué** es útil.
3. Si es posible, incluye un **ejemplo de uso**.

### 3. Enviar Código

1. Haz un **fork** del repositorio.
2. Crea una rama: `git checkout -b feature/nombre-feature`.
3. Implementa tus cambios.
4. Agrega tests si aplica.
5. Haz commit y push.
6. Abre un **Pull Request**.

> [!TIP]
> Revisa la sección [Desarrollo Local](#desarrollo-local) para configurar tu entorno.

---

## 🐛 Reportar Bugs

### Plantilla de Issue para Bugs

```markdown
### Descripción
Describe el bug encontrado.

### Pasos para Reproducir
1. Ir a '...'
2. Click en '...'
3. Scroll a '...'
4. Ver error

### Comportamiento Esperado
Qué debería pasar.

### Comportamiento Actual
Qué pasa realmente.

### Capturas de Pantalla
Si aplica, agrega imágenes.

### Entorno
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.12]
- Django: [e.g. 6.0.4]
- MySQL: [e.g. 8.0]

### Información Adicional
Cualquier otro detalle relevante.
```

---

## 💻 Desarrollo Local

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/crud-pedidos.git
cd crud-pedidos
```

### 2. Configurar Entorno

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Base de Datos

```sql
CREATE DATABASE crud_pedidos_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Crea el archivo `.env` basado en `.env.example`.

### 4. Ejecutar Migraciones

```bash
cd django_app
python manage.py migrate
```

### 5. Iniciar Servicios

**Terminal 1 — Django:**
```bash
cd django_app
python manage.py runserver
```

**Terminal 2 — FastAPI:**
```bash
cd fastapi_app
uvicorn main:app --reload
```

---

## 📐 Estándares de Código

### Python

- **Versión mínima:** Python 3.12
- **Estilo:** Seguir [PEP 8](https://peps.python.org/pep-0008/)
- **Type hints:** Usar en funciones nuevas siempre que sea posible
- **Docstrings:** Google style para funciones y clases públicas

**Ejemplo:**
```python
def get_cliente_by_id(db: Session, cliente_id: int) -> Cliente | None:
    """Obtiene un cliente por su ID.

    Args:
        db: Sesión de base de datos.
        cliente_id: ID del cliente.

    Returns:
        El cliente encontrado o None.
    """
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()
```

### Django

- **Vistas:** Usar Class-Based Views (CBV)
- **Formularios:** Validaciones en `clean_<campo>()`
- **Templates:** Bootstrap 5, evitar inline CSS/JS
- **Nombres de URL:** Siempre usar `name=` y `{% url 'nombre' %}`

### FastAPI

- **Routers:** Organizar por recurso (`clientes.py`, `productos.py`, etc.)
- **Schemas:** Pydantic para toda validación de request/response
- **Dependencias:** Reutilizar `get_db`, `get_current_user`, etc.
- **Documentación:** Agregar `summary` y `description` en endpoints

### Templates HTML

- **Indentación:** 4 espacios
- **CSRF:** Siempre incluir `{% csrf_token %}` en forms POST
- **Clases:** Usar Bootstrap 5
- **Comentarios:** En español, explicar el "por qué", no el "qué"

### JavaScript

- **Estilo:** Vanilla JS, evitar jQuery
- **Scope:** Usar IIFE `(function() { ... })();` para evitar polución global
- **Nombres:** camelCase para variables y funciones

---

## 📝 Commits y Pull Requests

### Commits

Usa mensajes claros y concisos:

```
# ✅ Buenos ejemplos
feat: agregar exportación de pedidos a Excel
fix: corregir validación de stock en creación de pedidos
docs: actualizar README con nuevas variables de entorno
test: agregar tests para PedidoCreateView

# ❌ Evitar
fix: fix bug
changes
update
```

**Formato recomendado:**
```
<tipo>: <descripción breve>

[opcional: cuerpo explicativo]
```

**Tipos comunes:**
| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Cambios en documentación |
| `style` | Formato, sin cambio de lógica |
| `refactor` | Refactorización de código |
| `test` | Agregar o corregir tests |
| `chore` | Tareas de mantenimiento |

### Pull Requests

**Título:** Claro y descriptivo.

**Descripción:**
```markdown
### ¿Qué hace este PR?
Descripción breve del cambio.

### ¿Por qué es necesario?
Explicación del problema o mejora.

### ¿Cómo probarlo?
1. Paso 1
2. Paso 2
3. Verificar resultado

### Checklist
- [ ] Código sigue estándares del proyecto
- [ ] Tests agregados/actualizados
- [ ] Documentación actualizada
- [ ] Sin warnings ni errores de lint
```

> [!CAUTION]
> **Nunca** subas archivos `.env` con secretos reales. Usa `.env.example` como plantilla.

---

## 🧪 Testing

### Django

```bash
cd django_app
python manage.py test
```

**Cobertura mínima:** 80% para código nuevo.

**Ejemplo de test:**
```python
from django.test import TestCase
from pedidos.models import Cliente

class ClienteModelTest(TestCase):
    def test_creacion_cliente(self):
        cliente = Cliente.objects.create(
            nombre='Juan Pérez',
            correo='juan@example.com'
        )
        self.assertEqual(cliente.nombre, 'Juan Pérez')
        self.assertEqual(cliente.correo, 'juan@example.com')
```

### FastAPI

```bash
# Pendiente de implementación con pytest
pip install pytest httpx
pytest
```

**Ejemplo de test:**
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/api/")
    assert response.status_code == 200
    assert "mensaje" in response.json()
```

> [!TIP]
> Ejecuta tests antes de cada PR para asegurar calidad.

---

## 📚 Documentación

### Archivos Principales

| Archivo | Propósito |
|---------|----------|
| `README.md` | Guía principal del proyecto |
| `DOCUMENTATION.md` | Documentación técnica completa |
| `ARCHITECTURE.md` | Diagramas y arquitectura |
| `FAQ.md` | Preguntas frecuentes |
| `CONTRIBUTING.md` | Este archivo |

### Cuándo Actualizar Documentación

- ✅ Nueva funcionalidad
- ✅ Cambio en variables de entorno
- ✅ Modificación en endpoints de API
- ✅ Cambio en modelo de datos
- ✅ Instrucciones de instalación/ejecución

> [!NOTE]
> La documentación en español es obligatoria. Código y comentarios pueden ser en inglés.

---

## 📄 Licencia

Al contribuir a este proyecto, aceptas que tus contribuciones estarán bajo la misma licencia MIT del proyecto.

---

## 🙏 ¡Gracias!

Cualquier contribución, por pequeña que sea, es valiosa. Si tienes dudas, abre un issue o contacta a los mantenedores.

> [!TIP]
> Revisa los issues con label `good first issue` para empezar con algo sencillo.
