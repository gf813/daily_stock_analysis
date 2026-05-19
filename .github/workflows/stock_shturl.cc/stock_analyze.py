import akshare as ak
import requests
from openai import OpenAI
import os

# 读取配置
stock_list = os.getenv("STOCK_LIST", "")
api_key = os.getenv("OPENROUTER_API_KEY", "")
webhook = os.getenv("WECHAT_WEBHOOK_URL", "")
base_url = "https://openrouter.ai/api/v1"
model_name = "deepseek/deepseek-chat-v1"

def get_stock_data(code):
    try:
        df = ak.stock_zh_a_daily(symbol=code, adjust="qfq")
        latest = df.iloc[-1]
        return {
            "代码": code,
            "现价": round(latest["close"],2),
            "涨幅": round((latest["close"]-latest["open"])/latest["open"]*100,2),
            "成交量": int(latest["volume"])
        }
    except:
        return {"代码":code,"数据":"获取失败"}

def ai_analysis(data_list):
    client = OpenAI(base_url=base_url, api_key=api_key)
    prompt = f"""
今日A股行情数据分析，结合MACD、KD、黄金分割支撑压力做短线研判，给出简明操作思路：
{data_list}
要求：大盘简评+个股点位+支撑压力+简短操作建议，通俗易懂
    """
    res = client.chat.completions.create(
        model=model_name,
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content

def send_wechat(msg):
    if not webhook:
        return
    requests.post(webhook, json={"msgtype":"text","text":{"content":msg}})

if __name__=="__main__":
    stocks = stock_list.split(",")
    all_data = []
    for s in stocks:
        all_data.append(get_stock_data(s.strip()))
    ai_text = ai_analysis(all_data)
    send_wechat(f"【每日股市自动分析】\n{ai_text}")
    print("分析推送完成")
