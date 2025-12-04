# 🚖 Sistema de Gestión de Mototaxis - Supatá, Cundinamarca

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?style=for-the-badge&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Sistema web completo para la gestión de servicios de mototaxi en Supatá, Cundinamarca**

[Demo en Vivo](#) • [Documentación API](#api-rest) • [Reportar Bug](#)

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
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Reglas de Negocio](#-reglas-de-negocio)
- [Testing](#-testing)
- [Despliegue](#-despliegue)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

---

## 📖 Descripción

Sistema web integral desarrollado con **FastAPI** para la administración eficiente de servicios de mototaxi en Supatá, Cundinamarca. Permite gestionar usuarios, conductores, vehículos y viajes con un dashboard interactivo y estadísticas en tiempo real.

### 🎯 Problema que Resuelve

- **Gestión manual ineficiente** de servicios de transporte
- **Falta de trazabilidad** en viajes y conductores
- **Dificultad para calcular tarifas** justas
- **Ausencia de estadísticas** para toma de decisiones

### ✨ Solución

Sistema centralizado que automatiza la gestión completa de servicios de mototaxi, desde la creación de usuarios hasta el seguimiento de viajes con análisis de datos históricos.

---

## 🚀 Características Principales

### Gestión Completa
- ✅ **CRUD completo** para 4 modelos relacionados (Usuarios, Conductores, Vehículos, Viajes)
- ✅ **Sistema de estados** para viajes (Pendiente → En Curso → Completado/Cancelado)
- ✅ **Soft delete** para mantener histórico de datos
- ✅ **Validaciones robustas** en frontend y backend

### Funcionalidades Avanzadas
- 📊 **Dashboard interactivo** con gráficas (Chart.js)
- 🔍 **Búsqueda global** en tiempo real
- 📸 **Subida de imágenes** para usuarios, conductores y vehículos
- 📈 **Estadísticas y análisis** de datos históricos
- 🚦 **Control de disponibilidad** de conductores

### Seguridad y Validación
- 🔒 **Validación de datos** con Pydantic
- 🛡️ **Reglas de negocio** centralizadas
- ✅ **Integridad referencial** garantizada
- 📝 **Logs detallados** para debugging

---

## 🛠️ Tecnologías Utilizadas

### Backend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| **FastAPI** | 0.104.1 | Framework web principal |
| **SQLAlchemy** | 2.0+ | ORM para base de datos |
| **Pydantic** | 2.0+ | Validación de datos |
| **PostgreSQL** | 14+ | Base de datos |
| **Python** | 3.10+ | Lenguaje de programación |

### Frontend
| Tecnología | Uso |
|------------|-----|
| **Jinja2** | Templates HTML |
| **Chart.js** | Gráficas interactivas |
| **CSS3** | Estilos personalizados |


---

## 🏗️ Arquitectura del Sistema

### Diagrama de Modelos

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│    Usuario      │       │    Conductor     │       │    Vehículo     │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ • id (PK)       │       │ • id (PK)        │       │ • id (PK)       │
│ • nombre        │       │ • nombre (UNIQUE)│       │ • placa (UNIQUE)│
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
│   │   ├── style.css
│   │   └── uploads/              # Imágenes subidas
│   │
│   └── templates/
│       ├── inicio.html           # Página de inicio
│       ├── dashboard.html        # Dashboard principal
│       ├── usuarios.html         # Gestión de usuarios
│       ├── conductores.html      # Gestión de conductores
│       ├── vehiculos.html        # Gestión de vehículos
│       ├── viajes.html           # Gestión de viajes
│       └── buscar.html           # Búsqueda global
│
├── tests/
│   └── test_crud.py              # Tests unitarios
│
├── main.py                       # Aplicación principal FastAPI
├── models.py                     # Modelos SQLAlchemy
├── schemas.py                    # Schemas Pydantic
├── crud.py                       # Operaciones de base de datos
├── business_rules.py             # Reglas de negocio
├── database.py                   # Configuración de BD
├── generar_datos_mock.py         # Generador de datos de prueba
├── requirements.txt              # Dependencias
└── README.md                     # Este archivo
```

---

## 💻 Instalación

### Requisitos Previos

- **Python 3.10+** instalado
- **PostgreSQL 14+** (o acceso a instancia cloud)
- **Git** para clonar el repositorio

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

### Paso 5: Crear Tablas

```bash
# Las tablas se crean automáticamente al iniciar
python main.py
```

### Paso 6: Generar Datos de Prueba (Opcional)

```bash
python generar_datos_mock.py
# Cuando pregunte, escribe 's' para limpiar la BD
```

---

## 🎮 Uso

### Iniciar el Servidor

```bash
uvicorn main:app --reload --port 8000
```

### Acceder a la Aplicación

| Recurso | URL |
|---------|-----|
| **Página de Inicio** | http://127.0.0.1:8000/ |
| **Dashboard** | http://127.0.0.1:8000/dashboard |
| **Documentación API** | http://127.0.0.1:8000/docs |
| **Redoc** | http://127.0.0.1:8000/redoc |

### Flujo de Trabajo Típico

1. **Crear Usuario** → `/usuarios`
2. **Crear Conductor** → `/conductores`
3. **Crear Vehículo y asignarlo** al conductor
4. **Crear Viaje** → `/viajes`
5. **Completar/Cancelar Viaje**
6. **Ver Estadísticas** → `/dashboard`

---

## 📡 API REST

### Autenticación

Actualmente no requiere autenticación (modo desarrollo).

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
POST   /api/conductores/                 # Crear conductor
GET    /api/conductores/{id}/estado      # Ver estado (libre/ocupado)
GET    /api/conductores/estado/{activo}  # Filtrar por estado
PATCH  /api/conductores/{id}/inactivar   # Inactivar
DELETE /api/conductores/{id}             # Eliminar
```

#### 🚗 Vehículos

```http
GET    /api/vehiculos/                   # Listar todos
POST   /api/vehiculos/                   # Crear vehículo
GET    /api/vehiculos/conductor/{id}     # Vehículos de un conductor
GET    /api/vehiculos/buscar/{placa}     # Buscar por placa
PATCH  /api/vehiculos/{id}/inactivar     # Inactivar
DELETE /api/vehiculos/{id}               # Eliminar
```

#### 🚖 Viajes

```http
GET    /api/viajes/                      # Listar todos
POST   /api/viajes/                      # Crear viaje
PATCH  /api/viajes/{id}/completar        # Marcar como completado
PATCH  /api/viajes/{id}/cancelar         # Cancelar viaje
PATCH  /api/viajes/{id}/estado           # Actualizar estado
GET    /api/viajes/conductor/{id}/activos # Viajes activos de conductor
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

### Ejemplos de Uso

#### Crear Usuario

```bash
curl -X POST "http://127.0.0.1:8000/api/usuarios/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Carlos Pérez",
    "telefono": "3101234567",
    "contrasena": "password123"
  }'
```

#### Crear Viaje

```bash
curl -X POST "http://127.0.0.1:8000/api/viajes/" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 1,
    "conductor_id": 2,
    "vehiculo_id": 3,
    "origen": "Centro Supatá",
    "destino": "Vereda La Palma",
    "precio": 8000,
    "estado": "en_curso"
  }'
```

---

## 📸 Capturas de Pantalla

### Dashboard Principal
![Dashboard](docs/images/dashboard.png)

### Gestión de Conductores
![Conductores](docs/images/conductores.png)

### Crear Viaje
![Viajes](docs/images/viajes.png)

---

## 📜 Reglas de Negocio

### Validaciones de Usuarios
- ✅ Nombre: 3-50 caracteres, solo letras y espacios
- ✅ Teléfono: 7-15 dígitos
- ✅ Contraseña: mínimo 4 caracteres (opcional en formulario HTML)

### Validaciones de Conductores
- ✅ Nombre: único, 3-50 caracteres
- ✅ Licencia: 1-6 caracteres (puede repetirse)
- ✅ No puede tener más de 1 viaje activo simultáneamente

### Validaciones de Vehículos
- ✅ Placa: formato ABC123 (única)
- ✅ Puede estar asignado a un conductor
- ✅ No puede usarse en 2 viajes activos simultáneamente

### Validaciones de Viajes
- ✅ Precio: entre $1,000 y $500,000 COP
- ✅ Origen y destino: mínimo 3 caracteres, no pueden ser iguales
- ✅ Estados válidos: pendiente → en_curso → completado/cancelado
- ✅ Usuario no puede tener más de 2 viajes activos

### Estados de Viaje

```
pendiente → en_curso → completado
    ↓           ↓
cancelado   cancelado
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/test_crud.py -v

# Con cobertura
pytest tests/test_crud.py --cov=. --cov-report=html
```

### Cobertura Actual

- ✅ CRUD de usuarios
- ✅ CRUD de conductores
- ✅ CRUD de vehículos
- ✅ CRUD de viajes
- ✅ Soft delete
- ✅ Búsquedas
- ✅ Validaciones

---

## 🚀 Despliegue

### Opción 1: Render.com (Recomendado)

1. Crear cuenta en [render.com](https://render.com)
2. Conectar repositorio de GitHub
3. Configurar Web Service:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Agregar PostgreSQL desde Add-ons
5. Deploy

### Opción 2: Railway.app

1. Crear cuenta en [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Agregar PostgreSQL
4. Variables de entorno se configuran automáticamente
5. Deploy

### Opción 3: Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Construir imagen
docker build -t mototaxi-supata .

# Ejecutar contenedor
docker run -p 8000:8000 mototaxi-supata
```

---

## 📊 Estadísticas del Proyecto

| Métrica | Valor |
|---------|-------|
| **Líneas de código** | ~3,500+ |
| **Endpoints API** | 30+ |
| **Modelos de datos** | 4 |
| **Tests unitarios** | 15+ |
| **Reglas de negocio** | 20+ |

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Sigue estos pasos:

1. **Fork** el proyecto
2. Crea una **rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add: Amazing Feature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. Abre un **Pull Request**

### Guía de Estilo

- Usa **type hints** en Python
- Documenta funciones con **docstrings**
- Sigue **PEP 8** para estilo de código
- Escribe **tests** para nuevas features

---

## 🐛 Reporte de Bugs

Si encuentras un bug, por favor:

1. Verifica que no esté ya reportado en [Issues](https://github.com/tu-usuario/mototaxi-supata/issues)
2. Crea un nuevo Issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots si aplica

---

## 📝 Roadmap

### ✅ Completado
- [x] CRUD completo de 4 modelos
- [x] Dashboard con estadísticas
- [x] Sistema de estados de viajes
- [x] Búsqueda global
- [x] Subida de imágenes
- [x] Validaciones robustas

### 🚧 En Progreso
- [ ] Sistema de autenticación completo
- [ ] Notificaciones en tiempo real
- [ ] App móvil (Flutter/React Native)

### 🔮 Futuro
- [ ] Sistema de pagos integrado
- [ ] Geolocalización GPS
- [ ] Chat conductor-usuario
- [ ] Reportes en PDF
- [ ] API pública con rate limiting

---

## 👨‍💻 Autor

**Jonathan - Mototaxi Supatá**

- GitHub: [@jonathan-mototaxi](https://github.com/jonathan-mototaxi)
- Email: contacto@mototaxisupata.com
- LinkedIn: [Tu Perfil](https://linkedin.com/in/tu-perfil)

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2025 Jonathan - Mototaxi Supatá

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Agradecimientos

- **FastAPI** - Por el increíble framework
- **Clever Cloud** - Por el hosting de PostgreSQL
- **Chart.js** - Por las gráficas interactivas
- **Comunidad de Supatá** - Por el apoyo y feedback

---

## 📞 Soporte

¿Necesitas ayuda? Contáctanos:

- 📧 Email: soporte@mototaxisupata.com
- 💬 Issues: [GitHub Issues](https://github.com/tu-usuario/mototaxi-supata/issues)
- 📱 WhatsApp: +57 300 123 4567

---

<div align="center">

**⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub ⭐**

[⬆ Volver arriba](#-sistema-de-gestión-de-mototaxis---supatá-cundinamarca)

---

Hecho con ❤️ en Supatá, Cundinamarca 🇨🇴

</div>