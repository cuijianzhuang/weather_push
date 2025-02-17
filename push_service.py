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
    def push_to_email(email_config, weather_data, subject):
        """推送到邮件"""
        try:
            # 获取北京时间
            current_time = MessagePusher.get_beijing_time().strftime('%Y-%m-%d %H:%M')
            
            # 使用北京时间作为邮件主题
            if subject is None:
                subject = f"天气预报 - {current_time}"
            
            # 添加调试日志
            logger.info("开始处理邮件数据")
            logger.info(f"在一起天数信息: {weather_data.get('together_days', '无')}")
            
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = email_config['sender']
            msg['To'] = ','.join(email_config['receivers'])
            msg['Subject'] = Header(subject, 'utf-8')

            # 处理问候语
            greeting = weather_data.get('greeting', '')
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
            warm_tip = weather_data.get('warm_tip', '')
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
            memorial_days = weather_data.get('memorial_days', '')
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
            together_days = weather_data.get('together_days', '')
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

            # 处理空气质量数据
            air_quality_data = weather_data.get('air_quality', {})
            if air_quality_data:
                email_data = {
                    'air_quality_aqi': air_quality_data.get('aqi', 'N/A'),
                    'air_quality_category': air_quality_data.get('category', 'N/A'),
                    'air_quality_pm25': air_quality_data.get('pm2p5', 'N/A'),
                    'air_quality_pm10': air_quality_data.get('pm10', 'N/A'),
                    'air_quality_no2': air_quality_data.get('no2', 'N/A'),
                    'air_quality_so2': air_quality_data.get('so2', 'N/A'),
                    'air_quality_co': air_quality_data.get('co', 'N/A'),
                    'air_quality_o3': air_quality_data.get('o3', 'N/A')
                }
            else:
                email_data = {}

            # 处理生活指数数据
            life_indices_data = weather_data.get('life_indices', {})
            if life_indices_data:
                indices_html = []
                for index_type, index in life_indices_data.items():
                    indices_html.append(f"""
                        <div class="life-index-item">
                            <div class="title">{index['name']}</div>
                            <div class="category">{index['category']}</div>
                            <div class="text">{index['text']}</div>
                        </div>
                    """)
                email_data['life_indices_html'] = "\n".join(indices_html)
            else:
                email_data['life_indices_html'] = '<div class="life-index-item">暂无生活指数数据</div>'

            # 准备模板数据
            template_data = {
                'greeting': greeting_html,
                'time': current_time,
                'province': config.USER_CONFIG['province'],
                'city': config.USER_CONFIG['city'],
                'temp': weather_data.get('temp', 'N/A'),
                'feels_like': weather_data.get('feels_like', 'N/A'),
                'wind_dir': weather_data.get('wind_dir', 'N/A'),
                'wind_scale': weather_data.get('wind_scale', 'N/A'),
                'humidity': weather_data.get('humidity', 'N/A'),
                'clothes_tip': weather_data.get('clothes_tip', 'N/A'),
                'warm_tip_html': warm_tip_html,
                'memorial_days_html': memorial_days_html,
                'together_days_html': together_days_html,
                'hitokoto_text': weather_data.get('hitokoto', {}).get('text', '今天也是美好的一天~'),
                'hitokoto_from': weather_data.get('hitokoto', {}).get('from', '天气助手'),
                **email_data
            }
            
            # 替换模板变量
            html_content = config.EMAIL_TEMPLATE
            for key, value in template_data.items():
                html_content = html_content.replace('{{' + key + '}}', str(value))
            
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            try:
                # 连接Gmail SMTP服务器
                smtp = smtplib.SMTP(email_config['smtp_host'], email_config['smtp_port'])
                smtp.starttls()  # 启用TLS加密
                smtp.login(email_config['sender'], email_config['password'])
                
                # 发送邮件
                smtp.sendmail(
                    email_config['sender'],
                    email_config['receivers'],
                    msg.as_string()
                )
                smtp.quit()
            except Exception as e:
                raise Exception(f"邮件发送失败: {str(e)}")

        except Exception as e:
            logger.error(f"邮件处理过程出错: {str(e)}", exc_info=True)
            raise 

    @staticmethod
    def push_to_wxpusher(weather_data):
        """推送消息到WxPusher"""
        if not config.PUSH_METHODS.get('wxpusher'):
            return
        
        # 获取当前时间
        current_time = datetime.now().strftime('%H:%M')
        
        # 构建HTML格式的消息内容
        html_content = f"""
        <div style="padding: 15px; background: linear-gradient(to bottom right, #f6f8fc, #ffffff); border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 15px;">
                <h2 style="color: #1a73e8; margin: 0;">🌈 今日天气预报</h2>
                <p style="color: #5f6368; margin: 5px 0;">{config.USER_CONFIG['province']} {config.USER_CONFIG['city']} · {current_time}</p>
            </div>
            
            <div style="background: #ffffff; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <p style="font-size: 24px; margin: 0; color: #202124;">🌡️ {weather_data['temp']}°C</p>
                <p style="color: #5f6368; margin: 5px 0;">体感温度 {weather_data['feels_like']}°C</p>
                <p style="color: #5f6368; margin: 5px 0;">💨 {weather_data['wind_dir']} {weather_data['wind_scale']}级</p>
                <p style="color: #5f6368; margin: 5px 0;">💧 相对湿度 {weather_data['humidity']}%</p>
            </div>
        """
        
        # 添加空气质量信息（如果有）
        if weather_data.get('air_quality'):
            air = weather_data['air_quality']
            # 根据AQI值选择颜色
            aqi = int(air['aqi'])
            if aqi <= 50:
                aqi_color = "#4caf50"  # 优
            elif aqi <= 100:
                aqi_color = "#ffeb3b"  # 良
            elif aqi <= 150:
                aqi_color = "#ff9800"  # 轻度污染
            elif aqi <= 200:
                aqi_color = "#f44336"  # 中度污染
            elif aqi <= 300:
                aqi_color = "#9c27b0"  # 重度污染
            else:
                aqi_color = "#795548"  # 严重污染
            
            html_content += f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h3 style="color: #1a73e8; margin: 0 0 10px 0;">🌬️ 空气质量</h3>
                <p style="margin: 5px 0; color: {aqi_color};">
                    AQI: {air['aqi']} ({air['category']})
                </p>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                    <p style="margin: 5px 0; color: #5f6368;">PM2.5: {air['pm2p5']}μg/m³</p>
                    <p style="margin: 5px 0; color: #5f6368;">PM10: {air['pm10']}μg/m³</p>
                    <p style="margin: 5px 0; color: #5f6368;">NO₂: {air['no2']}μg/m³</p>
                    <p style="margin: 5px 0; color: #5f6368;">SO₂: {air['so2']}μg/m³</p>
                    <p style="margin: 5px 0; color: #5f6368;">CO: {air['co']}mg/m³</p>
                    <p style="margin: 5px 0; color: #5f6368;">O₃: {air['o3']}μg/m³</p>
                </div>
            </div>
            """
        
        # 添加生活指数信息（如果有）
        if weather_data.get('life_indices'):
            indices = weather_data['life_indices']
            html_content += """
            <div style="background: #e8f0fe; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h3 style="color: #1a73e8; margin: 0 0 10px 0;">📋 生活指数</h3>
                <div style="display: grid; gap: 10px;">
            """
            
            # 指数对应的emoji
            index_emojis = {
                '1': '🏃',  # 运动指数
                '2': '🚗',  # 洗车指数
                '3': '👔',  # 穿衣指数
                '5': '☀️',  # 紫外线指数
                '9': '🤒'   # 感冒指数
            }
            
            for index_type, index in indices.items():
                emoji = index_emojis.get(index_type, '📌')
                html_content += f"""
                    <div style="background: #ffffff; padding: 10px; border-radius: 8px;">
                        <p style="margin: 0; color: #1a73e8;">{emoji} {index['name']}</p>
                        <p style="margin: 5px 0; color: #202124;">{index['category']}</p>
                        <p style="margin: 0; color: #5f6368; font-size: 14px;">{index['text']}</p>
                    </div>
                """
            
            html_content += """
                </div>
            </div>
            """
        
        # 添加温馨提示（如果有）
        if weather_data.get('warm_tip'):
            html_content += f"""
            <div style="background: #fce8e6; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h3 style="color: #d93025; margin: 0 0 10px 0;">💝 温馨提示</h3>
                <p style="margin: 0; color: #d93025;">{weather_data['warm_tip']}</p>
            </div>
            """
        
        # 添加穿衣建议
        html_content += f"""
            <div style="background: #e8f0fe; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h3 style="color: #1a73e8; margin: 0 0 10px 0;">👔 穿衣建议</h3>
                <p style="margin: 0; color: #202124;">{weather_data['clothes_tip']}</p>
            </div>
        """
        
        # 添加逐小时预报（如果有）
        if weather_data.get('hourly_forecast'):
            html_content += """
            <div style="background: #ffffff; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h3 style="color: #1a73e8; margin: 0 0 10px 0;">⏰ 未来天气</h3>
                <div style="display: flex; overflow-x: auto; padding-bottom: 10px;">
            """
            
            for hour in weather_data['hourly_forecast'][:6]:  # 只显示未来6小时
                html_content += f"""
                    <div style="min-width: 80px; text-align: center; margin-right: 10px;">
                        <p style="margin: 0; color: #202124;">{hour['time']}</p>
                        <p style="margin: 5px 0; color: #1a73e8;">{hour['temp']}°C</p>
                        <p style="margin: 0; color: #5f6368;">{hour['text']}</p>
                        <p style="margin: 5px 0; color: #5f6368;">💧 {hour['pop']}%</p>
                    </div>
                """
            
            html_content += """
                </div>
            </div>
            """
        
        # 添加一言（如果有）
        if weather_data.get('hitokoto'):
            hitokoto = weather_data['hitokoto']
            html_content += f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h3 style="color: #1a73e8; margin: 0 0 10px 0;">📖 今日一言</h3>
                <p style="color: #202124; margin: 0; font-style: italic;">「{hitokoto['text']}」</p>
                <p style="color: #5f6368; margin: 5px 0; text-align: right;">—— {hitokoto['from']}</p>
            </div>
            """
        
        # 添加纪念日信息（如果有）
        if weather_data.get('memorial_days'):
            html_content += f"""
            <div style="background: #fef7e0; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h3 style="color: #f9a825; margin: 0 0 10px 0;">🎯 纪念日提醒</h3>
                <p style="color: #f9a825; margin: 0;">{weather_data['memorial_days'].replace('━━━ 纪念日提醒 ━━━\n', '').strip()}</p>
            </div>
            """
        
        # 添加在一起的天数（如果有）
        if weather_data.get('together_days'):
            html_content += f"""
            <div style="background: #fce4ec; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h3 style="color: #e91e63; margin: 0 0 10px 0;">💑 在一起</h3>
                <p style="color: #e91e63; margin: 0;">{weather_data['together_days'].strip()}</p>
            </div>
            """
        
        html_content += "</div>"  # 关闭最外层div
        
        # 准备请求数据
        data = {
            "appToken": config.WXPUSHER_CONFIG['app_token'],
            "content": html_content,
            "summary": f"今日天气：{weather_data['temp']}°C",  # 消息摘要
            "contentType": 2,  # 内容类型：1表示文字，2表示html
            "uids": [config.WXPUSHER_CONFIG['uid']],
            "url": "",  # 可选：点击消息时要跳转的URL
        }
        
        # 发送请求
        response = requests.post(config.WXPUSHER_CONFIG['api_url'], json=data)
        
        if response.status_code != 200:
            raise Exception(f"WxPusher推送失败：{response.text}")
        
        result = response.json()
        if result.get('code') != 1000:
            raise Exception(f"WxPusher推送失败：{result.get('msg')}") 