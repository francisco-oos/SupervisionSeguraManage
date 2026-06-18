# Supervisión Segura Manager V1.0.0

Sistema Windows en Python para importar PDFs generados por la app Android Supervisión Segura, extraer el JSON cifrado, descifrarlo, almacenar evidencia en SQLite y generar estadísticas.

## Funciones incluidas

- Interfaz PySide6 profesional.
- Proyectos.
- Importación de uno o muchos PDF.
- Extracción del marcador `%%SUPERVISION_SEGURA_JSON_ENCRYPTED_BASE64:`.
- Descifrado AES-256-GCM.
- Guardado de PDF original como BLOB en SQLite.
- Guardado de payload cifrado y JSON descifrado.
- Hash SHA-256 de PDF y JSON.
- Tablas relacionales para reportes, empleados, respuestas y evidencias.
- Dashboard con métricas y gráficas.
- Exportación de PDF desde base de datos.
- Exportación Excel base.
- Trial local de 30 días.

## Instalación

```powershell
cd SupervisionSeguraManager
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Compilar EXE

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name SupervisionSeguraManager app.py
```

## Seguridad

El sistema guarda tres capas:

1. Datos normalizados para dashboard y consultas.
2. JSON cifrado original como evidencia digital.
3. PDF completo como BLOB.

La clave `DATA_KEY` debe coincidir con la app Android. En producción se recomienda moverla fuera del código fuente.

## Próximas mejoras

- Reporte gerencial PDF.
- Exportación controlada con licencia.
- Comparativa entre proyectos.
- Usuarios y contraseña.
- Firma digital de base de datos.
