# Diagnóstico de PDFs

El Manager lee el mismo marcador que el script de prueba:

```text
%%SUPERVISION_SEGURA_JSON_ENCRYPTED_BASE64:
```

Si aparece un error parecido a `FileNotFoundError`, no es problema del cifrado: Python no encontró el PDF en la ruta indicada.

## Prueba rápida desde consola

```bat
python tools_decrypt_pdf.py "C:\ruta\al\SUPERVISION_SEGURA_2026_06_18_NOMBRE.pdf"
```

## Errores comunes

- **No se encontró el archivo**: la ruta o el nombre del PDF no coinciden.
- **PDF no compatible**: el archivo no fue generado por la APK o fue reimpreso/editado.
- **JSON encontrado, pero no se pudo descifrar**: `DATA_KEY` no coincide con la clave usada por la APK o el PDF fue alterado.
- **Duplicado**: el hash SHA-256 del PDF ya existe en la base SQLite.
