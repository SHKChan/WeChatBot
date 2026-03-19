import http.client
import re


class ApiService:
    @staticmethod
    def fetch_60s_news(config):
        """根据配置获取 60s 新闻的原始 Bytes 数据"""
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
