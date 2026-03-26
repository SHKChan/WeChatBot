import http.client
import json
import re
from typing import Dict, Optional, Any
from contextlib import closing

from config import RobotConfig, ApiEndpoint
from logger_utils import LOGGER


class ApiService:
    """
    API 服务类：负责所有外部接口的请求与数据解析。
    """
    # 强类型配置引用
    CONFIG: Optional[RobotConfig] = None

    @classmethod
    def fetch_daily_news(cls) -> Optional[bytes | str]:
        """
        获取每日新闻图片。
        逻辑：先请求 HTML 页面，解析出真实的图片重定向链接，再下载图片。
        """
        if not cls.CONFIG:
            return None

        conf: ApiEndpoint = cls.CONFIG['api']['daily_news']
        LOGGER.info(f" api [请求] >>> 正在获取每日新闻 (Host: {conf['url']})")

        try:
            with closing(http.client.HTTPSConnection(conf['url'], timeout=10)) as conn:
                conn.request(conf['method'], conf['path'])
                res = conn.getresponse()
                return res
                raw_html = res.read().decode("utf-8")

                # 1. 尝试从返回的 HTML 中匹配图片重定向链接
                # 匹配规则针对: <a href="https://...">
                match = re.search(r'href="(https?://[^"]+)"', raw_html)
                if not match:
                    LOGGER.warning(" api [解析失败] >>> 未能在返回页面中找到新闻图片链接")
                    return None

                full_img_url: str = match.group(1)

                # 2. 拆解 URL 准备进行 CDN 请求
                # 示例: https://cdn.viki.moe/path/to/img.png
                url_parts = full_img_url.split("://")[1].split("/", 1)
                host: str = url_parts[0]
                img_path: str = "/" + url_parts[1]

                # 3. 请求真实的图片二进制数据
                with closing(http.client.HTTPSConnection(host, timeout=10)) as cdn_conn:
                    cdn_conn.request("GET", img_path)
                    img_res = cdn_conn.getresponse()
                    if img_res.status == 200:
                        img_data = img_res.read()
                        LOGGER.info(
                            f" api [成功] >>> 新闻图片下载完成, 大小: {len(img_data)} bytes")
                        return img_data

                return None

        except Exception as e:
            LOGGER.error(f" error [新闻接口失败] >>> {e}")
            return None

    @classmethod
    def fetch_crazy_kfc(cls) -> Optional[str]:
        """获取肯德基疯狂星期四文案"""
        return cls._fetch_text_data('crazy_kfc', json_key='kfc')

    @classmethod
    def fetch_slacker_daily(cls) -> Optional[str]:
        """获取摸鱼日报文案"""
        # 注意：这里的 path 在配置中已经带了 ?encoding=text，所以直接返回 body
        return cls._fetch_text_data('slacker_daily')

    @classmethod
    def fetch_dad_joke(cls) -> Optional[str]:
        """获取冷笑话文案"""
        return cls._fetch_text_data('dad_joke')

    @classmethod
    def _fetch_text_data(cls, api_key: str, json_key: Optional[str] = None) -> Optional[str]:
        """
        通用文本数据请求私有方法。

        Args:
            api_key: 配置中 api 节点的键名 (如 'crazy_kfc')
            json_key: 如果返回是 JSON，指定要提取的字段名
        """
        if not cls.CONFIG:
            return None

        conf: ApiEndpoint = cls.CONFIG['api'][api_key]  # type: ignore
        LOGGER.info(f" api [请求] >>> 正在调用接口: {api_key}")

        try:
            with closing(http.client.HTTPSConnection(conf['url'], timeout=10)) as conn:
                conn.request(conf['method'], conf['path'])
                res = conn.getresponse()
                raw_data: str = res.read().decode("utf-8")

                if json_key:
                    # 需要解析 JSON 的情况
                    data_obj = cls.__parse_json_response(raw_data)
                    return str(data_obj.get(json_key)) if isinstance(data_obj, dict) else None

                # 直接返回纯文本的情况
                return raw_data

        except Exception as e:
            LOGGER.error(f" error [接口异常] >>> {api_key} 失败: {e}")
            return None

    @classmethod
    def __parse_json_response(cls, raw_data: str) -> Dict[str, Any]:
        """
        统一解析 API 返回的 JSON 格式，并处理业务状态码。
        """
        try:
            resp: Dict[str, Any] = json.loads(raw_data)

            # 业务状态码校验 (假设 API 标准是 code 200 为成功)
            code = resp.get('code')
            if code != 200:
                msg = resp.get('message', '未知 API 错误')
                raise RuntimeError(f"API 业务逻辑报错: {msg} (Code: {code})")

            return resp.get('data', {})
        except json.JSONDecodeError:
            raise ValueError("返回数据不是有效的 JSON 格式")
