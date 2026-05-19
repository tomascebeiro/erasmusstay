# Proxecto de fin de ciclo DAW

Este proxecto é unha plataforma web deseñada para axudar a estudantes Erasmus que veñan a Malta a atopar aloxamento de forma segura e sinxela. A idea xorde da necesidade real de contar cunha alternativa fiable aos grupos de Facebook e WhatsApp, onde abundan os anuncios enganosos e os prezos abusivos.

A plataforma permite aos estudantes buscar e filtrar habitacións e pisos por zona, prezo e dispoxiñbilidade, mentres que os propietarios e axencias poden publicar os seus aloxamentos. O sistema está construido cunha arquitectura moderna: frontend en Vue.js con Tailwind CSS, backend en Django con PostgreSQL, e despregado mediante Docker.

O obxectivo final é crear un espazo de confianza onde estudantes e propietarios poidan conectar de forma transparente, eliminando intermediarios pouco fiables e reducindo o risco de estafa.

## Instalación/Posta en marcha

Requisitos previos: ter instalado **Docker** e **Docker Compose**.

```bash
# 1. Clonar o repositorio
git clone https://gitlab.iessanclemente.net/dawo/a25tomascc.git
cd a25tomascc

# 2. Copiar e configurar as variables de entorno
cp .env.example .env

# 3. Levantar os contedores
docker-compose up --build
```

A aplicación creará automaticamente a base de datos e cargara os datos iniciais de proba.

**Credenciais de proba:**
- Admin: `admin` / `admin1234`
- Propietario: `propietario1` / `test1234`
- Estudante: `estudante1` / `test1234`

## Uso

Unha vez levantados os contedores, accede á aplicación nos seguintes enderezos:

- **Aplicación web:** http://localhost:5173
- **API REST:** http://localhost:8000/api/
- **Panel admin Django:** http://localhost:8000/admin/

## Sobre a persoa autora

Són Tomás Cebeiro Cabo, estudante do ciclo superior de Desenvolvemento de Aplicacións Web (DAW) no IES San Clemente. Teño experiencia práctica en desenvolvemento web con WordPress, Django e Vue.js, xestión de comunidades online e creación de contido dixital. Decanteíme por este proxecto porque coñezo de primeira man o problema que resolve: pasei por esa situación buscando aloxamento en Malta e quixen darlle unha solución real a outros estudantes.

Contacto: a25tomascc@iessanclemente.net

## Licencia

Este proxecto está licenciado baixo a licencia **MIT**. Consulta o ficheiro [LICENSE](LICENSE) na raíz do repositorio para máis información.

## Guía de contribución

As contribucións son benvidas. Podes colaborar:

- Reportando erros ou suxerindo melloras abrindo un **Issue**.
- Facendo un **fork**, creando unha rama coa túa mellora e enviando un **Merge Request**.
- Mellorando a documentación ou engadindo tests automatizados.

Asegúrate de que o código segue o estilo do proxecto e os tests pasan antes de enviar o Merge Request.

## Memoria

1. [Estudo preliminar](doc/templates/1_estudo_preliminar.md)
2. [Análise](doc/templates/2_analise.md)
3. [Deseño](doc/templates/3_deseno.md)
4. [Planificación e Orzamento](doc/templates/a3_orzamento.md)
5. [Codificación e Probas](doc/templates/4_codificacion_probas.md)
6. [Futuro e comercialización](doc/templates/5_manuais.md)