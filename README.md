# Control Taller

Aplicación para gestionar órdenes de trabajo, clientes, empleados, servicios,
compras e intervenciones. Incluye un backend Flask con PostgreSQL y un frontend
Vue con Vite.

## Recibir el proyecto y publicar cambios

Empezar por la [guía completa para el nuevo responsable](docs/GUIA_PARA_TU_HERMANO.md).
Explica cómo preparar otra computadora, importar una base de prueba, editar,
probar, trabajar con GitHub y actualizar producción en AWS por SSH y Docker,
incluyendo la primera adopción del repositorio y cómo volver a la versión anterior.

El documento de referencia aportado describe EC2 en Ohio, acceso mediante WSL/SSH,
Docker con `sudo` y una base PostgreSQL en RDS. Los datos concretos de acceso deben
guardarse en la ficha privada y verificarse antes de publicar.

Completar también una copia privada de la
[ficha del servidor](docs/FICHA_DEL_SERVIDOR.example.md).
Hace falta recibir acceso a GitHub/SSH, la configuración real del servidor y una
base de prueba: el repositorio todavía no contiene esquema SQL ni datos iniciales.

## Configuración

1. Copiar `.env.example` a `.env` y `backend/.env.example` a `backend/.env`.
2. Definir las contraseñas y una clave aleatoria para `JWT_SECRET_KEY`.
3. En desarrollo Docker, usar la misma contraseña en `POSTGRES_PASSWORD` y en `DATABASE_URL`.
   Dentro de Docker el host de PostgreSQL es `db`; fuera de Docker es `localhost`.

Para desarrollo, seguir el perfil Docker `dev` de la guía. El proxy Vite actual
apunta a `http://backend:8000` dentro de Docker.

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

Para ejecutar el entorno de desarrollo, usar
`docker compose --profile dev up -d --build` desde la raíz, siguiendo la guía.
Los archivos `docker-compose.yml` y `docker-compose.dev.yml` contienen la
configuración de los contenedores; el segundo levanta solamente una DB alternativa.
`docker-compose.release.yml` se utiliza explícitamente junto al Compose base
para etiquetar las imágenes de producción por commit, según la guía.

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
