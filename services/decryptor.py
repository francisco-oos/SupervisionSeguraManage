from __future__ import annotations

"""Extracción y descifrado del JSON embebido en los PDFs Android.

La app Android genera el PDF visual y después agrega una línea al final del
archivo con este formato:

    %%SUPERVISION_SEGURA_JSON_ENCRYPTED_BASE64:<payload_en_base64>

El payload decodificado es un JSON con ``iv_b64`` y ``data_b64``. ``data_b64``
contiene el JSON real cifrado con AES-256-GCM. La llave se deriva igual que en
Kotlin:

    SHA-256(DATA_KEY) -> 32 bytes para AESGCM

Este módulo está diseñado para que el Manager no dependa del texto visible del
PDF ni del QR. Lo único obligatorio es que el PDF conserve el marcador agregado
por la APK original.
"""

import base64
import hashlib
import json
from dataclasses import dataclass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config.settings import DATA_KEY, MARKER


@dataclass
class ExtractedPayload:
    """Resultado completo de la extracción/descifrado de una evidencia PDF."""

    encrypted_payload: dict
    decrypted_json: dict
    encrypted_payload_bytes: bytes
    decrypted_json_text: str


class DecryptError(Exception):
    """Error controlado para mostrar mensajes entendibles al usuario."""


class SupervisionDecryptor:
    """Servicio encargado de leer el marcador y descifrar el JSON."""

    def __init__(self, data_key: str = DATA_KEY, marker: str = MARKER):
        self.data_key = data_key
        self.marker = marker
        self.marker_bytes = marker.encode("ascii")

    def extract_marker_payload(self, pdf_bytes: bytes) -> bytes:
        """Extrae del PDF el payload Base64 agregado por la APK.

        Se busca primero por bytes para evitar problemas con archivos binarios.
        Después se toma el primer token posterior al marcador, tal como hacía el
        script de prueba ``decifrado_JSON.PY``.
        """
        pos = pdf_bytes.find(self.marker_bytes)
        if pos == -1:
            raise DecryptError(
                "PDF no compatible: no contiene el marcador de Supervisión Segura. "
                "Verifica que sea un PDF generado directamente por la APK y que no haya sido reimpreso, editado o comprimido."
            )

        raw_tail = pdf_bytes[pos + len(self.marker_bytes):]
        payload_token = raw_tail.strip().split()[0] if raw_tail.strip() else b""
        if not payload_token:
            raise DecryptError("El marcador existe, pero el payload Base64 está vacío.")

        try:
            return base64.b64decode(payload_token, validate=False)
        except Exception as exc:
            raise DecryptError(f"No se pudo decodificar el payload Base64: {exc}") from exc

    def decrypt_payload(self, payload_bytes: bytes) -> ExtractedPayload:
        """Descifra el payload AES-256-GCM y devuelve el JSON original."""
        try:
            encrypted_payload = json.loads(payload_bytes.decode("utf-8"))

            if encrypted_payload.get("crypto") != "AES-256-GCM":
                raise DecryptError("El payload no indica cifrado AES-256-GCM.")

            required = ["iv_b64", "data_b64"]
            missing = [field for field in required if field not in encrypted_payload]
            if missing:
                raise DecryptError(f"Payload cifrado incompleto. Faltan campos: {', '.join(missing)}")

            iv = base64.b64decode(encrypted_payload["iv_b64"])
            ciphertext = base64.b64decode(encrypted_payload["data_b64"])
            key = hashlib.sha256(self.data_key.encode("utf-8")).digest()

            plain = AESGCM(key).decrypt(iv, ciphertext, None)
            json_text = plain.decode("utf-8")
            json_data = json.loads(json_text)

            return ExtractedPayload(
                encrypted_payload=encrypted_payload,
                decrypted_json=json_data,
                encrypted_payload_bytes=payload_bytes,
                decrypted_json_text=json_text,
            )
        except DecryptError:
            raise
        except Exception as exc:
            raise DecryptError(
                "JSON encontrado, pero no se pudo descifrar. Posibles causas: DATA_KEY diferente a la APK, "
                "PDF alterado después de generarse, o payload incompleto. "
                f"Detalle técnico: {exc}"
            ) from exc

    def extract_from_pdf_bytes(self, pdf_bytes: bytes) -> ExtractedPayload:
        """Flujo completo: PDF bytes -> payload cifrado -> JSON descifrado."""
        payload = self.extract_marker_payload(pdf_bytes)
        return self.decrypt_payload(payload)
