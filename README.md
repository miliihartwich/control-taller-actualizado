# Control Taller

Aplicación para gestionar órdenes de trabajo, clientes, empleados, servicios,
compras e intervenciones. Incluye un backend Flask con PostgreSQL y un frontend
Vue con Vite.

## Configuración

1. Copiar `.env.example` a `.env` y `backend/.env.example` a `backend/.env`.
2. Definir las contraseñas y una clave aleatoria para `JWT_SECRET_KEY`.
3. Usar la misma contraseña en `POSTGRES_PASSWORD` y en `DATABASE_URL`.
   Dentro de Docker el host de PostgreSQL es `db`; fuera de Docker es `localhost`.

Los archivos `.env` contienen la configuración privada de cada instalación y
están excluidos de Git. Los archivos `.env.production` del frontend contienen
únicamente configuración pública.

## Dependencias y compilación

El backend utiliza las dependencias de `backend/requirements.txt`:

```sh
python -m pip install -r backend/requirements.txt
```

Para instalar y compilar el frontend:

```sh
cd frontend
npm ci
npm run build
```

Para ejecutar el frontend en desarrollo, usar `npm run dev`.
Los archivos `docker-compose.yml` y `docker-compose.dev.yml` contienen la
configuración de los contenedores.

## Comprobación de la base de datos local

Configurar `PGPASSWORD` y, si corresponde, las demás variables `PG*` en el
archivo `.env` de la raíz. Luego ejecutar:

```sh
python testconnection.py
```

Las imágenes Docker exportadas y los paquetes ZIP/TAR de despliegue se generan
localmente y están excluidos del repositorio. El código, los recursos del
frontend, las dependencias y los archivos de configuración necesarios para
reconstruir el proyecto están incluidos.
