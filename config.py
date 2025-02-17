from templates import (
    EMAIL_TEMPLATE, 
    WX_TEMPLATE, 
    GREETINGS, 
    TIPS
)

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
TELEGRAM_CONFIGS = [
    {
        'name': '主账号',  # 配置名称，用于日志标识
        'bot_token': '7271301946:AAG-oAKmJyjX0GuNXSysWjLWCb-EFHoXT_Q',
        'chat_id': '698060508',
        'enabled': True
    },
    {
        'name': '备用账号',
        'bot_token': 'your_second_bot_token',
        'chat_id': 'your_second_chat_id',
        'enabled': False
    }
]

# 企业微信配置
WECOM_CONFIGS = [
    {
        'name': '主群',  # 群组名称，用于日志标识
        'webhook': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e6b48263-25ec-4750-ad01-4385543014d9',
        'enabled': True
    },
    {
        'name': '备用群',
        'webhook': 'your_second_webhook_url',
        'enabled': False
    }
]

# 天行API配置
TIANAPI_KEY = "204a01116fe07b933f100f36e1763831"

# 用户配置
USER_CONFIG = {
    'name': '崔健壮',           # 用户昵称
    'city': '北京',            # 所在城市
    'province': '北京市',      # 所在省份
    'morning_greeting': True,  # 是否启用早安问候
    'noon_greeting': True,     # 是否启用午安问候
    'evening_greeting': True,  # 是否启用晚安问候
    'memorial_days': True,    # 是否启用纪念日提醒
    'together_days': True     # 是否启用在一起天数提醒
}

# 邮件推送配置
EMAIL = {
    'enabled': True,
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender': 'cui2421011864@gmail.com',
    'password': 'tsqfhxarzzhdlgmm',
    'receivers': [
        '2421011864@qq.com',
        'tonrry@vip.qq.com'
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

# 更新推送配置
PUSH_METHODS = {
    'wecom': False,     # 企业微信推送开关
    'wechat': False,     # 微信公众号推送开关
    'telegram': True,  # Telegram推送开关
    'email': False,       # 邮件推送开关
    'wxpusher': True,  # 启用 WxPusher
}

# 消息模板控制
TEMPLATE_NAME = 'weather'  # 可选值: 'weather', 'elegant', 'modern', 'card', 'compact', 'simple', 'minimal'
ENABLE_CAIHONGPI = False   # 是否启用彩虹屁

# 日志配置
LOG_CONFIG = {
    'max_days': 7,          # 日志文件保留的最大天数
    'max_size': 5*1024*1024, # 单个日志文件的最大大小（5MB）
    'backup_count': 5,       # 保留的备份文件数量
    'log_dir': 'logs',       # 日志文件目录
}

# 在现有配置后添加纪念日配置
MEMORIAL_DAYS = {
    'love_day': {
        'date': '2024-01-01',  # 恋爱纪念日
        'name': '恋爱纪念日',
        'enabled': True
    },
    'birthday': {
        'date': '1995-01-01',  # 生日
        'name': '生日',
        'enabled': True
    },
    # 可以添加更多纪念日...
}

# 添加在一起的日期配置
TOGETHER_DATE = {
    'date': '2024-01-01',  # 在一起的日期
    'name': '在一起',      # 显示的名称
    'enabled': True        # 是否启用
}

# WxPusher配置
WXPUSHER_CONFIG = {
    'enabled': True,  # 是否启用WxPusher推送
    'app_token': 'AT_wRolNkqRMiplwZhyPQWeOniFQiEvn2Ef',  # 你的WxPusher的APP Token
    'uid': 'UID_PWMOAOC0f3xYzqbCv5pFaZSfsQfp',  # 你的WxPusher的接收消息的用户UID
    'api_url': 'http://wxpusher.zjiecode.com/api/send/message'  # WxPusher的API地址
}