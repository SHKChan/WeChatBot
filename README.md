
## Avaliable Approaches

- RPA, Robotic Process Automation
- Wechaty
- Hook

## Implement with RPA

- Enable Narrator with Registry, to force WeChat to expose its UI elements.

  ```
  Computer\HKEY_CURRENT_USER\Software\Microsoft\Narrator\NoRoam

  RunningState = 1
  ```
- Create Python Virtual Environment

  ```
  python -m venv .venv
  .\.venv\Scripts\Activate.bat
  // Uninstall other packages
  pip freeze | ForEach-Object { pip uninstall -y $_ }
  ```
- Install `pywecaht`

```powershell
git clone to Local
cd to repo
pip install -r requirements.txt
pip install -e .
copy pyweixin to repo root
```
