# API Reference - ErasmusStay

## 1. Introdución

Esta documentación describe a API REST de **ErasmusStay**, unha plataforma web para a busca e xestión de aloxamentos temporais orientada a estudantes Erasmus en Malta.

A API está desenvolvida con **Django** e **Django REST Framework**. O frontend, desenvolvido en **Vue**, consome estes endpoints para mostrar anuncios, rexistrar usuarios, iniciar sesión, crear anuncios, subir imaxes, xestionar solicitudes de contacto e moderar comentarios.

---

## 2. URL base

En contorno de desenvolvemento local, a URL base da API é:

```text
http://localhost:8000/api/
```

Exemplo:

```text
http://localhost:8000/api/anuncios/
```

---

## 3. Formato das respostas

A API utiliza JSON como formato principal de intercambio de datos.

### Cabeceiras habituais

```http
Content-Type: application/json
Accept: application/json
```

Nos endpoints que requiren autenticación débese enviar tamén o token:

```http
Authorization: Token TOKEN_DO_USUARIO
```

---

## 4. Autenticación

A API utiliza autenticación baseada en token mediante `TokenAuthentication` de Django REST Framework.

O usuario recibe un token ao rexistrarse ou ao iniciar sesión. Ese token debe enviarse nas peticións privadas mediante a cabeceira:

```http
Authorization: Token 123456789abcdef
```

---

## 5. Roles de usuario

A aplicación diferencia tres roles principais:

| Rol             | Descrición                                                                         |
| --------------- | ---------------------------------------------------------------------------------- |
| `estudiante`    | Pode buscar anuncios, consultar detalles, solicitar contacto e deixar valoracións. |
| `propietario`   | Pode crear anuncios, editalos, eliminalos e ver solicitudes recibidas.             |
| `administrador` | Pode xestionar usuarios, anuncios, solicitudes e moderar comentarios.              |

Os usuarios anónimos poden consultar anuncios aprobados e publicados, pero non poden crear anuncios, solicitar contacto nin deixar valoracións.

---

# 6. Autenticación e perfil

---

## 6.1. Rexistro de usuario

Rexistra un novo usuario na plataforma.

```http
POST /api/register/
```

### Permisos

Público.

### Corpo da petición

```json
{
  "username": "student1",
  "email": "student1@example.com",
  "password": "student1234",
  "rol": "estudiante",
  "telefono": "+34 600 111 222"
}
```

### Campos

| Campo      | Tipo   | Obrigatorio | Descrición                                      |
| ---------- | ------ | ----------: | ----------------------------------------------- |
| `username` | string |          Si | Nome de usuario único.                          |
| `email`    | string |          Si | Correo electrónico.                             |
| `password` | string |          Si | Contrasinal.                                    |
| `rol`      | string |          Si | `estudiante`, `propietario` ou `administrador`. |
| `telefono` | string |         Non | Teléfono asociado á conta.                      |

### Resposta correcta

```json
{
  "token": "TOKEN_XERADO",
  "user": {
    "id": 1,
    "username": "student1",
    "email": "student1@example.com",
    "rol": "estudiante",
    "telefono": "+34 600 111 222"
  }
}
```

### Posibles erros

```json
{
  "username": [
    "A user with that username already exists."
  ]
}
```

---

## 6.2. Inicio de sesión

Permite iniciar sesión e obter un token de autenticación.

```http
POST /api/login/
```

### Permisos

Público.

### Corpo da petición

```json
{
  "username": "student1",
  "password": "student1234"
}
```

### Resposta correcta

```json
{
  "token": "TOKEN_DO_USUARIO",
  "user": {
    "id": 2,
    "username": "student1",
    "email": "student1@example.com",
    "rol": "estudiante",
    "telefono": "+34 600 111 222"
  }
}
```

### Erro de credenciais

```json
{
  "error": "Credenciales incorrectas o cuenta suspendida."
}
```

---

## 6.3. Obter perfil do usuario autenticado

Obtén a información da conta autenticada.

```http
GET /api/me/
```

### Permisos

Usuario autenticado.

### Cabeceira

```http
Authorization: Token TOKEN_DO_USUARIO
```

### Resposta correcta

```json
{
  "id": 2,
  "username": "student1",
  "email": "student1@example.com",
  "rol": "estudiante",
  "telefono": "+34 600 111 222"
}
```

---

## 6.4. Actualizar perfil do usuario autenticado

Permite modificar datos básicos da conta, como o correo electrónico ou o teléfono.

```http
PATCH /api/me/
```

### Permisos

Usuario autenticado.

### Corpo da petición

```json
{
  "email": "novoemail@example.com",
  "telefono": "+34 600 999 888"
}
```

### Resposta correcta

```json
{
  "id": 2,
  "username": "student1",
  "email": "novoemail@example.com",
  "rol": "estudiante",
  "telefono": "+34 600 999 888"
}
```

### Nota sobre o teléfono

No caso das contas con rol `propietario`, o teléfono gardado no perfil é o que se mostra nos anuncios. Isto evita ter un teléfono distinto en cada anuncio.

---

# 7. Anuncios

---

## 7.1. Listar anuncios

Obtén a listaxe de anuncios dispoñibles.

```http
GET /api/anuncios/
```

### Permisos

Público.

### Comportamento segundo usuario

| Usuario       | Resultado                                                         |
| ------------- | ----------------------------------------------------------------- |
| Anónimo       | Só ve anuncios `aprobado=true` e `publicado=true`.                |
| Estudante     | Ve anuncios aprobados e publicados.                               |
| Propietario   | Ve anuncios aprobados e publicados máis os seus propios anuncios. |
| Administrador | Ve todos os anuncios.                                             |

### Parámetros de busca

| Parámetro       | Tipo    | Exemplo      | Descrición                   |
| --------------- | ------- | ------------ | ---------------------------- |
| `localizacion`  | string  | `Sliema`     | Filtra por localización.     |
| `tipo_vivienda` | string  | `habitacion` | Filtra por tipo de vivenda.  |
| `precio_min`    | number  | `300`        | Prezo mínimo mensual.        |
| `precio_max`    | number  | `700`        | Prezo máximo mensual.        |
| `wifi`          | boolean | `true`       | Filtra anuncios con WiFi.    |
| `terraza`       | boolean | `true`       | Filtra anuncios con terraza. |
| `garaje`        | boolean | `true`       | Filtra anuncios con garaxe.  |

### Tipos de vivenda dispoñibles

```text
habitacion
piso_completo
estudio
```

### Exemplo de petición

```http
GET /api/anuncios/?localizacion=Sliema&precio_max=600&wifi=true
```

### Resposta correcta

A API pode devolver unha lista directa ou unha resposta paginada segundo a configuración de Django REST Framework.

#### Exemplo de resposta paginada

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "propietario": 3,
      "propietario_nombre": "owner1",
      "propietario_telefono": "+356 9911 2233",
      "propietario_email": "owner1@example.com",
      "titulo": "Bright Room in Sliema",
      "descripcion": "Habitación luminosa e ampla no centro de Sliema.",
      "precio_mes": "450.00",
      "localizacion": "Sliema, Malta",
      "tipo_vivienda": "habitacion",
      "duracion_min_meses": 3,
      "duracion_max_meses": 12,
      "wifi": true,
      "terraza": false,
      "garaje": false,
      "telefono_contacto": "+356 9911 2233",
      "email_contacto": "owner1@example.com",
      "publicado": true,
      "aprobado": true,
      "fecha_creacion": "2026-06-02T09:00:00Z",
      "imagenes": [
        {
          "id": 1,
          "imagen": null,
          "imagen_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
          "url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
          "orden": 0
        }
      ],
      "valoraciones": []
    }
  ]
}
```

---

## 7.2. Ver detalle dun anuncio

Obtén a información completa dun anuncio concreto.

```http
GET /api/anuncios/{id}/
```

### Permisos

Público, pero respectando a visibilidade por rol.

### Exemplo

```http
GET /api/anuncios/1/
```

### Resposta correcta

```json
{
  "id": 1,
  "propietario": 3,
  "propietario_nombre": "owner1",
  "propietario_telefono": "+356 9911 2233",
  "propietario_email": "owner1@example.com",
  "titulo": "Bright Room in Sliema",
  "descripcion": "Habitación luminosa e ampla no centro de Sliema.",
  "precio_mes": "450.00",
  "localizacion": "Sliema, Malta",
  "tipo_vivienda": "habitacion",
  "duracion_min_meses": 3,
  "duracion_max_meses": 12,
  "wifi": true,
  "terraza": false,
  "garaje": false,
  "telefono_contacto": "+356 9911 2233",
  "email_contacto": "owner1@example.com",
  "publicado": true,
  "aprobado": true,
  "fecha_creacion": "2026-06-02T09:00:00Z",
  "imagenes": [
    {
      "id": 1,
      "imagen": null,
      "imagen_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
      "url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
      "orden": 0
    }
  ],
  "valoraciones": [
    {
      "id": 1,
      "anuncio": 1,
      "usuario": 5,
      "usuario_nombre": "student1",
      "puntuacion": 5,
      "comentario": "Moi boa ubicación.",
      "aprobado": true,
      "fecha_creacion": "2026-06-02T09:15:00Z"
    }
  ]
}
```

---

## 7.3. Crear anuncio

Crea un novo anuncio.

```http
POST /api/anuncios/
```

### Permisos

Usuario autenticado con rol:

```text
propietario
administrador
```

Os estudantes non poden publicar anuncios.

### Formato

Para permitir subida de imaxes reais, este endpoint acepta:

```http
multipart/form-data
```

### Campos

| Campo                | Tipo    | Obrigatorio | Descrición                                  |
| -------------------- | ------- | ----------: | ------------------------------------------- |
| `titulo`             | string  |          Si | Título do anuncio.                          |
| `descripcion`        | string  |          Si | Descrición completa.                        |
| `precio_mes`         | number  |          Si | Prezo mensual.                              |
| `localizacion`       | string  |          Si | Cidade ou zona.                             |
| `tipo_vivienda`      | string  |          Si | `habitacion`, `piso_completo` ou `estudio`. |
| `duracion_min_meses` | number  |         Non | Duración mínima.                            |
| `duracion_max_meses` | number  |         Non | Duración máxima.                            |
| `wifi`               | boolean |         Non | Se dispón de WiFi.                          |
| `terraza`            | boolean |         Non | Se dispón de terraza.                       |
| `garaje`             | boolean |         Non | Se dispón de garaxe.                        |
| `uploaded_images`    | file[]  |         Non | Unha ou varias imaxes.                      |

### Exemplo con `curl`

```bash
curl -X POST http://localhost:8000/api/anuncios/ \
  -H "Authorization: Token TOKEN_DO_PROPIETARIO" \
  -F "titulo=Bright Room in Sliema" \
  -F "descripcion=Habitación luminosa e ampla no centro de Sliema." \
  -F "precio_mes=450" \
  -F "localizacion=Sliema, Malta" \
  -F "tipo_vivienda=habitacion" \
  -F "duracion_min_meses=3" \
  -F "duracion_max_meses=12" \
  -F "wifi=true" \
  -F "terraza=false" \
  -F "garaje=false" \
  -F "uploaded_images=@/ruta/imaxe1.jpg" \
  -F "uploaded_images=@/ruta/imaxe2.jpg"
```

### Resposta correcta

```json
{
  "id": 10,
  "propietario": 3,
  "propietario_nombre": "owner1",
  "propietario_telefono": "+356 9911 2233",
  "propietario_email": "owner1@example.com",
  "titulo": "Bright Room in Sliema",
  "descripcion": "Habitación luminosa e ampla no centro de Sliema.",
  "precio_mes": "450.00",
  "localizacion": "Sliema, Malta",
  "tipo_vivienda": "habitacion",
  "duracion_min_meses": 3,
  "duracion_max_meses": 12,
  "wifi": true,
  "terraza": false,
  "garaje": false,
  "telefono_contacto": "+356 9911 2233",
  "email_contacto": "owner1@example.com",
  "publicado": true,
  "aprobado": false,
  "fecha_creacion": "2026-06-02T09:30:00Z",
  "imagenes": [
    {
      "id": 8,
      "imagen": "http://localhost:8000/media/anuncios/2026/06/02/imaxe1.jpg",
      "imagen_url": "",
      "url": "http://localhost:8000/media/anuncios/2026/06/02/imaxe1.jpg",
      "orden": 0
    }
  ],
  "valoraciones": []
}
```

### Nota

Os anuncios creados por propietarios quedan inicialmente con:

```json
"aprobado": false
```

O administrador pode aprobalos desde o panel.

---

## 7.4. Actualizar anuncio

Actualiza un anuncio existente.

```http
PATCH /api/anuncios/{id}/
```

### Permisos

| Rol           | Permiso                                            |
| ------------- | -------------------------------------------------- |
| Propietario   | Pode editar os seus propios anuncios.              |
| Administrador | Pode editar calquera anuncio e aprobar/desaprobar. |
| Estudante     | Non pode editar anuncios.                          |

### Exemplo JSON

```json
{
  "precio_mes": 500,
  "descripcion": "Descrición actualizada."
}
```

### Exemplo para aprobar anuncio como administrador

```json
{
  "aprobado": true
}
```

### Resposta correcta

```json
{
  "id": 10,
  "titulo": "Bright Room in Sliema",
  "precio_mes": "500.00",
  "aprobado": true
}
```

---

## 7.5. Eliminar anuncio

Elimina un anuncio.

```http
DELETE /api/anuncios/{id}/
```

### Permisos

| Rol           | Permiso                                 |
| ------------- | --------------------------------------- |
| Propietario   | Pode eliminar os seus propios anuncios. |
| Administrador | Pode eliminar calquera anuncio.         |
| Estudante     | Non pode eliminar anuncios.             |

### Resposta correcta

```http
204 No Content
```

### Erro por permisos

```json
{
  "error": "Operación denegada. Sin privilegios."
}
```

---

# 8. Valoracións e comentarios

---

## 8.1. Listar valoracións

Lista valoracións.

```http
GET /api/valoraciones/
```

### Permisos

Público.

### Comportamento

| Usuario       | Resultado                                  |
| ------------- | ------------------------------------------ |
| Anónimo       | Só valoracións aprobadas.                  |
| Estudante     | Só valoracións aprobadas.                  |
| Propietario   | Só valoracións aprobadas.                  |
| Administrador | Todas as valoracións, incluídas pendentes. |

### Resposta correcta

```json
[
  {
    "id": 1,
    "anuncio": 1,
    "usuario": 5,
    "usuario_nombre": "student1",
    "puntuacion": 5,
    "comentario": "Moi boa ubicación.",
    "aprobado": true,
    "fecha_creacion": "2026-06-02T09:15:00Z"
  }
]
```

---

## 8.2. Crear valoración

Permite que un estudante deixe unha valoración nun anuncio.

```http
POST /api/valoraciones/
```

### Permisos

Usuario autenticado con rol:

```text
estudiante
```

### Corpo da petición

```json
{
  "anuncio": 1,
  "puntuacion": 5,
  "comentario": "Moi boa ubicación e propietario atento."
}
```

### Resposta correcta

```json
{
  "id": 3,
  "anuncio": 1,
  "usuario": 5,
  "usuario_nombre": "student1",
  "puntuacion": 5,
  "comentario": "Moi boa ubicación e propietario atento.",
  "aprobado": false,
  "fecha_creacion": "2026-06-02T09:40:00Z"
}
```

### Nota

As valoracións novas quedan como:

```json
"aprobado": false
```

Deste modo, o administrador pode revisalas antes de que sexan visibles publicamente.

### Erro por rol incorrecto

```json
{
  "detail": "Solo las cuentas de estudiante pueden dejar valoraciones."
}
```

---

## 8.3. Aprobar ou ocultar valoración

Permite ao administrador moderar comentarios.

```http
PATCH /api/valoraciones/{id}/
```

### Permisos

Administrador.

### Aprobar comentario

```json
{
  "aprobado": true
}
```

### Ocultar comentario

```json
{
  "aprobado": false
}
```

### Resposta correcta

```json
{
  "id": 3,
  "anuncio": 1,
  "usuario": 5,
  "usuario_nombre": "student1",
  "puntuacion": 5,
  "comentario": "Moi boa ubicación e propietario atento.",
  "aprobado": true,
  "fecha_creacion": "2026-06-02T09:40:00Z"
}
```

---

## 8.4. Eliminar valoración

Elimina unha valoración.

```http
DELETE /api/valoraciones/{id}/
```

### Permisos

Administrador.

### Resposta correcta

```http
204 No Content
```

---

# 9. Solicitudes de contacto

---

## 9.1. Listar solicitudes

Obtén o historial de solicitudes de contacto.

```http
GET /api/solicitudes/
```

### Permisos

Usuario autenticado.

### Comportamento segundo rol

| Rol             | Resultado                                      |
| --------------- | ---------------------------------------------- |
| `estudiante`    | Ve as súas solicitudes realizadas.             |
| `propietario`   | Ve as solicitudes recibidas nos seus anuncios. |
| `administrador` | Ve todas as solicitudes.                       |

### Resposta correcta

```json
[
  {
    "id": 1,
    "estudiante": 5,
    "estudiante_nombre": "student1",
    "anuncio": 1,
    "anuncio_titulo": "Bright Room in Sliema",
    "anuncio_localizacion": "Sliema, Malta",
    "propietario_nombre": "owner1",
    "mensaje": "Hola, estoy interesado en la habitación.",
    "estado": "pendiente",
    "telefono_propietario_snapshot": "+356 9911 2233",
    "email_propietario_snapshot": "owner1@example.com",
    "fecha_creacion": "2026-06-02T10:00:00Z",
    "fecha_actualizacion": "2026-06-02T10:00:00Z"
  }
]
```

---

## 9.2. Crear solicitude de contacto

Rexistra unha solicitude de contacto dun estudante cara ao propietario dun anuncio.

```http
POST /api/solicitudes/
```

### Permisos

Usuario autenticado con rol:

```text
estudiante
```

### Corpo da petición

```json
{
  "anuncio": 1,
  "mensaje": "Hola, estoy interesado en este alojamiento. Llegaría a Malta en septiembre."
}
```

### Resposta correcta

```json
{
  "id": 2,
  "estudiante": 5,
  "estudiante_nombre": "student1",
  "anuncio": 1,
  "anuncio_titulo": "Bright Room in Sliema",
  "anuncio_localizacion": "Sliema, Malta",
  "propietario_nombre": "owner1",
  "mensaje": "Hola, estoy interesado en este alojamiento. Llegaría a Malta en septiembre.",
  "estado": "pendiente",
  "telefono_propietario_snapshot": "+356 9911 2233",
  "email_propietario_snapshot": "owner1@example.com",
  "fecha_creacion": "2026-06-02T10:05:00Z",
  "fecha_actualizacion": "2026-06-02T10:05:00Z"
}
```

### Nota sobre snapshot

A solicitude garda unha copia do teléfono e email do propietario no momento da solicitude:

```text
telefono_propietario_snapshot
email_propietario_snapshot
```

Isto permite manter un histórico aínda que o propietario modifique os seus datos máis tarde.

---

## 9.3. Actualizar estado dunha solicitude

Permite cambiar o estado dunha solicitude.

```http
PATCH /api/solicitudes/{id}/
```

### Permisos

| Rol           | Permiso                                                  |
| ------------- | -------------------------------------------------------- |
| Propietario   | Pode actualizar solicitudes recibidas nos seus anuncios. |
| Administrador | Pode actualizar calquera solicitude.                     |
| Estudante     | Non pode cambiar o estado.                               |

### Estados dispoñibles

```text
pendiente
respondida
cerrada
```

### Corpo da petición

```json
{
  "estado": "respondida"
}
```

### Resposta correcta

```json
{
  "id": 2,
  "estado": "respondida",
  "fecha_actualizacion": "2026-06-02T10:15:00Z"
}
```

---

# 10. Administración de usuarios

---

## 10.1. Listar usuarios

Lista usuarios da plataforma para administración.

```http
GET /api/admin/usuarios/
```

### Permisos

Administrador.

### Resposta correcta

```json
[
  {
    "id": 2,
    "username": "owner1",
    "email": "owner1@example.com",
    "rol": "propietario",
    "telefono": "+356 9911 2233",
    "activo": true
  },
  {
    "id": 3,
    "username": "student1",
    "email": "student1@example.com",
    "rol": "estudiante",
    "telefono": "+34 600 111 222",
    "activo": true
  }
]
```

---

## 10.2. Activar ou bloquear usuario

Permite modificar o estado dunha conta.

```http
PATCH /api/admin/usuarios/{id}/
```

### Permisos

Administrador.

### Bloquear usuario

```json
{
  "activo": false
}
```

### Activar usuario

```json
{
  "activo": true
}
```

### Resposta correcta

```json
{
  "id": 3,
  "activo": false
}
```

### Efecto do bloqueo

Se un usuario ten `activo=false`, non poderá iniciar sesión correctamente.

---

# 11. Endpoint alternativo de token

Django REST Framework tamén expón un endpoint estándar de token:

```http
POST /api-token-auth/
```

### Corpo da petición

```json
{
  "username": "student1",
  "password": "student1234"
}
```

### Resposta correcta

```json
{
  "token": "TOKEN_DO_USUARIO"
}
```

### Nota

No frontend da aplicación emprégase preferentemente:

```http
POST /api/login/
```

porque devolve tamén os datos básicos do usuario.

---

# 12. Códigos de estado HTTP

|                      Código | Significado                                   |
| --------------------------: | --------------------------------------------- |
|                    `200 OK` | Petición correcta.                            |
|               `201 Created` | Recurso creado correctamente.                 |
|            `204 No Content` | Recurso eliminado correctamente.              |
|           `400 Bad Request` | Datos incorrectos ou incompletos.             |
|          `401 Unauthorized` | Falta autenticación.                          |
|             `403 Forbidden` | Usuario autenticado sen permisos suficientes. |
|             `404 Not Found` | Recurso non atopado.                          |
| `500 Internal Server Error` | Erro interno do servidor.                     |

---

# 13. Exemplos de uso con `curl`

---

## 13.1. Iniciar sesión

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "password": "student1234"
  }'
```

---

## 13.2. Listar anuncios

```bash
curl http://localhost:8000/api/anuncios/
```

---

## 13.3. Filtrar anuncios

```bash
curl "http://localhost:8000/api/anuncios/?localizacion=Sliema&precio_max=600&wifi=true"
```

---

## 13.4. Crear anuncio como propietario

```bash
curl -X POST http://localhost:8000/api/anuncios/ \
  -H "Authorization: Token TOKEN_DO_PROPIETARIO" \
  -F "titulo=Modern Studio in St. Julian's" \
  -F "descripcion=Estudio moderno para estudantes Erasmus." \
  -F "precio_mes=650" \
  -F "localizacion=St. Julian's, Malta" \
  -F "tipo_vivienda=estudio" \
  -F "duracion_min_meses=1" \
  -F "duracion_max_meses=6" \
  -F "wifi=true" \
  -F "terraza=true" \
  -F "garaje=false" \
  -F "uploaded_images=@./imaxe.jpg"
```

---

## 13.5. Solicitar contacto como estudante

```bash
curl -X POST http://localhost:8000/api/solicitudes/ \
  -H "Authorization: Token TOKEN_DO_ESTUDIANTE" \
  -H "Content-Type: application/json" \
  -d '{
    "anuncio": 1,
    "mensaje": "Hola, estoy interesado en este alojamiento."
  }'
```

---

## 13.6. Enviar valoración como estudante

```bash
curl -X POST http://localhost:8000/api/valoraciones/ \
  -H "Authorization: Token TOKEN_DO_ESTUDIANTE" \
  -H "Content-Type: application/json" \
  -d '{
    "anuncio": 1,
    "puntuacion": 5,
    "comentario": "Boa ubicación e propietario atento."
  }'
```

---

## 13.7. Aprobar valoración como administrador

```bash
curl -X PATCH http://localhost:8000/api/valoraciones/3/ \
  -H "Authorization: Token TOKEN_DO_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "aprobado": true
  }'
```

---

## 13.8. Bloquear usuario como administrador

```bash
curl -X PATCH http://localhost:8000/api/admin/usuarios/3/ \
  -H "Authorization: Token TOKEN_DO_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "activo": false
  }'
```

---

# 14. Credenciais de proba

Se se executa o script de seed `create_data.py`, créanse os seguintes usuarios:

| Rol           | Usuario    | Contrasinal   |
| ------------- | ---------- | ------------- |
| Administrador | `admin`    | `admin1234`   |
| Propietario   | `owner1`   | `owner1234`   |
| Propietario   | `owner2`   | `owner1234`   |
| Estudante     | `student1` | `student1234` |
| Estudante     | `student2` | `student1234` |

---

# 15. Resumo de endpoints

| Método   | Endpoint                    | Descrición               | Permisos          |
| -------- | --------------------------- | ------------------------ | ----------------- |
| `POST`   | `/api/register/`            | Rexistro de usuario      | Público           |
| `POST`   | `/api/login/`               | Inicio de sesión         | Público           |
| `GET`    | `/api/me/`                  | Ver perfil propio        | Autenticado       |
| `PATCH`  | `/api/me/`                  | Actualizar perfil propio | Autenticado       |
| `GET`    | `/api/anuncios/`            | Listar anuncios          | Público           |
| `POST`   | `/api/anuncios/`            | Crear anuncio            | Propietario/Admin |
| `GET`    | `/api/anuncios/{id}/`       | Ver detalle de anuncio   | Público           |
| `PATCH`  | `/api/anuncios/{id}/`       | Editar anuncio           | Propietario/Admin |
| `DELETE` | `/api/anuncios/{id}/`       | Eliminar anuncio         | Propietario/Admin |
| `GET`    | `/api/valoraciones/`        | Listar valoracións       | Público           |
| `POST`   | `/api/valoraciones/`        | Crear valoración         | Estudante         |
| `PATCH`  | `/api/valoraciones/{id}/`   | Moderar valoración       | Administrador     |
| `DELETE` | `/api/valoraciones/{id}/`   | Eliminar valoración      | Administrador     |
| `GET`    | `/api/solicitudes/`         | Listar solicitudes       | Autenticado       |
| `POST`   | `/api/solicitudes/`         | Crear solicitude         | Estudante         |
| `PATCH`  | `/api/solicitudes/{id}/`    | Actualizar estado        | Propietario/Admin |
| `GET`    | `/api/admin/usuarios/`      | Listar usuarios          | Administrador     |
| `PATCH`  | `/api/admin/usuarios/{id}/` | Activar/bloquear usuario | Administrador     |
| `POST`   | `/api-token-auth/`          | Obter token DRF estándar | Público           |

---

# 16. Consideracións finais

A API está deseñada para separar claramente as responsabilidades de cada tipo de usuario:

* os estudantes poden buscar, contactar e valorar;
* os propietarios poden publicar e xestionar os seus anuncios;
* os administradores poden moderar contido e controlar usuarios.

Esta separación de permisos mellora a seguridade da aplicación e permite manter unha plataforma máis fiable para estudantes Erasmus que buscan aloxamento temporal.
