from __future__ import annotations

"""Utilidades criptográficas y de integridad.

Este módulo concentra operaciones pequeñas que se reutilizan en varios servicios:
- Hash SHA-256 para detectar PDFs duplicados.
- Hash SHA-256 del JSON descifrado para auditoría.

Mantenerlo separado ayuda a que el importador sea más legible y facilita pruebas.
"""

import hashlib


def sha256_bytes(data: bytes) -> str:
    """Devuelve el hash SHA-256 hexadecimal de una secuencia de bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    """Devuelve el hash SHA-256 hexadecimal de una cadena UTF-8."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
