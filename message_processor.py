from venv import logger

import yaml

from api_service import ApiService
import comm_untils

with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)


def smart_reply_logic(newMessage: str, contexts: list):
    """
    在这里扩展回复逻辑：
    返回 bytes -> 发送图片
    返回 str   -> 发送文字
    返回 None  -> 不回复
    """
    msg = newMessage.strip()
    logger.info(f"收到新消息: {msg}")

    if "每日新闻" in msg:
        logger.info(f"触发 每日新闻...")

        logger.info(f"获取 每日新闻...")
        img_data = ApiService.fetch_60s_news(cfg['api']['news_60s'])

        logger.info(f"复制到剪贴板...")
        img = comm_untils.bytes2Img(img_data)
        comm_untils.copy2Clipboard(img)
        return img

    if "帮助" in msg:
        logger.info(f"触发 帮助...")
        return "指令列表：\n1. 每日新闻\n2. 帮助"

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
                print("✨ 机器人回复：[图片] (已存入剪贴板)")
            else:
                print(f"💬 机器人回复：{reply_content}")
        else:
            print("无匹配指令， 无需回复")


if __name__ == "__main__":
    run_test()
