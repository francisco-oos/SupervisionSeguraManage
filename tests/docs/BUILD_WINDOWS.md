# Compilar SupervisionSeguraManager.exe en Windows

## 1. Crear entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

## 2. Instalar dependencias

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

## 3. Configurar clave de datos

Edita `config/settings.py` y asegúrate de que `DATA_KEY` sea exactamente la misma clave usada por la APK Android en `BuildConfig.DATA_KEY`.

Si la clave no coincide, el programa detectará el marcador del PDF pero no podrá descifrar el JSON.

## 4. Probar en modo desarrollo

```powershell
python app.py
```

## 5. Compilar

```powershell
.\build_exe.bat
```

El ejecutable queda en:

```text
dist\SupervisionSeguraManager\SupervisionSeguraManager.exe
```
