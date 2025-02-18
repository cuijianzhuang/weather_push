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
- ⚡ GitHub Actions 自动化部署
- 📅 灵活的定时任务调度

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
- **requests==2.31.0**: HTTP 请求库，用于调用各类 API
- **python-dateutil>=2.8.2**: 日期时间处理工具
- **python-telegram-bot>=2.0.0**: Telegram Bot API 客户端
- **wechatpy>=1.8.18**: 微信开发工具包
- **yagmail>=0.15.293**: 邮件发送工具
- **loguru>=0.7.2**: 日志处理库
- **python-dotenv>=1.0.0**: 环境变量管理
- **schedule>=1.2.1**: 定时任务调度
- **pytz>=2024.1**: 时区处理

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

# 时间配置
TIME_CONFIG = {
    'morning_hour': 7,    # 早安问候时间
    'noon_hour': 12,      # 午安问候时间
    'evening_hour': 21    # 晚安问候时间
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

# 企业微信配置
WECOM_CONFIG = {
    'webhook': 'YOUR_WEBHOOK_URL',
    'mentioned_list': ['@all']  # 可选：需要提醒的成员
}

# Telegram配置
TELEGRAM_CONFIG = {
    'bot_token': 'YOUR_BOT_TOKEN',
    'chat_id': 'YOUR_CHAT_ID'
}

# 邮件配置
EMAIL_CONFIG = {
    'sender': 'your-email@example.com',
    'password': 'your-password',
    'recipients': ['recipient@example.com'],
    'smtp_server': 'smtp.gmail.com'
}
```

### 时区配置
项目默认使用北京时间（Asia/Shanghai），可以通过以下方式设置时区：

1. 环境变量方式：
```bash
# Linux/Mac
export TZ=Asia/Shanghai

# Windows PowerShell
$env:TZ = "Asia/Shanghai"
```

2. Python代码方式：
```python
import os
os.environ['TZ'] = 'Asia/Shanghai'
```

3. Docker环境：
```dockerfile
ENV TZ=Asia/Shanghai
```

4. GitHub Actions配置：
```yaml
jobs:
  push:
    runs-on: ubuntu-latest
    
    steps:
    - name: Set timezone
      run: |
        sudo timedatectl set-timezone Asia/Shanghai
```

### 环境变量配置
```python
# 环境变量配置
ENV_CONFIG = {
    'timezone': 'Asia/Shanghai'
}
```

## 使用方法

1. 直接运行
```bash
python weather_push.py
```

2. 使用调度器（推荐）
```bash
python scheduler.py
```

3. 定时任务
- Linux/Mac (Crontab):
```bash
# 每天早上7点、中午12点和晚上9点运行
0 7,12,21 * * * cd /path/to/weather_push && python weather_push.py
```

- Windows (计划任务):
  - 使用 Windows 任务计划程序创建定时任务
  - 设置触发器为每天指定时间
  - 操作为运行 Python 脚本

## GitHub Actions 自动化

项目已集成 GitHub Actions 工作流，支持：
- 自动化测试
- 定时推送服务（北京时间 8:00, 12:00, 19:00, 0:00）
- Python 3.10 运行环境
- 依赖缓存加速部署
- 手动触发功能
- 自动时区设置（已配置为北京时间）

配置文件位于 `.github/workflows/weather-push.yml`

## 消息模板

支持多种消息模板样式，可在配置文件中设置：
```python
TEMPLATE_NAME = 'weather'  # 可选值: 'weather', 'elegant', 'modern', 'card', 'compact', 'simple', 'minimal'
```

自定义模板可在 `templates.py` 中添加。

## 日志管理

- 日志文件位于 `logs` 目录
- 自动清理超过指定天数的日志文件
- 支持日志文件大小限制和轮转
- 日志级别可配置

```python
# 日志配置
LOG_CONFIG = {
    'retention': '7 days',    # 日志保留时间
    'rotation': '500 MB',     # 单个日志文件大小限制
    'level': 'INFO'           # 日志级别
}
```

## 项目结构

```
weather_push/
├── weather_push.py    # 主程序
├── push_service.py    # 推送服务
├── config.py         # 配置文件
├── templates.py      # 消息模板
├── scheduler.py      # 调度器
├── requirements.txt  # 依赖管理
├── logs/            # 日志目录
└── .github/         # GitHub配置
    └── workflows/   # GitHub Actions
```

## 注意事项

1. 请确保所有 API 密钥和配置信息的安全性
2. 建议使用环境变量管理敏感配置信息
3. 定期检查日志文件，及时发现并处理异常情况
4. 推荐使用 Python 3.8 或更高版本

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至：[cui2421011864@gmail.com]

## 致谢

- [和风天气](https://www.qweather.com/) - 提供天气数据支持
- [天行API](https://www.tianapi.com/) - 提供彩虹屁接口
- [一言](https://hitokoto.cn/) - 提供一言接口