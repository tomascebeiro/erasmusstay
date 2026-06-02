# Explicación técnica del proyecto ErasmusStay

## 1. Introducción general

**ErasmusStay** es una aplicación web pensada para facilitar la búsqueda de alojamiento temporal a estudiantes Erasmus, especialmente en el contexto de una estancia en Malta.

La idea principal del proyecto es sencilla: una persona estudiante puede entrar en la plataforma, buscar alojamientos disponibles, aplicar filtros, ver los detalles de cada anuncio y solicitar contacto con el propietario. Por otra parte, una persona propietaria puede registrarse, publicar sus anuncios, añadir imágenes y gestionar sus alojamientos. Además, existe un rol de administrador encargado de revisar anuncios, gestionar usuarios, moderar comentarios y mantener cierto control sobre el contenido publicado.

Aunque para el usuario final la aplicación parece una web normal, internamente está dividida en varias partes:

* **Frontend**: la parte visual, desarrollada con Vue.
* **Backend**: la parte lógica y de datos, desarrollada con Django y Django REST Framework.
* **Base de datos**: donde se guardan usuarios, anuncios, imágenes, solicitudes y comentarios.
* **API REST**: la vía de comunicación entre el frontend y el backend.
* **Sistema de autenticación**: permite iniciar sesión y controlar qué puede hacer cada tipo de usuario.

El proyecto sigue una arquitectura moderna de aplicación web separada: el frontend no está mezclado directamente con el backend, sino que ambos se comunican mediante peticiones HTTP a una API.

---

## 2. Tecnologías utilizadas

### 2.1. Python

Python es el lenguaje principal utilizado en el backend.

En este proyecto, Python se usa para:

* definir los modelos de datos;
* crear la lógica del servidor;
* validar permisos;
* conectarse con la base de datos;
* gestionar usuarios;
* exponer endpoints de API REST;
* procesar formularios y subidas de imágenes.

Si nunca has tocado Python, puedes entenderlo como el lenguaje que permite escribir la “parte inteligente” del servidor.

Un ejemplo muy simple sería:

```python
def saludar(nombre):
    return f"Hola, {nombre}"
```

En Django, en lugar de funciones tan simples, se escriben clases y funciones que responden a peticiones web, crean objetos en la base de datos o verifican permisos.

---

### 2.2. Django

**Django** es un framework web de Python.

Un framework es un conjunto de herramientas que ya vienen preparadas para no tener que empezar desde cero. Django proporciona muchas piezas listas para usar:

* sistema de usuarios;
* panel de administración;
* conexión con base de datos;
* rutas;
* modelos;
* migraciones;
* seguridad básica;
* gestión de archivos;
* estructura de proyecto.

En ErasmusStay, Django se encarga de la parte del servidor. Es decir, recibe peticiones, consulta la base de datos, aplica reglas de negocio y devuelve respuestas.

Por ejemplo:

* cuando un estudiante pide ver los anuncios, Django busca los anuncios aprobados;
* cuando un propietario crea un anuncio, Django lo guarda en la base de datos;
* cuando un administrador aprueba un anuncio, Django actualiza su estado;
* cuando se sube una imagen, Django la almacena en la carpeta de medios.

---

### 2.3. Django REST Framework

**Django REST Framework**, normalmente abreviado como **DRF**, es una extensión de Django que permite construir APIs REST de forma ordenada.

Una API REST es una forma de comunicar dos partes de una aplicación mediante HTTP. En este caso:

* el frontend Vue hace peticiones;
* el backend Django responde con datos en formato JSON.

Ejemplo de respuesta JSON:

```json
{
  "id": 1,
  "titulo": "Habitación luminosa en Sliema",
  "precio_mes": "450.00",
  "localizacion": "Sliema, Malta"
}
```

Django REST Framework aporta elementos importantes:

* **serializers**: transforman modelos de Django en JSON y viceversa;
* **viewsets**: agrupan operaciones de listar, crear, editar y eliminar;
* **routers**: generan rutas automáticamente;
* **permisos**: controlan quién puede acceder a cada acción;
* **autenticación por token**: identifica al usuario en cada petición.

---

### 2.4. Vue

**Vue** es el framework utilizado para construir el frontend.

El frontend es lo que ve el usuario en el navegador:

* página de inicio;
* listado de alojamientos;
* detalle de anuncio;
* login;
* registro;
* perfil;
* panel de administración;
* formulario de creación de anuncios;
* sección de “Mis anuncios”.

Vue permite crear interfaces dinámicas. Esto significa que la página puede reaccionar a los datos sin tener que recargar completamente.

Por ejemplo:

* al iniciar sesión cambia el menú;
* si el usuario es propietario aparece “Mis anuncios”;
* si el usuario es administrador aparece “Panel de administración”;
* si se aprueba un comentario, cambia su estado;
* si se sube una imagen, aparece una vista previa.

---

### 2.5. Vue Router

**Vue Router** permite gestionar las rutas del frontend.

Por ejemplo:

```text
/
```

muestra la página de inicio.

```text
/anuncios
```

muestra el listado de alojamientos.

```text
/anuncio/1
```

muestra el detalle del anuncio con ID 1.

```text
/mis-anuncios
```

muestra los anuncios del propietario autenticado.

```text
/admin-panel
```

muestra el panel de administración.

Vue Router también permite proteger rutas. Por ejemplo, una persona sin iniciar sesión no debería entrar en `/mis-anuncios`, y una persona estudiante no debería entrar en `/admin-panel`.

---

### 2.6. JavaScript

JavaScript se usa en el frontend junto con Vue.

Sirve para:

* hacer peticiones al backend;
* gestionar formularios;
* mostrar errores;
* actualizar la interfaz;
* controlar el estado de autenticación;
* manejar imágenes seleccionadas;
* redirigir al usuario.

Ejemplo de petición al backend:

```js
const response = await fetch('http://localhost:8000/api/anuncios/')
const data = await response.json()
```

Esto pide al backend la lista de anuncios y convierte la respuesta en datos utilizables por Vue.

---

### 2.7. HTML y CSS

HTML define la estructura visual de las páginas.

CSS define el aspecto visual.

En este proyecto, el CSS se gestiona principalmente mediante clases de utilidad, probablemente con Tailwind CSS o una configuración similar. Esto se ve en clases como:

```html
<div class="bg-white border border-slate-200 rounded p-4">
```

Estas clases indican cosas como:

* fondo blanco;
* borde gris;
* esquinas redondeadas;
* separación interna.

---

### 2.8. Base de datos

La base de datos guarda la información persistente del sistema.

En ErasmusStay se guardan datos como:

* usuarios;
* perfiles de usuario;
* anuncios;
* imágenes de anuncios;
* valoraciones;
* solicitudes de contacto.

Aunque el usuario cierre el navegador, reinicie el ordenador o vuelva otro día, los datos siguen estando disponibles porque están guardados en la base de datos.

En Django, la base de datos se gestiona mediante **modelos**.

---

### 2.9. Docker

Docker permite ejecutar la aplicación en contenedores.

Un contenedor es como un entorno aislado donde se ejecuta una parte del proyecto. Esto evita muchos problemas de instalación, porque el proyecto puede arrancar con una configuración ya definida.

Normalmente se pueden tener contenedores para:

* backend Django;
* frontend Vue;
* base de datos.

Con Docker Compose se puede levantar todo el sistema con un comando como:

```bash
docker compose up -d --build
```

---

## 3. Arquitectura general del proyecto

La arquitectura general es una arquitectura **frontend-backend separada**.

Esto significa que el proyecto no funciona como una página tradicional donde el servidor genera todo el HTML. En su lugar:

1. Vue genera la interfaz visual en el navegador.
2. Vue pide datos al backend mediante HTTP.
3. Django responde con JSON.
4. Vue pinta esos datos en pantalla.

La arquitectura se puede representar así:

```text
Usuario
  ↓
Navegador
  ↓
Frontend Vue
  ↓ peticiones HTTP / JSON
API REST Django
  ↓
Modelos Django
  ↓
Base de datos
```

Ejemplo real:

```text
El usuario entra en /anuncios
  ↓
Vue carga el componente ListadoAnuncios.vue
  ↓
El componente hace GET /api/anuncios/
  ↓
Django recibe la petición
  ↓
Django consulta la tabla de anuncios
  ↓
Django devuelve JSON
  ↓
Vue muestra las tarjetas de alojamientos
```

---

## 4. Estructura del backend

El backend suele estar organizado en una carpeta tipo:

```text
backend/
└── src/
    ├── manage.py
    ├── config/
    │   ├── settings.py
    │   └── urls.py
    └── housing/
        ├── models.py
        ├── serializers.py
        ├── views.py
        ├── urls.py
        ├── admin.py
        └── migrations/
```

### 4.1. `manage.py`

Es el archivo principal para ejecutar comandos de Django.

Ejemplos:

```bash
python manage.py runserver
```

Arranca el servidor de desarrollo.

```bash
python manage.py migrate
```

Aplica cambios en la base de datos.

```bash
python manage.py createsuperuser
```

Crea un usuario administrador.

---

### 4.2. `config/settings.py`

Es el archivo de configuración general del proyecto.

Aquí se definen cosas como:

* aplicaciones instaladas;
* configuración de base de datos;
* configuración de archivos estáticos;
* configuración de archivos multimedia;
* permisos;
* autenticación;
* idioma;
* zona horaria;
* claves secretas;
* CORS.

Es uno de los archivos más importantes del backend.

---

### 4.3. `config/urls.py`

Es el archivo de rutas globales del backend.

Aquí se decide qué rutas principales existen.

Ejemplo conceptual:

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("housing.urls")),
]
```

Esto significa:

* todo lo que empiece por `/admin/` va al panel de Django;
* todo lo que empiece por `/api/` va a las rutas de la app `housing`.

---

### 4.4. App `housing`

En Django, una aplicación se divide en apps. En este caso, `housing` es la app principal del dominio del proyecto.

Contiene la lógica relacionada con:

* alojamientos;
* propietarios;
* estudiantes;
* imágenes;
* comentarios;
* solicitudes;
* roles.

---

## 5. Modelos del backend

Los modelos representan las tablas de la base de datos.

En Django, un modelo es una clase de Python. Django convierte esa clase en una tabla.

Ejemplo simplificado:

```python
class Anuncio(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio_mes = models.DecimalField(max_digits=8, decimal_places=2)
```

Esto se transforma en una tabla de base de datos con columnas como:

```text
id
titulo
descripcion
precio_mes
```

---

## 6. Principales modelos del proyecto

### 6.1. Usuario

El proyecto usa el modelo de usuario nativo de Django:

```python
User
```

Este modelo ya incluye:

* nombre de usuario;
* contraseña;
* email;
* estado activo;
* permisos;
* superusuario.

No se crea desde cero porque Django ya lo proporciona.

---

### 6.2. PerfilUsuario

El modelo `PerfilUsuario` amplía al usuario de Django.

Sirve para añadir datos que el modelo base no trae por defecto:

* rol;
* teléfono.

Los roles principales son:

```text
estudiante
propietario
administrador
```

El teléfono se guarda en el perfil y no en cada anuncio. Esto es importante porque evita duplicar datos.

Si un propietario cambia su teléfono, todos sus anuncios muestran automáticamente el teléfono nuevo.

---

### 6.3. Anuncio

El modelo `Anuncio` representa un alojamiento publicado en la plataforma.

Contiene información como:

* propietario;
* título;
* descripción;
* precio mensual;
* localización;
* tipo de vivienda;
* duración mínima;
* duración máxima;
* si tiene WiFi;
* si tiene terraza;
* si tiene garaje;
* si está publicado;
* si está aprobado.

El propietario es una relación con el usuario:

```python
propietario = models.ForeignKey(User, on_delete=models.CASCADE)
```

Esto significa que un usuario puede tener varios anuncios.

---

### 6.4. ImagenAnuncio

El modelo `ImagenAnuncio` guarda imágenes asociadas a un anuncio.

Un anuncio puede tener varias imágenes.

La relación es:

```text
Anuncio 1:N ImagenAnuncio
```

Es decir:

* un anuncio puede tener muchas imágenes;
* cada imagen pertenece a un único anuncio.

El sistema admite:

* imágenes subidas al servidor;
* URLs externas de imágenes, útil para datos de prueba.

---

### 6.5. Valoracion

El modelo `Valoracion` representa comentarios y puntuaciones de estudiantes.

Contiene:

* anuncio;
* usuario;
* puntuación;
* comentario;
* estado de aprobación;
* fecha de creación.

La parte importante es el campo `aprobado`.

Cuando un estudiante deja un comentario, no aparece directamente en público. Primero queda pendiente para que el administrador lo revise.

Esto evita comentarios ofensivos, spam o contenido inadecuado.

---

### 6.6. SolicitudContacto

El modelo `SolicitudContacto` registra cuando un estudiante solicita contactar con el propietario de un anuncio.

Guarda:

* estudiante;
* anuncio;
* mensaje;
* estado;
* teléfono del propietario en ese momento;
* email del propietario en ese momento;
* fecha de creación;
* fecha de actualización.

Los estados pueden ser:

```text
pendiente
respondida
cerrada
```

Este modelo permite tener un historial de solicitudes.

---

## 7. Migraciones

Las migraciones son archivos que Django genera para transformar los modelos en tablas reales.

Cuando se cambia un modelo, por ejemplo añadiendo un campo nuevo, hay que crear una migración.

Comando:

```bash
python manage.py makemigrations
```

Después hay que aplicar esa migración a la base de datos:

```bash
python manage.py migrate
```

Ejemplo práctico:

1. Añades un campo `telefono`.
2. Ejecutas `makemigrations`.
3. Django crea un archivo de migración.
4. Ejecutas `migrate`.
5. La columna aparece en la base de datos.

---

## 8. Serializers

Los serializers son una pieza clave de Django REST Framework.

Sirven para convertir modelos de Django en JSON y JSON en modelos de Django.

Por ejemplo, Django internamente trabaja con objetos como:

```python
anuncio.titulo
anuncio.precio_mes
anuncio.localizacion
```

Pero el frontend necesita JSON:

```json
{
  "titulo": "Habitación luminosa",
  "precio_mes": "450.00",
  "localizacion": "Sliema"
}
```

El serializer hace esa traducción.

También valida datos de entrada. Por ejemplo:

* comprueba que un precio sea válido;
* comprueba que un email tenga formato correcto;
* decide qué campos son de solo lectura;
* permite incluir campos calculados;
* permite incluir relaciones como imágenes o comentarios.

---

## 9. ViewSets

Un ViewSet es una clase de Django REST Framework que agrupa varias operaciones sobre un recurso.

Por ejemplo, el `AnuncioViewSet` puede gestionar:

```text
GET /api/anuncios/
POST /api/anuncios/
GET /api/anuncios/1/
PATCH /api/anuncios/1/
DELETE /api/anuncios/1/
```

Estas operaciones corresponden a:

| Método HTTP | Acción              |
| ----------- | ------------------- |
| GET lista   | Listar anuncios     |
| POST        | Crear anuncio       |
| GET detalle | Ver un anuncio      |
| PATCH       | Editar un anuncio   |
| DELETE      | Eliminar un anuncio |

Esto evita tener que escribir una función distinta para cada ruta.

---

## 10. Rutas del backend

Las rutas del backend están organizadas mediante routers.

Un router de Django REST Framework puede hacer esto:

```python
router.register(r"anuncios", AnuncioViewSet, basename="anuncio")
```

Y automáticamente genera rutas como:

```text
/api/anuncios/
/api/anuncios/1/
```

Esto se usa también para:

```text
/api/valoraciones/
/api/solicitudes/
```

Además hay rutas manuales para:

```text
/api/register/
/api/login/
/api/me/
/api/admin/usuarios/
```

---

## 11. API REST

La API REST es la capa de comunicación entre frontend y backend.

El frontend nunca toca directamente la base de datos. Siempre habla con el backend mediante peticiones HTTP.

Ejemplo:

```js
fetch('http://localhost:8000/api/anuncios/')
```

El backend responde:

```json
[
  {
    "id": 1,
    "titulo": "Habitación luminosa",
    "precio_mes": "450.00"
  }
]
```

Los métodos principales son:

| Método | Uso             |
| ------ | --------------- |
| GET    | Leer datos      |
| POST   | Crear datos     |
| PATCH  | Modificar datos |
| DELETE | Eliminar datos  |

---

## 12. Autenticación por token

El proyecto usa autenticación por token.

Cuando el usuario inicia sesión, el backend devuelve un token.

Ejemplo:

```json
{
  "token": "abc123",
  "user": {
    "username": "student1",
    "rol": "estudiante"
  }
}
```

El frontend guarda ese token en el navegador, normalmente en `localStorage`.

Después, en cada petición privada, el frontend manda:

```http
Authorization: Token abc123
```

Así el backend sabe quién está haciendo la petición.

Ejemplo:

```js
fetch('/api/me/', {
  headers: {
    Authorization: `Token ${token}`
  }
})
```

---

## 13. Roles y permisos

El proyecto diferencia tres roles principales.

### 13.1. Estudiante

Puede:

* ver anuncios aprobados;
* consultar detalles;
* solicitar contacto;
* dejar valoraciones;
* ver su historial de solicitudes.

No puede:

* crear anuncios;
* editar anuncios;
* acceder al panel de administración;
* aprobar comentarios.

---

### 13.2. Propietario

Puede:

* crear anuncios;
* editar sus propios anuncios;
* eliminar sus propios anuncios;
* ver “Mis anuncios”;
* ver solicitudes recibidas en sus anuncios.

No puede:

* aprobar sus propios anuncios;
* moderar comentarios;
* bloquear usuarios;
* acceder al panel global de administración.

Cuando un propietario edita un anuncio, el anuncio puede volver a quedar pendiente de aprobación. Esto tiene sentido porque evita que un propietario publique algo aprobado y luego cambie el contenido sin revisión.

---

### 13.3. Administrador

Puede:

* ver todos los anuncios;
* aprobar anuncios;
* desaprobar anuncios;
* editar anuncios;
* eliminar anuncios;
* ver usuarios;
* bloquear usuarios;
* activar usuarios;
* moderar comentarios;
* ver solicitudes.

Es el rol con más permisos.

---

## 14. Flujo de creación de anuncio

El flujo completo es:

```text
Propietario inicia sesión
  ↓
Entra en "Publicar anuncio"
  ↓
Rellena título, descripción, precio, ubicación y servicios
  ↓
Añade imágenes
  ↓
Vue envía FormData al backend
  ↓
Django crea el anuncio
  ↓
Django guarda las imágenes
  ↓
El anuncio queda pendiente
  ↓
Administrador lo revisa
  ↓
Administrador lo aprueba
  ↓
El anuncio aparece públicamente
```

Esto evita que cualquier anuncio aparezca automáticamente sin revisión.

---

## 15. Sistema de imágenes

El sistema de imágenes funciona mediante subida de archivos.

En el frontend, el usuario selecciona imágenes desde su ordenador:

```html
<input type="file" multiple accept="image/*">
```

Vue guarda esos archivos temporalmente y genera vistas previas.

Después se construye un `FormData`.

`FormData` es necesario porque no se pueden enviar imágenes igual que se envía JSON normal. Las imágenes son archivos binarios.

Ejemplo conceptual:

```js
const payload = new FormData()
payload.append('titulo', 'Habitación en Sliema')
payload.append('uploaded_images', file)
```

En el backend, Django recibe esas imágenes y las guarda mediante `ImageField`.

Después, cuando el frontend pide el anuncio, el backend devuelve la URL de la imagen.

---

## 16. Solicitudes de contacto

Cuando un estudiante quiere contactar con un propietario, no se limita a ver un teléfono sin más. Puede crear una solicitud.

El flujo es:

```text
Estudiante entra en detalle de anuncio
  ↓
Pulsa solicitar contacto
  ↓
Escribe mensaje opcional
  ↓
Vue envía POST /api/solicitudes/
  ↓
Django crea la solicitud
  ↓
Propietario puede verla
  ↓
Propietario puede marcarla como respondida o cerrada
```

Además, se guarda una copia del teléfono y email del propietario en el momento de la solicitud.

Esto es útil porque, si el propietario cambia su teléfono más tarde, el historial de la solicitud conserva el dato que existía cuando se hizo.

---

## 17. Moderación de comentarios

Los comentarios no se publican directamente.

El flujo es:

```text
Estudiante deja una valoración
  ↓
La valoración se guarda como aprobada = false
  ↓
No aparece públicamente todavía
  ↓
Administrador entra en panel
  ↓
Administrador aprueba, oculta o elimina
  ↓
Si está aprobada, aparece en el detalle del anuncio
```

Esto es una medida básica de seguridad y calidad.

Evita:

* insultos;
* spam;
* comentarios falsos;
* información sensible;
* contenido ofensivo.

---

## 18. Frontend: estructura general

El frontend suele estar organizado así:

```text
frontend/
└── src/
    ├── App.vue
    ├── main.js
    ├── router/
    │   └── index.js
    ├── composables/
    │   └── useAuth.js
    ├── components/
    │   ├── Navigation.vue
    │   └── ListadoAnuncios.vue
    └── views/
        ├── Inicio.vue
        ├── Login.vue
        ├── Register.vue
        ├── Profile.vue
        ├── CrearAnuncio.vue
        ├── MisAnuncios.vue
        ├── AnuncioDetalle.vue
        ├── Contacto.vue
        └── AdminPanel.vue
```

---

## 19. `App.vue`

`App.vue` es el componente raíz del frontend.

Normalmente contiene:

* la navegación;
* el `<router-view>`;
* el footer.

`router-view` es el lugar donde Vue Router coloca la página correspondiente.

Ejemplo:

```vue
<Navigation />
<router-view />
```

Si estás en `/anuncios`, dentro de `router-view` aparece el listado.

Si estás en `/login`, aparece el login.

---

## 20. `Navigation.vue`

Este componente muestra el menú superior.

Tiene lógica para mostrar enlaces según el usuario:

* si no hay sesión: muestra login y registro;
* si hay sesión: muestra perfil y cerrar sesión;
* si es propietario: muestra “Mis anuncios” y “Publicar anuncio”;
* si es administrador: muestra “Panel de administración”.

Es un buen ejemplo de interfaz basada en roles.

---

## 21. `useAuth.js`

`useAuth.js` es un composable de Vue.

Un composable es una función reutilizable que guarda lógica común.

En este caso, se encarga de:

* guardar el usuario;
* guardar si hay sesión iniciada;
* restaurar sesión desde el token;
* cerrar sesión;
* devolver cabeceras de autenticación.

Ejemplo conceptual:

```js
const { user, isAuthenticated, logout } = useAuth()
```

Esto permite usar la autenticación en muchas vistas sin repetir código.

---

## 22. `router/index.js`

Define las rutas del frontend.

También protege rutas mediante `meta`.

Ejemplo:

```js
{
  path: '/admin-panel',
  component: AdminPanel,
  meta: {
    requiresAuth: true,
    requiresAdmin: true
  }
}
```

Esto significa:

* hay que estar autenticado;
* además hay que ser administrador.

Antes de entrar en cada ruta, Vue Router ejecuta una comprobación.

Si el usuario no tiene permisos, se le redirige.

---

## 23. Comunicación frontend-backend

La comunicación se hace con `fetch`.

Ejemplo para listar anuncios:

```js
const response = await fetch(`${API_URL}/api/anuncios/`)
const data = await response.json()
```

Ejemplo para crear una solicitud:

```js
fetch(`${API_URL}/api/solicitudes/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Token ${token}`
  },
  body: JSON.stringify({
    anuncio: 1,
    mensaje: 'Estoy interesado'
  })
})
```

La comunicación siempre sigue este patrón:

```text
Vue prepara datos
  ↓
Vue hace fetch()
  ↓
Django recibe petición
  ↓
Django valida permisos
  ↓
Django consulta o modifica base de datos
  ↓
Django devuelve JSON
  ↓
Vue actualiza pantalla
```

---

## 24. Patrón cliente-servidor

El proyecto sigue el patrón **cliente-servidor**.

El cliente es el navegador con Vue.

El servidor es Django.

```text
Cliente = navegador + Vue
Servidor = Django + Django REST Framework
Base de datos = almacenamiento persistente
```

El cliente no guarda los datos importantes. Solo los muestra y permite interactuar.

El servidor controla:

* permisos;
* validaciones;
* base de datos;
* seguridad;
* autenticación;
* reglas del negocio.

---

## 25. Patrón MVC / MTV

Django suele explicarse con el patrón **MTV**:

```text
Model - Template - View
```

Pero en este proyecto, como el frontend está separado, no se usan tanto los templates de Django. Aun así, el patrón sigue estando parcialmente presente.

### Model

Representa los datos.

Ejemplo:

```text
Anuncio
PerfilUsuario
Valoracion
SolicitudContacto
```

### View

En Django, las views procesan peticiones.

En este proyecto son principalmente ViewSets y APIViews.

### Template

En una aplicación Django tradicional serían archivos HTML renderizados por el servidor.

En este proyecto, esa parte la cubre Vue. Por eso se podría decir que Django actúa más como backend API.

---

## 26. Patrón REST

REST es un estilo de arquitectura para APIs.

La idea es tratar cada entidad como un recurso.

Ejemplos:

```text
/anuncios/
/valoraciones/
/solicitudes/
/usuarios/
```

Y usar métodos HTTP para operar sobre esos recursos:

```text
GET    leer
POST   crear
PATCH  modificar parcialmente
DELETE eliminar
```

Ejemplo:

```text
GET /api/anuncios/
```

leer anuncios.

```text
POST /api/anuncios/
```

crear anuncio.

```text
PATCH /api/anuncios/1/
```

editar anuncio 1.

```text
DELETE /api/anuncios/1/
```

eliminar anuncio 1.

---

## 27. Patrón CRUD

CRUD significa:

```text
Create
Read
Update
Delete
```

En castellano:

```text
Crear
Leer
Actualizar
Eliminar
```

El proyecto implementa CRUD para varias entidades:

| Entidad      |    Crear |      Leer |         Actualizar |          Eliminar |
| ------------ | -------: | --------: | -----------------: | ----------------: |
| Anuncios     |       Sí |        Sí |                 Sí |                Sí |
| Valoraciones |       Sí |        Sí |          Sí, admin |         Sí, admin |
| Solicitudes  |       Sí |        Sí |                 Sí |           Parcial |
| Usuarios     | Registro | Sí, admin | Bloqueo/activación | No desde frontend |

---

## 28. Panel de administración

El panel de administración del frontend permite controlar el contenido desde una interfaz propia.

Incluye varias secciones:

* anuncios;
* usuarios;
* comentarios;
* solicitudes.

### Anuncios

El administrador puede:

* ver todos los anuncios;
* filtrar por pendientes o aprobados;
* aprobar anuncios;
* desaprobar anuncios;
* editar anuncios;
* eliminar anuncios.

### Usuarios

El administrador puede:

* ver usuarios;
* ver roles;
* ver teléfonos;
* bloquear cuentas;
* activar cuentas.

### Comentarios

El administrador puede:

* ver comentarios aprobados y pendientes;
* aprobar comentarios;
* ocultar comentarios;
* eliminar comentarios.

### Solicitudes

El administrador puede:

* ver solicitudes de contacto;
* revisar mensajes;
* marcar solicitudes como respondidas;
* cerrar solicitudes.

---

## 29. “Mis anuncios”

La sección “Mis anuncios” está pensada para propietarios.

Permite:

* ver solo los anuncios del propietario autenticado;
* comprobar si están aprobados o pendientes;
* editar anuncios;
* eliminar anuncios;
* crear un nuevo anuncio.

Esto evita que el propietario tenga que entrar en el panel de administración global.

El backend lo permite mediante:

```text
GET /api/anuncios/?mine=true
```

Si el usuario es propietario, devuelve solo sus anuncios.

---

## 30. Perfil del usuario

La sección de perfil permite modificar datos de la cuenta.

Especialmente importante es el teléfono.

El teléfono del propietario se muestra en sus anuncios, por lo que no se guarda un teléfono independiente en cada anuncio.

Esto es mejor por varias razones:

* evita datos duplicados;
* permite cambiar el teléfono una sola vez;
* mantiene los anuncios coherentes;
* simplifica el mantenimiento.

---

## 31. Carga de datos inicial

El proyecto usa un script de seed llamado `create_data.py`.

Sirve para cargar datos de prueba automáticamente.

Normalmente crea:

* usuario administrador;
* propietarios;
* estudiantes;
* perfiles;
* anuncios;
* imágenes;
* valoraciones;
* solicitudes.

Esto es útil para evaluación porque permite probar la aplicación sin tener que introducir datos manualmente desde cero.

Ejemplo de ejecución:

```bash
python create_data.py
```

Si se usa Docker:

```bash
docker compose exec backend python create_data.py
```

---

## 32. Seguridad básica

El proyecto aplica varias medidas básicas de seguridad.

### 32.1. Autenticación

Las acciones privadas requieren token.

Ejemplo:

* crear anuncio;
* editar anuncio;
* eliminar anuncio;
* solicitar contacto;
* comentar;
* acceder al perfil;
* acceder al panel admin.

### 32.2. Roles

No todos los usuarios pueden hacer lo mismo.

Esto evita que un estudiante pueda aprobar anuncios o que un propietario pueda bloquear usuarios.

### 32.3. Moderación

Los comentarios quedan pendientes hasta revisión.

### 32.4. Aprobación de anuncios

Los anuncios no aparecen públicamente hasta que un administrador los aprueba.

### 32.5. Protección de rutas en frontend

Vue Router evita que un usuario sin permisos entre en ciertas páginas.

### 32.6. Validación backend

Aunque el frontend oculte botones, la seguridad real está en el backend.

Esto es importante: ocultar un botón no es suficiente. El backend también comprueba permisos.

---

## 33. CORS

Cuando frontend y backend están en puertos diferentes, por ejemplo:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
```

el navegador aplica una política de seguridad llamada CORS.

Django necesita permitir que el frontend pueda hacer peticiones al backend.

Esto se configura normalmente con `django-cors-headers`.

---

## 34. Archivos multimedia

Las imágenes subidas por usuarios se guardan como archivos multimedia.

Django suele usar:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

`MEDIA_URL` es la URL pública.

`MEDIA_ROOT` es la carpeta física donde se guardan los archivos.

En desarrollo, para que Django sirva esas imágenes, se añade en `config/urls.py`:

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Sin esto, las imágenes pueden subirse pero no visualizarse correctamente en el navegador.

---

## 35. Variables de entorno

Las variables de entorno sirven para separar configuración sensible o cambiante.

Ejemplos:

* clave secreta;
* datos de base de datos;
* URL de API;
* modo debug.

En el frontend se usa:

```js
import.meta.env.VITE_API_URL
```

Esto permite cambiar la URL del backend sin modificar el código.

Por ejemplo:

```env
VITE_API_URL=http://localhost:8000
```

---

## 36. Diferencia entre entorno local y producción

En local se usa para desarrollar y probar.

En producción se usaría para usuarios reales.

Diferencias típicas:

| Aspecto        | Local          | Producción                        |
| -------------- | -------------- | --------------------------------- |
| DEBUG          | true           | false                             |
| Base de datos  | local o Docker | servidor real                     |
| Archivos media | carpeta local  | almacenamiento externo o servidor |
| Seguridad      | básica         | reforzada                         |
| Dominio        | localhost      | dominio real                      |
| Servidor       | runserver      | gunicorn/nginx                    |

---

## 37. Posible flujo completo de uso

Un flujo completo del sistema sería:

```text
1. El propietario crea una cuenta.
2. Configura su teléfono en el perfil.
3. Publica un anuncio con imágenes.
4. El anuncio queda pendiente.
5. El administrador entra en el panel.
6. El administrador aprueba el anuncio.
7. El anuncio aparece en la home y en el listado.
8. Un estudiante entra en el anuncio.
9. El estudiante solicita contacto.
10. El propietario ve la solicitud.
11. El estudiante deja una valoración.
12. El administrador modera la valoración.
13. Si se aprueba, aparece públicamente.
```

Este flujo resume prácticamente toda la lógica principal de la aplicación.

---

## 38. Explicación sencilla de cada capa

### Frontend

Es la “cara” de la aplicación.

Se encarga de:

* mostrar pantallas;
* recoger datos del usuario;
* hacer peticiones;
* mostrar errores;
* mostrar resultados.

### Backend

Es el “cerebro” de la aplicación.

Se encarga de:

* decidir qué datos puede ver cada usuario;
* guardar información;
* comprobar permisos;
* crear tokens;
* gestionar imágenes;
* aplicar reglas.

### Base de datos

Es la “memoria” de la aplicación.

Guarda:

* usuarios;
* anuncios;
* imágenes;
* comentarios;
* solicitudes.

### API REST

Es el “idioma” con el que hablan frontend y backend.

El frontend pide:

```text
Dame los anuncios
```

El backend responde:

```json
[
  {
    "titulo": "Habitación en Sliema"
  }
]
```

---

## 39. Decisiones importantes del diseño técnico

### 39.1. Separar frontend y backend

Ventajas:

* más ordenado;
* frontend y backend pueden evolucionar por separado;
* se puede crear app móvil en el futuro usando la misma API;
* la API puede documentarse y probarse de forma independiente.

### 39.2. Usar roles

Permite controlar permisos de forma clara.

No todos los usuarios necesitan las mismas funciones.

### 39.3. Usar aprobación de anuncios

Evita contenido no revisado.

### 39.4. Usar moderación de comentarios

Mejora la seguridad y la calidad del contenido.

### 39.5. Teléfono en el perfil

Evita duplicar datos en cada anuncio.

### 39.6. Historial de solicitudes

Permite seguimiento tanto para estudiantes como para propietarios.

---

## 40. Posibles mejoras futuras

El proyecto puede ampliarse con:

* sistema de favoritos;
* chat interno entre estudiante y propietario;
* verificación documental de propietarios;
* mapa con ubicación aproximada;
* sistema de disponibilidad por fechas;
* notificaciones por email;
* recuperación de contraseña;
* panel estadístico;
* subida múltiple avanzada de imágenes;
* eliminación individual de imágenes;
* paginación visual;
* tests automatizados más completos;
* internacionalización;
* despliegue en servidor real;
* integración con servicios de almacenamiento externo.

---

## 41. Cómo explicar el proyecto en una defensa

Una forma clara de explicarlo sería:

> ErasmusStay es una plataforma web para facilitar la búsqueda de alojamiento temporal a estudiantes Erasmus. El proyecto está dividido en un frontend en Vue y un backend en Django con Django REST Framework. El frontend muestra la interfaz y se comunica con el backend mediante una API REST. El backend gestiona usuarios, roles, anuncios, imágenes, valoraciones y solicitudes de contacto. La aplicación diferencia tres roles: estudiante, propietario y administrador. Los propietarios pueden publicar y gestionar sus anuncios, los estudiantes pueden buscar alojamiento y solicitar contacto, y el administrador puede aprobar anuncios, moderar comentarios y gestionar usuarios. La arquitectura separada permite que el proyecto sea más mantenible y escalable.

---

## 42. Resumen final

ErasmusStay es una aplicación web completa con una arquitectura moderna basada en frontend y backend separados.

El frontend en Vue permite una experiencia dinámica para el usuario. El backend en Django centraliza la lógica, los permisos y la persistencia de datos. Django REST Framework permite exponer una API REST que comunica ambas partes. La base de datos almacena toda la información del sistema y Docker facilita la puesta en marcha del proyecto.

Las funcionalidades principales son:

* registro e inicio de sesión;
* roles de estudiante, propietario y administrador;
* publicación de anuncios;
* subida de imágenes;
* edición y eliminación de anuncios propios;
* sección de “Mis anuncios”;
* listado y detalle de alojamientos;
* solicitudes de contacto;
* historial de solicitudes;
* valoraciones;
* moderación de comentarios;
* aprobación de anuncios;
* gestión de usuarios.

En conjunto, el proyecto demuestra el funcionamiento de una aplicación web full stack real, con separación de responsabilidades, comunicación mediante API REST, control de permisos y una estructura preparada para seguir creciendo.
