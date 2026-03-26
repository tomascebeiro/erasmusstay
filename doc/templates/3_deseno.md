# Deseño

## Esquema (boceto ou wireframe)

A continuación móstranse os wireframes das principais pantallas da aplicación. Estes representan unha primeira aproximación da interface e poden sufrir cambios durante o desenvolvemento.

### Vista principal (Home)

![Home](img/Home.png)

Nesta pantalla principal o usuario pode realizar búsquedas de aloxamento introducindo filtros como localización, prezo ou duración da estancia. Tamén se mostran algúns anuncios destacados.

---

### Lista de anuncios

![Lista](img/listaAnuncios.png)

Nesta vista móstranse os resultados da búsqueda. O usuario pode aplicar filtros na barra lateral e ver diferentes anuncios dispoñibles con información básica como prezo e localización.

---

### Detalle de anuncio

![Detalle](img/DetalleyPublicar.png)

Nesta pantalla móstrase a información completa dun aloxamento, incluíndo descrición, características e imaxes. Tamén se inclúe o número de teléfono do propietario para poder contactar directamente con el.

---

### Publicar anuncio

![Publicar](img/DetalleyPublicar.png)

Nesta vista os propietarios poden crear novos anuncios introducindo información como título, descrición, prezo, localización, características e imaxes.

---

## Identidade visual 

A aplicación terá un deseño sinxelo e moderno, orientado a facilitar o uso por parte dos estudantes.

- **Cores:** Empregaranse principalmente tons azuis e brancos para transmitir confianza e claridade.
- **Tipografía:** Utilizaranse fontes sans-serif para mellorar a lexibilidade.
- **Estilo:** Interface limpa e minimalista, evitando sobrecargar a pantalla con demasiada información.

---

## Diagrama de Bases de Datos

A continuación móstrase un diagrama entidade-relación simplificado da base de datos do sistema:

```mermaid
erDiagram
    USUARIO {
        int id
        string nome
        string email
        string password
        string rol
        string telefono
    }

    ANUNCIO {
        int id
        string titulo
        string descripcion
        float prezo
        string localizacion
        int usuario_id
    }

    VALORACION {
        int id
        int puntuacion
        string comentario
        int usuario_id
        int anuncio_id
    }

    USUARIO ||--o{ ANUNCIO : publica
    USUARIO ||--o{ VALORACION : escribe
    ANUNCIO ||--o{ VALORACION : recibe