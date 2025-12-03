# 🚖 Sistema de Gestión de Mototaxis - Supatá, Cundinamarca

![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite)

## 📖 Descripción

Sistema web completo para la gestión de servicios de mototaxi en Supatá, Cundinamarca. Permite administrar usuarios, conductores, vehículos y viajes con estadísticas en tiempo real.

**URL Desplegada:** [Agregar URL cuando esté desplegado]

**Repositorio:** [https://github.com/TU_USUARIO/mototaxi-supata](https://github.com/TU_USUARIO/mototaxi-supata)

---

## 🎯 Características Principales

- ✅ **CRUD Completo** para 4 modelos relacionados
- ✅ **Dashboard con gráficas** interactivas (Chart.js)
- ✅ **Sistema de autenticación** con contraseñas hasheadas
- ✅ **Búsqueda global** en tiempo real
- ✅ **Subida de imágenes** para usuarios, conductores y vehículos
- ✅ **Soft delete** para mantener histórico
- ✅ **Validaciones** en frontend y backend
- ✅ **Datos mock realistas** de Supatá
- ✅ **API REST documentada** con Swagger

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Modelos (Relaciones)

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   Usuario   │       │  Conductor   │       │  Vehículo   │
├─────────────┤       ├──────────────┤       ├─────────────┤
│ id          │       │ id           │       │ id          │
│ nombre      │       │ nombre       │       │ placa       │
│ telefono    │       │ licencia     │       │ modelo      │
│ foto_path   │       │ foto_path    │       │ foto_path   │
│ password_hash│      │ activo       │       │ activo      │
│ activo      │       └──────────────┘       └─────────────┘
└─────────────┘              │                      │
       │                     │                      │
       │                     └──────────┬───────────┘
       │                                │
       │                         ┌──────▼──────┐
       └────────────────────────►│    Viaje    │
                                 ├─────────────┤
                                 │ id          │
                                 │ usuario_id  │◄────FK
                                 │ conductor_id│◄────FK
                                 │ vehiculo_id │◄────FK
                                 │ origen      │
                                 │ destino     │
                                 │ precio      │
                                 │ fecha       │
                                 │ estado      │
                                 │ activo      │
                                 └─────────────┘
```

### Estructura de Carpetas

```
backend/
├── app/
│   ├── static/
│   │   ├── style.css
│   │   └── uploads/          # Imágenes subidas
│   └── templates/
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── usuarios.html
│       ├── conductores.html
│       ├── vehiculos.html
│       └── buscar.html
├── routers/                  # Endpoints organizados
├── tests/                    # Tests unitarios
├── main.py                   # Aplicación principal
├── models.py                 # Modelos SQLAlchemy
├── schemas.py                # Schemas Pydantic
├── crud.py                   # Operaciones BD
├── database.py               # Configuración BD
├── generar_datos_mock.py     # Genera datos de prueba
├── requirements.txt
└── README.md
```

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes)

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/TU_USUARIO/mototaxi-supata.git
cd mototaxi-supata/backend
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Generar datos de prueba** (opcional)
```bash
python generar_datos_mock.py
```

4. **Ejecutar el servidor**
```bash
uvicorn main:app --reload --port 8000
```

5. **Acceder a la aplicación**
- Frontend: `http://127.0.0.1:8000/`
- API Docs: `http://127.0.0.1:8000/docs`
- Dashboard: `http://127.0.0.1:8000/dashboard`

---

## 📊 Endpoints de la API

### 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Página de login |
| POST | `/login` | Autenticar usuario |
| GET | `/register` | Página de registro |
| POST | `/register` | Registrar nuevo usuario |

### 👥 Usuarios

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/usuarios/` | Listar todos los usuarios |
| POST | `/api/usuarios/` | Crear usuario |
| GET | `/api/usuarios/estado/{activo}` | Filtrar por estado |
| GET | `/api/usuarios/buscar/{nombre}` | Buscar por nombre |
| PATCH | `/api/usuarios/{id}/inactivar` | Inactivar usuario |
| DELETE | `/api/usuarios/{id}` | Eliminar usuario |

### 🏍️ Conductores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/conductores/` | Listar conductores |
| POST | `/api/conductores/` | Crear conductor |
| GET | `/api/conductores/estado/{activo}` | Filtrar por estado |
| PATCH | `/api/conductores/{id}/inactivar` | Inactivar |
| DELETE | `/api/conductores/{id}` | Eliminar |

### 🚗 Vehículos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/vehiculos/` | Listar vehículos |
| POST | `/api/vehiculos/` | Crear vehículo |
| GET | `/api/vehiculos/estado/{activo}` | Filtrar por estado |
| GET | `/api/vehiculos/buscar/{placa}` | Buscar por placa |
| PATCH | `/api/vehiculos/{id}/inactivar` | Inactivar |
| DELETE | `/api/vehiculos/{id}` | Eliminar |

### 🚖 Viajes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/viajes/` | Listar viajes |
| POST | `/api/viajes/` | Crear viaje |
| DELETE | `/api/viajes/{id}` | Eliminar viaje |

### 📸 Multimedia

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/upload/usuario/{id}` | Subir foto de usuario |
| POST | `/api/upload/conductor/{id}` | Subir foto de conductor |
| POST | `/api/upload/vehiculo/{id}` | Subir foto de vehículo |

### 🔍 Búsqueda

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/buscar` | Página de búsqueda |
| GET | `/api/buscar?q={query}` | Búsqueda global |

---

## 💾 Modelos de Datos

### Usuario
```python
{
  "id": 1,
  "nombre": "Carlos Mendoza",
  "telefono": "3101234567",
  "foto_path": "/static/uploads/usuario_1.jpg",
  "activo": true
}
```

### Conductor
```python
{
  "id": 1,
  "nombre": "Roberto Gómez",
  "licencia": "C2-12345678",
  "foto_path": "/static/uploads/conductor_1.jpg",
  "activo": true
}
```

### Vehículo
```python
{
  "id": 1,
  "placa": "ABC123",
  "modelo": "Yamaha FZ 150",
  "foto_path": "/static/uploads/vehiculo_1.jpg",
  "activo": true
}
```

### Viaje
```python
{
  "id": 1,
  "usuario_id": 1,
  "conductor_id": 1,
  "vehiculo_id": 1,
  "origen": "Centro Supatá",
  "destino": "La Pradera",
  "precio": 5000.0,
  "fecha": "2024-11-30T14:30:00",
  "estado": "completado",
  "activo": true
}
```

---

## 🎨 Capturas de Pantalla

### Login
![Login](docs/images/login.png)

### Dashboard con Estadísticas
![Dashboard](docs/images/dashboard.png)

### Gestión de Conductores
![Conductores](docs/images/conductores.png)

### Búsqueda Global
![Búsqueda](docs/images/buscar.png)

---

## 🧪 Testing

Ejecutar tests unitarios:

```bash
pytest tests/test_crud.py -v
```

Cobertura:
- ✅ CRUD de usuarios
- ✅ CRUD de conductores
- ✅ CRUD de vehículos
- ✅ CRUD de viajes
- ✅ Soft delete
- ✅ Búsquedas

---

## 📈 Datos de Análisis

El sistema genera automáticamente estadísticas basadas en:

1. **Viajes completados vs cancelados** (últimos 30 días)
2. **Ingresos totales** por período
3. **Conductores más activos** (Top 5)
4. **Destinos más frecuentes** (Top 5)
5. **Tendencia de viajes** (últimos 7 días)

Estos datos se visualizan en el dashboard mediante gráficas de:
- Líneas (tendencias)
- Donas (estados)
- Barras horizontales/verticales (rankings)

---

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con **PBKDF2-SHA256**
- ✅ Validación de datos con **Pydantic**
- ✅ Validación de tipos de archivo en uploads
- ✅ Soft delete para mantener integridad referencial
- ✅ Sanitización de inputs

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** 0.104.1 - Framework web
- **SQLAlchemy** - ORM
- **Pydantic** - Validación de datos
- **Passlib** - Hash de contraseñas
- **SQLite** - Base de datos

### Frontend
- **Jinja2** - Templates HTML
- **Chart.js** - Gráficas interactivas
- **CSS3** - Estilos personalizados
- **JavaScript** - Interactividad

---

## 📦 Despliegue

### Render.com (Recomendado)

1. Crear cuenta en [render.com](https://render.com)
2. Conectar repositorio de GitHub
3. Configurar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy

### Railway.app

1. Crear cuenta en [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Seleccionar repositorio
4. Variables de entorno:
   - `PORT=8000`
5. Deploy

---

## 👨‍💻 Autor

**[Tu Nombre]**
- GitHub: [@tu_usuario](https://github.com/tu_usuario)
- Email: tu_email@ejemplo.com

---

## 📄 Licencia

Este proyecto es de código abierto bajo la licencia MIT.

---

## 🙏 Agradecimientos

Proyecto desarrollado como parte del curso de FastAPI.

**Institución:** [Nombre de tu institución]
**Curso:** Desarrollo Web con FastAPI
**Año:** 2024

---

## 📞 Soporte

Para reportar bugs o solicitar características:
- Abrir un [Issue en GitHub](https://github.com/TU_USUARIO/mototaxi-supata/issues)
- Contactar por email

---

**¡Gracias por usar el Sistema de Gestión de Mototaxis Supatá! 🚖**
