from typing import List, Dict, TypedDict, Any, Final

import yaml

from logger_utils import LOGGER

# --- API 接口子结构 ---


class ApiEndpoint(TypedDict):
    url: str
    path: str
    method: str

# --- API 配置集合 ---


class ApiConfig(TypedDict):
    daily_news: ApiEndpoint
    crazy_kfc: ApiEndpoint
    slacker_daily: ApiEndpoint
    dad_joke: ApiEndpoint

# --- 机器人基础设置 ---


class SettingsConfig(TypedDict):
    trigger: str        # 机器人名称/触发词
    duration: str       # 监听时长 (例如 "30s")
    loop_interval: int  # 轮询间隔 (秒)
    max_workers: int    # 最大并发线程数

# --- 完整配置根结构 ---


class RobotConfig(TypedDict):
    version: str
    settings: SettingsConfig
    api: ApiConfig
    friends: List[str]

# --- 配置校验工具 ---


class ConfigHelper:
    """用于确保加载的 YAML 数据符合 RobotConfig 结构"""

    @classmethod
    def validate(cls, data: Any) -> RobotConfig:
        # 基础检查：确保是字典且包含必要的主键
        if not isinstance(data, dict):
            raise TypeError("配置数据必须是字典格式")

        required_keys = ['settings', 'api', 'friends']
        for key in required_keys:
            if key not in data:
                raise KeyError(f"配置文件缺失关键节点: {key}")

        # 自动转换好友列表为 List (防止 YAML 只有一个好友时解析成字符串)
        if not isinstance(data['friends'], list):
            data['friends'] = [str(data['friends'])]

        return data  # 返回强类型的 RobotConfig 对象

    @classmethod
    def load_config(cls) -> RobotConfig:
        """加载并校验强类型配置"""
        try:
            with open("config.yaml", "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)
                # 使用验证器强制转换为 RobotConfig 类型
                return cls.validate(raw_data)
        except Exception as e:
            LOGGER.error(f" error [配置失败] >>> 加载或校验失败: {e}")
            raise


__VERSION__: Final[str] = ConfigHelper.load_config()['version']
