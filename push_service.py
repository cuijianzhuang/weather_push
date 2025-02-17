import requests
from datetime import datetime
import config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import logging
import pytz

logger = logging.getLogger(__name__)

class MessagePusher:
    @staticmethod
    def get_beijing_time():
        """获取北京时间"""
        beijing_tz = pytz.timezone('Asia/Shanghai')
        utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        beijing_now = utc_now.astimezone(beijing_tz)
        return beijing_now

    @staticmethod
    def push_to_wechat(app_id, app_secret, user_openid, message_data):
        """推送到微信公众号"""
        # 获取access_token
        token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
        response = requests.get(token_url)
        access_token = response.json()['access_token']
        
        # 发送消息
        push_url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
        
        # 获取问候语和温馨提示
        greeting = message_data.get('greeting', '')
        warm_tip = message_data.get('warm_tip', '')
        current_time = MessagePusher.get_beijing_time().strftime('%Y-%m-%d %H:%M')
        
        # 准备标题，优先使用问候语
        first_value = greeting if greeting else f"✨ 天气播报 ({current_time})"
        
        # 预处理温馨提示
        remark_value = "\n🤖 来自天气助手"
        if warm_tip:
            remark_value = f"\n💝 温馨提示：\n{warm_tip}"
        
        template_data = {
            "first": {
                "value": first_value,
                "color": "#1e90ff"
            },
            "temp": {
                "value": f"{message_data['temp']}°C",
                "color": "#ff6b6b"
            },
            "feels_like": {
                "value": f"{message_data['feels_like']}°C",
                "color": "#ff6b6b"
            },
            "wind_dir": {
                "value": message_data['wind_dir'],
                "color": "#44bd32"
            },
            "wind_scale": {
                "value": f"{message_data['wind_scale']}级",
                "color": "#44bd32"
            },
            "humidity": {
                "value": f"{message_data['humidity']}%",
                "color": "#00a8ff"
            },
            "clothes_tip": {
                "value": message_data['clothes_tip'],
                "color": "#ff7f50"
            },
            "remark": {
                "value": remark_value,
                "color": "#888888"
            }
        }
        
        # 如果有彩虹屁文本，添加到remark中
        if message_data.get('caihongpi'):
            caihongpi_text = message_data['caihongpi']
            template_data["remark"]["value"] = f"\n✨ 每日寄语：\n{caihongpi_text}\n\n🤖 来自天气助手"
            template_data["remark"]["color"] = "#ff69b4"
        
        # 准备请求数据
        post_data = {
            "touser": user_openid,
            "template_id": config.WX_TEMPLATE_ID,
            "data": template_data
        }
        
        # 发送请求
        response = requests.post(push_url, json=post_data)
        result = response.json()
        
        if result.get('errcode', 0) != 0:
            raise Exception(f"微信推送失败: {result.get('errmsg', '未知错误')}")

    @staticmethod
    def push_to_telegram(bot_token, chat_id, message):
        """推送到单个 Telegram 账号"""
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=data)
        result = response.json()
        
        if not result.get('ok'):
            raise Exception(f"Telegram API 错误: {result.get('description', '未知错误')}")

    @staticmethod
    def push_to_wecom(webhook_url, message_data):
        """推送到单个企业微信群组"""
        # 获取问候语和温馨提示
        greeting = message_data.get('greeting', '')
        warm_tip = message_data.get('warm_tip', '')
        current_time = MessagePusher.get_beijing_time().strftime('%Y-%m-%d %H:%M')
        
        # 预处理各部分内容
        title = greeting if greeting else f'# ☁️ 天气播报 ({current_time})'
        
        # 预处理温度信息
        temp_text = f"{message_data['temp']}°C"
        feels_like_text = f"{message_data['feels_like']}°C"
        wind_dir_text = message_data['wind_dir']
        wind_scale_text = f"{message_data['wind_scale']}级"
        humidity_text = f"{message_data['humidity']}%"
        
        # 组装天气实况部分
        weather_lines = [
            "## 🌡️ 天气实况",
            f"> 当前温度：<font color=\"warning\">{temp_text}</font>",
            f"> 体感温度：<font color=\"warning\">{feels_like_text}</font>",
            f"> 风向状况：<font color=\"info\">{wind_dir_text}</font>",
            f"> 风力等级：<font color=\"info\">{wind_scale_text}</font>",
            f"> 相对湿度：<font color=\"info\">{humidity_text}</font>"
        ]
        weather_info = '\n'.join(weather_lines)
        
        # 组装穿衣建议部分
        clothes_info = '\n'.join([
            "\n## 👔 穿衣建议",
            message_data['clothes_tip']
        ])
        
        # 组装温馨提示部分
        tip_info = f"\n## 💝 温馨提示\n{warm_tip}" if warm_tip else ""
        
        # 组合完整消息
        markdown_content = '\n\n'.join([title, weather_info, clothes_info, tip_info])
        
        # 准备请求数据
        post_data = {
            "msgtype": "markdown",
            "markdown": {
                "content": markdown_content
            }
        }
        
        # 发送请求
        response = requests.post(webhook_url, json=post_data)
        result = response.json()
        
        if result.get('errcode', 0) != 0:
            raise Exception(f"企业微信推送失败: {result.get('errmsg', '未知错误')}")

    @staticmethod
    def push_to_email(smtp_config, message_data, subject=None):
        """推送到邮件"""
        try:
            # 获取北京时间
            current_time = MessagePusher.get_beijing_time().strftime('%Y-%m-%d %H:%M')
            
            # 使用北京时间作为邮件主题
            if subject is None:
                subject = f"天气预报 - {current_time}"
            
            # 添加调试日志
            logger.info("开始处理邮件数据")
            logger.info(f"在一起天数信息: {message_data.get('together_days', '无')}")
            
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = smtp_config['sender']
            msg['To'] = ','.join(smtp_config['receivers'])
            msg['Subject'] = Header(subject, 'utf-8')

            # 处理问候语
            greeting = message_data.get('greeting', '')
            if greeting:
                greeting_html = ''.join([
                    '<div style="background: linear-gradient(135deg, #6B8DD6 0%, #4B6CB7 100%); ',
                    'padding: 30px; text-align: center; color: white; margin-bottom: 20px; ',
                    'border-radius: 15px; animation: fadeIn 0.5s ease-out;">',
                    f'<h1 style="margin: 0; font-size: 28px;">{greeting}</h1>',
                    '</div>'
                ])
            else:
                greeting_html = ''

            # 处理温馨提示
            warm_tip = message_data.get('warm_tip', '')
            if warm_tip:
                # 预处理温馨提示文本
                processed_tip = warm_tip.replace('💝 温馨提示：', '').replace('\n', '')
                warm_tip_html = ''.join([
                    '<div style="margin-bottom: 30px; animation: fadeIn 0.5s ease-out 0.3s;">',
                    '<h2 style="color: #333; font-size: 20px; margin-bottom: 15px;">',
                    '<span style="display: inline-block; margin-right: 8px;">💝</span>',
                    '温馨提示',
                    '</h2>',
                    '<div style="background: linear-gradient(135deg, #fff0f3 0%, #ffe6ea 100%); ',
                    'padding: 20px; border-radius: 10px; color: #ff6b6b; line-height: 1.6; ',
                    'box-shadow: 0 4px 15px rgba(255,107,107,0.1);">',
                    processed_tip,
                    '</div>',
                    '</div>'
                ])
            else:
                warm_tip_html = ''

            # 处理纪念日信息
            memorial_days = message_data.get('memorial_days', '')
            if memorial_days:
                # 预处理纪念日文本
                processed_memorial = memorial_days.replace('\n', '<br>')
                memorial_days_html = ''.join([
                    '<div class="memorial-days">',
                    '<h2 style="color: #333; font-size: 20px; margin: 0 0 15px;">',
                    '<span style="display: inline-block; margin-right: 8px;">🎯</span>',
                    '纪念日提醒',
                    '</h2>',
                    processed_memorial,
                    '</div>'
                ])
            else:
                memorial_days_html = ''

            # 处理在一起天数
            together_days = message_data.get('together_days', '')
            if together_days:
                logger.info("正在处理在一起天数HTML")
                # 预处理在一起天数文本
                processed_together = together_days.replace('\n', '<br>')
                together_days_html = ''.join([
                    '<div class="together-days">',
                    '<h2 style="color: #333; font-size: 20px; margin: 0 0 15px;">',
                    '<span style="display: inline-block; margin-right: 8px;">💑</span>',
                    '在一起',
                    '</h2>',
                    '<div style="font-size: 18px; line-height: 1.6;">',
                    processed_together,
                    '</div>',
                    '</div>'
                ])
                logger.info("在一起天数HTML生成完成")
            else:
                together_days_html = ''
                logger.info("未找到在一起天数信息")

            # 准备模板数据
            template_data = {
                'greeting': greeting_html,
                'time': current_time,
                'province': config.USER_CONFIG['province'],
                'city': config.USER_CONFIG['city'],
                'temp': message_data.get('temp', 'N/A'),
                'feels_like': message_data.get('feels_like', 'N/A'),
                'wind_dir': message_data.get('wind_dir', 'N/A'),
                'wind_scale': message_data.get('wind_scale', 'N/A'),
                'humidity': message_data.get('humidity', 'N/A'),
                'clothes_tip': message_data.get('clothes_tip', 'N/A'),
                'warm_tip_html': warm_tip_html,
                'memorial_days_html': memorial_days_html,
                'together_days_html': together_days_html,
                'hitokoto_text': message_data.get('hitokoto', {}).get('text', '今天也是美好的一天~'),
                'hitokoto_from': message_data.get('hitokoto', {}).get('from', '天气助手')
            }
            
            # 替换模板变量
            html_content = config.EMAIL_TEMPLATE
            for key, value in template_data.items():
                html_content = html_content.replace('{{' + key + '}}', str(value))
            
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            try:
                # 连接Gmail SMTP服务器
                smtp = smtplib.SMTP(smtp_config['smtp_host'], smtp_config['smtp_port'])
                smtp.starttls()  # 启用TLS加密
                smtp.login(smtp_config['sender'], smtp_config['password'])
                
                # 发送邮件
                smtp.sendmail(
                    smtp_config['sender'],
                    smtp_config['receivers'],
                    msg.as_string()
                )
                smtp.quit()
            except Exception as e:
                raise Exception(f"邮件发送失败: {str(e)}")

        except Exception as e:
            logger.error(f"邮件处理过程出错: {str(e)}", exc_info=True)
            raise 