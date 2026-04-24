FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --prefer-offline --no-audit

COPY . .

RUN chmod +x node_modules/.bin/*

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]