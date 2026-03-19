import logging
import os
from datetime import datetime


def setup_logger(name="WeChatRobot"):
    # 1. 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. 生成日志文件名 (按天生成)
    log_filename = os.path.join(
        log_dir, f"robot_{datetime.now().strftime('%Y-%m-%d')}.log")

    # 3. 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 4. 定义日志格式：[时间] [级别] [内容]
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 5. 文件处理器：记录到硬盘
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # 6. 控制台处理器：实时显示在屏幕
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 7. 添加处理器
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# 初始化一个全局 logger
logger = setup_logger()
