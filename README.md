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
Copy pyweixin to repo root

Modify to support image reply
				# 支持回复图片
                                if isinstance(reply_content, bytes):
                                    input_edit.click_input()
                                    pyautogui.hotkey('ctrl', 'v')
                                else:
                                    input_edit.set_text(reply_content)
                                pyautogui.hotkey('alt', 's')
                                if isinstance(reply_content, bytes):
                                    input_edit.click_input()
                                    pyautogui.hotkey('ctrl', 'v')
                                else:
                                    input_edit.set_text(reply_content)
                                pyautogui.hotkey('alt', 's')
```
