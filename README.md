# todo_list_api

API RESTful de lista de tareas hecha con **FastAPI**, **SQLAlchemy**, **Alembic**, **Pydantic v2**, **JWT** y **SQLite**.

## Requisitos

* Python 3.10 o superior
* Git

## Instalación

    git clone https://github.com/TU_USUARIO/todo_list_api.git
    cd todo_list_api
    python -m venv venv
    source venv/bin/activate        # Windows (Git Bash): source venv/Scripts/activate
    pip install -r requirements.txt
    cp .env.example .env

Edita `.env` y cambia `SECRET_KEY` por una clave larga. Puedes generarla con:

    python -c "import secrets; print(secrets.token_hex(32))"

## Variables de entorno

| Variable | Descripción |
| --- | --- |
| SECRET_KEY | Clave para firmar los JWT |
| ALGORITHM | Algoritmo del JWT (HS256) |
| ACCESS_TOKEN_EXPIRE_MINUTES | Minutos de vigencia del token |
| DATABASE_URL | Cadena de conexión (SQLite por defecto) |

## Base de datos

    alembic upgrade head

## Crear un administrador

    python -m scripts.create_admin

## Ejecución

    uvicorn app.main:app --reload

* Swagger UI: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc

## Estructura

| Carpeta | Responsabilidad |
| --- | --- |
| app/routes | Endpoints, códigos de estado y response models |
| app/schemas | Modelos Pydantic de entrada y salida |
| app/models | Tablas SQLAlchemy |
| app/services | Reglas de negocio y consultas |
| app/dependencies | Funciones reutilizables con Depends() |
| app/auth | Hash de contraseñas y JWT |
| app/middlewares | Cabeceras y registro de peticiones |
| alembic | Migraciones |

## Endpoints

| Método y ruta | Acceso | Éxito |
| --- | --- | --- |
| POST /auth/register | Público | 201 |
| POST /auth/login | Público | 200 |
| GET /auth/me | Autenticado | 200 |
| POST /categories | Autenticado | 201 |
| GET /categories | Autenticado | 200 |
| DELETE /categories/{category_id} | Dueño | 204 |
| POST /todos | Autenticado | 201 |
| GET /todos | Autenticado | 200 |
| GET /todos/{todo_id} | Dueño | 200 |
| PUT /todos/{todo_id} | Dueño | 200 |
| PATCH /todos/{todo_id} | Dueño | 200 |
| DELETE /todos/{todo_id} | Dueño | 204 |
| GET /admin/todos | Solo admin | 200 |

Parámetros de `GET /todos`: `page`, `limit`, `status` (pending, in_progress, done), `priority` (low, medium, high), `search`, `sort_by` (created_at, due_date, priority, title) y `order` (asc, desc).

## Códigos de error

| Caso | Código |
| --- | --- |
| Correo ya registrado, PATCH sin campos | 400 |
| Credenciales incorrectas, token ausente, inválido o vencido | 401 |
| Usuario inactivo, tarea ajena, ruta admin sin rol admin | 403 |
| Tarea o categoría inexistente | 404 |
| Categoría con tareas, o categoría de otro usuario | 409 |
| Datos inválidos | 422 |
| Límite de peticiones superado | 429 |

## Límites de peticiones

Login 5 por minuto, register 3, POST /todos 20 y GET /todos 60.

## Flujo de Git (Git Flow)

`main` (versiones estables), `develop` (integración), `feature/*` (una por fase), `release/1.0.0` y `hotfix/*` solo si hace falta corregir tras la versión 1.0.0.

| Tag | Fase |
| --- | --- |
| v0.1 | F1 Configuración |
| v0.2 | F2 Persistencia y migraciones |
| v0.3 | F3 Schemas y validaciones |
| v0.4 | F4 Autenticación y roles |
| v0.5 | F5 CRUD, paginación y filtros |
| v0.6 | F6 Middleware, CORS y rate limiting |
| v1.0.0 | F7 Documentación y cierre |

## Pruebas y evidencias

Las capturas están en `docs/evidencias/`.

| N.º | Prueba | Resultado esperado | Evidencia |
| --- | --- | --- | --- |
| 1 | alembic upgrade head en base vacía | Se crean users, categories y todos | prueba_01_migracion.png |
| 2 | Registrar usuario válido | 201 y la BD guarda el hash | prueba_02_registro.png |
| 3 | Registrar con contraseña débil | 422 | prueba_03_password_debil.png |
| 4 | Registrar con correo duplicado | 400 | prueba_04_correo_duplicado.png |
| 5 | Login correcto e incorrecto | 200 con token; 401 | prueba_05_login.png |
| 6 | GET /auth/me con y sin token | 200; 401 | prueba_06_me.png |
| 7 | POST /todos con token | 201 con owner_id | prueba_07_crear_tarea.png |
| 8 | POST /todos sin token o alterado | 401 | prueba_08_sin_token.png |
| 9 | Paginación con 5 tareas | 2 elementos, total 5 | prueba_09_paginacion.png |
| 10 | Filtros y orden | Solo las tareas que cumplen | prueba_10_filtros.png |
| 11 | GET de ID inexistente | 404 | prueba_11_404.png |
| 12 | PUT y DELETE de tarea ajena | 403 | prueba_12_403.png |
| 13 | PUT y PATCH propios | 200 | prueba_13_put_patch.png |
| 14 | PATCH con cuerpo vacío | 400 | prueba_14_patch_vacio.png |
| 15 | DELETE propio y GET posterior | 204 y luego 404 | prueba_15_delete.png |
| 16 | GET /admin/todos como user y como admin | 403 y 200 | prueba_16_admin.png |
| 17 | Cabeceras del middleware | X-Request-ID, X-Process-Time, X-App-Name | prueba_17_cabeceras.png |
| 18 | Preflight CORS | Permitido solo desde localhost:5173 | prueba_18_cors.png |
| 19 | Seis logins en un minuto | El sexto responde 429 | prueba_19_429.png |
| 20 | /docs y /redoc | Tags, Authorize, modelos y códigos | prueba_20_docs.png |

## Autor

Tu Nombre
