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
- AWS CLI configurado
- SAM CLI instalado
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

#### Opción 1: SAM Local (Recomendado)

```bash
# Construir la aplicación
sam build

# Ejecutar servidor local que simula Lambda
sam local start-api --port 3000

# El servidor estará disponible en: http://localhost:3000
# Documentación automática en: http://localhost:3000/docs
```

#### Opción 2: FastAPI CLI (Solo para desarrollo rápido)

```bash
# Servidor de desarrollo con auto-reload
fastapi dev src/app/main.py --port 8000

# El servidor estará disponible en: http://localhost:8000
# Documentación automática en: http://localhost:8000/docs
```

### 6. Verificar que Funciona

```bash
# Con SAM Local
curl http://localhost:3000/transactions
open http://localhost:3000/docs

# Con FastAPI CLI
curl http://localhost:8000/transactions
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

## 🌐 Endpoints Disponibles

### Usuarios

#### `POST /user/create`
**Crear un nuevo usuario con ID auto-generado**

- **Body (JSON):**
  ```json
  {
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "phone": "+573001234567",
    "balance": 100000,
    "notify_channel": "email"
  }
  ```

- **Respuesta:** Objeto usuario creado con `user_id` generado automáticamente
  ```json
  {
    "user_id": "u234567890",
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "phone": "+573001234567",
    "balance": 100000,
    "notify_channel": "email"
  }
  ```

- **Nota:** El `user_id` se genera automáticamente con formato `u{timestamp}{random}` (ej: `u234567890`)

### Suscripciones

#### `POST /user/{user_id}/subscribe/{fund_id}`
**Crear suscripción a un fondo**

- **Parámetros de ruta:**
  - `user_id` (string): ID del usuario
  - `fund_id` (string): ID del fondo de inversión
  
- **Body (JSON):**
  ```json
  {
    "amount": 100000,
    "notification_channel": "email"
  }
  ```

- **Respuesta:** Objeto de suscripción creada

#### `DELETE /user/{user_id}/subscribe/{fund_id}`
**Cancelar suscripción a un fondo**

- **Parámetros de ruta:**
  - `user_id` (string): ID del usuario
  - `fund_id` (string): ID del fondo de inversión

- **Respuesta:** Confirmación de cancelación

### Transacciones

#### `GET /transactions`
**Obtener historial completo de transacciones**

- **Respuesta:** Lista de todas las transacciones del sistema

#### `GET /user/{user_id}/transactions`
**Obtener transacciones de un usuario específico**

- **Parámetros de ruta:**
  - `user_id` (string): ID del usuario

- **Respuesta:** Lista de transacciones del usuario

### Documentación Automática

- **`GET /docs`** - Swagger UI (interfaz interactiva)
- **`GET /redoc`** - ReDoc (documentación alternativa)

## 📋 Ejemplos de Uso

### Desarrollo Local (SAM)

```bash
# Crear usuario (ID auto-generado)
curl -X POST "http://localhost:3000/user/create" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "María García",
       "email": "maria@example.com",
       "phone": "+573001234567",
       "balance": 200000,
       "notify_channel": "email"
     }'

# Obtener todas las transacciones
curl http://localhost:3000/transactions

# Obtener transacciones de un usuario
curl http://localhost:3000/user/u001/transactions

# Crear suscripción
curl -X POST "http://localhost:3000/user/u001/subscribe/f001" \
     -H "Content-Type: application/json" \
     -d '{
       "amount": 100000,
       "notification_channel": "email"
     }'

# Cancelar suscripción
curl -X DELETE "http://localhost:3000/user/u001/subscribe/f001"
```

### AWS Lambda (Producción)

```bash
# Base URL: https://YOUR_API_GATEWAY_URL/Prod

# Crear usuario
curl -X POST "https://jbl7qzhgni.execute-api.us-east-1.amazonaws.com/Prod/user/create" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Carlos López",
       "email": "carlos@example.com",
       "phone": "+573009876543",
       "balance": 150000,
       "notify_channel": "sms"
     }'

# Obtener todas las transacciones
curl https://jbl7qzhgni.execute-api.us-east-1.amazonaws.com/Prod/transactions

# Obtener transacciones de un usuario
curl https://jbl7qzhgni.execute-api.us-east-1.amazonaws.com/Prod/user/u001/transactions

# Crear suscripción
curl -X POST "https://jbl7qzhgni.execute-api.us-east-1.amazonaws.com/Prod/user/u001/subscribe/f001" \
     -H "Content-Type: application/json" \
     -d '{
       "amount": 100000,
       "notification_channel": "email"
     }'
```

## 💼 Reglas de Negocio

1. **User ID automático**: Se genera automáticamente con formato `u{timestamp}{random}`
2. **Balance inicial**: Definido por el usuario al crear cuenta
3. **Monto mínimo**: Cada fondo tiene su monto mínimo de vinculación
4. **Identificadores únicos**: Cada transacción tiene ID basado en timestamp
5. **Cancelación**: El valor se devuelve al usuario al cancelar
6. **Validación de saldo**: Mensaje específico cuando no hay suficiente saldo
7. **Validación 400**: Errores de negocio retornan código 400 en lugar de 500

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

### Con SAM (Serverless Application Model)

```bash
# Construir aplicación
sam build

# Desplegar a AWS
sam deploy --guided  # Primera vez
sam deploy          # Despliegues posteriores

# Ver logs en tiempo real
sam logs -n API --tail
```

### Para AWS Lambda

El proyecto usa SAM con soporte Lambda integrado:

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