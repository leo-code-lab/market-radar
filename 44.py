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
    message['Subject'] = Header(f"⛅ A股气象雷达与天气预测报告 ({datetime.now().strftime('%Y-%m-%d')})", 'utf-8')

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

def weather_market_radar():
    report_lines = []
    
    def log(text=""):
        print(text)
        report_lines.append(text)

    log("=" * 85)
    log(f" ⛅ A股气象级量化雷达与盘面天气预测系统 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    log("=" * 85)
    
    try:
        # 1. 中期数据：价格趋势与均线支撑/压制
        df_hist = ak.stock_zh_index_daily(symbol="sh000001")
        if df_hist is not None and not df_hist.empty:
            df_recent = df_hist.tail(20).copy()
            df_recent['MA5'] = df_recent['close'].rolling(5).mean()
            df_recent['MA20'] = df_recent['close'].rolling(20).mean()
            latest = df_recent.iloc[-1]
            close_price, ma5, ma20 = latest['close'], latest['MA5'], latest['MA20']
        else:
            close_price, ma5, ma20 = 0, 0, 0

        # 2. 短期数据：市场流动性、普涨率与情绪极值
        df_spot = ak.stock_zh_a_spot_em()
        if df_spot is not None and not df_spot.empty:
            total_stocks = len(df_spot)
            total_turnover = df_spot['成交额'].sum() / 1e8  # 亿元
            up_count = len(df_spot[df_spot['涨跌幅'] > 0])
            down_count = len(df_spot[df_spot['涨跌幅'] < 0])
            up_ratio = (up_count / total_stocks) * 100
            avg_change = df_spot['涨跌幅'].mean()
            limit_up = len(df_spot[df_spot['涨跌幅'] >= 9.9])
            limit_down = len(df_spot[df_spot['涨跌幅'] <= -9.9])
            heavy_up = len(df_spot[df_spot['涨跌幅'] >= 5.0])
            heavy_down = len(df_spot[df_spot['涨跌幅'] <= -5.0])
        else:
            total_turnover, up_ratio, avg_change, limit_up, limit_down, heavy_up, heavy_down = 0, 0, 0, 0, 0, 0, 0

        # 3. 进阶维度：风格与宽基ETF
        try:
            df_hs300 = ak.stock_zh_index_daily(symbol="sz399300")
            hs300_chg = ((df_hs300.iloc[-1]['close'] - df_hs300.iloc[-2]['close']) / df_hs300.iloc[-2]['close']) * 100
        except:
            hs300_chg = 0.0

        etf_turnover = 0.0
        try:
            df_etf = ak.fund_etf_spot_em()
            etf_row = df_etf[df_etf['代码'] == '510300']
            if not etf_row.empty:
                etf_turnover = float(etf_row.iloc[0]['成交额']) / 1e8
        except:
            pass

        # ================= 气象化逻辑与报告排版 =================
        log("\n" + "─" * 35 + " 【一、今日盘面基本信息清单】 " + "─" * 35)
        log(f"  • 两市总成交额 : {total_turnover:.2f} 亿元 {'(放量活跃)' if total_turnover > 10000 else '(常规/缩量)'}")
        log(f"  • 市场普涨率   : {up_ratio:.1f}%  (上涨: {up_count}家 vs 下跌: {down_count}家 | 平均涨幅: {avg_change:+.2f}%)")
        log(f"  • 情绪极端频次 : 涨停 {limit_up} 家 vs 跌停 {limit_down} 家 | 大涨>5%: {heavy_up}家 vs 大跌<-5%: {heavy_down}家")
        log(f"  • 中期气压点位 : 上证指数 {close_price:.2f} | 5日均线: {ma5:.2f} | 20日均线: {ma20:.2f}")
        log(f"  • 风格与护盘手 : 沪深300单日变动 {hs300_chg:+.2f}% | 沪深300ETF(510300)成交额: {etf_turnover:.2f}亿")

        log("\n" + "─" * 35 + " 【二、盘面天气与气象状态解析】 " + "─" * 35)
        
        # 依据数据判定天气模型
        if total_turnover >= 10000 and up_ratio < 45:
            weather_type = "⚡【局部暴雨交加（雷暴台风天）】"
            weather_desc = "虽然成交额突破万亿（热能量极高），但普涨率低于 45%（大部分地区在大雨失血）。这属于典型的‘局部狂风暴雨、多数个股阴冷’的结构性撕裂天气。"
            inertia_forecast = "【天气惯性预测】：根据热钱高位对倒和均线压制的惯性，短期内这种‘少数大树遮阴、多数小草挨冻’的抽血暴雨天还将惯性维持。贸然在大雨中出行（追高）容易受凉感冒，需防范雷击。"
            strategy = "🛡️【出行气象建议】：高位躲进避风港（减仓防守），切忌盲目在狂风暴雨中追高。等待气压平衡。"
            
        elif total_turnover >= 9000 and up_ratio >= 60:
            weather_type = "☀️【晴空万里顺风天（艳阳高照）】"
            weather_desc = "成交额稳健、普涨率超 60%，且多头均线向上发散。场内阳光充足，百花齐放，赚钱效应极佳。"
            inertia_forecast = "【天气惯性预测】：多头趋势一旦形成，短期内会带有强大的‘顺风惯性’，热气上升，后续几天大概率延续晴好天气，做多动能充沛。"
            strategy = "🚀【出行气象建议】：大好晴天，适合顺风扬帆，积极保持进攻仓位，尽情享受阳光。"
            
        else:
            weather_type = "🌥️【多云阴冷震荡天（存量胶着）】"
            weather_desc = "多空双方势均力敌，没有形成绝对放量或单边普涨，天空云层较厚，缺乏单边方向。"
            inertia_forecast = "【天气惯性预测】：多云天气下，气温上下浮动有限，市场将惯性维持横盘震荡摩擦，变盘窗口还在酝酿。"
            strategy = "⚖️【出行气象建议】：气温不冷不热，适合轻仓高抛低吸，带好雨伞防备突发阵雨，耐心等待晴雨表给出明确信号。"

        log(f"  • 当前气象定性 : {weather_type}")
        log(f"  • 天气成因剖析 : {weather_desc}")
        
        log("\n" + "─" * 35 + " 【三、天气惯性与未来趋势预测】 " + "─" * 35)
        log(f"  {inertia_forecast}")
        log(f"  {strategy}")
        log("=" * 85)

        # 触发邮件发送
        full_report_text = "\n".join(report_lines)
        send_email_report(full_report_text)

    except Exception as e:
        err_msg = f"❌ 气象雷达系统运行出错: {e}"
        print(err_msg)
        send_email_report(err_msg)

if __name__ == "__main__":
    weather_market_radar()
