import threading
import time
from typing import Dict, Set, Any, Final

from config import RobotConfig, ConfigHelper
from logger_utils import LOGGER
from message_processor import smart_reply_logic
from pyweixin.WeChatAuto import AutoReply
from pyweixin.WeChatTools import Navigator

# --- 全局常量 ---
# UI_LOCK: 确保微信搜索栏在同一时刻只被一个线程占用
UI_LOCK: Final[threading.Lock] = threading.Lock()

# ACTIVE_WORKERS: 管理活跃的线程停止信号
ACTIVE_WORKERS: Dict[str, threading.Event] = {}


def friend_worker_thread(friend_name: str, config: RobotConfig, stop_event: threading.Event) -> None:
    """
    针对单个好友的监听线程，负责打开窗口并执行自动回复逻辑。
    """
    LOGGER.info(f" threading [启动] >>> 开启好友 [{friend_name}] 的专属监听任务")

    try:
        # 1. 获取 UI 锁，执行窗口初始化
        with UI_LOCK:
            LOGGER.info(f" UI_LOCK [占用] >>> 正在为 [{friend_name}] 操作微信搜索栏...")
            # win 类型取决于 pywinauto，标注为 Any
            win: Any = Navigator.open_seperate_dialog_window(
                friend=friend_name,
                is_maximize=True
            )
            # 留出 1.5s 让微信 UI 缓冲，防止搜索框状态冲突
            time.sleep(1.5)

        LOGGER.info(f" status [就绪] >>> 好友 [{friend_name}] 窗口已挂载，进入监听循环")

        # 2. 持续监听循环
        while not stop_event.is_set():
            try:
                AutoReply.auto_reply_to_friend(
                    win,
                    config['settings']['duration'],
                    smart_reply_logic,
                    save_file=False,
                    target_folder=None,
                    close_dialog_window=False
                )
            except Exception as e:
                LOGGER.error(f" error [循环异常] >>> 好友 [{friend_name}]: {e}")

            # 轮询休眠
            time.sleep(config['settings']['loop_interval'])

    except Exception as e:
        LOGGER.error(f" critical [严重故障] >>> 好友 [{friend_name}] 线程崩溃: {e}")
    finally:
        LOGGER.info(f" threading [退出] <<< 好友 [{friend_name}] 监听任务已安全结束")


def start_robot() -> None:
    """
    管理主进程：负责动态同步配置与线程状态。
    """
    global ACTIVE_WORKERS
    LOGGER.info("================================================")
    LOGGER.info("  WeChat Multi-Thread Robot v0.2.0 (Hot Reload)   ")
    LOGGER.info("================================================")

    while True:
        try:
            # 1. 热加载配置
            config: RobotConfig = ConfigHelper.load_config()
            new_friends_list: Set[str] = set(config['friends'])
            current_running: Set[str] = set(ACTIVE_WORKERS.keys())

            # 2. 同步：停止已移除的好友线程
            to_remove: Set[str] = current_running - new_friends_list
            for friend in to_remove:
                LOGGER.info(f" sync [-] 移除任务: 正在停止好友 [{friend}] 的监听线程...")
                ACTIVE_WORKERS[friend].set()
                del ACTIVE_WORKERS[friend]

            # 3. 同步：启动新增加的好友线程
            to_add: Set[str] = new_friends_list - current_running
            for friend in to_add:
                LOGGER.info(f" sync [+] 新增任务: 正在初始化好友 [{friend}] 的监听线程...")
                stop_event: threading.Event = threading.Event()
                ACTIVE_WORKERS[friend] = stop_event

                worker: threading.Thread = threading.Thread(
                    target=friend_worker_thread,
                    args=(friend, config, stop_event),
                    daemon=True
                )
                worker.start()

            # 4. 主线程心跳日志（改进后显示更多细节）
            active_names: str = ", ".join(
                ACTIVE_WORKERS.keys()) if ACTIVE_WORKERS else "无"
            LOGGER.info(
                f" heart_beat [*] 管理进程运行中 | 活跃数: {len(ACTIVE_WORKERS)} | 监听名单: [{active_names}]")

            # 5. 等待下一轮同步检查
            time.sleep(config['settings']['loop_interval'])

        except KeyboardInterrupt:
            LOGGER.warning(" system [中断] >>> 检测到退出信号，正在释放资源...")
            for event in ACTIVE_WORKERS.values():
                event.set()
            break
        except Exception as e:
            LOGGER.error(f" system [异常] >>> 主进程发生错误: {e}")
            time.sleep(5)


if __name__ == "__main__":
    start_robot()
