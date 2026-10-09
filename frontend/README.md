# Frontend de Control Taller

El flujo completo de instalación, desarrollo y publicación está en
[la guía del proyecto](../docs/GUIA_PARA_TU_HERMANO.md).

Para desarrollo usar `docker compose --profile dev up -d --build` desde la raíz,
después de configurar los `.env` y la base de prueba. Vite sirve la aplicación
en `http://localhost:5174` y reenvía `/api` al backend dentro de Docker.

Para comprobar el frontend fuera de Docker, desde esta carpeta:

```sh
npm ci --include=optional
npm run build
```

Los scripts disponibles son `dev`, `build`, `serve` y `start`.
El repo usa Vite; `serve` ejecuta una vista previa del build y no reemplaza el
proxy ni el despliegue HTTPS de producción. La instalación limpia se verificó
con Node 20.19.0. En PowerShell puede usarse `npm.cmd`.
