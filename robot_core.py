import yaml
import time
import comm_untils
from logger_utils import logger
from concurrent.futures import ThreadPoolExecutor
from pyweixin import Navigator, AutoReply
from api_service import ApiService

# 加载配置
with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)


def smart_reply_logic(newMessage: str, contexts: list):
    """
    在这里扩展业务逻辑：
    返回 bytes -> 发送图片
    返回 str   -> 发送文字
    返回 None  -> 不回复
    """
    msg = newMessage.strip()
    logger.info(f"收到新消息: {msg}")

    if "每日新闻" in msg:
        logger.info(f"触发 每日新闻...")

        logger.info(f"获取 60s 新闻...")
        img_data = ApiService.fetch_60s_news(cfg['api']['news_60s'])

        logger.info(f"复制到剪贴板...")
        img = comm_untils.bytes2Img(img_data)
        comm_untils.copy2Clipboard(img)
        return img

    if "帮助" in msg:
        logger.info(f"触发 帮助...")
        return "指令列表：\n1. 每日新闻\n2. 帮助"

    return None


def start_robot():
    friends_list = cfg['friends']
    logger.info(f"正在初始化机器人，监听好友: {friends_list}")

    # 1. 初始化所有窗口
    dialog_windows = []
    for friend in friends_list:
        dw = Navigator.open_seperate_dialog_window(
            friend=friend, window_minimize=True, close_weixin=False
        )
        dialog_windows.append(dw)

    # 2. 进入持续监听大循环
    logger.info("机器人已启动，进入监听模式...")
    try:
        while True:
            with ThreadPoolExecutor(max_workers=cfg['settings']['max_workers']) as pool:
                # 派发任务
                tasks = []
                for win in dialog_windows:
                    tasks.append(pool.submit(
                        AutoReply.auto_reply_to_friend,
                        win,
                        cfg['settings']['duration'],
                        smart_reply_logic
                    ))

                # 等待这一轮所有好友的任务结束
                for future in tasks:
                    try:
                        future.result()
                    except Exception as e:
                        logger.info(f"线程执行出错: {e}")

            logger.info(
                f"--- 轮询结束，等待 {cfg['settings']['loop_interval']}s 后开启下一轮 ---")
            time.sleep(cfg['settings']['loop_interval'])

    except KeyboardInterrupt:
        logger.info("机器人正在关闭...")


if __name__ == "__main__":
    start_robot()
