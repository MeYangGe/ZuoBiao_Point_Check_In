# ZuoBiao_Point_Check_In

# ZuoBiao自动刷积分

> ZuoBiao自动刷积分，现已增强IP伪装功能

## 🚀 新增功能

### IP伪装功能
- 自动生成随机IP地址池
- 多种User-Agent轮换
- 模拟真实浏览器请求头
- 添加常见代理服务器头部信息
- 每次请求自动更换伪装IP

### 安全特性
- 不使用代理服务器，纯本地IP伪装
- 随机化的请求特征
- 防止被服务器识别为机器人
- 提高账号安全性

## Github Actions 部署指南

### 一、Fork 此仓库

### 二、设置账号密码
# 新增
添加名为  **CONFIG**的变量: Settings-->Secrets-->New secret ,使用下面json模板配置多账户，支持邮箱,手机号
```
{
  "ZUOBIAO": [
            {
                "account": "XXXX",
                "password": "XXXX",
                "dingtalk": "XXXX"
            }
        ]
}
```
> 添加名为  **PAT** 的变量: Settings-->Secrets-->New secret

| Secrets |  格式  |
| -------- | ----- |
| PAT |   此处**PAT**需要申请，值为github token，教程详见：https://www.jianshu.com/p/bb82b3ad1d11 ,需要repo和workflow权限,此项必填，避免git push的权限错误。 |

## 🔧 技术实现

### IP伪装原理
1. **随机IP生成**: 从预定义的公网IP段中随机生成合法IP地址
2. **请求头伪装**: 添加X-Forwarded-For、X-Real-IP等常见代理头部
3. **User-Agent轮换**: 在多种浏览器User-Agent之间随机切换
4. **动态更新**: 每次HTTP请求都会使用新的伪装IP

### 支持的伪装头部
- `X-Forwarded-For`: 模拟代理服务器转发
- `X-Real-IP`: 模拟真实客户端IP
- `X-Originating-IP`: 模拟源IP地址
- `X-Remote-IP`: 模拟远程IP
- `X-Client-IP`: 模拟客户端IP
- `True-Client-IP`: Cloudflare风格的真实IP
- `CF-Connecting-IP`: Cloudflare连接IP
- `Fastly-Client-IP`: Fastly CDN客户端IP
- `Via`: 代理路径信息
- `Forwarded`: 标准转发头部

## ⚠️ 注意事项

1. 本功能仅用于学习研究，请遵守相关服务条款
2. 不建议频繁调用，以免对服务器造成压力
3. IP伪装不能保证100%不被检测，仅为辅助手段
4. 请合理使用，避免影响正常用户