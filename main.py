# 多线程打开多个好友窗口进行消息监听
from pyweixin import Navigator
from pyweixin import Navigator, AutoReply
from pyweixin import AutoReply, Navigator
import re
import win32clipboard
from PIL import Image
import io
import http.client
from concurrent.futures import ThreadPoolExecutor
import http


def get_60s_news():
    # 1. 初始请求
    conn = http.client.HTTPSConnection("60s.viki.moe")
    path = "/v2/60s?encoding=image"  # 此时 encoding=base64 可能失效，因为服务器直接跳转了

    try:
        conn.request("GET", path)
        res = conn.getresponse()
        raw_data = res.read().decode("utf-8")

        # 2. 检查是否是重定向 HTML (根据你提供的文本)
        # 使用正则提取出 href 里的真实图片链接
        match = re.search(r'href="(https?://[^"]+)"', raw_data)

        if match:
            img_url = match.group(1)
            print(f"检测到重定向，正在从 CDN 获取图片: {img_url}")

            # 解析 URL 准备第二次请求
            # 例如从 https://cdn.jsdmirror.com/gh/... 提取域名和路径
            host = img_url.split("://")[1].split("/")[0]
            img_path = "/" + "/".join(img_url.split("://")[1].split("/")[1:])

            # 发起第二次请求获取真正的图片二进制流
            conn2 = http.client.HTTPSConnection(host)
            conn2.request("GET", img_path)
            res2 = conn2.getresponse()
            img_bytes = res2.read()
            conn2.close()
        else:
            # 如果没有重定向，尝试按原逻辑解析 Base64 (兼容某些情况)
            # 这里略过，通常上面那个正则就能搞定
            print("未发现重定向链接，请检查 API 返回内容")
            return None

        # 3. 将二进制流转为图片对象
        image = Image.open(io.BytesIO(img_bytes))

        # 4. 写入 Windows 剪贴板
        output = io.BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

        print("✅ 60s 新闻图片（来自 CDN）已存入剪贴板")
        return data

    except Exception as e:
        print(f"❌ 获取图片失败: {e}")
        return False
    finally:
        conn.close()


def reply_func(newMessage: str, contexts: list[str]):
    if '每日新闻' in newMessage:
        print(f"【触发】发送每日新闻")
        return get_60s_news()


# Independent dialog windows for each friend
dialog_windows = []
friends = ['Felix']
durations = ['15s']*len(friends)
# 不添加其他参数Monitor.listen_on_chat,比如save_photos,该操作涉及键鼠,无法多线程，只是监听消息，获取文本内容,移动保存文件还是可以的
for friend in friends:
    dialog_window = Navigator.open_seperate_dialog_window(
        friend=friend, window_minimize=True, close_weixin=True)  # window_minimize独立窗口最小化
    dialog_windows.append(dialog_window)
with ThreadPoolExecutor(max_workers=len(friends)) as pool:
    for win, dur in zip(dialog_windows, durations):
        task = pool.submit(
            AutoReply.auto_reply_to_friend, win, dur, reply_func)

    import time
    for i in range(15):
        print(f"主程序正在运行中... {i}")
        time.sleep(2)  # 模拟主程序在干别的事
