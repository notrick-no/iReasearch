#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试上传功能的脚本
"""

import requests
import json

def test_upload():
    # 测试数据
    test_data = [
        {
            "company_name": "测试公司",
            "website": "https://test.com",
            "address": "测试地址",
            "team_info": "测试团队信息",
            "funding_info": "测试融资信息",
            "product_service": "测试产品服务",
            "biz_model": "测试商业模式",
            "partners": "测试合作伙伴",
            "clients": "测试客户",
            "field": "测试领域",
            "detail": "测试详细描述",
            "source": "https://test.com/source",
            "explain": {
                "测试概念1": "这是测试概念1的解释",
                "测试概念2": "这是测试概念2的解释"
            }
        }
    ]
    
    # 创建临时JSON文件
    with open('test_upload.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    # 登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # 登录
        login_response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.status_code} - {login_response.text}")
            return
        
        token = login_response.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 上传文件
        with open('test_upload.json', 'rb') as f:
            files = {'file': ('test_upload.json', f, 'application/json')}
            upload_response = requests.post('http://localhost:5000/api/upload', files=files, headers=headers)
        
        print(f"上传响应状态码: {upload_response.status_code}")
        print(f"上传响应内容: {upload_response.text}")
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            print(f"上传成功!")
            print(f"添加公司数: {result.get('companies_added', 0)}")
            print(f"添加概念数: {result.get('concepts_added', 0)}")
            if result.get('errors'):
                print(f"错误信息: {result['errors']}")
        else:
            print(f"上传失败: {upload_response.text}")
    
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    
    finally:
        # 清理临时文件
        import os
        if os.path.exists('test_upload.json'):
            os.remove('test_upload.json')

if __name__ == '__main__':
    test_upload()
