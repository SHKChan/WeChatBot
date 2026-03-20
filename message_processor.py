from venv import logger

import yaml

from api_service import ApiService
import comm_untils

with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
    ApiService.CONFIG = cfg


def smart_reply_logic(newMessage: str, contexts: list):
    """
    在这里扩展回复逻辑：
    返回 bytes -> 发送图片
    返回 str   -> 发送文字
    返回 None  -> 不回复
    """

    if "帮助" == newMessage:
        logger.info(f"触发 帮助...")
        return "指令列表：\n1. 帮助\n2. 每日新闻\n3. KFC"
    elif "每日新闻" == newMessage:
        logger.info(f"触发 每日新闻...")

        img_data = ApiService.fetch_daily_news()
        logger.info(f"获取 每日新闻...")

        reply = comm_untils.bytes2Img(img_data)
        comm_untils.copy2Clipboard(reply)
        logger.info(f"复制到剪贴板...")
        return reply
    elif newMessage.upper() == "KFC":
        logger.info(f"触发 KFC文案...")

        reply = ApiService.fetch_kfc_copywriting()
        logger.info(f"获取 KFC文案...")
        return reply

    return None


def run_test():
    print("=== 机器人逻辑模拟测试 (输入 'exit' 退出) ===")

    while True:
        user_input = input("\n模拟收到消息 > ")

        if user_input.lower() == 'exit':
            break

        reply_content = smart_reply_logic(user_input, cfg)

        if reply_content is not None:
            if isinstance(reply_content, bytes):
                print("✨ 机器人回复：\n[图片] (已存入剪贴板)")
            else:
                print(f"💬 机器人回复：\n{reply_content}")
        else:
            print("无匹配指令， 无需回复")


if __name__ == "__main__":
    run_test()
