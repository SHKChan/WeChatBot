
import io
import os
import platform
import subprocess

from PIL import Image

system_type = platform.system()

if system_type == "Windows":
    import win32clipboard
elif system_type == "Darwin":  # Darwin 就是 Mac OS 的内核名
    pass


def bytes2Img(img_bytes):
    # 将原始字节流转为 PIL 对象
    image = Image.open(io.BytesIO(img_bytes))

    if system_type == "Windows":
        # Windows 逻辑：需要 DIB 格式
        output = io.BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # 必须去掉 14 字节
        return data
    else:
        # Mac 逻辑：需要一个完整、标准的图片字节流
        output = io.BytesIO()
        # 转为 PNG，因为 AppleScript 读取 «class PNGf» 兼容性最好
        image.save(output, format="PNG")
        data = output.getvalue()
        return data


def copy2Clipboard(data):
    if system_type == "Windows":
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            print(f"Windows 剪贴板写入失败: {e}")
            return False

    elif system_type == "Darwin":
        try:
            # 1. Mac 需要一个临时文件作为中转，因为 AppleScript 无法直接读取内存字节
            temp_path = os.path.abspath("temp_clipboard_img.png")
            with open(temp_path, "wb") as f:
                f.write(data)

            # 2. 构建 AppleScript：将文件读取为 PNGf 类并存入剪贴板
            # «class PNGf» 是 Mac 剪贴板识别图片的关键标志
            script = f'set the clipboard to (read (POSIX file "{temp_path}") as «class PNGf»)'

            # 3. 执行脚本
            process = subprocess.run(
                ["osascript", "-e", script], capture_output=True)

            # 4. 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

            if process.returncode == 0:
                return True
            else:
                return False

        except Exception as e:
            print(f"Mac 剪贴板写入失败: {e}")
            return False

    else:
        print(f"目前不支持的操作系统: {system_type}")
        return False
