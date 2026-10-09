# Ficha de entrega del servidor

Completar una copia privada en `.local/FICHA_DEL_SERVIDOR.md` o fuera del repo.
Registrar ubicaciones y responsables; guardar contraseñas y claves en el canal
privado acordado, sin incluirlas en esta ficha ni en GitHub.

| Dato | Valor que debe completar la persona que entrega el proyecto |
| --- | --- |
| Responsable actual y contacto | COMPLETAR |
| Cuenta GitHub del nuevo responsable | COMPLETAR |
| URL de producción | El repo configura `https://app.hartwich.com.uy`; confirmar |
| Cuenta AWS / identificador de instancia | COMPLETAR |
| Región de producción | El documento existente indica Ohio, `us-east-2`; confirmar |
| Región de staging | El documento existente indica Virginia, `us-east-1`; confirmar si sigue existiendo |
| Host/IP para SSH | COMPLETAR PRIVADAMENTE; el documento aporta una IP de referencia |
| Usuario Linux para SSH | El documento registra `ec2-user`; confirmar |
| Puerto SSH / bastión / VPN, si aplica | COMPLETAR |
| Ubicación de la clave SSH o acceso personal habilitado | COMPLETAR UBICACIÓN, sin contenido de la clave |
| Carpeta original del proyecto en producción | COMPLETAR RUTA ABSOLUTA |
| Comando Docker original, incluyendo todos los `-f`, `-p` y perfiles | COMPLETAR |
| Nombre exacto del proyecto Compose | COMPLETAR SEGÚN LABEL DE LOS CONTENEDORES |
| Archivos Compose originales y overrides | COMPLETAR |
| Contenedores backend / frontend / DB | El repo usa `backend_controltaller`, `frontend_controltaller`, `postgres_controltaller`; confirmar |
| Red Docker que usa el backend | COMPLETAR |
| Host de la DB / nombre de DB / versión mayor de PostgreSQL | Endpoint privado por completar; documento: `controltaller`, usuario `postgres`, puerto `5432`; versión pendiente |
| DB en Docker o servicio externo, por ejemplo RDS | El documento indica Amazon RDS en `us-east-2`; confirmar conexión efectiva |
| Nombre real del volumen o ubicación real de los datos PostgreSQL | COMPLETAR |
| Ubicación original de los `.env` de producción | COMPLETAR |
| TLS hacia PostgreSQL / valor `PGSSLMODE` efectivo | Documento indica `sslmode=require`; confirmar |
| Certificados HTTPS y renovación automática | El repo monta `/etc/letsencrypt`; confirmar mecanismo de renovación |
| Forma de descargar GitHub desde el servidor | Repo público, deploy key u otro acceso configurado; confirmar |
| Tareas programadas / cron / timers / backups automáticos | COMPLETAR, incluyendo rutas que dependan del directorio viejo |
| Ubicación de los respaldos y procedimiento de recuperación probado | COMPLETAR |
| Archivo privado de base de prueba y cuenta de prueba | COMPLETAR UBICACIONES, sin credenciales |
| Directorio de operación / releases, luego de la primera adopción | COMPLETAR |
| Commit publicado actualmente / release anterior | COMPLETAR |
| Tiempo de mantenimiento acordado para publicar | COMPLETAR |

La guía completa está en [GUIA_PARA_TU_HERMANO.md](GUIA_PARA_TU_HERMANO.md).
