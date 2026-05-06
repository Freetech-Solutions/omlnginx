# Changelog Técnico: OMniLeads NGINX (oml-773-dev-oml-3)

## Resumen Ejecutivo
La rama `oml-773-dev-oml-3` introduce una refactorización crítica en la configuración y despliegue del componente NGINX, orientada a mejorar la resiliencia, la escalabilidad y la modernización de la plataforma OMniLeads 3.0. Se optimizó la resolución dinámica de dependencias (Lazy Loading), evitando caídas del proxy durante el arranque, y se implementó una abstracción agnóstica para el almacenamiento multimedia compatible con S3/MinIO.

## Nuevas Funcionalidades (Features)
- **Soporte para Kamailio WebSockets:** Se añadió la nueva ruta `/kamailio-ws/` para enrutar tráfico WebSocket directamente hacia el nuevo proxy Kamailio, integrándose con la arquitectura de microservicios de telefonía.
- **Abstracción de Almacenamiento Multimedia (MinIO/S3):** Se reemplazó la configuración condicional por una ruta estandarizada (`/minio/`) que actúa como proxy genérico para buckets S3 o MinIO, facilitando arquitecturas híbridas o locales.
- **Soporte Nativo de DNS para Podman/Netavark:** Se incorporó la auto-detección del servidor DNS del orquestador (inyectado como `resolver` global), garantizando la conectividad entre contenedores sin requerir nombres de host estáticos a nivel de sistema operativo.

## Cambios Arquitectónicos / Técnicos
- **Mejora en el uso de variables (Lazy Loading):** 
  - Se migró de una declaración estática (donde el servicio fallaba si el backend no estaba disponible en el arranque) al uso dinámico de variables de NGINX (`set $django_backend ...; proxy_pass http://$django_backend;`).
  - Esto fuerza a NGINX a resolver los DNS en tiempo de petición en lugar de tiempo de arranque, mejorando drásticamente la resiliencia en reinicios o redes lentas.
- **Mejora en el uso de buckets:** 
  - Se eliminó la lógica acoplada a `CALLREC_DEVICE != "s3-aws"`.
  - Ahora se procesan las cabeceras S3 (`S3_HOST_HEADER`) dinámicamente y se abstrae el upstream S3 para un ruteo más limpio y mantenible.
- **Reestructuración de Archivos de Configuración:** 
  - Se modularizó la configuración creando un servidor "Padre" (`00-oml-app.conf`) que agrupa la terminación SSL y las redirecciones de puerto 80 a 443.
  - El mapa de actualizaciones WebSocket se movió a un bloque dedicado (`websocket_upgrade.conf`).
- **Actualización de Dependencias:** Se actualizó la imagen base en el `Dockerfile` de `nginx:1.23.2-alpine` a `nginx:1.29.4-alpine`, incorporando los últimos parches de seguridad y rendimiento.

## Impacto y Consideraciones para Despliegue

### Para el Equipo de QA
- **Pruebas de Resiliencia:** Verificar que si los contenedores backend (Django, Daphne, Kamailio) se reinician o tardan en iniciar, el contenedor de NGINX ya no se cae, sino que devuelve un error temporal (502/504) y se recupera automáticamente cuando el servicio vuelve a estar disponible.
- **Validación de WebSockets:** Probar intensivamente la nueva ruta de WebSockets para Kamailio (`/kamailio-ws/`) asegurando que la conexión y el audio WebRTC fluyan correctamente.
- **Verificación de Grabaciones:** Validar la reproducción de grabaciones de llamadas a través de la nueva ruta `/minio/`, asegurando que el proxy a S3/MinIO funciona sin problemas de CORS ni cabeceras.

### Para el Equipo de DevOps
- **Nuevas Variables de Entorno Requeridas:** El arranque de NGINX fallará explícitamente si faltan estas nuevas variables:
  - `WEBSOCKETS_HOSTNAME` y `WEBSOCKETS_PORT`
  - `KAMAILIO_HOSTNAME` y `KAMAILIO_PORT`
  - `S3_ENDPOINT`
- **Cambio en Resolución DNS:** Asegurarse de que el entorno despliega NGINX con acceso al DNS interno de Podman/Docker. El script detecta el DNS leyendo `/etc/resolv.conf`, por lo que redes personalizadas (como Netavark) serán soportadas nativamente.
- **Despliegue y Migraciones:** No se requieren migraciones de base de datos para este componente, pero el aprovisionamiento debe asegurar que las nuevas variables del inventario (`inventory.yml`) se pasen correctamente al despliegue del contenedor de NGINX.
