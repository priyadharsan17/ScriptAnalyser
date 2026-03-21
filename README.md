# ScriptAnalyser

**Setup Virtual Environment**

- **From repo root:** open PowerShell and run:

```powershell
cd StockNotificationManager
.\setup_venv_and_freeze.bat
```

This creates a `.venv` folder, installs `PySide6`, and writes `requirements.txt` into the `StockNotificationManager` folder.

- **Activate the venv later:**

```powershell
.\.venv\Scripts\activate.bat
```

- **Notes:** Ensure `python` (3.8+) is on your PATH. If the script fails, you can create the venv and install manually:

```powershell
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install PySide6
pip freeze > requirements.txt
```