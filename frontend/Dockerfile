FROM node:20-alpine

WORKDIR /app

COPY package.json .
RUN npm install
RUN chmod -R 755 node_modules/.bin/

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]