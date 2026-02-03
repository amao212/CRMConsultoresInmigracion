# CRM para Consultores de Inmigración
## Verificación y validación de software
## GRUPO 3
### Integrantes:
- Angel Anguaya
- Jimmy Arias
- Sebastian Correa
- Brandon Jaya
- Daniel Oña

Guía paso a paso para instalar y ejecutar el proyecto en un entorno local (Windows y Linux).

## 📋 Requisitos Previos

Asegúrate de tener instalado lo siguiente antes de comenzar:

*   **Python**: Versión 3.10 o superior.
    *   Verificar: `python --version`
*   **PostgreSQL**: Versión 12 o superior.
    *   Verificar: `psql --version`
*   **Git**: Para clonar el repositorio.
*   **Administrador de paquetes**: `pip` (incluido con Python).

---

## 🚀 Guía de Instalación

### 1. Clonar el repositorio

Abre tu terminal (PowerShell en Windows o Terminal en Linux) y ejecuta:

```bash
git clone <URL_DEL_REPOSITORIO>
cd CRMConsultoresInmigracion
```

### 2. Configurar el Entorno Virtual

Es recomendable usar un entorno virtual para aislar las dependencias.

**En Windows:**
```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\Activate
```

**En Linux/Mac:**
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate
```

### 3. Instalar Dependencias

Con el entorno virtual activado, instala las librerías necesarias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configuración de la Base de Datos

Este proyecto utiliza **PostgreSQL**. Debes crear una base de datos y un usuario.

1.  Abre `pgAdmin` o tu terminal de PostgreSQL (`psql`).
2.  Ejecuta los siguientes comandos SQL para crear la BD y el usuario (ajusta la contraseña si lo deseas):

```sql
-- Crear base de datos
CREATE DATABASE crm_tramites;

-- Crear usuario (opcional, puedes usar postgres)
CREATE USER crm_user WITH PASSWORD 'password123';

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE crm_tramites TO crm_user;
```

### 5. Configuración del Proyecto

El proyecto utiliza `core/settings.py` para la configuración.

1.  Abre el archivo `core/settings.py`.
2.  Busca la sección `DATABASES` y actualiza las credenciales según tu configuración local:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crm_tramites',      # Nombre de la BD creada
        'USER': 'postgres',          # Tu usuario de PostgreSQL (ej. crm_user o postgres)
        'PASSWORD': '1234',          # Tu contraseña
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

> **Nota:** Si deseas usar variables de entorno, puedes crear un archivo `.env` (si instalas `python-dotenv`) o configurar las variables en tu sistema operativo y leerlas con `os.getenv` en `settings.py`.

### 6. Migraciones y Datos Iniciales

Una vez configurada la base de datos, crea las tablas y el superusuario.

```bash
# Crear las tablas en la base de datos
python manage.py migrate

# Crear superusuario (Administrador)
# Opción A: Usar el script automático (si está disponible)
python manage.py seed_superuser

# Opción B: Crear manualmente
python manage.py createsuperuser
```

*Si usaste `seed_superuser`, las credenciales son:*
*   **Email:** `admin@admin.com`
*   **Password:** `admin123`

### 7. Ejecutar el Servidor

Inicia el servidor de desarrollo:

```bash
python manage.py runserver
```

Accede al sistema en tu navegador:
*   **Web:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
*   **Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🛠️ Solución de Errores Comunes

### 1. Error: `role "postgres" does not exist` o `password authentication failed`
*   **Causa:** Las credenciales en `core/settings.py` no coinciden con las de tu PostgreSQL local.
*   **Solución:** Verifica `USER` y `PASSWORD` en `settings.py`. Asegúrate de que el servicio de PostgreSQL esté corriendo.

### 2. Error: `database "crm_tramites" does not exist`
*   **Causa:** No has creado la base de datos.
*   **Solución:** Ejecuta `CREATE DATABASE crm_tramites;` en tu consola SQL.

### 3. Error: `port is already in use`
*   **Causa:** Otro proceso está usando el puerto 8000.
*   **Solución:** Ejecuta el servidor en otro puerto:
    ```bash
    python manage.py runserver 8080
    ```

### 4. Error con `psycopg2` en Linux
*   **Causa:** Faltan librerías de desarrollo de PostgreSQL.
*   **Solución:** Instala las dependencias del sistema:
    ```bash
    sudo apt-get install libpq-dev python3-dev
    ```

### 5. Error: `no such table`
*   **Causa:** No se han aplicado las migraciones.
*   **Solución:** Ejecuta `python manage.py migrate`.

---

## 📂 Estructura del Proyecto

```
CRMConsultoresInmigracion/
├── apps/
│   ├── usuarios/        # Gestión de usuarios y roles
│   └── tramites/        # Lógica de trámites y documentos
├── core/                # Configuración global (settings, urls)
├── media/               # Archivos generados (PDFs, adjuntos)
├── static/              # Archivos CSS/JS/Imágenes
├── templates/           # Plantillas HTML
├── manage.py            # Script de gestión de Django
└── requirements.txt     # Dependencias del proyecto
```
