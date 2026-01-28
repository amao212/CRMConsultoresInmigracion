# Documentación del Proyecto: CRM Consultores Inmigración

Este proyecto es un sistema CRM (Customer Relationship Management) especializado en la gestión de trámites migratorios. Permite a solicitantes iniciar procesos, a tramitadores gestionarlos y a administradores supervisar el flujo y las plantillas del sistema.

## Árbol de Directorios

```text
/
├── apps/
│   ├── tramites/
│   │   ├── migrations/
│   │   ├── services/
│   │   │   ├── aprobacion_service.py
│   │   │   ├── asignacion_service.py
│   │   │   ├── automation_service.py
│   │   │   ├── monitoring_service.py
│   │   │   ├── pdf_field_extractor.py
│   │   │   ├── storage_service.py
│   │   │   ├── tramite_data_service.py
│   │   │   └── tramite_service.py
│   │   ├── templatetags/
│   │   ├── admin.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── selectors.py
│   │   ├── storage.py
│   │   ├── urls.py
│   │   ├── urls_empleado.py
│   │   ├── urls_tramitador.py
│   │   ├── views.py
│   │   ├── views_empleado.py
│   │   └── views_tramitador.py
│   └── usuarios/
│       ├── management/
│       ├── migrations/
│       ├── views_roles/
│       │   ├── admin_view.py
│       │   ├── empleado_view.py
│       │   ├── login_view.py
│       │   ├── registro_view.py
│       │   ├── solicitante_view.py
│       │   ├── staff_view.py
│       │   ├── tramitador_view.py
│       │   └── user_view.py
│       ├── models.py
│       ├── selectors.py
│       ├── services.py
│       └── urls.py
├── core/
│   ├── middleware.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/
├── static/
│   ├── css/
│   ├── js/
│   └── vendor/
├── templates/
│   ├── administrador/
│   ├── empleado/
│   ├── solicitante/
│   ├── tramitador/
│   ├── tramites/
│   ├── base.html
│   ├── login.html
│   └── registro.html
├── tests/
│   └── features/
│       ├── steps/
│       ├── environment.py
│       └── *.feature
├── estructura.md
├── manage.py
├── README.md
├── requirements.txt
└── tecno.md
```

## Explicación por Carpeta

### `/apps`
Contiene las aplicaciones de Django que encapsulan la lógica de negocio del proyecto.
- **`tramites/`**: Es el núcleo del CRM. Maneja todo lo relacionado con la creación, seguimiento, asignación y gestión de trámites migratorios y documentos.
- **`usuarios/`**: Gestiona la autenticación, registro y los diferentes roles de usuario (Solicitante, Tramitador, Administrador, Empleado).

### `/core`
Es el corazón de la configuración de Django.
- Contiene los ajustes globales, la configuración de URLs principal y middlewares personalizados. No contiene lógica de negocio, solo configuración del framework.

### `/media`
Directorio destinado al almacenamiento de archivos subidos por los usuarios.
- Aquí se guardan los PDFs de los trámites, documentos adjuntos y plantillas base.

### `/static`
Almacena los archivos estáticos del frontend que no cambian.
- **`css/`**: Hojas de estilo personalizadas para el diseño del CRM.
- **`js/`**: Scripts de JavaScript para interactividad en el cliente.
- **`vendor/`**: Librerías de terceros (como Bootstrap o FontAwesome).

### `/templates`
Contiene los archivos HTML (plantillas de Django) que renderizan la interfaz de usuario.
- Están organizados por carpetas según el rol del usuario (`administrador`, `solicitante`, `tramitador`) para mantener modularidad en las vistas.

### `/tests`
Contiene las pruebas del sistema.
- **`features/`**: Pruebas de comportamiento (BDD) escritas en lenguaje Gherkin (`.feature`), que describen cómo debe comportarse el sistema desde la perspectiva del usuario.

---

## Explicación por Archivo Clave

### Raíz
- **`manage.py`**: Utilidad de línea de comandos de Django para interactuar con el proyecto (correr servidor, migraciones, tests).
- **`requirements.txt`**: Lista de dependencias y librerías Python necesarias para ejecutar el proyecto.
- **`estructura.md`**: Este documento.

### `core/`
- **`settings.py`**: Configuración global: base de datos, apps instaladas, zona horaria, rutas de estáticos y media.
- **`urls.py`**: "Tabla de contenidos" de las URLs. Redirige las peticiones entrantes a las apps correspondientes (`usuarios` o `tramites`).
- **`middleware.py`**: Lógica que se ejecuta en cada petición/respuesta (ej. control de caché o seguridad).

### `apps/tramites/`
- **`models.py`**: Define la estructura de datos: `Tramite`, `Documento`, `Plantilla`, etc.
- **`views.py`**: Vistas generales para la gestión de trámites.
- **`views_tramitador.py` / `views_empleado.py`**: Vistas específicas para los roles de tramitador y empleado, separando la lógica por perfil.
- **`forms.py`**: Formularios para validar entrada de datos (creación de trámites, carga de documentos).
- **`services/`**: Capa de lógica de negocio compleja:
  - `tramite_service.py`: Lógica central de creación y actualización de trámites.
  - `asignacion_service.py`: Reglas para asignar trámites a usuarios.
  - `pdf_field_extractor.py`: Utilidad para leer campos de formularios PDF.
  - `storage_service.py`: Manejo de almacenamiento de archivos.

### `apps/usuarios/`
- **`models.py`**: Modelo de usuario personalizado (`UsuarioCRM`) que extiende el de Django para incluir roles y datos extra.
- **`views_roles/`**: Vistas separadas por rol para mantener el código limpio:
  - `login_view.py`: Manejo de inicio de sesión.
  - `registro_view.py`: Registro de nuevos solicitantes.
  - `admin_view.py`, `solicitante_view.py`, etc.: Dashboards y lógicas específicas de cada rol.

### `templates/`
- **`base.html`**: Plantilla maestra que define la estructura común (cabecera, pie de página, imports de CSS/JS).
- **`login.html` / `registro.html`**: Pantallas de acceso público.
- **`administrador/gestion_plantillas.html`**: Pantalla para subir y gestionar plantillas PDF.

### `tests/features/`
- **`*.feature`**: Archivos de texto plano describiendo escenarios de prueba (ej. "Crear un trámite exitoso").
- **`steps/`**: Código Python que ejecuta los pasos definidos en los archivos `.feature`.

---

## Flujo General del Sistema

El sistema opera bajo un modelo de roles bien definidos:

1.  **Solicitante**: Se registra e inicia sesión. Desde su panel (`solicitante_view.py`), crea nuevos trámites llenando formularios que se mapean a modelos en `tramites`. Puede ver el estado de sus solicitudes en tiempo real.
2.  **Tramitador**: Recibe los trámites creados. Su vista (`views_tramitador.py`) le permite revisar la documentación, aprobar pasos o solicitar correcciones. Utiliza los servicios de `tramites/services` para procesar la lógica.
3.  **Administrador**: Tiene control total (`admin_view.py`). Gestiona usuarios y, crucialmente, sube las **Plantillas Maestras** (PDFs) que el sistema utiliza para generar los documentos de los trámites.
4.  **Sistema (Backend)**:
    - Cuando se sube un PDF, `pdf_field_extractor.py` analiza sus campos.
    - Cuando se crea un trámite, `tramite_service.py` orquesta la creación en base de datos.
    - Las pruebas en `tests/features` aseguran que flujos críticos (como la asignación automática de tareas) funcionen como se espera.

Toda la interacción visual ocurre a través de las plantillas en `templates/`, servidas por Django, mientras que los archivos PDF y evidencias se almacenan de forma segura en `media/`.
