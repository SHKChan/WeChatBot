from venv import logger

import yaml

from api_service import ApiService
import comm_untils

with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
    ApiService.CONFIG = cfg

SUPPORTED_COMMANDS = ["帮助", "每日新闻", "KFC", "摸鱼日报", "冷笑话"]


def smart_reply_logic(newMessage: str, contexts: list):
    """
    在这里扩展回复逻辑：
    返回 bytes -> 发送图片
    返回 str   -> 发送文字
    返回 None  -> 不回复
    """

    messages = newMessage.strip().split(" ")
    if messages.__len__() < 2 or messages[0] != cfg['settings']['trigger'] or messages[1].upper() not in SUPPORTED_COMMANDS:
        return None
    else:
        logger.info(f"触发 {newMessage} 指令")

    reply = None
    if "帮助" == messages[1]:
        reply = "指令列表:\n"
        for i, command in enumerate(SUPPORTED_COMMANDS, start=1):
            reply += f"  {i}.巴拉 {command}\n"
    elif "每日新闻" == messages[1]:
        img_data = ApiService.fetch_daily_news()
        reply = comm_untils.bytes2Img(img_data)
        comm_untils.copy2Clipboard(reply)
    elif messages[1].upper() == "KFC":
        reply = ApiService.fetch_crazy_kfc()
    elif messages[1] == "摸鱼日报":
        reply = ApiService.fetch_slacker_daily()
        return reply
    elif messages[1] == "冷笑话":
        reply = ApiService.fetch_dad_joke()

    logger.info(f"回复消息：{reply}")
    return reply


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
