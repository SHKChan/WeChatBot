import http.client
import json
import re
from typing import Dict, Optional
from datetime import date as date_type


class ApiService:
    CONFIG: Dict[str, any] = None

    @classmethod
    def fetch_daily_news(cls) -> Optional[bytes]:
        config = cls.CONFIG['api']['daily_news']
        conn = http.client.HTTPSConnection(config['url'])

        try:
            conn.request(config['method'], config['path'])
            res = conn.getresponse()
            raw_data = res.read().decode("utf-8")

            # 尝试匹配重定向链接
            match = re.search(r'href="(https?://[^"]+)"', raw_data)
            if match:
                img_url = match.group(1)
                host = img_url.split("://")[1].split("/")[0]
                img_path = "/" + \
                    "/".join(img_url.split("://")[1].split("/")[1:])

                cdn_conn = http.client.HTTPSConnection(host)
                cdn_conn.request("GET", img_path)
                img_bytes = cdn_conn.getresponse().read()
                cdn_conn.close()
                return img_bytes
            return None
        except Exception as e:
            print(f"API 请求失败: {e}")
            return None
        finally:
            conn.close()

    """编码方式，支持 text/json/markdown"""
    encoding: Optional[str]

    @classmethod
    def fetch_crazy_kfc(cls) -> None:
        config: dict[str, any] = cls.CONFIG['api']['crazy_kfc']
        conn = http.client.HTTPSConnection(config['url'])

        try:
            conn.request(config['method'], config['path'])
            res = conn.getresponse()
            raw_data = res.read().decode("utf-8")
            return cls.__get_return_data(raw_data)['kfc']
        except Exception as e:
            print(f"API 请求失败: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def fetch_slacker_daily(cls) -> None:
        config: dict[str, any] = cls.CONFIG['api']['slacker_daily']
        conn = http.client.HTTPSConnection(config['url'])

        try:
            conn.request(config['method'], config['path'])
            res = conn.getresponse()
            raw_data = res.read().decode("utf-8")
            return raw_data
        except Exception as e:
            print(f"API 请求失败: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def fetch_dad_joke(cls) -> None:
        config: dict[str, any] = cls.CONFIG['api']['dad_joke']
        conn = http.client.HTTPSConnection(config['url'])

        try:
            conn.request(config['method'], config['path'])
            res = conn.getresponse()
            raw_data = res.read().decode("utf-8")
            return raw_data
        except Exception as e:
            print(f"API 请求失败: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def __get_return_data(self, raw_data: str) -> str | Dict[str, any]:
        data: Dict[str, any] = json.loads(raw_data)
        if (data is None or data['code'] is None):
            raise Exception("API 返回数据异常")
        if (data['code'] != 200):
            raise Exception(raw_data['message'])
        return data['data']
