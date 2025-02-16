# 和风天气配置
HEFENG_KEY = "a4b90c17754a42e89c6347dc57a940ec"
LOCATION = "101010100"  # 例如：101010100 北京

# 微信公众号配置
WX_APP_ID = "wx21919d2c956f1fa0"
WX_APP_SECRET = "3b63f81ba90e0ee8dcee60ed40d9cbeb"
WX_TEMPLATE_ID = "mEjk-SKY3uX88mdsL71knIq-WUtD2hRHLhz4YUumHQo"  # 添加模板ID配置
WX_USER_OPENID = "oD8bv7Mo84RkWf_njHsXK_9g7jZA"  # 替换为您的实际OpenID

# 微信消息模板
WX_TEMPLATE = """
{{first.DATA}}

━━━ 天气实况 ━━━
🌡️ 温度：{{temp.DATA}}
🎭 体感：{{feels_like.DATA}}
🌪️ 风向：{{wind_dir.DATA}}
💨 风力：{{wind_scale.DATA}}
💧 湿度：{{humidity.DATA}}

━━━ 贴心建议 ━━━
👔 {{clothes_tip.DATA}}

{{remark.DATA}}
"""

# Telegram配置
TELEGRAM_BOT_TOKEN = "7271301946:AAG-oAKmJyjX0GuNXSysWjLWCb-EFHoXT_Q"
TELEGRAM_CHAT_ID = "698060508"

# 企业微信配置
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e6b48263-25ec-4750-ad01-4385543014d9"

# 天行API配置
TIANAPI_KEY = "204a01116fe07b933f100f36e1763831"

# 用户配置
USER_CONFIG = {
    'name': '崔健壮',           # 用户昵称
    'city': '北京',            # 所在城市
    'morning_greeting': True,  # 是否启用早安问候
    'noon_greeting': True,     # 是否启用午安问候
    'evening_greeting': True   # 是否启用晚安问候
}

# 问候语模板
GREETINGS = {
    'morning': [
        "早安，{name}！新的一天开始啦 ☀️",
        "嗨，{name}！让我们开启美好的一天 🌅",
        "早上好，{name}！愿你今天心情愉快 ✨",
        "早安，{name}！{city}的天气为你播报 🌈",
        "新的一天，新的开始！{name}，准备好了吗？🌟"
    ],
    'noon': [
        "午安，{name}！记得按时吃午饭哦 🍚",
        "中午好，{name}！休息一下吧 ☕",
        "{name}，是时候享用午餐啦 🍜",
        "别忘了午休哦，{name}！养精蓄锐 🌤️",
        "记得补充能量哦，{name}！下午也要加油 🌞"
    ],
    'evening': [
        "晚安，{name}！愿你有个好梦 🌙",
        "晚上好，{name}！该休息啦 ⭐",
        "{name}，记得早点休息哦 💫",
        "晚安，{name}！明天见 🌠",
        "祝{name}晚安，期待明天的相见 ✨"
    ]
}

# 温馨提示模板
TIPS = {
    'cold': [
        "今天温度偏低，{name}记得多穿点哦 🧥",
        "天气转凉，{name}注意保暖 🧣",
        "{name}出门要注意保暖，别着凉啦 🧤"
    ],
    'hot': [
        "今天气温较高，{name}记得防晒 ☂️",
        "天气炎热，{name}要多补充水分哦 💧",
        "注意防暑降温，{name}要照顾好自己 🌊"
    ],
    'rain': [
        "{name}出门记得带伞哦 ☔",
        "今天可能会下雨，{name}要准备好雨具 🌧️",
        "雨天路滑，{name}要注意安全 ⚡"
    ]
}

# 邮件推送配置
EMAIL = {
    'enabled': True,
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender': 'cui2421011864@gmail.com',
    'password': 'tsqfhxarzzhdlgmm',
    'receivers': [
        '2421011864@qq.com'
    ]
}

# 一言API配置
HITOKOTO = {
    'enabled': True,           # 一言开关
    'api_url': 'https://v1.hitokoto.cn/',  # 一言API地址
    'params': {
        'c': 'i',             # 一言类型：i=诗词，a=动画，b=漫画，c=游戏，d=文学，e=原创，f=来自网络，g=其他
        'encode': 'json'       # 返回格式
    }
}

# 邮件HTML模板配置
EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f6f9fc 0%, #eef2f7 100%);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        .container {
            max-width: 650px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 问候语部分 -->
        {{greeting}}

        <!-- 天气预报标题 -->
        <div style="background: linear-gradient(135deg, #6B8DD6 0%, #4B6CB7 100%); padding: 30px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 28px;">🌈 今日天气预报</h1>
            <p style="margin: 10px 0 0;">{{time}}</p>
        </div>

        <!-- 天气数据部分 -->
        <div style="padding: 30px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div style="background: #f8faff; padding: 20px; border-radius: 10px;">
                    <div style="color: #666; font-size: 14px;">当前温度</div>
                    <div style="color: #ff6b6b; font-size: 24px; font-weight: bold;">{{temp}}°C</div>
                </div>
                <div style="background: #f8faff; padding: 20px; border-radius: 10px;">
                    <div style="color: #666; font-size: 14px;">体感温度</div>
                    <div style="color: #ff6b6b; font-size: 24px; font-weight: bold;">{{feels_like}}°C</div>
                </div>
                <div style="background: #f8faff; padding: 20px; border-radius: 10px;">
                    <div style="color: #666; font-size: 14px;">风向</div>
                    <div style="color: #4B6CB7; font-size: 20px; font-weight: bold;">{{wind_dir}}</div>
                </div>
                <div style="background: #f8faff; padding: 20px; border-radius: 10px;">
                    <div style="color: #666; font-size: 14px;">风力等级</div>
                    <div style="color: #4B6CB7; font-size: 20px; font-weight: bold;">{{wind_scale}}级</div>
                </div>
            </div>

            <!-- 湿度 -->
            <div style="background: #f8faff; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
                <div style="color: #666; font-size: 14px;">相对湿度</div>
                <div style="color: #00a8ff; font-size: 20px; font-weight: bold;">{{humidity}}%</div>
            </div>

            <!-- 穿衣建议 -->
            <div style="margin-bottom: 30px;">
                <h2 style="color: #333; font-size: 20px; margin-bottom: 15px;">👔 穿衣建议</h2>
                <div style="background: #f8faff; padding: 20px; border-radius: 10px; line-height: 1.6;">
                    {{clothes_tip}}
                </div>
            </div>

            <!-- 温馨提示 -->
            {{warm_tip}}

            <!-- 一言 -->
            <div style="background: #EEF2FF; padding: 20px; border-radius: 10px; margin-top: 30px;">
                <h2 style="color: #333; font-size: 20px; margin: 0 0 15px;">📖 今日一言</h2>
                <p style="margin: 0; color: #4B6CB7; font-size: 16px;">{{hitokoto_text}}</p>
                <p style="margin: 10px 0 0; color: #666; font-size: 14px; text-align: right;">
                    —— {{hitokoto_from}}
                </p>
            </div>
        </div>

        <!-- 页脚 -->
        <div style="text-align: center; padding: 20px; color: #666; font-size: 14px; background: #f8faff;">
            <p style="margin: 5px 0;">Weather Assistant | 天气助手</p>
            <p style="margin: 5px 0;">{{time}} 更新</p>
        </div>
    </div>
</body>
</html>
"""

# 更新推送配置
PUSH_METHODS = {
    'wecom': True,     # 企业微信推送开关
    'wechat': True,     # 微信公众号推送开关
    'telegram': True,  # Telegram推送开关
    'email': True       # 邮件推送开关
}

# 消息模板控制
TEMPLATE_NAME = 'weather'  # 可选值: 'weather', 'elegant', 'modern', 'card', 'compact', 'simple', 'minimal'
ENABLE_CAIHONGPI = False   # 是否启用彩虹屁

# 日志配置
LOG_CONFIG = {
    'max_days': 30,          # 日志文件保留的最大天数
    'max_size': 5*1024*1024, # 单个日志文件的最大大小（5MB）
    'backup_count': 5,       # 保留的备份文件数量
    'log_dir': 'logs',       # 日志文件目录
}