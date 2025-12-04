#  Sistema de Gestión de Mototaxis - Supatá, Cundinamarca

##  Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características-principales)
- [Tecnologías](#-tecnologías-utilizadas)
- [Arquitectura](#-arquitectura-del-sistema)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [API REST](#-api-rest)
- [Base de Datos](#-base-de-datos)
- [Validaciones](#-validaciones-y-reglas-de-negocio)
- [Despliegue](#-despliegue)



##  Descripción

Sistema web integral desarrollado con **FastAPI** (Python) para la administración eficiente de servicios de mototaxi en Supatá, Cundinamarca. Permite gestionar usuarios, conductores, vehículos y viajes con un dashboard interactivo y estadísticas en tiempo real.

###  Problema que Resuelve

El transporte en mototaxi en Supatá carece de un sistema centralizado para:
- Registro y seguimiento de conductores y vehículos
- Trazabilidad de viajes y tarifas
- Control de disponibilidad de conductores
- Estadísticas para toma de decisiones

###  Solución Implementada

Sistema web responsive con gestión completa de:
- ✅ **Usuarios** - Registro con foto de perfil
- ✅ **Conductores** - Gestión con licencias y vehículos asignados
- ✅ **Vehículos** - Registro con placas y fotos
- ✅ **Viajes** - Seguimiento de estados y tarifas
- ✅ **Dashboard** - Estadísticas en tiempo real con gráficas
- ✅ **Búsqueda Global** - Búsqueda en tiempo real en toda la aplicación
- ✅ **Reportes** - Generación de estadísticas y análisis de datos

---

##  Características Principales

###  Dashboard Interactivo
- Gráficas de viajes por día (Chart.js)
- Estados de viajes (Completados, En curso, Cancelados)
- Estadísticas de ingresos totales
- Contadores de usuarios, conductores y vehículos activos
- Vista en tabs de todas las entidades activas

###  Gestión de Datos
- **CRUD Completo** para 4 modelos relacionados
- **Subida de imágenes** para usuarios, conductores y vehículos (máx 5MB)
- **Soft delete** para mantener histórico
- **Validaciones robustas** en frontend (HTML5) y backend (Pydantic)

###  Búsqueda y Navegación
- **Búsqueda global** en navbar con resultados en tiempo real
- Búsqueda por nombre, teléfono y placa
- Filtros por estado (Activo/Inactivo)
- Navegación intuitiva con menús consistentes

###  Reportes y Estadísticas
- Gráfica de viajes por día (últimos 7 días)
- Distribución de estados de viajes (Doughnut chart)
- Total de viajes e ingresos
- Análisis de conductores y vehículos disponibles
- Gestión de entidades activas/inactivas

---

##  Tecnologías Utilizadas

### Backend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| **FastAPI** | 0.104.1 | Framework web REST API |
| **Python** | 3.10+ | Lenguaje de programación |
| **SQLAlchemy** | 2.0+ | ORM para base de datos |
| **Pydantic** | 2.0+ | Validación de datos |
| **PostgreSQL** | 14+ | Base de datos relacional |
| **Passlib** | 1.7+ | Hash de contraseñas |

### Frontend
| Tecnología | Uso |
|------------|-----|
| **HTML5** | Estructura semántica |
| **CSS3** | Estilos, gradientes, animaciones |
| **Jinja2** | Templates del lado del servidor |
| **Chart.js** | Gráficas interactivas |

### Infraestructura
- **Clever Cloud** - Hosting de PostgreSQL
- **Render.com** - Despliegue de aplicación web
- **Git/GitHub** - Control de versiones

---



### Estructura de Carpetas

```
mototaxi-supata/
│
├── app/
│   ├── static/
│   │   └── uploads/              # Imágenes subidas (usuarios, conductores, vehículos)
│   │
│   └── templates/
│       ├── inicio.html           # Página de inicio
│       ├── dashboard.html        # Dashboard con estadísticas
│       ├── Usuarios.html         # Formulario crear usuario
│       ├── lista_usuarios.html   # Lista completa de usuarios
│       ├── conductores.html      # Gestión de conductores
│       ├── vehiculos.html        # Gestión de vehículos
│       ├── viajes.html           # Gestión de viajes
│       ├── buscar.html           # Búsqueda global
│       └── inactivos.html        # Gestión de inactivos
│
├── main.py                       # Aplicación FastAPI principal
├── models.py                     # Modelos SQLAlchemy
├── schemas.py                    # Schemas Pydantic (validación)
├── crud.py                       # Operaciones CRUD
├── business_rules.py             # Reglas de negocio
├── database.py                   # Configuración PostgreSQL
├── inicializar_bd.py             # Script de inicialización de BD
├── limpiar_bd.py                 # Script para limpiar datos
├── requirements.txt              # Dependencias Python
└── README.md                     # Este archivo
```

---

## 💻 Instalación

### Requisitos Previos

- Python 3.10 o superior
- PostgreSQL 14+ (o cuenta en Clever Cloud)
- Git

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/jonathan-mototaxi/mototaxi-supata.git
cd mototaxi-supata
```

### Paso 2: Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Base de Datos

Edita `database.py` con tus credenciales de PostgreSQL:

```python
DATABASE_URL = "postgresql://usuario:contraseña@host:puerto/basedatos"
```

### Paso 5: Inicializar Base de Datos

```bash
python inicializar_bd.py
```

### Paso 6: Generar Datos de Prueba (Opcional)

```bash
python generar_datos_mock.py
```

---

##  Uso

### Iniciar el Servidor

```bash
uvicorn main:app --reload 
```

### Acceder a la Aplicación

| Recurso | URL | Descripción |
|---------|-----|-------------|
| **Inicio** | http://127.0.0.1:8000/ | Página principal |
| **Dashboard** | http://127.0.0.1:8000/dashboard | Estadísticas y gráficas |
| **Crear Usuario** | http://127.0.0.1:8000/usuarios | Formulario con foto |
| **Lista Usuarios** | http://127.0.0.1:8000/lista-usuarios | Todos los usuarios |
| **Conductores** | http://127.0.0.1:8000/conductores | Gestión de conductores |
| **Vehículos** | http://127.0.0.1:8000/vehiculos | Gestión de vehículos |
| **Viajes** | http://127.0.0.1:8000/viajes | Gestión de viajes |
| **Búsqueda** | http://127.0.0.1:8000/buscar | Búsqueda global |
| **Inactivos** | http://127.0.0.1:8000/inactivos | Gestión de inactivos |
| **API Docs** | http://127.0.0.1:8000/docs | Documentación Swagger |

### Flujo de Trabajo

1. **Crear Usuario** → Subir foto de perfil obligatoria
2. **Crear Conductor** → Opcionalmente crear vehículo asignado
3. **Crear Vehículo** → Asignar a conductor existente
4. **Crear Viaje** → Seleccionar usuario, conductor y vehículo disponibles
5. **Ver Estadísticas** → Dashboard con gráficas y contadores
6. **Gestionar Inactivos** → Reactivar o eliminar entidades

---

## 📡 API REST

### Endpoints Principales

####  Usuarios

```http
GET    /api/usuarios/                    # Listar todos
POST   /api/usuarios/                    # Crear usuario
GET    /api/usuarios/estado/{activo}     # Filtrar por estado
GET    /api/usuarios/buscar/{nombre}     # Buscar por nombre
PATCH  /api/usuarios/{id}/inactivar      # Inactivar
PATCH  /api/usuarios/{id}/reactivar      # Reactivar
DELETE /api/usuarios/{id}                # Eliminar permanentemente
```

####  Conductores

```http
GET    /api/conductores/                 # Listar todos
POST   /api/conductores/                 # Crear conductor + vehículo
GET    /api/conductores/{id}/estado      # Ver estado (libre/ocupado)
GET    /api/conductores/estado/{activo}  # Filtrar por estado
PATCH  /api/conductores/{id}/inactivar   # Inactivar
PATCH  /api/conductores/{id}/activar     # Reactivar
DELETE /api/conductores/{id}             # Eliminar permanentemente
```

####  Vehículos

```http
GET    /api/vehiculos/                   # Listar todos
POST   /api/vehiculos/                   # Crear vehículo
GET    /api/vehiculos/conductor/{id}     # Vehículos de un conductor
GET    /api/vehiculos/buscar/{placa}     # Buscar por placa
GET    /api/vehiculos/estado/{activo}    # Filtrar por estado
PATCH  /api/vehiculos/{id}/inactivar     # Inactivar
PATCH  /api/vehiculos/{id}/activar       # Reactivar
DELETE /api/vehiculos/{id}               # Eliminar permanentemente
```

####  Viajes

```http
GET    /api/viajes/                      # Listar todos
POST   /api/viajes/                      # Crear viaje
PATCH  /api/viajes/{id}/completar        # Completar viaje
PATCH  /api/viajes/{id}/cancelar         # Cancelar viaje
PATCH  /api/viajes/{id}/estado           # Actualizar estado
GET    /api/viajes/conductor/{id}/activos # Viajes activos de conductor
DELETE /api/viajes/{id}                  # Eliminar viaje
```

####  Uploads

```http
POST   /api/upload/usuario/{id}         # Subir foto de usuario
POST   /api/upload/conductor/{id}       # Subir foto de conductor
POST   /api/upload/vehiculo/{id}        # Subir foto de vehículo
```

####  Búsqueda

```http
GET    /api/buscar?q={query}            # Búsqueda global
```

---

## 💾 Base de Datos

### Configuración PostgreSQL (Clever Cloud)

El sistema utiliza PostgreSQL alojado en Clever Cloud con las siguientes características:

- **Motor**: PostgreSQL 14
- **SSL**: Requerido para conexiones seguras
- **Conexiones**: Pool de conexiones con SQLAlchemy
- **Migraciones**: Automáticas con SQLAlchemy

