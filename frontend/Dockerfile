# 1. Fase de construcción (Builder)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Esto genera la carpeta 'dist' (o 'build' dependiendo de tu framework)
RUN npm run build

# 2. Fase de servidor (Nginx)
FROM nginx:alpine
# Copiamos lo que se construyó en la fase anterior al servidor Nginx
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]