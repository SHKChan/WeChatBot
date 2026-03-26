import io
import os
import platform
import subprocess
from typing import Final

# 导入图像处理库
from PIL import Image

# 导入自定义日志
from logger_utils import LOGGER

# --- 系统环境常量定义 ---
SYSTEM_TYPE: Final[str] = platform.system()

# 根据系统类型按需导入 Windows 特有库
if SYSTEM_TYPE == "Windows":
    try:
        import win32clipboard
    except ImportError:
        LOGGER.error(
            " error [依赖缺失] >>> Windows 环境下缺失 pywin32 库，请运行: pip install pywin32")
elif SYSTEM_TYPE == "Darwin":
    # macOS (Darwin) 主要通过 subprocess 调用 osascript，无需额外库
    pass


def bytes2Img(img_bytes: bytes) -> bytes:
    """
    将原始字节流转换为符合当前操作系统剪贴板要求的图片格式数据。

    Args:
        img_bytes: 从 API 获取的原始图片字节流

    Returns:
        bytes: 处理后的图片数据（Windows 为 DIB 格式，Mac 为 PNG 格式）
    """
    try:
        # 将原始字节流转为 PIL 对象
        image: Image.Image = Image.open(io.BytesIO(img_bytes))
        output: io.BytesIO = io.BytesIO()

        if SYSTEM_TYPE == "Windows":
            # Windows 逻辑：剪贴板写入图片通常需要去掉文件头的 DIB 格式
            image.convert("RGB").save(output, "BMP")
            # BMP 文件头占 14 字节，去掉后即为 DIB 数据
            data: bytes = output.getvalue()[14:]
            LOGGER.info(" utils [图片转换] >>> 已处理为 Windows DIB 格式")
            return data

        elif SYSTEM_TYPE == "Darwin":
            # Mac 逻辑：转换为 PNG 格式以获得最佳兼容性
            image.save(output, format="PNG")
            data: bytes = output.getvalue()
            LOGGER.info(" utils [图片转换] >>> 已处理为 macOS PNG 格式")
            return data

        else:
            LOGGER.warning(f" utils [转换警告] >>> 未知系统 {SYSTEM_TYPE}，返回原始数据")
            return img_bytes

    except Exception as e:
        LOGGER.error(f" error [图片转换失败] >>> {e}")
        return b""


def copy2Clipboard(data: bytes) -> bool:
    """
    将处理后的图片数据写入系统剪贴板。

    Args:
        data: 处理后的图片字节流

    Returns:
        bool: 写入是否成功
    """
    if not data:
        LOGGER.error(" utils [剪贴板] >>> 写入失败：输入数据为空")
        return False

    if SYSTEM_TYPE == "Windows":
        return _copy_to_windows_clipboard(data)
    elif SYSTEM_TYPE == "Darwin":
        return _copy_to_mac_clipboard(data)
    else:
        LOGGER.error(f" utils [剪贴板] >>> 目前不支持的操作系统: {SYSTEM_TYPE}")
        return False


def _copy_to_windows_clipboard(data: bytes) -> bool:
    """Windows 专用剪贴板写入逻辑"""
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        # CF_DIB 是 Windows 剪贴板位图的标准格式
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        LOGGER.info(" utils [剪贴板] >>> 图片已成功存入 Windows 剪贴板")
        return True
    except Exception as e:
        LOGGER.error(f" error [Windows 剪贴板失败] >>> {e}")
        return False


def _copy_to_mac_clipboard(data: bytes) -> bool:
    """macOS 专用剪贴板写入逻辑 (AppleScript)"""
    temp_path: str = os.path.abspath("temp_clipboard_img.png")
    try:
        # 1. 写入临时文件（macOS osascript 无法直接读取内存中的字节流）
        with open(temp_path, "wb") as f:
            f.write(data)

        # 2. 构建并执行 AppleScript
        # «class PNGf» 是 macOS 剪贴板识别图片的关键元数据标志
        script: str = f'set the clipboard to (read (POSIX file "{temp_path}") as «class PNGf»)'

        process: subprocess.CompletedProcess = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )

        if process.returncode == 0:
            LOGGER.info(" utils [剪贴板] >>> 图片已成功存入 macOS 剪贴板")
            return True
        else:
            LOGGER.error(
                f" error [macOS 剪贴板失败] >>> AppleScript 返回码: {process.returncode}")
            return False

    except Exception as e:
        LOGGER.error(f" error [macOS 剪贴板异常] >>> {e}")
        return False
    finally:
        # 无论成功与否，清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
