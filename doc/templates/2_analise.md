# Análise

Este documento ten como obxectivo describir os requirimentos do sistema, explicando que funcionalidades ofrecerá a aplicación e como se comportará en xeral.

---

## Tipos de usuarios

Na aplicación existirán diferentes tipos de usuarios segundo o nivel de acceso e as accións que poidan realizar dentro da plataforma.

- **Usuarios anónimos (non rexistrados):**  
Son aqueles que entran na web sen ter conta. Poderán ver información xeral da plataforma e consultar algúns anuncios, pero con limitacións. Non poderán contactar cos propietarios.

- **Usuarios rexistrados (estudantes):**  
Son estudantes que crean unha conta na plataforma. Poderán buscar aloxamentos con filtros, ver detalles completos dos anuncios e acceder ao número de teléfono dos propietarios. Tamén poderán deixar valoracións unha vez rematada a estancia.

- **Usuarios propietarios:**  
Son persoas ou axencias que ofrecen vivenda. Poderán publicar anuncios, editalos ou eliminalos, así como mostrar o seu número de teléfono para ser contactados.

- **Usuarios administradores:**  
Encárganse de xestionar o sistema. Poderán revisar anuncios, eliminar contido inapropiado, bloquear usuarios sospeitosos e moderar comentarios.

- **Usuarios bloqueados:**  
Son usuarios que incumpren normas da plataforma. Terán o acceso restrinxido e non poderán realizar accións ata que se revise o seu caso.

---

## Requirimentos funcionais

A aplicación deberá permitir as seguintes funcionalidades:

1. Rexistro de usuarios na plataforma diferenciando entre estudantes e propietarios.

2. Inicio de sesión seguro mediante usuario e contrasinal.

3. Edición do perfil de usuario (datos persoais básicos).

4. Publicación de anuncios por parte dos propietarios, incluíndo descrición, prezo, imaxes e características do aloxamento.

5. Modificación e eliminación de anuncios por parte dos propietarios.

6. Sistema de busca de aloxamentos con filtros (prezo, localización, duración da estancia, características, etc).

7. Visualización detallada dos anuncios con toda a información dispoñible.

8. Visualización do número de teléfono do propietario para que os estudantes poidan contactar directamente con el.

9. Sistema de valoracións e comentarios dos estudantes sobre os aloxamentos.

10. Panel de administración para xestionar usuarios, anuncios e comentarios.

11. Posibilidade de bloquear ou eliminar usuarios por parte dos administradores.

12. Sistema básico de reportes de anuncios ou usuarios sospeitosos.

> O sistema non incluirá mensaxería interna para simplificar o desenvolvemento, polo que o contacto realizarase directamente mediante teléfono entre estudantes e propietarios xa que vía que se me facía moi grande

---

## Requirimentos non funcionais

A aplicación tamén deberá cumprir unha serie de requisitos non relacionados directamente coas funcionalidades, pero que son importantes para o correcto funcionamento:

- **Seguridade:**  
A información dos usuarios debe estar protexida. As contrasinais gardaranse cifradas e haberá control de acceso segundo o tipo de usuario. O número de teléfono só será visible para usuarios rexistrados para evitar usos indebidos.

- **Usabilidade:**  
A interface debe ser sinxela e fácil de usar, xa que vai dirixida a estudantes que poden non ter moita experiencia en este tipo de plataformas.

- **Compatibilidade:**  
A aplicación deberá funcionar correctamente en distintos dispositivos (móbil, tablet e ordenador) e nos navegadores máis comúns.

- **Rendemento:**  
O sistema debería responder de forma rápida, sobre todo nas búsquedas de anuncios, ainda que pode haber algun pequeno retraso se hai moitos datos.

- **Escalabilidade:**  
A aplicación debería permitir no futuro engadir novas funcionalidades ou ampliar o número de usuarios sen ter que cambialo todo.

- **Disponibilidade:**  
Intentarase que a web estea dispoñible a maior parte do tempo, ainda que poden existir pequenas caídas por mantemento.

- **Accesibilidade:**  
Intentarase que a aplicación sexa usable por calquera persoa, ainda que non se vai profundizar moito neste aspecto nesta versión.