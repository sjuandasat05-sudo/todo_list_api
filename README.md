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

## Decisiones de diseño

### Modelo SQLAlchemy y schema Pydantic son distintos

El modelo (`User`, `Todo`) describe cómo se guarda el dato: tablas, tipos, constraints y relaciones, incluido `hashed_password`. El schema (`UserCreate`, `UserPublic`, `TodoOut`) describe qué entra y qué sale por la API, y valida los datos. Separarlos permite:

* **Seguridad:** `UserPublic` no tiene `hashed_password`, así que ninguna respuesta puede exponerlo.
* **Formatos distintos por entidad:** al crear se exige `title`, en el PATCH todo es opcional y en la respuesta aparecen `id` y fechas que el cliente no envía.
* **Independencia:** se puede cambiar la base de datos sin romper el contrato de la API. El puente es `ConfigDict(from_attributes=True)`.

### Uso de `Depends()`

Cada regla vive en una sola función reutilizable y FastAPI las resuelve en cadena:

* `get_db` entrega la sesión y la cierra al terminar la petición.
* `get_current_user` valida el token (401 si falla).
* `get_current_active_user` agrega el 403 por usuario inactivo.
* `require_admin` exige el rol admin (403).
* `get_owned_todo_or_404` responde 404 si la tarea no existe y 403 si es de otro usuario.

Así, un endpoint como `PUT /todos/{id}` solo declara `Depends(get_owned_todo_or_404)` y ya tiene autenticación, existencia y propiedad resueltas.

### CORS sin `"*"` cuando hay credenciales

Con `allow_credentials=True` el navegador envía credenciales al otro origen, y la especificación de CORS no permite responder `Access-Control-Allow-Origin: *` en ese caso. Además, cualquier sitio podría hacer peticiones autenticadas en nombre del usuario. Por eso se listan los orígenes de forma explícita (`http://localhost:5173` y `http://localhost:3000`), y la prueba 18 comprueba que otro origen no recibe el permiso. Los `"*"` de `allow_methods` y `allow_headers` no tienen ese problema, porque limitan qué métodos y cabeceras se aceptan, no quién puede hacer la petición.


1. alembic upgrade head en base vacía

![alt text](docs/evidencias/image.png)


![alt text](docs/evidencias/image-1.png)

2. Registrar usuario válido

![alt text](docs/evidencias/image-2.png)

![alt text](docs/evidencias/image-3.png)

3. Registrar con contraseña debil

![alt text](docs/evidencias/image-4.png)

4. Registrar con correo duplicado

![alt text](docs/evidencias/image-5.png)

5. Login correcto e incorrecto

![alt text](docs/evidencias/image-6.png)

![alt text](docs/evidencias/image-7.png)

6. GET /auth/me con y sin token

![alt text](docs/evidencias/image-8.png)

![alt text](docs/evidencias/image-9.png)

7. POST /todos con token

![alt text](docs/evidencias/image-10.png)

8. POST /todos sin token o alterado

![alt text](docs/evidencias/image-11.png)

9. Paginación con 5 tareas

![alt text](docs/evidencias/image-12.png)

10. Filtros y orden

![alt text](docs/evidencias/image-13.png)

![alt text](docs/evidencias/image-14.png)

11. GET de ID inexistente

![alt text](docs/evidencias/image-15.png)

12. PUT y DELETE de tarea ajena

![alt text](docs/evidencias/image-16.png)

![alt text](docs/evidencias/image-17.png)

13. PUT y PATCH propios

![alt text](docs/evidencias/image-18.png)

![alt text](docs/evidencias/image-19.png)

14. PATCH con cuerpo vacío

![alt text](docs/evidencias/image-20.png)

15. DELETE propio y GET posterior

![alt text](docs/evidencias/image-21.png)

![alt text](docs/evidencias/image-22.png)

![alt text](docs/evidencias/image-23.png)

16. GET /admin/todos como user y como admin

![alt text](docs/evidencias/image-24.png)

![alt text](docs/evidencias/image-25.png)

![alt text](docs/evidencias/mage-26.png)

17. Cabeceras del middleware

![alt text](docs/evidencias/image-27.png)

18. Preflight CORS
![alt text](docs/evidencias/image-28.png)

19.

![alt text](docs/evidencias/image-29.png)

20. 
Redoc

![alt text](docs/evidencias/image-30.png)

docs

![alt text](docs/evidencias/image-31.png)

## REFLEXION

Cuando empecé este proyecto pensaba que lo difícil iba a ser escribir el código. Con el tiempo me di cuenta de que lo que más me costaba, y lo que más me ayudó, era mantener el orden. Trabajar por fases, con ramas y commits, al principio me pareció un exceso, hasta que algo falló y pude encontrar el problema sin volverme loco buscando.

También entendí que una API es mucho más que hacer que los endpoints respondan. Hay que pensar en quién puede ver qué, en cuidar las contraseñas, en validar lo que llega y en explicar bien los errores. Cuando vi en Swagger los códigos 401, 403, 404 y 422 funcionando, por fin les encontré sentido: dejaron de ser números raros y pasaron a ser respuestas con una razón de ser.

Hubo errores, y varios momentos en los que me frustré. Pero cada uno me obligó a frenar, leer con calma y preguntarme por qué pasaban las cosas, en lugar de copiar una solución y seguir. Eso fue lo que más me cambió.

Termino con más seguridad, mejores hábitos y la tranquilidad de saber que, con orden y constancia, soy capaz de sacar adelante un proyecto completo.




## Autor

Juan David Salazar Torres

