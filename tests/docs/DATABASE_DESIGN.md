# Diseño de base de datos

La base se diseñó para mantener evidencia y análisis separados.

- `reports`: datos normalizados para filtros y dashboard.
- `answers`: cada respuesta SI/NO/CAMBIO.
- `evidence`: PDF completo BLOB, JSON cifrado original y JSON descifrado.
- `employees`: catálogo de empleados por ID.
- `projects`: permite trabajar proyecto por proyecto.

Esto permite velocidad de consulta sin perder trazabilidad.
