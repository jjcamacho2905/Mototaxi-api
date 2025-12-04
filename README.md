# 🚖 Sistema de Gestión de Mototaxis - Supatá, Cundinamarca

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?style=for-the-badge&logo=postgresql)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

**Sistema web completo para la gestión de servicios de mototaxi en Supatá, Cundinamarca**

🌐 **[Demo en Vivo](https://tu-app.render.com)** • 📚 **[Documentación API](https://tu-app.render.com/docs)**

</div>

---

## 📋 Tabla de Contenidos

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
- [Autor](#-autor)
- [Licencia](#-licencia)

---

## 📖 Descripción

Sistema web integral desarrollado con **FastAPI** (Python) para la administración eficiente de servicios de mototaxi en Supatá, Cundinamarca. Permite gestionar usuarios, conductores, vehículos y viajes con un dashboard interactivo y estadísticas en tiempo real.

### 🎯 Problema que Resuelve

El transporte en mototaxi en Supatá carece de un sistema centralizado para:
- Registro y seguimiento de conductores y vehículos
- Trazabilidad de viajes y tarifas
- Control de disponibilidad de conductores
- Estadísticas para toma de decisiones

### ✨ Solución Implementada

Sistema web responsive con gestión completa de:
- ✅ **Usuarios** - Registro con foto de perfil
- ✅ **Conductores** - Gestión con licencias y vehículos asignados
- ✅ **Vehículos** - Registro con placas y fotos
- ✅ **Viajes** - Seguimiento de estados y tarifas
- ✅ **Dashboard** - Estadísticas en tiempo real con gráficas
- ✅ **Búsqueda Global** - Búsqueda en tiempo real en toda la aplicación

---

## 🚀 Características Principales

### 📊 Dashboard Interactivo
- Gráficas de viajes por día (Chart.js)
- Estados de viajes (Completados, En curso, Cancelados)
- Estadísticas de ingresos totales
- Contadores de usuarios y conductores activos
- Vista previa de usuarios registrados

### 🔐 Gestión de Datos
- **CRUD Completo** para 4 modelos relacionados
- **Subida de imágenes** para usuarios, conductores y vehículos (máx 5MB)
- **Soft delete** para mantener histórico
- **Validaciones robustas** en frontend (HTML5) y backend (Pydantic)

### 🔍 Búsqueda y Navegación
- **Búsqueda global** en navbar con resultados en tiempo real
- Búsqueda por nombre, teléfono y placa
- Filtros por estado (Activo/Inactivo)
- Navegación intuitiva con menús consistentes

### 📈 Reportes y Estadísticas
- Gráfica de viajes por día (últimos 7 días)
- Distribución de estados de viajes (Doughnut chart)
- Total de viajes e ingresos
- Listado de todos los usuarios con fotos

### 🎨 Diseño y Estilado
- **Diseño responsive** adaptable a móviles y tablets
- **Estilos CSS3 personalizados** con gradientes y animaciones
- **Efectos hover** y transiciones suaves
- **Paleta de colores** moderna (#667eea, #764ba2)

---

## 🛠️ Tecnologías Utilizadas

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
| **JavaScript** | Interactividad y AJAX |
| **Jinja2** | Templates del lado del servidor |
| **Chart.js** | Gráficas interactivas |

### Infraestructura
- **Clever Cloud** - Hosting de PostgreSQL
- **Render.com** - Despliegue de aplicación web
- **Git/GitHub** - Control de versiones

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Modelos

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│    Usuario      │       │    Conductor     │       │    Vehículo     │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ • id (PK)       │       │ • id (PK)        │       │ • id (PK)       │
│ • nombre        │       │ • nombre (UNIQUE)│       │ • placa         │
│ • telefono      │       │ • licencia       │       │ • modelo        │
│ • foto_path     │       │ • foto_path      │       │ • foto_path     │
│ • password_hash │       │ • activo         │◄──────┤ • conductor_id  │
│ • activo        │       └──────────────────┘       │ • activo        │
└─────────────────┘                │                 └─────────────────┘
         │                         │                          │
         │                         │                          │
         │                         └──────────┬───────────────┘
         │                                    │
         │                             ┌──────▼──────────┐
         └────────────────────────────►│     Viaje       │
                                       ├─────────────────┤
                                       │ • id (PK)       │
                                       │ • usuario_id FK │
                                       │ • conductor_id FK│
                                       │ • vehiculo_id FK│
                                       │ • origen        │
                                       │ • destino       │
                                       │ • precio        │
                                       │ • fecha         │
                                       │ • estado        │
                                       │ • activo        │
                                       └─────────────────┘
```

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
│       └── buscar.html           # Búsqueda global
│
├── main.py                       # Aplicación FastAPI principal
├── models.py                     # Modelos SQLAlchemy
├── schemas.py                    # Schemas Pydantic (validación)
├── crud.py                       # Operaciones CRUD
├── business_rules.py             # Reglas de negocio
├── database.py                   # Configuración PostgreSQL
├── generar_datos_mock.py         # Generador de datos de prueba
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
git clone https://github.com/tu-usuario/mototaxi-supata.git
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

## 🎮 Uso

### Iniciar el Servidor

```bash
uvicorn main:app --reload --port 8000
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
| **API Docs** | http://127.0.0.1:8000/docs | Documentación Swagger |

### Flujo de Trabajo

1. **Crear Usuario** → Subir foto de perfil
2. **Crear Conductor** → Opcionalmente crear vehículo asignado
3. **Crear Vehículo** → Asignar a conductor
4. **Crear Viaje** → Seleccionar usuario, conductor y vehículo
5. **Ver Estadísticas** → Dashboard con gráficas

---

## 📡 API REST

### Endpoints Principales

#### 👥 Usuarios

```http
GET    /api/usuarios/                    # Listar todos
POST   /api/usuarios/                    # Crear usuario
GET    /api/usuarios/estado/{activo}     # Filtrar por estado
GET    /api/usuarios/buscar/{nombre}     # Buscar por nombre
PATCH  /api/usuarios/{id}/inactivar      # Inactivar
DELETE /api/usuarios/{id}                # Eliminar
```

#### 🏍️ Conductores

```http
GET    /api/conductores/                 # Listar todos
POST   /api/conductores/                 # Crear conductor + vehículo
GET    /api/conductores/{id}/estado      # Ver estado (libre/ocupado)
GET    /api/conductores/estado/{activo}  # Filtrar por estado
DELETE /api/conductores/{id}             # Eliminar
```

#### 🚗 Vehículos

```http
GET    /api/vehiculos/                   # Listar todos
POST   /api/vehiculos/                   # Crear vehículo
GET    /api/vehiculos/conductor/{id}     # Vehículos de un conductor
GET    /api/vehiculos/buscar/{placa}     # Buscar por placa
DELETE /api/vehiculos/{id}               # Eliminar
```

#### 🚖 Viajes

```http
GET    /api/viajes/                      # Listar todos
POST   /api/viajes/                      # Crear viaje
PATCH  /api/viajes/{id}/completar        # Completar viaje
PATCH  /api/viajes/{id}/cancelar         # Cancelar viaje
DELETE /api/viajes/{id}                  # Eliminar
```

#### 📸 Uploads

```http
POST   /api/upload/usuario/{id}         # Subir foto de usuario
POST   /api/upload/conductor/{id}       # Subir foto de conductor
POST   /api/upload/vehiculo/{id}        # Subir foto de vehículo
```

#### 🔍 Búsqueda

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

### Modelos de Datos

#### Usuario
```python
{
  "id": 1,
  "nombre": "Carlos Mendoza",
  "telefono": "3101234567",
  "foto_path": "/static/uploads/usuario_abc123.jpg",
  "activo": true
}
```

#### Conductor
```python
{
  "id": 1,
  "nombre": "Roberto Gómez",
  "licencia": "123456",
  "foto_path": "/static/uploads/conductor_xyz789.jpg",
  "activo": true
}
```

#### Vehículo
```python
{
  "id": 1,
  "placa": "ABC123",
  "modelo": "Yamaha FZ 150",
  "conductor_id": 1,
  "foto_path": "/static/uploads/vehiculo_def456.jpg",
  "activo": true
}
```

#### Viaje
```python
{
  "id": 1,
  "usuario_id": 1,
  "conductor_id": 1,
  "vehiculo_id": 1,
  "origen": "Centro Supatá",
  "destino": "Vereda La Palma",
  "precio": 8000.0,
  "fecha": "2024-12-04T14:30:00",
  "estado": "completado",
  "activo": true
}
```

---

## ✅ Validaciones y Reglas de Negocio

### Validaciones Frontend (HTML5 + JavaScript)

- **Nombres**: Mínimo 3 caracteres, solo letras
- **Teléfonos**: 7-15 dígitos numéricos
- **Placas**: Formato ABC123 (6 caracteres)
- **Imágenes**: Máximo 5MB, solo JPG/PNG/GIF
- **Precios**: Entre $1,000 y $500,000 COP

### Validaciones Backend (Pydantic + Business Rules)

```python
# Archivo: business_rules.py

✅ Usuarios
  - Nombre único en el sistema
  - Teléfono de 7-15 dígitos
  - No puede tener más de 2 viajes activos

✅ Conductores
  - Nombre único
  - Licencia de 1-6 caracteres (opcional)
  - No puede tener más de 1 viaje activo simultáneamente
  
✅ Vehículos
  - Placa única en formato ABC123
  - Debe estar asignado a un conductor activo
  - No puede estar en 2 viajes activos simultáneamente

✅ Viajes
  - Origen y destino diferentes
  - Precio entre $1,000 y $500,000
  - Estados válidos: pendiente → en_curso → completado/cancelado
  - Conductor y vehículo deben estar disponibles
```

### Estados de Viaje

```
pendiente → en_curso → completado
    ↓           ↓
cancelado   cancelado
```

---

## 🚀 Despliegue

### Opción 1: Render.com (Recomendado)

1. Crear cuenta en [render.com](https://render.com)
2. Conectar repositorio de GitHub
3. Configurar Web Service:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
4. Agregar PostgreSQL desde Clever Cloud
5. Configurar variable `DATABASE_URL`
6. Deploy automático

### Opción 2: Railway.app

1. Conectar repositorio en [railway.app](https://railway.app)
2. Agregar PostgreSQL addon
3. Variables de entorno se configuran automáticamente
4. Deploy

### Variables de Entorno

```env
DATABASE_URL=ufrqizsynh7hw1lwkypl:TDIEkb5nDrOF8Ow4SVacVAicm8bjb8@bcjwxq3t9ckvbf5r82mu-postgresql.services.clever-cloud.com:50013/bcjwxq3t9ckvbf5r82mu
```

---


---

## 👨‍💻 Autor

**Jonathan - Mototaxi Supatá**

- 📧 Email: camachogomezjonathanjesus@gmail.com
- 🐙 GitHub: [@jonathan-mototaxi](https://github.com/jonathan-mototaxi)

---


## 🙏 Agradecimientos

- **FastAPI** - Por el increíble framework
- **Clever Cloud** - Por el hosting de PostgreSQL
- **Chart.js** - Por las gráficas interactivas
- **Comunidad de Supatá** - Por el apoyo y feedback

---

## 📞 Soporte

¿Necesitas ayuda?

- 📧 Email: soporte@mototaxisupata.com
- 💬 Issues: [GitHub Issues](https://github.com/tu-usuario/mototaxi-supata/issues)

---

<div align="center">

**⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub ⭐**

---

Hecho con ❤️ en Supatá, Cundinamarca 🇨🇴

**Universidad Nacional de Colombia**  
Facultad de Ingeniería  
Curso: Desarrollo Web  
Año: 2025

</div>