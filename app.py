import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 網頁標題與說明
st.title("DAT.co 指標追蹤器：MSTR 溢價分析")
st.write("本網站用於追蹤 MicroStrategy (MSTR) 的股價與比特幣價格之關聯，並計算其「溢價 (Premium)」趨勢。")

# 2. 抓取資料
st.subheader("正在載入過去一年的歷史資料...")
mstr_data = yf.Ticker("MSTR").history(period="1y")
btc_data = yf.Ticker("BTC-USD").history(period="1y")

# 【修復關鍵】：把時間軸統一（強制移除時區資訊），這樣兩邊的日期才能完美對齊！
mstr_data.index = pd.to_datetime(mstr_data.index).tz_localize(None)
btc_data.index = pd.to_datetime(btc_data.index).tz_localize(None)

# 3. 整理資料
df = pd.DataFrame({
    "MSTR 股價 (USD)": mstr_data['Close'],
    "比特幣價格 (USD)": btc_data['Close']
})
df = df.dropna() # 移除遇到假日沒有開盤的日子

# 檢查是否有抓到資料
if df.empty:
    st.error("糟糕！無法處理資料。這可能是因為 Yahoo Finance 暫時阻擋了雲端主機的請求。")
else:
    # 4. 核心指標計算
    df['溢價指標 (MSTR/BTC Ratio)'] = (df['MSTR 股價 (USD)'] / df['比特幣價格 (USD)']) * 1000

    # 5. 在網頁上畫圖
    st.write("### 1. 絕對價格走勢比較")
    st.line_chart(df[['MSTR 股價 (USD)', '比特幣價格 (USD)']])

    st.write("### 2. DAT.co 核心指標：MSTR 溢價趨勢 (Premium Trend)")
    st.write("💡 **指標意義**：當這條線上升，代表市場極度樂觀，投資人願意付更高的「溢價」買 MSTR 股票；當線條下降，則代表溢價縮水。")
    st.line_chart(df['溢價指標 (MSTR/BTC Ratio)'])

    st.success("資料分析與圖表繪製完成！")
