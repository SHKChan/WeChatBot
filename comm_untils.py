
import io
import win32clipboard

from PIL import Image


def bytes2Img(img_bytes):
    image = Image.open(io.BytesIO(img_bytes))
    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    return data


def copy2Clipboard(data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()
