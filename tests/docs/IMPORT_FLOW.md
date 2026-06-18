# Flujo de importación PDF

1. El usuario selecciona uno o muchos PDFs.
2. El sistema calcula `pdf_sha256` del archivo completo.
3. Si el hash ya existe en `reports`, se marca como duplicado.
4. Se busca el marcador `%%SUPERVISION_SEGURA_JSON_ENCRYPTED_BASE64:`.
5. Se decodifica el payload Base64.
6. Se descifra el JSON usando AES-256-GCM con llave derivada por SHA-256 de `DATA_KEY`.
7. Se validan los campos mínimos del formato.
8. Se guarda información normalizada en `reports`, `answers`, `employees` y `questions`.
9. Se guarda el PDF completo como BLOB en `evidence`.
10. Se guarda también el payload cifrado original y el JSON descifrado para auditoría controlada.
