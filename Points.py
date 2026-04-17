import requests
import re
import time
import os
import json
import random
import ipaddress
from dingtalkchatbot.chatbot import DingtalkChatbot


# --- 配置信息 ---
HOST = 'https://teamwork.cnhis.cc'
LOGIN_URI = f'{HOST}/teamworkapi/user/login'
GET_DOCUMENT_ID_URI = f'{HOST}/teamworkapi/api/ajax/inside/knowledge/getList'
DOCUMENT_RECORD_URI = f'{HOST}/process/dataDocument/documentRecord'
GET_INFO_URI = f'{HOST}/process/score/info'
GET_TODO_URI = f'{HOST}/process/ho-schedule/dealScheduleList?type=1'
EXECUT_TODO_URI = f'{HOST}/process/ho-schedule/execute'
# --- HTTP 请求头 ---
# 替代 notify 功能
def send(title, message):
    print(f"{title}: {message}")

class IPSpoofer:
    '''
    IP伪装工具类，用于生成随机IP地址和伪装HTTP请求头
    '''

    def __init__(self):
        '''初始化IP伪装器'''
        self.ip_pool = []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1'
        ]
        self.generate_ip_pool()

    def _is_public_ipv4(self, ip_str: str) -> bool:
        ip_obj = ipaddress.ip_address(ip_str)
        return (
                ip_obj.version == 4
                and not ip_obj.is_private
                and not ip_obj.is_loopback
                and not ip_obj.is_multicast
                and not ip_obj.is_reserved
                and not ip_obj.is_link_local
        )

    def generate_random_ip(self):
        '''
        生成随机公网IP地址
        :return: 随机IP地址字符串
        '''
        ip_segments = [
            [8, 8],
            [13, 15],
            [20, 22],
            [34, 36],
            [45, 47],
            [52, 54],
            [102, 109],
            [104, 107],
            [108, 110],
            [185, 187]
        ]

        for _ in range(20):
            segment = random.choice(ip_segments)
            first_octet = random.randint(segment[0], segment[1])
            second_octet = random.randint(0, 255)
            third_octet = random.randint(0, 255)
            fourth_octet = random.randint(1, 254)
            ip_str = f"{first_octet}.{second_octet}.{third_octet}.{fourth_octet}"
            if self._is_public_ipv4(ip_str):
                return ip_str

        return "8.8.8.8"

    def generate_ip_pool(self, pool_size=50):
        '''
        生成IP池
        :param pool_size: IP池大小
        '''
        self.ip_pool = [self.generate_random_ip() for _ in range(pool_size)]

    def get_random_ip(self):
        '''
        从IP池中获取随机IP
        :return: 随机IP地址
        '''
        if not self.ip_pool:
            self.generate_ip_pool()
        return random.choice(self.ip_pool)

    def get_random_user_agent(self):
        '''
        获取随机User-Agent
        :return: User-Agent字符串
        '''
        return random.choice(self.user_agents)

    def generate_spoofed_headers(self, base_headers=None):
        '''
        生成伪装的HTTP请求头（每次都从干净模板生成）
        :param base_headers: 基础请求头
        :return: 包含伪装信息的请求头字典
        '''
        random_ip = self.get_random_ip()

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'User-Agent': self.get_random_user_agent(),
            'Connection': 'keep-alive',
            'X-Forwarded-For': random_ip,
            'X-Real-IP': random_ip,
            'Forwarded': f'for={random_ip};proto=https'
        }

        if base_headers:
            headers.update(base_headers)

        return headers


# ... existing code ...

class ZuoBiao:
    '''
    ZuoBiao类封装了签到、领取积分奖励的方法
    '''
    def __init__(self, user_data):
        '''
        初始化方法
        :param user_data: 用户信息，用于后续的请求
        '''
        self.param = user_data
        self.pageNum = os.environ.get('PageNum')
        self.todo = {"id": "", "status": 2, "description": "", "fj": "[]"}
        self.ip_spoofer = IPSpoofer()
        self.cookie = None
        self.base_headers = {
            'Origin': 'https://teamwork.cnhis.cc',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://teamwork.cnhis.cc/'
        }
        self.headers = self.ip_spoofer.generate_spoofed_headers(self.base_headers)

    def _refresh_headers(self, content_type=None):
        base = dict(self.base_headers)
        if content_type:
            base['Content-Type'] = content_type
        if self.cookie:
            base['Cookie'] = self.cookie
        self.headers = self.ip_spoofer.generate_spoofed_headers(base)

    def getInfo_uri(self):
        self._refresh_headers()
        return requests.get(GET_INFO_URI, headers=self.headers, timeout=30).json()['data']['totalScore']

    def convert_bytes(self, b):
        '''
        将字节转换为 MB GB TB
        :param b: 字节数
        :return: 返回 MB GB TB
        '''
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = 0
        while b >= 1024 and i < len(units) - 1:
            b /= 1024
            i += 1
        return f"{b:.2f} {units[i]}"

    def set_document_record(self):
        '''
        写阅读记录
        '''
        for document in self.documents:
            self._refresh_headers(content_type='application/json;charset=utf-8')
            param = {
                'documentId': document['id'],
                'type': '0'
            }
            response = requests.post(url=DOCUMENT_RECORD_URI, headers=self.headers, json=param, timeout=30).json()
            if response.get('code') == '1000':
                send('✅记录成功', f'文章标题：{document["title"]}')
            else:
                send('❌记录失败', f'文章标题：{document["title"]}')
            time.sleep(30)

    def get_document_id(self):
        '''
        获取文章
        :return: 返回所有文章
        '''
        self._refresh_headers(content_type='application/x-www-form-urlencoded')
        send("开始获取帖子", self.headers)
        param = {
            "pageNum": self.pageNum,
            "pageSize": 50,
            "orderBy": 'asc',
            "secondarySort": 'createdTime',
        }
        send("开始请求获取帖子", self.headers)

        try:
            response = requests.post(url=GET_DOCUMENT_ID_URI, headers=self.headers, params=param, timeout=30)
            if response.status_code != 200:
                error_msg = f"获取文章列表失败，状态码: {response.status_code}"
                print(error_msg)
                return False, error_msg

            response_text = response.text.strip()
            if not response_text:
                error_msg = "收到空响应"
                print(error_msg)
                return False, error_msg

            try:
                response_json = response.json()
                send("获取帖子返回值", response_json)
            except json.JSONDecodeError as e:
                error_msg = f"JSON解析失败: {e}"
                print(f"{error_msg}\n原始响应: {response_text[:200]}...")
                return False, error_msg

            if response_json.get("map"):
                self.documents = response_json['map']['rows']
                self.set_document_record()
                return True, self.documents
            else:
                error_msg = response_json.get("message", "未知错误")
                return False, error_msg

        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求异常: {str(e)}"
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(error_msg)
            return False, error_msg

    def get_todo_id(self):
        '''
        获取代办任务
        :return: 返回所有代办任务id
        '''
        send("开始请求获取代办", self.headers)
        self._refresh_headers()

        try:
            response = requests.get(url=GET_TODO_URI, headers=self.headers, timeout=30)

            if response.status_code != 200:
                error_msg = f"获取代办任务失败，状态码: {response.status_code}"
                print(error_msg)
                return False, error_msg

            response_text = response.text.strip()
            if not response_text:
                error_msg = "收到空响应"
                print(error_msg)
                return False, error_msg

            try:
                response_json = response.json()
                send("开始请求获取代办响应", response_json)
            except json.JSONDecodeError as e:
                error_msg = f"JSON解析失败: {e}"
                print(f"{error_msg}\n原始响应: {response_text[:200]}...")
                return False, error_msg

            if response_json.get('code') == '1000':
                self.todoList = response_json['data']
                self.set_todo_record()
                return True, self.todoList
            else:
                error_msg = response_json.get("message", "未知错误")
                return False, error_msg

        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求异常: {str(e)}"
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(error_msg)
            return False, error_msg

    def set_todo_record(self):
        '''
        写阅读记录
        '''
        for todoRecord in self.todoList:
            self._refresh_headers(content_type='application/json')
            self.todo['id'] = todoRecord['id']
            response = requests.post(url=EXECUT_TODO_URI, headers=self.headers, json=self.todo, timeout=30).json()
            if response.get('code') == '1000':
                send('✅代办任务成功', f'任务名称：{todoRecord["title"]}')
            else:
                send('❌代办任务失败', f'任务名称：{todoRecord["title"]}')
            time.sleep(20)

    def do_login(self):
        """通过登录来刷新会话cookie"""
        print(f"正在为账号 [{self.param.get('account')}] 尝试登录并刷新Cookie...")
        self.cookie = None
        self._refresh_headers(content_type='application/x-www-form-urlencoded')

        data = {'loginName': self.param.get('account'), 'password': self.param.get('password')}

        try:
            response = requests.post(LOGIN_URI, headers=self.headers, data=data, timeout=30)
            send("登录头", self.headers)
            send("登录数据", data)
            send("登录状态码", response.status_code)
            send("登录响应头", dict(response.headers))

            if response.status_code != 200:
                print(f"账号 [{self.param.get('account')}] 登录请求失败，状态码: {response.status_code}")
                return f"账号 [{self.param.get('account')}] 登录失败，状态码: {response.status_code}"

            response_text = response.text.strip()
            if not response_text:
                print(f"账号 [{self.param.get('account')}] 收到空响应")
                return f"账号 [{self.param.get('account')}] 收到空响应"

            try:
                response_json = response.json()
                send("登录响应", response_json)
            except json.JSONDecodeError as e:
                print(f"账号 [{self.param.get('account')}] JSON解析失败: {e}")
                print(f"原始响应内容: {response_text[:200]}...")
                return f"账号 [{self.param.get('account')}] JSON解析失败"

            set_cookie_headers = response.headers.get('set-cookie')
            if set_cookie_headers:
                session_match = re.search(r'SESSION=([^;,\s]+)', set_cookie_headers)
                zbsid_match = re.search(r'zb_sid=([^;,\s]+)', set_cookie_headers)

                if session_match and zbsid_match:
                    session_val = session_match.group(1)
                    zbsid_val = zbsid_match.group(1)

                    self.cookie = f"SESSION={session_val}; zb_sid={zbsid_val}"
                    print(f'账号 [{self.param.get("account")}] 的Cookie刷新成功！')

                    send("开始贴子", "1111111111111111")
                    self.get_document_id()
                    send("开始待办", "1111111111111111")
                    self.get_todo_id()
                    return f"账号 [{self.param.get('account')}]"
                else:
                    print(f"账号 [{self.param.get('account')}] 的Cookie解析失败，未找到SESSION或zb_sid。")
                    print(f"原始Set-Cookie头: {set_cookie_headers}")
                    return f"账号 [{self.param.get('account')}] Cookie解析失败"
            else:
                print(f"账号 [{self.param.get('account')}] 未收到Cookie信息")
                return f"账号 [{self.param.get('account')}] 未收到Cookie"

        except requests.exceptions.Timeout:
            print(f"账号 [{self.param.get('account')}] 登录请求超时")
            return f"账号 [{self.param.get('account')}] 请求超时"
        except requests.exceptions.ConnectionError:
            print(f"账号 [{self.param.get('account')}] 连接错误")
            return f"账号 [{self.param.get('account')}] 连接错误"
        except requests.exceptions.RequestException as e:
            print(f"账号 [{self.param.get('account')}] 刷新Cookie时出错: {e}")
            return f"账号 [{self.param.get('account')}] 请求异常: {str(e)}"
        except Exception as e:
            print(f"账号 [{self.param.get('account')}] 发生未知错误: {e}")
            return f"账号 [{self.param.get('account')}] 未知错误: {str(e)}"

# ... existing code ...