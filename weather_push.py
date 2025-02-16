import requests
from datetime import datetime, date
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

def format_message(weather_data, life_info, caihongpi_text=None):
    """根据模板格式化消息"""
    logger.info("开始格式化消息")
    
    # 获取当前时间
    current_hour = datetime.now().hour
    
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
    
    # 根据温度选择温馨提示
    temp = float(weather_data.get('temp', 0))
    tip = ""
    if temp <= 15:
        tip = random.choice(config.TIPS['cold'])
        logger.info("使用寒冷天气提示")
    elif temp >= 30:
        tip = random.choice(config.TIPS['hot'])
        logger.info("使用炎热天气提示")
    
    if weather_data.get('wind_dir', '').find('雨') != -1:
        tip = random.choice(config.TIPS['rain'])
        logger.info("使用雨天提示")
    
    if tip:
        tip = tip.format(name=config.USER_CONFIG['name'])
    
    logger.info(f"使用模板: {config.TEMPLATE_NAME}")
    template = ALL_TEMPLATES.get(config.TEMPLATE_NAME, ALL_TEMPLATES['weather'])
    
    # 准备基础数据
    message_data = {
        'greeting': greeting or "",  # 如果没有问候语，使用空字符串
        'city': config.USER_CONFIG['city'],
        'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'temp': weather_data.get('temp', 'N/A'),
        'wind_dir': weather_data.get('wind_dir', 'N/A'),
        'wind_scale': weather_data.get('wind_scale', 'N/A'),
        'humidity': weather_data.get('humidity', 'N/A'),
        'feels_like': weather_data.get('feels_like', 'N/A'),
        'clothes_tip': weather_data.get('clothes_tip', 'N/A'),
        'warm_tip': f"💝 温馨提示：\n{tip}" if tip else "",
        'province': config.USER_CONFIG['province'],
        'memorial_days': get_memorial_days_message()
    }
    
    # 格式化基础消息
    formatted_message = template.format(**message_data)
    
    # 添加一言内容
    if weather_data.get('hitokoto'):
        hitokoto_text = f"""
📖 今日一言：
「{weather_data['hitokoto']['text']}」
—— {weather_data['hitokoto']['from']}
"""
        formatted_message = f"{formatted_message}\n{hitokoto_text}"
    
    # 如果启用彩虹屁且提供了彩虹屁文本
    if config.ENABLE_CAIHONGPI and caihongpi_text:
        formatted_message = f"{formatted_message}\n🌈 彩虹屁：\n{caihongpi_text}"
    
    logger.info("消息格式化完成")
    return formatted_message.strip()

def get_weather():
    """获取和风天气数据"""
    url = f"https://devapi.qweather.com/v7/weather/now?location={config.LOCATION}&key={config.HEFENG_KEY}"
    response = requests.get(url)
    weather_data = response.json()
    
    # 获取生活指数
    life_url = f"https://devapi.qweather.com/v7/indices/1d?type=3&location={config.LOCATION}&key={config.HEFENG_KEY}"
    life_response = requests.get(life_url)
    life_data = life_response.json()
    
    if weather_data['code'] == '200' and life_data['code'] == '200':
        weather = weather_data['now']
        life_info = life_data['daily'][0]
        
        # 获取当前时间
        current_hour = datetime.now().hour
        
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
        
        # 根据温度选择温馨提示
        temp = float(weather.get('temp', 0))
        tip = ""
        if temp <= 15:
            tip = random.choice(config.TIPS['cold'])
            logger.info("使用寒冷天气提示")
        elif temp >= 30:
            tip = random.choice(config.TIPS['hot'])
            logger.info("使用炎热天气提示")
        
        if weather.get('windDir', '').find('雨') != -1:
            tip = random.choice(config.TIPS['rain'])
            logger.info("使用雨天提示")
        
        if tip:
            tip = tip.format(name=config.USER_CONFIG['name'])
        
        # 准备消息数据
        message_data = {
            'temp': weather.get('temp', 'N/A'),
            'wind_dir': weather.get('windDir', 'N/A'),
            'wind_scale': weather.get('windScale', 'N/A'),
            'humidity': weather.get('humidity', 'N/A'),
            'feels_like': weather.get('feelsLike', 'N/A'),
            'clothes_tip': life_info.get('text', 'N/A'),
            'greeting': greeting,  # 添加问候语
            'warm_tip': tip       # 添加温馨提示
        }
        
        # 如果启用彩虹屁，添加到消息数据中
        if config.ENABLE_CAIHONGPI:
            message_data['caihongpi'] = get_caihongpi()
            
        # 获取一言
        hitokoto = get_hitokoto()
        if hitokoto:
            message_data['hitokoto'] = hitokoto
        
        return message_data
    return None

def push_message(weather_data, formatted_message):
    """推送消息到各个平台"""
    logger.info("开始推送消息")
    success_count = 0
    results = []
    
    # 微信公众号推送
    if config.PUSH_METHODS.get('wechat'):
        try:
            logger.info("尝试推送到微信公众号")
            MessagePusher.push_to_wechat(
                config.WX_APP_ID,
                config.WX_APP_SECRET,
                config.WX_USER_OPENID,
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
    
    # Telegram 多账号推送
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
            formatted_message = format_message(weather_data, weather_data, caihongpi_text)
            
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