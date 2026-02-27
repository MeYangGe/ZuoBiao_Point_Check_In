#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP伪装功能测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Points import IPSpoofer
import json

def test_ip_spoofing():
    """测试IP伪装功能"""
    print('=== IP伪装功能测试 ===')
    
    # 创建IP伪装器实例
    spoofer = IPSpoofer()
    
    print('1. 生成随机IP测试:')
    for i in range(3):
        ip = spoofer.get_random_ip()
        print(f'   随机IP {i+1}: {ip}')
    
    print('\n2. 随机User-Agent测试:')
    for i in range(3):
        ua = spoofer.get_random_user_agent()
        print(f'   User-Agent {i+1}: {ua[:50]}...')
    
    print('\n3. 伪装请求头生成测试:')
    headers = spoofer.generate_spoofed_headers()
    
    # 显示关键的伪装头部
    spoof_headers = ['X-Forwarded-For', 'X-Real-IP', 'User-Agent']
    for header in spoof_headers:
        if header in headers:
            print(f'   {header}: {headers[header]}')
    
    print('\n4. IP池容量测试:')
    print(f'   IP池大小: {len(spoofer.ip_pool)}')
    
    # 验证IP格式
    test_ip = spoofer.get_random_ip()
    ip_parts = test_ip.split('.')
    is_valid = len(ip_parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts)
    
    print(f'\n5. IP格式验证:')
    print(f'   测试IP: {test_ip}')
    print(f'   格式有效: {"✅" if is_valid else "❌"}')
    
    print('\n✅ IP伪装功能测试完成!')

if __name__ == '__main__':
    test_ip_spoofing()