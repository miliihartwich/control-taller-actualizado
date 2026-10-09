# ---------- build stage ----------
FROM node:20-slim AS build
WORKDIR /app

# Evita que Rollup busque binarios nativos
ENV ROLLUP_NO_NATIVE=1

COPY package*.json ./
RUN npm ci --include=optional --no-audit --no-fund
COPY . .
# Si servís bajo subcarpeta, setea BASE=/subcarpeta; por defecto "/"
ARG BASE=/
ENV BASE=$BASE
RUN npm run build

# ---------- runtime stage ----------
FROM nginx:alpine AS runtime
# Copiamos el build de Vite
COPY --from=build /app/dist /usr/share/nginx/html
# Nginx config con SPA + proxy a backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
