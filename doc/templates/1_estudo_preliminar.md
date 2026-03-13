# Estudo preliminar - Anteproxecto


## Descrición do proxecto
O proxecto consiste no desenvolvemento dunha plataforma web para a busca e xestión de aloxamento dirixida a estudantes Erasmus que se desprazan a Malta. A aplicación permitirá poñer en contacto estudantes que buscan aloxamento temporal con propietarios ou axencias que ofrecen pisos ou habitacións adaptadas a estancias de 3 a 6 meses. 
O obxectivo principal do proxecto é facilitar un sistema seguro e especializado que permita aos estudantes atopar aloxamento de forma fiable, reducindo os riscos de fraude e as dificultades habituais asociadas á procura de vivenda nun país estranxeiro. 
A plataforma terá un frontend independente, un backend con Django e unha base de datos relacional, todo creado con Docker.


### Xustificación do proxecto
A idea do proxecto xorde das dificultades que tiven como estudante de Erasmus fai 2 anos á hora de atopar aloxamento en Malta. Os estudantes necesitan utilizar grupos de WhatsApp e Facebook onde existe unha alta probabilidade de atopar información incompleta, prezos elevados ou mesmo estafas. 
O principal obxectivo da posta en marcha deste proxecto é resolver o problema da falta de plataformas especializadas en aloxamento para estudantes Erasmus, ofrecendo unha solución adaptada ás súas necesidades específicas, con maior seguridade e menos riscos.


### Funcionalidades do proxecto
A aplicación ofrecerá, de forma xeral, as seguintes funcionalidades:

1. **Rexistro e autenticación de usuarios**:
   - Rexistro de diferentes roles: estudantes, propietarios e administradores. Cada rol terá permisos específicos adaptados ás súas necesidades. O sistema de autenticación será seguro e facilitará o acceso á plataforma.
  
2. **Publicación e xestión de anuncios**:
   - Os propietarios poderán publicar anuncios de aloxamento, incluíndo descricións, imaxes e condicións.
   - Os administradores poderán revisar, aprobar ou eliminar anuncios. 

3. **Sistema de busca avanzada de aloxamentos**:
   - Filtros personalizables: busca por cidade, tipo de vivenda, prezo, duración da estancia, e outros parámetros (Se ten internet, terraza, garage etc).
   - Resultados detallados: visualización de anuncios con imaxes e descricións detalladas.

4. **Sistema de contacto entre estudantes e propietarios**:
   - En lugar de realizar reservas directas a través da plataforma, o sistema permitirá o contacto directo entre estudantes e propietarios para organizar as estancias. 
   - Os estudantes poderán enviar mensaxes de contacto aos propietarios para solicitar máis información ou acordar as condicións.
   - O sistema manterá un historial das solicitudes realizadas para facilitar o seguimento.

5. **Sistema de valoracións e comentarios sobre os aloxamentos**:
   - Os estudantes poderán deixar valoracións e comentarios sobre os aloxamentos unha vez finalizada a súa estancia. Isto permitirá crear unha comunidade de confianza.

6. **Panel de administración para moderar contidos e usuarios**:
   - O panel de administración incluirá funcionalidades para que os administradores poidan xestionar os usuarios, moderar os anuncios e os comentarios, tamém bloquear usuarios sospeitosos.
   - A interface de administración tamén permitirá a xestión de filtros de búsqueda, categorías de vivenda, e outras configuracións do sistema.

7. **Interface responsiva adaptada a dispositivos móbiles**:
   - A interface será sinxela e amigable, adaptada a todos os dispositivos, garantindo unha boa experiencia de usuario tanto en dispositivos móbiles como en escritorios.


### Estudo de necesidades. Proposta de valor respecto ao que hai no mercado
Actualmente existen aplicacións como Airbnb, Idealista ou grupos de Facebook que ofrecen solucións parciais ao problema, pero estas plataformas:

- Non están enfocadas exclusivamente a estudantes.
- Non teñen filtros adaptados a estancias académicas ou necesidades específicas dos estudantes Erasmus.
- Non ofrecen mecanismos de verificación para evitar estafas e fraudes.

A proposta de valor desta aplicación reside en ser unha plataforma de nicho, deseñada especificamente para estudantes Erasmus, cunha interface sinxela, funcionalidades adaptadas ao seu contexto e unha maior seguridade nas transaccións e contactos.

### Persoas destinatarias
A aplicación está dirixida principalmente a:

- **Persoas**: Estudantes universitarios ou de formación profesional que participan en programas Erasmus.
- **Empresas e profesionais**: Propietarios de vivendas e axencias inmobiliarias que ofrecen aloxamento temporal.
- **Entidades educativas ou intermediarios**: Institucións ou persoas que colaboran coa mobilidade internacional.

 

### Promoción
A idea é dar a coñecer a web falando coas universidades e cos coordinadores Erasmus para que a recomenden ós estudantes que veñen a Malta. Tamén se usarán redes sociais e grupos de Facebook/WhatsApp de Erasmus en Malta, explicando que aquí hai máis seguridade e menos estafas que nos anuncios soltos.


### Modelo de negocio

O modelo de negocio baséase en subscricions para propietarios e axencias inmobiliarias, adaptado o nicho de estudantes Erasmus en Malta.

#### Principios xerais
- **Gratuíto para estudantes**: Rexistro, busca de aloxamento, contacto con propietarios e valoracións sen custo.
- **Propietarios e axencias**: Publican anuncios de forma gratuíta, pero teñen **plans de suscrición** para mellorar visibilidade e acceder a máis funcionalidades.

#### Estructura de plans de suscrición

1. **Plan Básico (Gratuito)**
   - 1-2 anuncios activos simultáneamente.
   - Visibilidade estándar nas búsquedas.
   - Acceso á mensaxería interna e panel sinxelo.

2. **Plan Estándar (Mensual/Trimestral)**
   - Ata 5-10 anuncios activos.
   - Maior prioridade nas buscas.
   - Estatísticas básicas, máis fotos e mellores descricións.

3. **Plan Premium (Mensual/Trimestral)**
   - Ata 20 ou máis anuncios activos.
   - Máxima prioridade nas búsquedas, destacamento de anuncios.
   - Estatísticas avanzadas.
   - Soporte dedicado e opción de engadir a marca da axencia nos anuncios.


## Requirimentos

Servidor web para o despregamento da aplicación.
Servidor de base de datos dedicado.
Contedores Docker.

#Backend
Linguaxe de programación: Python.
Framework principal: Django.
Base de datos relacional: PostgreSQL.
Creado con Docker.

#Frontend
Framework Vue.
Interface responsiva e adaptada a dispositivos móbiles.
Utilización de Docker.

