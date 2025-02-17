import requests
from datetime import datetime, date, timedelta
import pytz  # 添加时区支持
import config
from push_service import MessagePusher
import http.client
import urllib
import json
from templates import ALL_TEMPLATES, CAIHONGPI_TEMPLATES
import random
import logging
from logging.handlers import RotatingFileHandler
import os

# 创建日志目录
log_dir = config.LOG_CONFIG['log_dir']
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def cleanup_logs():
    """清理超过指定天数的日志文件"""
    max_days = config.LOG_CONFIG['max_days']
    logger.info(f"开始清理{max_days}天前的日志文件")
    try:
        # 获取日志目录下的所有文件
        log_files = [f for f in os.listdir(log_dir) if f.startswith('weather_push_') and f.endswith('.log')]
        current_time = datetime.now()
        deleted_count = 0
        
        for log_file in log_files:
            file_path = os.path.join(log_dir, log_file)
            # 获取文件最后修改时间
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            # 计算文件存在的天数
            days_old = (current_time - file_mtime).days
            
            # 如果文件超过指定天数，则删除
            if days_old > max_days:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    logger.info(f"已删除日志文件: {log_file}")
                except Exception as e:
                    logger.error(f"删除日志文件失败 {log_file}: {str(e)}")
        
        logger.info(f"日志清理完成，共删除 {deleted_count} 个文件")
    except Exception as e:
        logger.error(f"日志清理过程出错: {str(e)}", exc_info=True)

# 生成日志文件名（包含日期）
log_file = os.path.join(log_dir, f'weather_push_{datetime.now().strftime("%Y%m")}.log')

# 配置日志
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 创建 RotatingFileHandler（使用配置的大小限制）
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=config.LOG_CONFIG['max_size'],
    backupCount=config.LOG_CONFIG['backup_count'],
    encoding='utf-8'
)
file_handler.setFormatter(formatter)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# 配置根日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 添加获取北京时间的辅助函数
def get_beijing_time():
    """获取北京时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    beijing_now = utc_now.astimezone(beijing_tz)
    return beijing_now

def get_caihongpi():
    """获取彩虹屁内容"""
    try:
        logger.info("开始获取彩虹屁内容")
        conn = http.client.HTTPSConnection('apis.tianapi.com')
        params = urllib.parse.urlencode({'key': config.TIANAPI_KEY})
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        conn.request('POST', '/caihongpi/index', params, headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode('utf-8'))
        
        if result['code'] == 200:
            logger.info("彩虹屁内容获取成功")
            return result['result']['content']
        logger.warning(f"彩虹屁API返回异常状态码: {result['code']}")
        return "今天也是充满希望的一天~"
    except Exception as e:
        logger.error(f"获取彩虹屁失败: {str(e)}", exc_info=True)
        return "今天也是充满希望的一天~"

def get_hitokoto():
    """获取一言内容"""
    if not config.HITOKOTO['enabled']:
        logger.info("一言功能未启用")
        return None
        
    try:
        logger.info("开始获取一言内容")
        response = requests.get(
            config.HITOKOTO['api_url'],
            params=config.HITOKOTO['params']
        )
        result = response.json()
        
        logger.info("一言内容获取成功")
        return {
            'text': result['hitokoto'],
            'from': f"{result['from']} - {result['from_who']}" if result.get('from_who') else result['from']
        }
    except Exception as e:
        logger.error(f"获取一言失败: {str(e)}", exc_info=True)
        return None

def calculate_days(target_date_str):
    """计算距离目标日期的天数"""
    target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    today = date.today()
    
    # 计算今年的纪念日
    this_year_date = target_date.replace(year=today.year)
    
    # 如果今年的纪念日已过，计算明年的
    if this_year_date < today:
        this_year_date = this_year_date.replace(year=today.year + 1)
    
    days_remaining = (this_year_date - today).days
    years_passed = today.year - target_date.year
    
    return days_remaining, years_passed

def get_memorial_days_message():
    """获取纪念日消息"""
    if not config.USER_CONFIG.get('memorial_days'):
        return ""
        
    memorial_messages = []
    for key, day_info in config.MEMORIAL_DAYS.items():
        if day_info['enabled']:
            days_remaining, years_passed = calculate_days(day_info['date'])
            if days_remaining <= 30:  # 只显示30天内的纪念日
                if days_remaining == 0:
                    message = f"🎉 今天是{day_info['name']}！"
                else:
                    message = f"🎯 距离{day_info['name']}还有{days_remaining}天"
                if years_passed > 0:
                    message += f"（{years_passed}周年）"
                memorial_messages.append(message)
    
    if memorial_messages:
        return "\n━━━ 纪念日提醒 ━━━\n" + "\n".join(memorial_messages) + "\n"
    return ""

def calculate_memorial_days():
    """计算纪念日天数"""
    beijing_now = get_beijing_time()
    today = beijing_now.date()
    
    memorial_messages = []
    for key, memorial in config.MEMORIAL_DAYS.items():
        if memorial['enabled']:
            memorial_date = datetime.strptime(memorial['date'], '%Y-%m-%d').date()
            days = (today - memorial_date).days
            if days <= 30:  # 只显示30天内的纪念日
                if days == 0:
                    message = f"🎉 今天是{memorial['name']}！"
                else:
                    message = f"🎯 距离{memorial['name']}还有{days}天"
                if memorial.get('years_passed', 0) > 0:
                    message += f"（{memorial['years_passed']}周年）"
                memorial_messages.append(message)
    
    if memorial_messages:
        return "\n━━━ 纪念日提醒 ━━━\n" + "\n".join(memorial_messages) + "\n"
    return ""

def calculate_together_days():
    """计算在一起的天数"""
    if not config.TOGETHER_DATE['enabled']:
        return ""
        
    beijing_now = get_beijing_time()
    today = beijing_now.date()
    together_date = datetime.strptime(config.TOGETHER_DATE['date'], '%Y-%m-%d').date()
    days = (today - together_date).days
    
    if days < 0:
        return ""
    
    # 计算年月日
    years = days // 365
    remaining_days = days % 365
    months = remaining_days // 30
    days = remaining_days % 30
    
    # 构建消息
    time_parts = []
    if years > 0:
        time_parts.append(f"{years}年")
    if months > 0:
        time_parts.append(f"{months}个月")
    if days > 0:
        time_parts.append(f"{days}天")
        
    time_str = "".join(time_parts)
    
    return f"\n💑 我们已经在一起{time_str}啦~\n"

def format_hourly_forecast(hourly_data):
    """格式化逐小时预报数据"""
    if not hourly_data:
        return ""
        
    forecast_lines = ["━━━ 未来天气 ━━━"]
    for hour in hourly_data:
        forecast_lines.append(
            f"⏰ {hour['time']} "
            f"🌡️ {hour['temp']}°C "
            f"☁️ {hour['text']} "
            f"💨 {hour['windDir']}{hour['windScale']}级 "
            f"☔ {hour['pop']}%"
        )
    return "\n".join(forecast_lines)

def format_air_quality(air_data):
    """格式化空气质量数据"""
    if not air_data:
        return ""
        
    # 添加空气质量表情符号
    aqi = int(air_data['aqi'])
    if aqi <= 50:
        quality_emoji = "🟢"  # 优
    elif aqi <= 100:
        quality_emoji = "🟡"  # 良
    elif aqi <= 150:
        quality_emoji = "🟠"  # 轻度污染
    elif aqi <= 200:
        quality_emoji = "🔴"  # 中度污染
    elif aqi <= 300:
        quality_emoji = "🟣"  # 重度污染
    else:
        quality_emoji = "🟤"  # 严重污染
    
    air_lines = [
        "━━━ 空气质量 ━━━",
        f"{quality_emoji} AQI指数：{air_data['aqi']} ({air_data['category']})",
        f"😷 PM2.5：{air_data['pm2p5']}μg/m³",
        f"💨 PM10：{air_data['pm10']}μg/m³",
        f"🌫️ 其他指标：",
        f"  • NO₂：{air_data['no2']}μg/m³",
        f"  • SO₂：{air_data['so2']}μg/m³",
        f"  • CO：{air_data['co']}mg/m³",
        f"  • O₃：{air_data['o3']}μg/m³"
    ]
    return "\n".join(air_lines)

def format_life_indices(indices_data):
    """格式化生活指数数据"""
    if not indices_data:
        return ""
        
    # 指数对应的emoji
    index_emojis = {
        '1': '🏃',  # 运动指数
        '2': '🚗',  # 洗车指数
        '3': '👔',  # 穿衣指数
        '5': '☀️',  # 紫外线指数
        '9': '🤒'   # 感冒指数
    }
    
    indices_lines = ["━━━ 生活指数 ━━━"]
    for index_type, emoji in index_emojis.items():
        if index_type in indices_data:
            index = indices_data[index_type]
            indices_lines.append(
                f"{emoji} {index['name']}：{index['category']}\n"
                f"   {index['text']}"
            )
    
    return "\n".join(indices_lines)

def format_message(weather_data, caihongpi_text=None):
    """根据模板格式化消息"""
    logger.info("开始格式化消息")
    
    # 获取北京时间
    beijing_now = get_beijing_time()
    current_hour = beijing_now.hour
    current_time = beijing_now.strftime('%Y-%m-%d %H:%M')
    
    # 根据时间选择问候语
    greeting = ""
    if config.USER_CONFIG['morning_greeting'] and 5 <= current_hour <= 10:
        greeting = random.choice(config.GREETINGS['morning'])
        logger.info("使用早安问候语")
    elif config.USER_CONFIG['noon_greeting'] and 11 <= current_hour <= 13:
        greeting = random.choice(config.GREETINGS['noon'])
        logger.info("使用午安问候语")
    elif config.USER_CONFIG['evening_greeting'] and 18 <= current_hour <= 23:
        greeting = random.choice(config.GREETINGS['evening'])
        logger.info("使用晚安问候语")
    
    # 格式化问候语
    if greeting:
        greeting = greeting.format(
            name=config.USER_CONFIG['name'],
            city=config.USER_CONFIG['city']
        )
    
    # 格式化逐小时预报
    hourly_forecast = ""
    if weather_data.get('hourly_forecast'):
        hourly_forecast = format_hourly_forecast(weather_data['hourly_forecast'])
    
    # 格式化空气质量数据
    air_quality = ""
    if weather_data.get('air_quality'):
        air_quality = format_air_quality(weather_data['air_quality'])
    
    # 格式化生活指数数据
    life_indices = ""
    if weather_data.get('life_indices'):
        life_indices = format_life_indices(weather_data['life_indices'])
    
    # 准备基础数据
    message_data = {
        'greeting': greeting or "",
        'city': config.USER_CONFIG['city'],
        'time': current_time,
        'temp': weather_data.get('temp', 'N/A'),
        'wind_dir': weather_data.get('wind_dir', 'N/A'),
        'wind_scale': weather_data.get('wind_scale', 'N/A'),
        'humidity': weather_data.get('humidity', 'N/A'),
        'feels_like': weather_data.get('feels_like', 'N/A'),
        'clothes_tip': weather_data.get('clothes_tip', 'N/A'),
        'warm_tip': weather_data.get('warm_tip', ''),
        'province': config.USER_CONFIG['province'],
        'memorial_days': calculate_memorial_days(),
        'together_days': calculate_together_days(),
        'hourly_forecast': hourly_forecast,
        'air_quality': air_quality,
        'life_indices': life_indices  # 添加生活指数
    }
    
    # 格式化基础消息
    template = ALL_TEMPLATES.get(config.TEMPLATE_NAME, ALL_TEMPLATES['weather'])
    formatted_message = template.format(**message_data)
    
    # 添加一言内容
    if weather_data.get('hitokoto'):
        hitokoto_data = weather_data['hitokoto']
        hitokoto_text = '\n'.join([
            "📖 今日一言：",
            f"「{hitokoto_data['text']}」",
            f"—— {hitokoto_data['from']}"
        ])
        formatted_message = f"{formatted_message}\n{hitokoto_text}"
    
    # 如果启用彩虹屁且提供了彩虹屁文本
    if config.ENABLE_CAIHONGPI and caihongpi_text:
        formatted_message = f"{formatted_message}\n🌈 彩虹屁：\n{caihongpi_text}"
    
    return formatted_message.strip()

def get_weather():
    """获取天气信息"""
    try:
        # 获取实时天气数据
        url = f"https://devapi.qweather.com/v7/weather/now?location={config.LOCATION}&key={config.HEFENG_KEY}"
        response = requests.get(url)
        weather_data = response.json()
        
        # 获取逐小时预报
        hourly_forecast = get_hourly_forecast()
        
        # 获取生活指数数据
        life_indices = get_life_indices()
        
        # 获取空气质量数据
        air_quality = get_air_quality()
        
        if weather_data.get('code') == '200':
            now = weather_data['now']
            
            # 获取一言
            hitokoto = get_hitokoto()
            
            # 获取穿衣建议
            clothes_tip = "注意适当增减衣物"
            if life_indices and '3' in life_indices:  # 使用生活指数中的穿衣指数
                clothes_tip = life_indices['3']['text']
            
            # 根据温度生成温馨提示
            temp = float(now['temp'])
            tip = ""
            if temp <= 15:
                tip = random.choice(config.TIPS['cold'])
            elif temp >= 30:
                tip = random.choice(config.TIPS['hot'])
            
            if now.get('text', '').find('雨') != -1:
                tip = random.choice(config.TIPS['rain'])
            
            if tip:
                tip = tip.format(name=config.USER_CONFIG['name'])
                warm_tip = f"💝 温馨提示：\n{tip}"
            else:
                warm_tip = ""
            
            # 整合数据
            weather_info = {
                'temp': now['temp'],
                'feels_like': now['feelsLike'],
                'wind_dir': now['windDir'],
                'wind_scale': now['windScale'],
                'humidity': now['humidity'],
                'clothes_tip': clothes_tip,
                'hitokoto': hitokoto,
                'greeting': '',
                'warm_tip': warm_tip,
                'memorial_days': '',
                'together_days': calculate_together_days(),
                'hourly_forecast': hourly_forecast,
                'air_quality': air_quality,
                'life_indices': life_indices  # 添加生活指数数据
            }
            
            return weather_info
        else:
            logger.error(f"获取天气数据失败: {weather_data.get('code')} - {weather_data.get('msg', '未知错误')}")
            return None
            
    except Exception as e:
        logger.error(f"获取天气信息异常: {str(e)}", exc_info=True)
        return None

def get_hourly_forecast():
    """获取逐小时天气预报"""
    try:
        logger.info("开始获取逐小时天气预报")
        url = f"https://devapi.qweather.com/v7/weather/24h?location={config.LOCATION}&key={config.HEFENG_KEY}"
        response = requests.get(url)
        forecast_data = response.json()
        
        if forecast_data.get('code') == '200':
            hourly_forecasts = []
            for hour in forecast_data['hourly'][:12]:  # 只取未来12小时
                forecast_time = datetime.strptime(hour['fxTime'], '%Y-%m-%dT%H:%M%z')
                hourly_forecasts.append({
                    'time': forecast_time.strftime('%H:00'),
                    'temp': hour['temp'],
                    'text': hour['text'],
                    'windDir': hour['windDir'],
                    'windScale': hour['windScale'],
                    'pop': hour.get('pop', '0')  # 降水概率
                })
            logger.info("逐小时天气预报获取成功")
            return hourly_forecasts
        else:
            logger.error(f"获取逐小时预报失败: {forecast_data.get('code')} - {forecast_data.get('msg', '未知错误')}")
            return None
            
    except Exception as e:
        logger.error(f"获取逐小时天气预报异常: {str(e)}", exc_info=True)
        return None

def get_air_quality():
    """获取空气质量信息"""
    try:
        logger.info("开始获取空气质量数据")
        url = f"https://devapi.qweather.com/v7/air/now?location={config.LOCATION}&key={config.HEFENG_KEY}"
        response = requests.get(url)
        air_data = response.json()
        
        if air_data.get('code') == '200':
            air = air_data['now']
            air_quality = {
                'aqi': air['aqi'],  # 空气质量指数
                'category': air['category'],  # 空气质量级别
                'pm2p5': air['pm2p5'],  # PM2.5
                'pm10': air['pm10'],  # PM10
                'no2': air['no2'],  # 二氧化氮
                'so2': air['so2'],  # 二氧化硫
                'co': air['co'],  # 一氧化碳
                'o3': air['o3']  # 臭氧
            }
            logger.info("空气质量数据获取成功")
            return air_quality
        else:
            logger.error(f"获取空气质量数据失败: {air_data.get('code')} - {air_data.get('msg', '未知错误')}")
            return None
            
    except Exception as e:
        logger.error(f"获取空气质量数据异常: {str(e)}", exc_info=True)
        return None

def get_life_indices():
    """获取生活指数信息"""
    try:
        logger.info("开始获取生活指数数据")
        # 获取多个生活指数: 1-运动，2-洗车，3-穿衣，5-紫外线，9-感冒
        indices_types = "1,2,3,5,9"
        url = f"https://devapi.qweather.com/v7/indices/1d?location={config.LOCATION}&key={config.HEFENG_KEY}&type={indices_types}"
        response = requests.get(url)
        indices_data = response.json()
        
        if indices_data.get('code') == '200':
            indices = {}
            for index in indices_data['daily']:
                indices[index['type']] = {
                    'name': index['name'],
                    'category': index['category'],
                    'text': index['text']
                }
            logger.info("生活指数数据获取成功")
            return indices
        else:
            logger.error(f"获取生活指数数据失败: {indices_data.get('code')} - {indices_data.get('msg', '未知错误')}")
            return None
            
    except Exception as e:
        logger.error(f"获取生活指数数据异常: {str(e)}", exc_info=True)
        return None

def push_message(weather_data, formatted_message):
    """推送消息到各个平台"""
    success_count = 0
    results = []
    
    # 获取问候语和温馨提示
    current_hour = datetime.now().hour
    greeting = ""
    if config.USER_CONFIG['morning_greeting'] and 5 <= current_hour <= 10:
        greeting = random.choice(config.GREETINGS['morning'])
    elif config.USER_CONFIG['noon_greeting'] and 11 <= current_hour <= 13:
        greeting = random.choice(config.GREETINGS['noon'])
    elif config.USER_CONFIG['evening_greeting'] and 18 <= current_hour <= 23:
        greeting = random.choice(config.GREETINGS['evening'])
    
    if greeting:
        greeting = greeting.format(
            name=config.USER_CONFIG['name'],
            city=config.USER_CONFIG['city']
        )
    
    # 更新 weather_data
    weather_data.update({
        'greeting': greeting,
        'memorial_days': calculate_memorial_days(),
        'together_days': calculate_together_days(),
        'warm_tip': weather_data.get('warm_tip', '')  # 保持原有的温馨提示
    })
    
    # 微信公众号推送
    if config.PUSH_METHODS.get('wechat'):
        try:
            logger.info("尝试推送到微信公众号")
            MessagePusher.push_to_wechat(
                config.WX_APP_ID,
                config.WX_APP_SECRET,
                config.WX_USER_ID,
                weather_data
            )
            success_count += 1
            results.append("✅ 微信公众号：推送成功")
            logger.info("微信公众号推送成功")
        except Exception as e:
            results.append(f"❌ 微信公众号：推送失败 - {str(e)}")
            logger.error(f"微信公众号推送失败: {str(e)}", exc_info=True)
    else:
        results.append("⏭️ 微信公众号：未启用")
        logger.info("微信公众号推送未启用")
    
    # Telegram多账号推送
    if config.PUSH_METHODS.get('telegram'):
        for tg_config in config.TELEGRAM_CONFIGS:
            if tg_config['enabled']:
                try:
                    logger.info(f"尝试推送到 Telegram - {tg_config['name']}")
                    MessagePusher.push_to_telegram(
                        tg_config['bot_token'],
                        tg_config['chat_id'],
                        formatted_message
                    )
                    success_count += 1
                    results.append(f"✅ Telegram({tg_config['name']})：推送成功")
                    logger.info(f"Telegram({tg_config['name']}) 推送成功")
                except Exception as e:
                    results.append(f"❌ Telegram({tg_config['name']})：推送失败 - {str(e)}")
                    logger.error(f"Telegram({tg_config['name']}) 推送失败: {str(e)}", exc_info=True)
    else:
        results.append("⏭️ Telegram：未启用")
        logger.info("Telegram 推送未启用")
    
    # 企业微信多群组推送
    if config.PUSH_METHODS.get('wecom'):
        for wecom_config in config.WECOM_CONFIGS:
            if wecom_config['enabled']:
                try:
                    logger.info(f"尝试推送到企业微信 - {wecom_config['name']}")
                    MessagePusher.push_to_wecom(
                        wecom_config['webhook'],
                        weather_data
                    )
                    success_count += 1
                    results.append(f"✅ 企业微信({wecom_config['name']})：推送成功")
                    logger.info(f"企业微信({wecom_config['name']}) 推送成功")
                except Exception as e:
                    results.append(f"❌ 企业微信({wecom_config['name']})：推送失败 - {str(e)}")
                    logger.error(f"企业微信({wecom_config['name']}) 推送失败: {str(e)}", exc_info=True)
    else:
        results.append("⏭️ 企业微信：未启用")
        logger.info("企业微信推送未启用")
    
    # 邮件推送
    if config.PUSH_METHODS.get('email'):
        try:
            logger.info("尝试推送到邮件")
            MessagePusher.push_to_email(
                config.EMAIL,
                weather_data,
                f"天气预报 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            success_count += 1
            results.append("✅ 邮件推送：推送成功")
            logger.info("邮件推送成功")
        except Exception as e:
            results.append(f"❌ 邮件推送：推送失败 - {str(e)}")
            logger.error(f"邮件推送失败: {str(e)}", exc_info=True)
    else:
        results.append("⏭️ 邮件推送：未启用")
        logger.info("邮件推送未启用")
    
    # WxPusher推送（个人微信）
    if config.WXPUSHER_CONFIG.get('enabled'):
        try:
            logger.info("尝试推送到WxPusher")
            MessagePusher.push_to_wxpusher(weather_data)
            success_count += 1
            results.append("✅ WxPusher：推送成功")
            logger.info("WxPusher推送成功")
        except Exception as e:
            results.append(f"❌ WxPusher：推送失败 - {str(e)}")
            logger.error(f"WxPusher推送失败: {str(e)}", exc_info=True)
    else:
        results.append("⏭️ WxPusher：未启用")
        logger.info("WxPusher推送未启用")
    
    logger.info(f"推送完成，成功次数: {success_count}")
    return success_count, results

def main():
    logger.info("=" * 50)
    logger.info("天气推送服务启动")
    
    try:
        # 清理过期日志文件
        cleanup_logs()
        
        # 获取天气信息
        weather_data = get_weather()
        
        if weather_data:
            logger.info("天气数据获取成功")
            
            # 使用模板格式化消息
            caihongpi_text = weather_data.get('caihongpi', None)
            formatted_message = format_message(weather_data, caihongpi_text)
            
            # 推送消息
            success_count, results = push_message(weather_data, formatted_message)
            
            # 输出推送结果
            logger.info("\n=== 推送结果汇总 ===")
            logger.info(f"启用的推送渠道数：{sum(config.PUSH_METHODS.values())}")
            logger.info(f"成功推送数：{success_count}")
            logger.info("\n=== 详细结果 ===")
            for result in results:
                logger.info(result)
            logger.info("=" * 50)
        else:
            logger.error("获取天气信息失败")
    except Exception as e:
        logger.error("天气推送服务运行异常", exc_info=True)
    finally:
        logger.info("天气推送服务结束")
        logger.info("=" * 50)

if __name__ == "__main__":
    main() 