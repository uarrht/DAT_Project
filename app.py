import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# 1. 網頁標題
st.title("DAT.co 指標追蹤器：MSTR 溢價分析")
st.write("本網站追蹤 MicroStrategy (MSTR) 的溢價 (Premium) 趨勢，並由 AI 自動生成市場情緒分析。")

# 2. 抓取與整理資料
mstr_data = yf.Ticker("MSTR").history(period="1y")
btc_data = yf.Ticker("BTC-USD").history(period="1y")

mstr_data.index = pd.to_datetime(mstr_data.index).tz_localize(None)
btc_data.index = pd.to_datetime(btc_data.index).tz_localize(None)

df = pd.DataFrame({
    "MSTR 股價 (USD)": mstr_data['Close'],
    "比特幣價格 (USD)": btc_data['Close']
}).dropna()

# 3. 指標計算與畫圖
df['溢價指標 (MSTR/BTC Ratio)'] = (df['MSTR 股價 (USD)'] / df['比特幣價格 (USD)']) * 1000

st.write("### 1. 絕對價格走勢比較")
st.line_chart(df[['MSTR 股價 (USD)', '比特幣價格 (USD)']])

st.write("### 2. DAT.co 核心指標：MSTR 溢價趨勢")
st.line_chart(df['溢價指標 (MSTR/BTC Ratio)'])

# 4. === Bonus: AI 智能總結 ===
st.write("### 3. 🤖 AI 智能數據總結 (Bonus)")

# 檢查有沒有設定金鑰
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 擷取最近 7 天的數據給 AI
    recent_7_days = df.tail(7)
    avg_premium = recent_7_days['溢價指標 (MSTR/BTC Ratio)'].mean()
    latest_premium = recent_7_days['溢價指標 (MSTR/BTC Ratio)'].iloc[-1]
    
    # 寫給 AI 的指令 (Prompt)
    prompt = f"""
    你是一位專業的加密貨幣與傳統金融分析師。
    我們正在分析比特幣儲備公司 MicroStrategy (MSTR) 的「溢價指標 (MSTR股價/比特幣價格 * 1000)」。
    該指標過去七天的平均值為：{avg_premium:.2f}
    而最新一天的數值為：{latest_premium:.2f}
    
    請用繁體中文寫一段約 80~100 字的簡短總結，分析：
    1. 最新指標高於還是低於七天平均？這代表市場對 MSTR 的情緒是轉趨狂熱還是降溫？
    2. 給投資人的一句簡短提醒。
    語氣要專業、客觀。
    """
    
    # 製作一個按鈕，按下去才讓 AI 寫報告
    if st.button("✨ 點擊生成今日 AI 數據總結"):
        with st.spinner("AI 正在分析最新數據..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                st.error("⚠️ AI 呼叫失敗，請確認 API Key 是否設定正確。")
else:
    st.warning("⚠️ 請先在 Streamlit 的 Secrets 中設定 GEMINI_API_KEY！")
