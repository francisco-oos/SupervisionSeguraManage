from __future__ import annotations

"""Herramienta rápida de diagnóstico para un PDF de Supervisión Segura.

Uso desde consola, dentro de la carpeta del proyecto:

    python tools_decrypt_pdf.py "C:\\ruta\\al\\archivo.pdf"

Sirve para comprobar si un PDF contiene el marcador, si la clave DATA_KEY es
correcta y si el JSON puede descifrarse antes de importarlo al Manager.
"""

import json
import sys
from pathlib import Path
from services.decryptor import SupervisionDecryptor, DecryptError


def main() -> int:
    if len(sys.argv) < 2:
        print('Uso: python tools_decrypt_pdf.py "C:\\ruta\\al\\archivo.pdf"')
        return 1

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"ERROR: No se encontró el archivo: {pdf_path}")
        print("Revisa que el nombre, la carpeta y la extensión .pdf estén escritos exactamente igual.")
        return 2

    try:
        pdf_bytes = pdf_path.read_bytes()
        extracted = SupervisionDecryptor().extract_from_pdf_bytes(pdf_bytes)
        print("OK: JSON descifrado correctamente.\n")
        print(json.dumps(extracted.decrypted_json, indent=4, ensure_ascii=False))
        return 0
    except DecryptError as exc:
        print(f"ERROR DE DESCIFRADO: {exc}")
        return 3
    except Exception as exc:
        print(f"ERROR INESPERADO: {exc}")
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
