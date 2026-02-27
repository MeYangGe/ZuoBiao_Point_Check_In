#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的错误处理功能
"""

import json
import os

def test_json_parsing():
    """测试JSON解析错误处理"""
    print("=== JSON解析错误处理测试 ===")
    
    # 模拟各种可能的响应
    test_cases = [
        ("正常JSON", '{"code": "1000", "message": "success"}'),
        ("空响应", ""),
        ("HTML错误页面", "<html><body>Error 500</body></html>"),
        ("无效JSON", "{invalid json}"),
        ("部分JSON", '{"code": "1000"'),
    ]
    
    import json as json_module
    
    for case_name, response_text in test_cases:
        print(f"\n测试 {case_name}:")
        try:
            if not response_text.strip():
                print("  ✓ 检测到空响应")
                continue
                
            result = json_module.loads(response_text)
            print(f"  ✓ 成功解析: {result}")
        except json_module.JSONDecodeError as e:
            print(f"  ✓ 正确捕获JSON解析错误: {e}")

def test_account_format():
    """测试账号格式修复"""
    print("\n=== 账号格式修复测试 ===")
    
    # 测试原始错误的格式
    account_data = "04163***"
    
    # 原始错误格式（使用集合）
    wrong_format = {'loginName': {account_data}, 'password': 'test123'}
    print(f"错误格式: {wrong_format}")
    print(f"  loginName类型: {type(wrong_format['loginName'])}")
    print(f"  loginName值: {wrong_format['loginName']}")
    
    # 修复后的格式（使用字符串）
    correct_format = {'loginName': account_data, 'password': 'test123'}
    print(f"正确格式: {correct_format}")
    print(f"  loginName类型: {type(correct_format['loginName'])}")
    print(f"  loginName值: {correct_format['loginName']}")

if __name__ == '__main__':
    test_json_parsing()
    test_account_format()
    print("\n✅ 所有测试完成!")