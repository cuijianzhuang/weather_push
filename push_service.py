import requests
from datetime import datetime
import config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

class MessagePusher:
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
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 准备标题，优先使用问候语
        first_value = greeting if greeting else f"✨ 天气播报 ({current_time})"
        
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
                "value": f"\n💝 温馨提示：\n{warm_tip}" if warm_tip else "\n🤖 来自天气助手",
                "color": "#888888"
            }
        }
        
        # 如果有彩虹屁文本，添加到remark中
        if message_data.get('caihongpi'):
            template_data["remark"]["value"] = f"\n✨ 每日寄语：\n{message_data['caihongpi']}\n\n🤖 来自天气助手"
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
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 准备 Markdown 格式的消息
        markdown_content = f"""
{greeting if greeting else f'# ☁️ 天气播报 ({current_time})'}

## 🌡️ 天气实况
> 当前温度：<font color=\"warning\">{message_data['temp']}°C</font>
> 体感温度：<font color=\"warning\">{message_data['feels_like']}°C</font>
> 风向状况：<font color=\"info\">{message_data['wind_dir']}</font>
> 风力等级：<font color=\"info\">{message_data['wind_scale']}级</font>
> 相对湿度：<font color=\"info\">{message_data['humidity']}%</font>

## 👔 穿衣建议
{message_data['clothes_tip']}

{f'## 💝 温馨提示\n{warm_tip}' if warm_tip else ''}
"""
        
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
    def push_to_email(smtp_config, message_data, subject="天气预报"):
        """推送到邮件"""
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = smtp_config['sender']
        msg['To'] = ','.join(smtp_config['receivers'])
        msg['Subject'] = Header(subject, 'utf-8')

        # 处理问候语
        greeting = message_data.get('greeting', '')
        if greeting:
            greeting_html = f'''
            <div style="background: linear-gradient(135deg, #6B8DD6 0%, #4B6CB7 100%); 
                        padding: 30px; 
                        text-align: center; 
                        color: white; 
                        margin-bottom: 20px; 
                        border-radius: 15px;
                        animation: fadeIn 0.5s ease-out;">
                <h1 style="margin: 0; font-size: 28px;">{greeting}</h1>
            </div>
            '''
        else:
            greeting_html = ''

        # 处理温馨提示
        warm_tip = message_data.get('warm_tip', '')
        if warm_tip:
            warm_tip_html = f'''
            <div style="margin-bottom: 30px; animation: fadeIn 0.5s ease-out 0.3s;">
                <h2 style="color: #333; font-size: 20px; margin-bottom: 15px;">
                    <span style="display: inline-block; margin-right: 8px;">💝</span>
                    温馨提示
                </h2>
                <div style="background: linear-gradient(135deg, #fff0f3 0%, #ffe6ea 100%);
                          padding: 20px;
                          border-radius: 10px;
                          color: #ff6b6b;
                          line-height: 1.6;
                          box-shadow: 0 4px 15px rgba(255,107,107,0.1);">
                    {warm_tip}
                </div>
            </div>
            '''
        else:
            warm_tip_html = ''

        # 处理纪念日信息
        memorial_days = message_data.get('memorial_days', '')
        if memorial_days:
            memorial_days_html = f'''
            <div class="memorial-days">
                <h2 style="color: #333; font-size: 20px; margin: 0 0 15px;">
                    <span style="display: inline-block; margin-right: 8px;">🎯</span>
                    纪念日提醒
                </h2>
                {memorial_days.replace('\n', '<br>')}
            </div>
            '''
        else:
            memorial_days_html = ''

        # 准备模板数据
        template_data = {
            'greeting': greeting_html,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'province': config.USER_CONFIG['province'],
            'city': config.USER_CONFIG['city'],
            'temp': message_data.get('temp', 'N/A'),
            'feels_like': message_data.get('feels_like', 'N/A'),
            'wind_dir': message_data.get('wind_dir', 'N/A'),
            'wind_scale': message_data.get('wind_scale', 'N/A'),
            'humidity': message_data.get('humidity', 'N/A'),
            'clothes_tip': message_data.get('clothes_tip', 'N/A'),
            'warm_tip': warm_tip_html,
            'memorial_days_html': memorial_days_html,
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