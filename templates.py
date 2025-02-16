# 在文件顶部添加导出
__all__ = ['ALL_TEMPLATES', 'CAIHONGPI_TEMPLATES']

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