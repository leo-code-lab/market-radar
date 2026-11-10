import akshare as ak
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os

# ================= 邮箱配置区 =================
MAIL_SENDER = "1441417231@qq.com"
MAIL_RECEIVER = "1441417231@qq.com"
# ============================================

def send_email_report(content):
    auth_code = os.environ.get("MAIL_AUTH_CODE", "")
    
    if not auth_code:
        print("⚠️ 未检测到 MAIL_AUTH_CODE 环境变量，跳过邮件发送。")
        return

    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = MAIL_SENDER
    message['To'] = MAIL_RECEIVER
    message['Subject'] = Header(f"⛅ A股多日动量天气雷达与惯性预测报告 ({datetime.now().strftime('%Y-%m-%d')})", 'utf-8')

    try:
        smtp_server = "smtp.qq.com"
        port = 465
        
        server = smtplib.SMTP_SSL(smtp_server, port)
        server.login(MAIL_SENDER, auth_code)
        server.sendmail(MAIL_SENDER, [MAIL_RECEIVER], message.as_string())
        server.quit()
        print(f"✅ 邮件报告已成功发送至：{MAIL_RECEIVER}")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def advanced_momentum_weather_radar():
    report_lines = []
    
    def log(text=""):
        print(text)
        report_lines.append(text)

    log("=" * 85)
    log(f" ⛅ A股多日动量天气雷达与趋势惯性预测系统 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    log("=" * 85)
    
    try:
        # 1. 获取指数历史数据（用于计算最近5天的动量变化，避免单日噪声）
        df_hist = ak.stock_zh_index_daily(symbol="sh000001")
        if df_hist is not None and not df_hist.empty:
            df_recent = df_hist.tail(10).copy()
            df_recent['MA5'] = df_recent['close'].rolling(5).mean()
            df_recent['MA20'] = df_recent['close'].rolling(20).mean()
            
            latest = df_recent.iloc[-1]
            close_price, ma5, ma20 = latest['close'], latest['MA5'], latest['MA20']
            
            # 动量计算：最近5天指数的累计涨跌幅，判断中期气压变化趋势
            index_5d_chg = ((df_recent.iloc[-1]['close'] - df_recent.iloc[-5]['close']) / df_recent.iloc[-5]['close']) * 100
        else:
            close_price, ma5, ma20, index_5d_chg = 0, 0, 0, 0.0

        # 2. 短期数据：市场流动性、普涨率与情绪极值
        df_spot = ak.stock_zh_a_spot_em()
        if df_spot is not None
