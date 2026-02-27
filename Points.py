
import requests
import re
import time
import os
import sys
import json
import traceback
import random
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

    def generate_random_ip(self):
        '''
        生成随机IP地址
        :return: 随机IP地址字符串
        '''
        # 生成常见的公网IP段
        ip_segments = [
            [102, 109],      # 常见美国IP段
            [104, 107],      # 美国IP段
            [172, 174],      # 美国IP段
            [185, 187],      # 欧洲IP段
            [45, 47],        # 美国IP段
            [52, 54],        # AWS IP段
            [13, 15],        # Amazon IP段
            [20, 22],        # Microsoft IP段
            [34, 36],        # Google IP段
            [108, 110]       # 美国IP段
        ]

        # 随机选择一个IP段
        segment = random.choice(ip_segments)
        first_octet = random.randint(segment[0], segment[1])
        second_octet = random.randint(0, 255)
        third_octet = random.randint(0, 255)
        fourth_octet = random.randint(1, 254)  # 避免0和255

        return f"{first_octet}.{second_octet}.{third_octet}.{fourth_octet}"

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
        生成伪装的HTTP请求头
        :param base_headers: 基础请求头
        :return: 包含伪装信息的请求头字典
        '''
        # 生成随机IP
        random_ip = self.get_random_ip()

        # 基础请求头
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.get_random_user_agent(),
            'Host': 'teamwork.cnhis.cc',
            'Connection': 'keep-alive',
            'Sec-Ch-Ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }

        # 添加IP伪装相关头部
        ip_headers = {
            'X-Forwarded-For': random_ip,
            'X-Real-IP': random_ip,
            'X-Originating-IP': random_ip,
            'X-Remote-IP': random_ip,
            'X-Client-IP': random_ip,
            'True-Client-IP': random_ip,
            'CF-Connecting-IP': random_ip,
            'Fastly-Client-IP': random_ip,
            'Via': f'1.1 {random_ip}',
            'Forwarded': f'for={random_ip};proto=http;by={random_ip}'
        }

        # 合并请求头
        if base_headers:
            headers.update(base_headers)
        headers.update(ip_headers)

        return headers

    def update_request_headers(self, session_or_headers):
        '''
        更新请求的头部信息
        :param session_or_headers: requests.Session对象或headers字典
        :return: 更新后的对象
        '''
        if isinstance(session_or_headers, dict):
            return self.generate_spoofed_headers(session_or_headers)
        elif hasattr(session_or_headers, 'headers'):
            session_or_headers.headers.update(self.generate_spoofed_headers())
            return session_or_headers
        else:
            raise ValueError("参数必须是dict类型或具有headers属性的对象")

# 替代 notify 功能
def send(title, message):
    print(f"{title}: {message}")
# 推送 功能
def push_dt(dingtalk, msg,atAll,type):
    try:
        webhook = 'https://oapi.dingtalk.com/robot/send?access_token='+dingtalk

        dingTalk = DingtalkChatbot(webhook,fail_notice=True)
        if type == 1:
            dingTalk.send_text(msg, is_at_all=atAll)
        # Markdown消息@所有人
        dingTalk.send_markdown(title="ZUOBIAO", text=msg,
                               is_at_all=atAll)
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(error_traceback)
# 获取环境变量 
def get_env():
    #判断 COOKIE_ZUOBIAO否存在于环境变量 
    if "ZUOBIAO" in os.environ:
        # 读取系统变量以 \n 或 && 分割变量 
        cookie_list = os.environ.get('ZUOBIAO')
    else:
        # 标准日志输出 
        print('❌未添加ZUOBIAO变量')
        send('坐标自动刷积分', '❌未添加ZUOBIAO变量')

        # 脚本退出 
        sys.exit(0)

    return cookie_list


# 其他代码...

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
        self.todo = { "id": "", "status": 2, "description": "", "fj": "[]" }
        # 初始化IP伪装器
        self.ip_spoofer = IPSpoofer()
        # 生成初始伪装请求头
        self.headers = self.ip_spoofer.generate_spoofed_headers({
            'Origin': 'https://teamwork.cnhis.cc',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Sec-Fetch-Site': 'same-origin'
        })
    def getInfo_uri(self):
        # 更新请求头以使用新的伪装IP
        self.headers = self.ip_spoofer.generate_spoofed_headers(self.headers)
        return requests.get(GET_INFO_URI, self.headers).json()['data']['totalScore']
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
        self.headers['Content-Type']= 'application/json;charset=utf-8'
        for document in self.documents:
            # 为每个请求更新伪装IP
            self.headers = self.ip_spoofer.generate_spoofed_headers(self.headers)
            param = {
                'documentId': document['id'],
                'type': '0'
            }
            response = requests.post(url=DOCUMENT_RECORD_URI, headers=self.headers, json=param).json()
            if response.get('code') == '1000':
                send('✅记录成功', f'文章标题：{document["title"]}')
                #push_dt(self.param.get('dingtalk'),'✅记录成功'+'\n'+f'文章标题：{document["title"]}',False,1)
            else:
                send('❌记录失败', f'文章标题：{document["title"]}')
            time.sleep(30) # 休眠30秒

    def get_document_id(self):
        '''
        获取文章
        :return: 返回所有文章
        '''
        # 更新请求头以使用新的伪装IP
        self.headers = self.ip_spoofer.generate_spoofed_headers(self.headers)
        send("开始获取帖子",self.headers)
        param = {
            "pageNum": self.pageNum,
            "pageSize": 50,
            "orderBy": 'asc',
            "secondarySort": 'createdTime',
        }
        #请求文章连接
        send("开始请求获取帖子",self.headers)
        response = requests.post(url=GET_DOCUMENT_ID_URI, headers=self.headers, params=param).json()
        send("开始结束获取帖子，返回值",response)
        if response.get("map"):
            self.documents = response['map']['rows']
            self.set_document_record()
            return True, self.documents
        else:
            return False, response["message"]
    def get_todo_id(self):
        '''
        获取代办任务
        :return: 返回所有代办任务id
        '''
        # 更新请求头以使用新的伪装IP
        send("开始请求获取代办",self.headers)
        self.headers = self.ip_spoofer.generate_spoofed_headers(self.headers)

        #请求代办连接
        response = requests.get(url=GET_TODO_URI, headers=self.headers).json()
        send("开始请求获取代办响应",response)
        if response.get('code') == '1000':
            self.todoList = response['data']
            self.set_todo_record()
            return True, self.todoList
        else:
            return False, response["message"]
    def set_todo_record(self):
        '''
        写阅读记录
        '''
        self.headers['Content-Type']= 'application/json'
        for todoRecord in self.todoList:
            # 为每个请求更新伪装IP
            self.headers = self.ip_spoofer.generate_spoofed_headers(self.headers)
            self.todo['id'] = todoRecord['id']
            response = requests.post(url=EXECUT_TODO_URI, headers=self.headers, json=self.todo).json()
            if response.get('code') == '1000':
                send('✅代办任务成功', f'任务名称：{todoRecord["title"]}')
                # push_dt(self.param.get('dingtalk'),'✅代办任务成功'+'\n'+f'任务名称：{todoRecord["title"]}',False,1)
            else:
                send('❌代办任务失败', f'任务名称：{todoRecord["title"]}')
            time.sleep(20) # 休眠20秒

    def do_login(self):
        """通过登录来刷新会话cookie"""
        print(f"正在为账号 [{self.param.get('account')}] 尝试登录并刷新Cookie...")
        self.headers.pop('Cookie', None)  # 移除旧的Cookie
        # 为登录请求更新伪装IP
        self.headers = self.ip_spoofer.generate_spoofed_headers(self.headers)
        data = {'loginName': {self.param.get('account')}, 'password': self.param.get('password')}

        try:
            response = requests.post(LOGIN_URI, headers=self.headers, data=data)
            send("登录头",self.headers)
            send("登录数据",data)
            send("登录信息",response)
            response.raise_for_status()  # 如果请求失败（如4xx或5xx错误），则抛出异常
            set_cookie_headers = response.headers.get('set-cookie')
            if set_cookie_headers:
                # 使用正则表达式从set-cookie头中提取SESSION和zb_sid
                session_match = re.search(r'SESSION=([^;,\s]+)', set_cookie_headers)
                zbsid_match = re.search(r'zb_sid=([^;,\s]+)', set_cookie_headers)

                if session_match and zbsid_match:
                    session_val = session_match.group(1)
                    zbsid_val = zbsid_match.group(1)

                    my_cookie = f"SESSION={session_val}; zb_sid={zbsid_val}"
                    print(f'账号 [{self.param.get("account")}] 的Cookie刷新成功！')
                    self.headers['Cookie'] = my_cookie
                    send("开始贴子","1111111111111111")
                    self.get_document_id() #开始获取帖子
                    send("开始待办","1111111111111111")
                    self.get_todo_id() #开始获取帖子
                    return f"账号 [{self.param.get('account')}]"

                else:
                    print(f"账号 [{self.param.get('account')}] 的Cookie解析失败，未找到SESSION或zb_sid。")
                    print(f"原始Set-Cookie头: {set_cookie_headers}")
                    return f"账号 [{self.param.get('account')}]"
        except requests.exceptions.RequestException as e:
            print(f"账号 [{self.param.get('account')}] 刷新Cookie时出错: {e}")
        return f"账号 [{self.param.get('account')}]"

def main():
    '''
    主函数
    :return: 返回一个字符串，包含积分结果
    '''
    msg = ""
    global cookie_zuobiao
    cookie_zuobiao = get_env()
    datas = json.loads(cookie_zuobiao)
    print("✅ 检测到共", len(datas["ZUOBIAO"]), "个坐标账号\n")

    i = 0
    for i in range(len(datas.get("ZUOBIAO", []))):
        _check_item = datas.get("ZUOBIAO", [])[i]
        # 开始任务
        # 登录
        log = f"完成🙍🏻‍♂️ 第{i + 1}个"+ZuoBiao(_check_item).do_login()

        push_dt(_check_item['dingtalk'],log,True,2)
        msg += log + "\n"

        i += 1
    try:
        send('开始', msg)
    except Exception as err:
        print('%s\n❌ 错误，请查看运行日志！' % err)
    return msg[:-1]


if __name__ == "__main__":
    print("----------ZuoBiao开始刷积分----------")
    main()
    print("----------ZuoBiao刷积分完毕----------")
