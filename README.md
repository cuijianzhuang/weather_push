# Weather Push Service 天气推送服务

一个功能强大的天气信息推送服务，支持多平台消息推送，包括企业微信、微信公众号、Telegram 和邮件推送。

## 功能特点

- 🌤️ 实时天气数据获取（基于和风天气 API）
- 🕒 支持早、午、晚间问候
- 👔 智能穿衣建议
- 💡 根据天气情况提供温馨提示
- 📱 多平台消息推送：
  - 企业微信
  - 微信公众号
  - Telegram
  - 邮件推送
- 🎨 支持多种消息模板样式
- 💝 集成彩虹屁和一言 API
- 📝 完善的日志记录系统

## 安装说明

1. 克隆仓库
```bash
git clone https://github.com/yourusername/weather_push.git
cd weather_push
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

### 依赖包说明
项目使用的主要依赖包：
- **requests**: HTTP 请求库，用于调用各类 API
- **python-dateutil**: 日期时间处理工具
- **python-telegram-bot**: Telegram Bot API 客户端
- **wechatpy**: 微信开发工具包
- **yagmail**: 邮件发送工具
- **loguru**: 日志处理库
- **python-dotenv**: 环境变量管理
- **schedule**: 定时任务调度

3. 配置服务
复制 `config.py` 并填写相关配置信息：
- 和风天气 API 密钥
- 微信公众号配置
- Telegram Bot 配置
- 邮件服务配置
- 企业微信 Webhook
- 其他可选配置

## 配置说明

### 基础配置
```python
# 和风天气配置
HEFENG_KEY = "你的和风天气KEY"
LOCATION = "城市ID"  # 例如：101010100 北京

# 用户配置
USER_CONFIG = {
    'name': '用户名',           # 用户昵称
    'city': '城市名',          # 所在城市
    'morning_greeting': True,  # 是否启用早安问候
    'noon_greeting': True,     # 是否启用午安问候
    'evening_greeting': True   # 是否启用晚安问候
}
```

### 推送渠道配置
```python
# 推送方式配置
PUSH_METHODS = {
    'wecom': True,     # 企业微信推送开关
    'wechat': True,    # 微信公众号推送开关
    'telegram': True,  # Telegram推送开关
    'email': True      # 邮件推送开关
}
```

## 使用方法

1. 直接运行
```bash
python weather_push.py
```

2. 定时任务（推荐）
- Linux/Mac (Crontab):
```bash
# 每天早上7点、中午12点和晚上9点运行
0 7,12,21 * * * cd /path/to/weather_push && python weather_push.py
```

- Windows (计划任务):
  - 使用 Windows 任务计划程序创建定时任务
  - 设置触发器为每天指定时间
  - 操作为运行 Python 脚本

## 消息模板

支持多种消息模板样式，可在配置文件中设置：
```python
TEMPLATE_NAME = 'weather'  # 可选值: 'weather', 'elegant', 'modern', 'card', 'compact', 'simple', 'minimal'
```

## 日志管理

- 日志文件位于 `logs` 目录
- 自动清理超过指定天数的日志文件
- 支持日志文件大小限制和轮转

## 注意事项

1. 请确保所有 API 密钥和配置信息的安全性
2. 建议使用环境变量管理敏感配置信息
3. 定期检查日志文件，及时发现并处理异常情况

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至：[cui2421011864@gmail.com]

## 致谢

- [和风天气](https://www.qweather.com/) - 提供天气数据支持
- [天行API](https://www.tianapi.com/) - 提供彩虹屁接口
- [一言](https://hitokoto.cn/) - 提供一言接口