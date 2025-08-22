# Fund Subscription API

API para gestionar suscripciones a fondos de inversión con arquitectura limpia, DynamoDB y FastAPI.

## 🏗️ Arquitectura

El proyecto sigue los principios de **Clean Architecture** con las siguientes capas:

```
app/
├── domain/          # Modelos de dominio y reglas de negocio
├── application/     # Puertos (interfaces) y casos de uso
├── infrastructure/  # Adaptadores (DynamoDB, FastAPI)
├── use_cases/       # Lógica de negocio
└── routes/          # Endpoints de la API
```

## 🚀 Desarrollo Local

### Prerrequisitos

- Python 3.13+
- pip
- Credenciales de AWS configuradas

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd amaris-consulting
```

### 2. Configurar Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # macOS/Linux
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependencias

```bash
# Dependencias de producción
pip install -r app/requirements.txt

# Dependencias de desarrollo (opcional)
pip install -r app/requirements-dev.txt
```

### 4. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
AWS_ACCESS_KEY_ID=tu_access_key_id
AWS_SECRET_ACCESS_KEY=tu_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```

### 5. Ejecutar Servidor de Desarrollo

#### Opción 1: FastAPI CLI (Recomendado)

```bash
# Servidor de desarrollo con auto-reload
fastapi dev app/main.py --port 8000

# El servidor estará disponible en: http://localhost:8000
# Documentación automática en: http://localhost:8000/docs
```

#### Opción 2: Uvicorn Directo

```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Verificar que Funciona

```bash
# Healthcheck básico
curl http://localhost:8000/transactions

# Documentación interactiva
open http://localhost:8000/docs
```

## 🔧 Scripts de Desarrollo

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest

# Tests específicos con verbose
python -m pytest app/use_cases/tests/ -v

# Tests con cobertura
python -m pytest --cov=app
```

### Linting y Formato

```bash
# Verificar formato (si tienes configurado)
flake8 app/

# Formato automático (si tienes black)
black app/
```

## 📊 Base de Datos

El proyecto usa **DynamoDB** con un diseño de tabla única (`AppChallenge`):

### Estructura de Datos

```
PK              SK                      Tipo
USER#u001       PROFILE                 Usuario
USER#u001       SUB#f001               Suscripción  
USER#u001       TX#20250822T100000#T001 Transacción
FUND#f001       PROFILE                 Fondo
```

### Datos de Prueba

Los datos de prueba están disponibles en `results.csv` con usuarios, fondos, suscripciones y transacciones de ejemplo.

## 🌐 Endpoints Disponibles

### Suscripciones

- `POST /user/{user_id}/subscribe/{fund_id}` - Crear suscripción
- `DELETE /user/{user_id}/subscribe/{fund_id}` - Cancelar suscripción

### Transacciones

- `GET /transactions` - Historial completo
- `GET /user/transactions?user_id={user_id}` - Por usuario

### Documentación

- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

## 💼 Reglas de Negocio

1. **Balance inicial**: COP $500.000 por usuario
2. **Monto mínimo**: Cada fondo tiene su monto mínimo de vinculación
3. **Identificadores únicos**: Cada transacción tiene ID basado en timestamp
4. **Cancelación**: El valor se devuelve al usuario al cancelar
5. **Validación de saldo**: Mensaje específico cuando no hay suficiente saldo

## 🧪 Testing

Los tests unitarios verifican todas las reglas de negocio:

```bash
# Ejecutar tests de reglas de negocio
python -m pytest app/use_cases/tests/test_subscription_use_case.py -v
```

### Cobertura de Tests

- ✅ Validación de monto mínimo
- ✅ Manejo de saldo insuficiente  
- ✅ Identificadores únicos de transacciones
- ✅ Retorno de dinero al cancelar
- ✅ Validación de fondos existentes

## 🚢 Despliegue

### Para AWS Lambda

El proyecto incluye soporte para Lambda con `mangum`:

```python
# En main.py
from mangum import Mangum
lambda_handler = Mangum(app)
```

### Variables de Entorno Requeridas

```env
AWS_ACCESS_KEY_ID=<tu-access-key>
AWS_SECRET_ACCESS_KEY=<tu-secret-key>
AWS_DEFAULT_REGION=us-east-1
```

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama de feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📝 Notas de Desarrollo

- La aplicación usa **Clean Architecture** con inyección de dependencias
- Los adapters están desacoplados usando **Protocol classes**
- DynamoDB usa **single table design** para eficiencia
- Tests unitarios con **mocks** para aislamiento completo
- Documentación automática con **FastAPI/OpenAPI**

---

**Tecnologías**: FastAPI • DynamoDB • AWS • Python 3.13 • Pydantic • Pytest