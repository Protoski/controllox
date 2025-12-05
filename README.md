# Sistema de Gestión de Gases Medicinales - MSPBS Paraguay

## 📋 Descripción

Sistema web responsivo desarrollado por la **DGGIES (Dirección General de Gestión de Información y Estadísticas de Salud)** para el **Ministerio de Salud y Bienestar Social de Paraguay (MSPBS)** que permite a hospitales y centros de salud reportar consumos de gases medicinales, generar reportes y estadísticas centralizadas.

## 🎯 Características Principales

### Para Hospitales
- ✅ Registro de consumos de gases medicinales
- 📊 Dashboard con estadísticas del hospital
- 📄 Generación de reportes en PDF
- 📈 Gráficos de consumo mensual
- 🔍 Filtros por fecha, gas y modo de suministro

### Para Administradores (MSPBS)
- 👥 Gestión de usuarios y hospitales
- 🏥 Gestión del catálogo de gases medicinales
- 📊 Dashboard global con estadísticas nacionales
- 📄 Reportes globales (PDF, Excel, CSV)
- 🔍 Top consumidores y análisis por gas
- 📝 Sistema de auditoría completo
- ⚠️ Sistema de alertas

### Características Técnicas
- 🔐 Autenticación JWT con roles (ADMIN, HOSPITAL_USER)
- 📱 Diseño responsive (móvil, tablet, desktop)
- 🚀 Keep-alive automático para Render.com
- 🗄️ Base de datos PostgreSQL
- 📧 Recuperación de contraseña por email
- 📄 Exportación múltiple (PDF, XLSX, CSV)

---

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.11+**
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para PostgreSQL
- **PostgreSQL** - Base de datos
- **JWT** - Autenticación
- **ReportLab** - Generación de PDFs
- **Pandas/OpenPyXL** - Exportación Excel

### Frontend
- **React 18** - Framework UI
- **Vite** - Build tool
- **Tailwind CSS** - Estilos
- **React Router** - Navegación
- **Recharts** - Gráficos
- **Axios** - HTTP client
- **Zustand** - State management

---

## 📁 Estructura del Proyecto

```
sistema-gases-mspbs/
├── backend/
│   ├── app/
│   │   ├── api/                 # Endpoints REST
│   │   │   ├── auth.py
│   │   │   ├── usuarios.py
│   │   │   ├── hospitales.py
│   │   │   ├── gases_consumos.py
│   │   │   ├── reportes.py
│   │   │   └── auditoria.py
│   │   ├── core/                # Configuración core
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/              # Modelos SQLAlchemy
│   │   │   └── models.py
│   │   ├── schemas/             # Schemas Pydantic
│   │   │   └── schemas.py
│   │   └── services/            # Servicios auxiliares
│   │       ├── pdf_service.py
│   │       ├── excel_service.py
│   │       ├── email_service.py
│   │       └── keep_alive_service.py
│   ├── scripts/
│   │   └── init_db.py          # Inicialización de DB
│   ├── static/
│   │   ├── logos/
│   │   └── reports/
│   ├── main.py                 # App principal
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/         # Componentes React
│   │   │   ├── admin/
│   │   │   ├── hospital/
│   │   │   ├── shared/
│   │   │   └── auth/
│   │   ├── pages/              # Páginas principales
│   │   ├── services/           # API services
│   │   ├── context/            # Context providers
│   │   └── styles/
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── docs/                       # Documentación adicional
├── render.yaml                 # Configuración Render
└── README.md                   # Este archivo
```

---

## 🚀 Instalación Local

### Prerrequisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/sistema-gases-mspbs.git
cd sistema-gases-mspbs
```

### 2. Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar archivo de variables de entorno
cp .env.example .env

# Editar .env con tus configuraciones
nano .env
```

#### Configuración .env mínima:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/gases_mspbs
SECRET_KEY=genera-una-clave-segura-aqui
BACKEND_CORS_ORIGINS=http://localhost:3000
```

#### Inicializar Base de Datos:
```bash
# Crear base de datos en PostgreSQL
createdb gases_mspbs

# Ejecutar script de inicialización
python scripts/init_db.py
```

Este script creará:
- ✅ Usuario admin: `admin@mspbs.gov.py` / `admin123`
- ✅ Catálogo de gases medicinales
- ✅ Hospitales de ejemplo
- ✅ Configuraciones iniciales

#### Ejecutar Backend:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend disponible en: `http://localhost:8000`
Documentación API: `http://localhost:8000/docs`

### 3. Configurar Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install

# Copiar variables de entorno
cp .env.example .env

# Editar .env
echo "VITE_API_URL=http://localhost:8000" > .env

# Ejecutar en desarrollo
npm run dev
```

Frontend disponible en: `http://localhost:3000`

---

## 🌐 Despliegue en Render.com

### Opción 1: Despliegue Automático con render.yaml

1. **Fork o Push a GitHub**
   ```bash
   git remote add origin https://github.com/tu-usuario/sistema-gases-mspbs.git
   git push -u origin main
   ```

2. **Conectar con Render**
   - Ve a [render.com](https://render.com)
   - Crea una cuenta o inicia sesión
   - Clic en "New" → "Blueprint"
   - Conecta tu repositorio de GitHub
   - Render detectará automáticamente `render.yaml`
   - Configura las variables de entorno requeridas

3. **Variables de Entorno en Render**
   
   Para el **Backend**:
   ```
   SECRET_KEY=genera-clave-segura-con-openssl-rand-hex-32
   KEEP_ALIVE_URL=https://tu-backend.onrender.com
   BACKEND_CORS_ORIGINS=https://tu-frontend.onrender.com
   ```

   Para el **Frontend**:
   ```
   VITE_API_URL=https://tu-backend.onrender.com
   ```

### Opción 2: Despliegue Manual

#### Backend:
1. New → Web Service
2. Conectar repositorio
3. Configurar:
   - **Name**: `gases-mspbs-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`

#### Base de Datos:
1. New → PostgreSQL
2. Configurar:
   - **Name**: `gases-mspbs-db`
   - **Plan**: Free
3. Copiar la DATABASE_URL a las variables del backend

#### Frontend:
1. New → Static Site
2. Conectar repositorio
3. Configurar:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

### Inicialización Post-Despliegue

Una vez desplegado el backend:

1. **Acceder a Shell de Render**
   - En el dashboard del backend → "Shell"
   
2. **Ejecutar inicialización**
   ```bash
   python scripts/init_db.py
   ```

---

## 🔐 Credenciales Iniciales

### Usuario Administrador
- **Email**: admin@mspbs.gov.py
- **Password**: admin123

⚠️ **IMPORTANTE**: Cambiar contraseña inmediatamente en producción

---

## 📊 Uso del Sistema

### Para Hospitales

1. **Login**
   - Usar credenciales proporcionadas por ADMIN
   
2. **Dashboard**
   - Ver estadísticas de consumo
   - Gráficos mensuales
   
3. **Registrar Consumo**
   - Ir a "Consumos" → "Nuevo Registro"
   - Llenar formulario:
     - Gas medicinal
     - Periodo (fecha inicio/fin)
     - Modo de suministro
     - Cantidad y unidad
     - Observaciones (opcional)
   
4. **Generar Reporte**
   - Ir a "Reportes"
   - Seleccionar filtros (fechas, gas, modo)
   - Clic en "Generar PDF" o "Exportar Excel"

### Para Administradores

1. **Gestión de Usuarios**
   - Crear usuarios de hospitales
   - Asignar roles y hospitales
   - Activar/desactivar usuarios

2. **Gestión de Hospitales**
   - Registrar nuevos hospitales
   - Actualizar información de contacto
   - Ver estadísticas por hospital

3. **Dashboard Global**
   - Ver consumo total nacional
   - Top 5 hospitales consumidores
   - Consumo por tipo de gas
   - Alertas de hospitales sin registro

4. **Reportes Globales**
   - Reporte por periodo
   - Reporte por gas específico
   - Reporte por hospital
   - Exportar en PDF/Excel/CSV

5. **Auditoría**
   - Ver todas las acciones del sistema
   - Filtrar por usuario, acción, fecha
   - Estadísticas de uso

---

## 🛡️ Seguridad

### Implementaciones de Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Autenticación JWT
- ✅ Tokens con expiración (8 horas por defecto)
- ✅ Validación de inputs (Pydantic)
- ✅ Protección contra inyección SQL (SQLAlchemy ORM)
- ✅ CORS configurado
- ✅ Sistema de auditoría completo
- ✅ Variables de entorno para secretos

### Recomendaciones

1. **Cambiar SECRET_KEY**: Genera una clave segura
   ```bash
   openssl rand -hex 32
   ```

2. **Configurar SMTP**: Para recuperación de contraseñas
3. **Cambiar contraseña admin**: Inmediatamente
4. **Revisar logs**: Periódicamente en auditoría
5. **Backups**: Configurar backups automáticos de PostgreSQL

---

## 🚀 Características Anti-Sleep de Render

### Keep-Alive Service

El sistema incluye un servicio automático que previene que Render.com ponga el backend en modo sleep:

**Funcionamiento**:
- Hace ping al endpoint `/health` cada 14 minutos
- Se activa automáticamente al iniciar el backend
- Configurable via `KEEP_ALIVE_INTERVAL`

**Configuración**:
```env
KEEP_ALIVE_URL=https://tu-backend.onrender.com
KEEP_ALIVE_INTERVAL=840  # 14 minutos (en segundos)
```

---

## 📧 Configuración de Email (Opcional)

Para habilitar recuperación de contraseña por email:

### Gmail (Recomendado para desarrollo)

1. **Habilitar 2FA** en tu cuenta Gmail
2. **Generar App Password**:
   - Google Account → Security → 2-Step Verification → App passwords
   - Generar una contraseña para "Mail"
3. **Configurar .env**:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=tu-email@gmail.com
   SMTP_PASSWORD=tu-app-password-de-16-digitos
   EMAIL_FROM=noreply@mspbs.gov.py
   ```

### Otros Proveedores

- **Outlook**: smtp-mail.outlook.com:587
- **SendGrid**: smtp.sendgrid.net:587
- **Mailgun**: smtp.mailgun.org:587

---

## 📚 Documentación API

Una vez iniciado el backend, la documentación interactiva está disponible en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

#### Autenticación
- `POST /api/auth/login` - Login
- `POST /api/auth/recuperar-password` - Solicitar recuperación
- `POST /api/auth/reset-password` - Resetear contraseña

#### Usuarios
- `GET /api/usuarios/` - Listar usuarios (ADMIN)
- `POST /api/usuarios/` - Crear usuario (ADMIN)
- `GET /api/usuarios/me` - Usuario actual
- `PUT /api/usuarios/{id}` - Actualizar usuario (ADMIN)

#### Hospitales
- `GET /api/hospitales/` - Listar hospitales
- `POST /api/hospitales/` - Crear hospital (ADMIN)
- `GET /api/hospitales/{id}` - Detalles hospital
- `GET /api/hospitales/{id}/estadisticas` - Estadísticas

#### Gases
- `GET /api/gases/` - Listar gases
- `POST /api/gases/` - Crear gas (ADMIN)

#### Consumos
- `GET /api/consumos/` - Listar consumos
- `POST /api/consumos/` - Crear consumo
- `PUT /api/consumos/{id}` - Actualizar consumo
- `DELETE /api/consumos/{id}` - Eliminar consumo
- `POST /api/consumos/{id}/validar` - Validar consumo (ADMIN)

#### Reportes
- `GET /api/reportes/dashboard` - Dashboard admin
- `GET /api/reportes/dashboard/hospital` - Dashboard hospital
- `POST /api/reportes/generar-pdf` - Generar PDF
- `POST /api/reportes/generar-excel` - Generar Excel/CSV
- `GET /api/reportes/consumo-mensual` - Datos para gráficos

#### Auditoría
- `GET /api/auditoria/` - Listar auditoría (ADMIN)
- `GET /api/auditoria/estadisticas` - Estadísticas (ADMIN)

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm run test
```

---

## 📝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto fue desarrollado por la **DGGIES** para el **Ministerio de Salud y Bienestar Social de Paraguay**.

---

## 👥 Contacto y Soporte

**DGGIES** - Dirección General de Gestión de Información y Estadísticas de Salud  
**Ministerio de Salud y Bienestar Social**  
República del Paraguay

Para soporte técnico o consultas:
- Email: dggies@mspbs.gov.py
- Web: https://www.mspbs.gov.py

---

## 🎯 Roadmap

### v1.1 (Próximas características)
- [ ] Notificaciones push
- [ ] Exportación automática programada
- [ ] Dashboard con mapas de Paraguay
- [ ] App móvil nativa
- [ ] Integración con sistemas hospitalarios
- [ ] Análisis predictivo de consumos
- [ ] Sistema de aprobaciones multi-nivel

---

## 🙏 Agradecimientos

Desarrollado con ❤️ por la DGGIES para mejorar la gestión de gases medicinales en todo el sistema de salud paraguayo.

**¡Salud para todos los paraguayos!** 🇵🇾
