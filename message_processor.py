from typing import Dict, List, Optional, Union, Final, Any

import comm_utils
from config import ConfigHelper
from logger_utils import LOGGER
from api_service import ApiService

# --- 类型别名定义 ---
# 回复内容可以是 字节流(图片)、字符串(文字) 或 None(不回复)
ReplyContent = Union[bytes, str, None]

# --- 常量定义 ---
# 使用 Final 确保指令列表不被修改
SUPPORTED_COMMANDS: Final[List[str]] = ["帮助", "每日新闻", "KFC", "摸鱼日报", "冷笑话"]

# 初始化加载配置 (仅用于测试或 API 初始化)
GLOBAL_CFG: Final[Dict[str, Any]] = None


def smart_reply_logic(newMessage: str, contexts: Optional[List[Any]] = None) -> ReplyContent:
    """
    核心回复逻辑处理函数。

    Args:
        newMessage: 接收到的原始文本消息
        contexts: 历史上下文信息（可选）

    Returns:
        ReplyContent: 返回字节流(图片)、字符串(文字) 或 None
    """
    global GLOBAL_CFG
    GLOBAL_CFG = ConfigHelper.load_config()
    ApiService.CONFIG = GLOBAL_CFG
    # 1. 基础校验与预处理
    clean_msg: str = newMessage.strip()
    parts: List[str] = clean_msg.split(" ")

    trigger: str = GLOBAL_CFG.get('settings', {}).get('trigger', "巴拉")

    # 判定是否触发：字数不足、触发词不符、指令不在支持列表中
    if len(parts) < 2 or parts[0] != trigger:
        return None

    command: str = parts[1].upper()
    if command not in [c.upper() for c in SUPPORTED_COMMANDS]:
        return None

    LOGGER.info(f" logic [触发指令] >>> 收到有效指令: [{clean_msg}]")

    # 2. 指令分发处理
    reply: ReplyContent = None
    cmd_text: str = parts[1]  # 原始指令文本

    try:
        if cmd_text == "帮助":
            reply = "🤖 机器人指令列表:\n"
            for i, cmd in enumerate(SUPPORTED_COMMANDS, start=1):
                reply += f"  {i}. {trigger} {cmd}\n"
            reply += "\n提示: 请确保指令之间有空格。"

        elif cmd_text == "每日新闻":
            img_data: bytes = ApiService.fetch_daily_news()
            # 将字节流转换为图片并存入剪贴板（具体实现参考 comm_utils）
            reply = comm_utils.bytes2Img(img_data)
            comm_utils.copy2Clipboard(reply)
            LOGGER.info(" logic [图片处理] >>> 新闻图片已转换并存入剪贴板")

        elif cmd_text.upper() == "KFC":
            reply = ApiService.fetch_crazy_kfc()

        elif cmd_text == "摸鱼日报":
            # 摸鱼日报通常返回文本
            reply = ApiService.fetch_slacker_daily()

        elif cmd_text == "冷笑话":
            reply = ApiService.fetch_dad_joke()

        # 3. 最终回复状态记录
        if reply:
            display_reply = "[图片数据]" if isinstance(
                reply, bytes) else reply.replace('\n', ' ')[:50] + "..."
            LOGGER.info(f" logic [回复准备] >>> 内容摘要: {display_reply}")

        return reply

    except Exception as e:
        LOGGER.error(f" error [逻辑执行异常] >>> 处理指令 '{cmd_text}' 时出错: {e}")
        return f"❌ 抱歉，执行指令 [{cmd_text}] 时发生了错误。"


def run_test() -> None:
    """
    逻辑模拟测试函数，带增强版日志显示。
    """
    LOGGER.info("================================================")
    LOGGER.info("   Robot Logic Simulator - 模拟测试模式开启       ")
    LOGGER.info("================================================")
    print("\n💡 输入示例: '巴拉 帮助' 或 '巴拉 KFC' (输入 'exit' 退出)")

    while True:
        try:
            user_input: str = input("\n模拟收到消息 > ").strip()

            if user_input.lower() == 'exit':
                LOGGER.info(" system [退出] >>> 模拟测试已结束。")
                break

            # 执行逻辑
            reply_content: ReplyContent = smart_reply_logic(user_input)

            # 测试输出格式美化
            if reply_content is not None:
                if isinstance(reply_content, bytes):
                    print(
                        f"\n✨ 【机器人回复】\n[图片数据 ({len(reply_content)} bytes)]\n✅ 已尝试存入剪贴板")
                else:
                    print(f"\n💬 【机器人回复】\n{reply_content}")
            else:
                print("\n⚪ [无响应] >>> 消息未触发指令")

        except KeyboardInterrupt:
            break
        except Exception as e:
            LOGGER.error(f" system [测试异常] >>> {e}")


if __name__ == "__main__":
    run_test()
