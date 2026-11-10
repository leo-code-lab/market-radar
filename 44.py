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

        # ================= 多日动量与天气惯性逻辑 =================
        log("\n" + "─" * 35 + " 【一、今日盘面基本信息清单】 " + "─" * 35)
        log(f"  • 两市总成交额 : {total_turnover:.2f} 亿元")
        log(f"  • 市场普涨率   : {up_ratio:.1f}%  (上涨: {up_count}家 vs 下跌: {down_count}家 | 平均涨幅: {avg_change:+.2f}%)")
        log(f"  • 情绪极端频次 : 涨停 {limit_up} 家 vs 跌停 {limit_down} 家 | 大涨>5%: {heavy_up}家 vs 大跌<-5%: {heavy_down}家")
        log(f"  • 气压与均线   : 上证指数 {close_price:.2f} | 5日均线: {ma5:.2f} | 20日均线: {ma20:.2f}")
        log(f"  • 近5日气压动量: 指数5日累计涨跌幅 {index_5d_chg:+.2f}%（观察多日趋势动量，过滤单日噪声）")
        log(f"  • 风格与护盘手 : 沪深300单日变动 {hs300_chg:+.2f}% | 沪深300ETF(510300)成交额: {etf_turnover:.2f}亿")

        log("\n" + "─" * 35 + " 【二、多维气象交叉诊断】 " + "─" * 35)
        
        # 综合单日极值与多日动量进行天气定性
        if total_turnover >= 10000 and up_ratio < 45:
            weather_type = "⚡【局部雷暴台风（高位结构抽血）】"
            weather_desc = "虽然成交额超万亿，但普涨率低于45%，且伴随较多大跌个股。资金在局部抱团，多数中小散户遭遇抽血阴雨。"
            inertia_forecast = f"【天气惯性与趋势预测】：结合近5日动量（{index_5d_chg:+.2f}%）来看，市场并非偶然一天撕裂。热钱高位对倒和均线压制已经形成了一定的‘风向惯性’。在普涨率没有连续修复到60%以上之前，这种局部暴雨、大面积阴冷的惯性将大概率延续，不宜盲目在大雨中远行。"
            strategy = "🛡️【实战风控建议】：顺应防守惯性，严控仓位，拒绝盲目追高，等待气压彻底企稳。"
            
        elif total_turnover >= 9000 and up_ratio >= 60 and index_5d_chg > -1.0:
            weather_type = "☀️【晴空万里顺风（多头趋势共振）】"
            weather_desc = "成交额稳健、普涨率超60%，且多日动量保持向上发散，市场暖意融融，赚钱效应良好。"
            inertia_forecast = f"【天气惯性与趋势预测】：近5日动量表现强劲（{index_5d_chg:+.2f}%），多头趋势一旦在时间序列上形成合力，会自带强大的‘顺风上扬惯性’。后续几天大概率延续晴好天气，动能充沛。"
            strategy = "🚀【实战进攻建议】：顺应多头惯性，保持进攻仓位，积极参与主流热点。"
            
        else:
            weather_type = "🌥️【多云阴冷震荡（存量拉锯周期）】"
            weather_desc = "多空双方在关键均线附近反复拉锯，单日数据与多日动量均未形成单边突破的合力。"
            inertia_forecast = f"【天气惯性与趋势预测】：近5日动量温和（{index_5d_chg:+.2f}%），天空云层较厚。市场将惯性维持横盘震荡，缺乏单边方向，变盘窗口仍在酝酿中。"
            strategy = "⚖️【实战操作建议】：采取高抛低吸的震荡策略，切勿盲目押注单边，耐心等待风向明朗。"

        log(f"  • 当前气象定性 : {weather_type}")
        log(f"  • 天气成因剖析 : {weather_desc}")
        
        log("\n" + "─" * 35 + " 【三、趋势惯性与未来走势预测】 " + "─" * 35)
        log(f"  {inertia_forecast}")
        log(f"  {strategy}")
        log("=" * 85)

        # 触发邮件发送
        full_report_text = "\n".join(report_lines)
        send_email_report(full_report_text)

    except Exception as e:
        err_msg = f"❌ 多日动量雷达系统运行出错: {e}"
        print(err_msg)
        send_email_report(err_msg)

if __name__ == "__main__":
    advanced_momentum_weather_radar()
