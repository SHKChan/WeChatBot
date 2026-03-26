import logging
import os
from datetime import datetime
from typing import Final


def setup_logger(name: str = "WeChatRobot") -> logging.Logger:
    """
    配置并返回一个强类型的全局日志记录器。

    Args:
        name: 日志记录器的名称，默认为 "WeChatRobot"

    Returns:
        logging.Logger: 配置完成的 Logger 实例
    """
    # 1. 创建日志目录
    log_dir: Final[str] = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. 生成日志文件名 (按天生成)
    # 使用 Final 确保路径在函数内不被修改
    log_filename: Final[str] = os.path.join(
        log_dir, f"robot_{datetime.now().strftime('%Y-%m-%d')}.log"
    )

    # 3. 获取或创建日志记录器
    # 注意：使用 getLogger(name) 可以确保在不同模块获取的是同一个实例
    logger_instance: logging.Logger = logging.getLogger(name)

    # 如果已经配置过 Handler，则直接返回，防止重复打印日志
    if logger_instance.handlers:
        return logger_instance

    logger_instance.setLevel(logging.INFO)

    # 4. 定义日志格式：[时间] [级别] [内容]
    formatter: Final[logging.Formatter] = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 5. 文件处理器：记录到硬盘 (使用 utf-8 防止中文乱码)
    try:
        file_handler: logging.FileHandler = logging.FileHandler(
            log_filename, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger_instance.addHandler(file_handler)
    except Exception as e:
        # 如果文件无法打开，至少保证控制台能看到错误
        print(f"无法创建日志文件处理器: {e}")

    # 6. 控制台处理器：实时显示在屏幕
    console_handler: logging.StreamHandler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger_instance.addHandler(console_handler)

    return logger_instance


# --- 初始化全局单例 ---
# 统一导出小写的 logger 变量，以匹配你其他模块的 import 语句：
# from logger_utils import logger
LOGGER: Final[logging.Logger] = setup_logger()
