# 在文件顶部添加导出
__all__ = ['ALL_TEMPLATES', 'CAIHONGPI_TEMPLATES', 'GREETINGS', 'TIPS']

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

# 邮件HTML模板
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
        .location-badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            margin-top: 10px;
            font-size: 14px;
        }
        .memorial-days {
            background: linear-gradient(135deg, #FFE6E6 0%, #FFF0F0 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .memorial-item {
            margin: 10px 0;
            color: #FF6B6B;
        }
        .together-days {
            background: linear-gradient(135deg, #FFE6F0 0%, #FFF0F5 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }
        .together-days h2 {
            color: #333;
            font-size: 20px;
            margin: 0 0 15px;
        }
        .together-days div {
            color: #FF69B4;
            font-size: 18px;
            font-weight: bold;
            line-height: 1.6;
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
            <div class="location-badge">📍 {{province}}{{city}}</div>
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

            <!-- 纪念日提醒 -->
            {{memorial_days_html}}

            <!-- 在一起天数 -->
            {{together_days_html}}

            <!-- 温馨提示 -->
            {{warm_tip_html}}

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

# 消息模板配置
TEMPLATES = {
    'weather': """
{greeting}

🌈 {province}{city}天气播报 
⏰ 更新时间：{time}
━━━━━━━━━━━━━━━
🌡️ 当前温度：{temp}°C
🎭 体感温度：{feels_like}°C
🌪️ 风向状况：{wind_dir}
💨 风力等级：{wind_scale}级
💧 相对湿度：{humidity}%
━━━━━━━━━━━━━━━
👔 穿衣建议：
{clothes_tip}

{memorial_days}
{together_days}
{warm_tip}
""",
    
    'elegant': """
{greeting}

╭────✨ 天气预报 ✨────╮

     {time}
⋆｡°✩ 天气状况 ✩°｡⋆

🌡️ 温度：{temp}°C
🎭 体感：{feels_like}°C
🌪️ 风向：{wind_dir}
💨 风力：{wind_scale}级
💧 湿度：{humidity}%

✿ 穿衣建议 ✿
{clothes_tip}

{warm_tip}
╰─────────────────╯
""",

    'modern': """
{greeting}

⚡️ 实时天气快报 ⚡️
───────────────
📍 {city} | ⏰ {time}

🌡️ 温度情况
• 实际温度：{temp}°C
• 体感温度：{feels_like}°C

🌪️ 风力情况
• 风向：{wind_dir}
• 风力：{wind_scale}级
• 湿度：{humidity}%

🎯 出行建议
{clothes_tip}

💝 温馨提示
{warm_tip}
───────────────
""",

    'fancy': """
{greeting}

•❅──────✧ 天气播报 ✧──────❅•

      {time}

╭── 天气状况 ──╮
⋆ 温度：{temp}°C
⋆ 体感：{feels_like}°C
⋆ 风向：{wind_dir}
⋆ 风力：{wind_scale}级
⋆ 湿度：{humidity}%
╰──────────╯

╭── 贴心建议 ──╮
{clothes_tip}

{warm_tip}
╰──────────╯
""",

    'simple': """
📱 {time} | 天气速报
• 温度：{temp}°C ({feels_like}°C)
• 风况：{wind_dir} {wind_scale}级
• 湿度：{humidity}%
• 建议：{clothes_tip}
""",

    'minimal': """
🌡️ {temp}°C | 💨 {wind_dir} | 👔 {clothes_tip}
""",

    'card': """
┏━━━━ 天气速览 ━━━━┓
  
   📅 {time}
   🌡️ {temp}°C
   🌪️ {wind_dir}
   💨 {wind_scale}级
   💧 {humidity}%
   
   👔 {clothes_tip}
  
┗━━━━━━━━━━━━━━━┛
""",

    'box': """
┌─────────────────┐
│    天气实况速递    │
├─────────────────┤
│ ⏰ {time}
│ 🌡️ {temp}°C
│ 🎭 体感 {feels_like}°C
│ 🌪️ {wind_dir} {wind_scale}级
│ 💧 湿度 {humidity}%
├─────────────────┤
│ 👔 穿衣建议：
│ {clothes_tip}
└─────────────────┘
""",

    'compact': """
⚡️ 天气速览 | {time}
────────────────
🌡️ {temp}°C ({feels_like}°C)
🌪️ {wind_dir} · {wind_scale}级 · 💧{humidity}%
👔 {clothes_tip}
"""
}

# 彩虹屁模板
CAIHONGPI_TEMPLATES = {
    'normal': """
🌈 每日彩虹屁：
{caihongpi_text}
"""
}

# 自定义模板示例
CUSTOM_TEMPLATES = {
    'custom': """
🎯 天气速报 | {time}
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
温度：{temp}°C
体感：{feels_like}°C
风向：{wind_dir}
风力：{wind_scale}级
湿度：{humidity}%
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
{clothes_tip}
"""
}

# 合并所有模板
ALL_TEMPLATES = {**TEMPLATES, **CUSTOM_TEMPLATES} 