import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os
#from summarizer import summarize_news_article

st.set_page_config(page_title="Market Analysis", page_icon=":icon_emoji:")
# Define the directory where the OHLCV data is stored
data_dir = 'crypto_data/'

crypto_names = {
    'AAVE_ohlcv': 'Aave',
    'ADA_ohlcv': 'Cardano',
    'APT_ohlcv': 'Aptos',
    'ARB_ohlcv': 'Arbitrum',
    'AR_ohlcv': 'Arweave',
    'ATOM_ohlcv': 'Cosmos',
    'AVAX_ohlcv': 'Avalanche',
    'BCH_ohlcv': 'Bitcoin Cash',
    'BNB_ohlcv': 'Binance Coin',
    'BTC_ohlcv': 'Bitcoin',
    'CRO_ohlcv': 'Crypto.com Coin',
    'DAI_ohlcv': 'Dai',
    'DOGE_ohlcv': 'Dogecoin',
    'DOT_ohlcv': 'Polkadot',
    'ETC_ohlcv': 'Ethereum Classic',
    'ETH_ohlcv': 'Ethereum',
    'FDUSD_ohlcv': 'First Digital USD',
    'FET_ohlcv': 'Fetch.ai',
    'FIL_ohlcv': 'Filecoin',
    'HBAR_ohlcv': 'Hedera',
    'ICP_ohlcv': 'Internet Computer',
    'IMX_ohlcv': 'Immutable',
    'INJ_ohlcv': 'Injective',
    'KAS_ohlcv': 'Kaspa',
    'LINK_ohlcv': 'Chainlink',
    'LTC_ohlcv': 'Litecoin',
    'MATIC_ohlcv': 'Polygon',
    'MKR_ohlcv': 'Maker',
    'MNT_ohlcv': 'Mantle',
    'NEAR_ohlcv': 'NEAR Protocol',
    'OP_ohlcv': 'Optimism',
    'PEPE_ohlcv': 'Pepe',
    'RENDER_ohlcv': 'Render Token',
    'SHIB_ohlcv': 'Shiba Inu',
    'SOL_ohlcv': 'Solana',
    'STX_ohlcv': 'Stacks',
    'SUI_ohlcv': 'Sui',
    'TAO_ohlcv': 'Lamden',
    'TON_ohlcv': 'Toncoin',
    'TRX_ohlcv': 'TRON',
    'UNI_ohlcv': 'Uniswap',
    'USDC_ohlcv': 'USD Coin',
    'VET_ohlcv': 'VeChain',
    'WIF_ohlcv': 'WiFi Coin',
    'XLM_ohlcv': 'Stellar',
    'XMR_ohlcv': 'Monero',
    'XRP_ohlcv': 'Ripple'
}



# Get the list of available cryptocurrencies (assuming each file is named after the cryptocurrency)
cryptos = [f.split('.')[0] for f in os.listdir(data_dir) if f.endswith('_ohlcv.csv')]

print(cryptos)

# Streamlit UI for selecting cryptocurrency
st.title('Cryptocurrency OHLCV Data Viewer')
selected_crypto = st.selectbox('Select a Cryptocurrency', cryptos)

# Load the selected cryptocurrency's data
file_path = os.path.join(data_dir, f'{selected_crypto}.csv')
df = pd.read_csv(file_path)

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Create subplots: 2 rows, 1 column with shared x-axis
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

# Add OHLC trace to upper subplot
fig.add_trace(go.Candlestick(x=df['timestamp'],
                             open=df['open'],
                             high=df['high'],
                             low=df['low'],
                             close=df['close'],
                             name='OHLC'),
              row=1, col=1)

# Add volume trace to lower subplot
fig.add_trace(go.Bar(x=df['timestamp'],
                     y=df['volume'],
                     name='Volume',
                     marker_color='blue'),
              row=2, col=1)

# Update layout
fig.update_layout(
    title=f'{selected_crypto} OHLC and Volume Data',
    xaxis_title='Date',
    yaxis_title='Price',
    xaxis_rangeslider_visible=False
)

# Update y-axis labels
fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="Volume", row=2, col=1)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)

maxvolume = df['volume'].max()

maxvolume_date = df[df['volume'] == maxvolume]['timestamp'].values[0]

st.write(f"Maximum volume ({maxvolume:.2f}) occurred on {maxvolume_date}")

st.header('News around the Maximal Volume Date')

news_df=pd.read_csv("./cryptocurrency_newsapi.csv")

news_df['date'] = pd.to_datetime(news_df['date'])

news_df = news_df[(news_df['date'] >= maxvolume_date - pd.Timedelta(days=10)) & (news_df['date'] <= maxvolume_date + pd.Timedelta(days=10))]
news_df = news_df.sort_values(by='date', ascending=False)



st.subheader(f"Displaying {len(news_df)} news items")
for index, row in news_df.iterrows():
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button(f"📰 {row.get('title', 'Untitled')}", key=f"news_{index}"):
            with st.expander("Article Details", expanded=True):
                st.write(f"**Source:** {row.get('source', 'Unknown')}")
                st.write(f"**Published:** {row.get('date', 'Unknown')}")
                st.write(f"**Link:** {row.get('url', 'No link available')}")
                
                summary=summarize_news_article(row.get('body', ''))
                st.write(f"**Summary:** {summary}")
    
    with col2:
        image_url = row.get('image')
        if image_url and isinstance(image_url, str):
            st.image(image_url, use_column_width=True)
