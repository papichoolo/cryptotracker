
import os
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

"""This one is using the groq libary directly"""
from dotenv import load_dotenv

load_dotenv()
import json
  
#GROQ_API_KEY = os.getenv("GROQ_API_KEY")
#from langchain_core.pydantic_v1 import BaseModel, Field
from typing_extensions import Annotated, TypedDict
from langchain.prompts import PromptTemplate
#from langchain.chains import LLMChain

from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()


import pandas as pd

cmcdf= pd.read_csv('coinmarketcap.csv')



top_cryptos = cmcdf['name'].tolist()





from langchain_groq import ChatGroq

def crypto_categorizer(text):
    seen=set()
    words=text.split()
    cryptos=[]
    for word in words:
        if word in top_cryptos and word not in seen:
            cryptos.append(word)
            seen.add(word)
    if(not cryptos):
        cryptos.append("GeneralNews")
    print(cryptos)
    return cryptos
    '''llm = ChatGroq(groq_api_key = GROQ_API_KEY,model="llama3-8b-8192")
    #chain = LLMChain(prompt=prompt, llm=llm)
    chain = prompt | llm | parser
    result = chain.invoke({"text":text,"top_cryptos":top_cryptos})
    return eval(result)'''

"""### Using langchain to make our thing

Prompt Template
"""

def get_sentiment(news_articles,sentiment,categories):




  # The filtered data is now in 'filtered_data_dict' as a dictionary
  

  

  filtered_df = cmcdf[cmcdf['name'].isin(categories)]
  """filtered_df = filtered_df.drop(filtered_df.index[0])

# Reset the index to maintain consistency if needed
  filtered_df = filtered_df.reset_index(drop=True)"""

  # Display the filtered DataFrame after dropping the first row
  print(filtered_df)

  biggest_gainer = filtered_df.loc[filtered_df['percent_change_7d'].idxmax()]
  biggest_loser = filtered_df.loc[filtered_df['percent_change_7d'].idxmin()]
  time_frames = ['90d', '60d', '30d', '7d', '24h', '1h']
  positions = [0,1,2,3,4,5]
  # Combine biggest gainer and loser in a new DataFrame
  gainers_losers_df = pd.DataFrame([biggest_gainer, biggest_loser])

    # Step 2: Create a subplot with two rows: one for percentage changes and one for prices
  fig = go.Figure()

  # Plot percentage changes for both gainer and loser
  for index, row in gainers_losers_df.iterrows():
      percent_changes = row[['percent_change_90d', 'percent_change_60d', 'percent_change_30d', 
                            'percent_change_7d', 'percent_change_24h', 'percent_change_1h']].values
      color = 'red' if row['percent_change_7d'] == biggest_loser['percent_change_7d'] else 'blue'
      fig.add_trace(go.Scatter(
          x=positions,
          y=percent_changes,
          mode='lines+markers',
          name=f"{row['name']} - {'Loser' if color == 'red' else 'Gainer'}",
          marker=dict(size=8),
          line=dict(color=color)
      ))

  # Customize layout for percentage changes plot
  fig.update_layout(
      title='Biggest Gainers and Losers: Percentage Growth',
      xaxis=dict(
          tickvals=positions,
          ticktext=time_frames,
          title='Time Frame (Most Recent to Oldest)'
      ),
      yaxis_title='Percent Change (%)',
      legend_title='Legend'
  )

  # Display the percentage growth plot in Streamlit
  st.plotly_chart(fig)
# Horizontal bar chart for prices with logarithmic scale
  fig_price = go.Figure()

  # Gainer (in blue)
  fig_price.add_trace(go.Bar(
      x=[biggest_gainer['price']],
      y=[biggest_gainer['name']],
      orientation='h',
      marker=dict(color='blue'),
      text=[f"{biggest_gainer['price']:.2f}"],
      textposition='outside'
  ))

  # Loser (in red)
  fig_price.add_trace(go.Bar(
      x=[biggest_loser['price']],
      y=[biggest_loser['name']],
      orientation='h',
      marker=dict(color='red'),
      text=[f"{biggest_loser['price']:.2f}"],
      textposition='outside'
  ))

  # Update layout with logarithmic x-axis
  fig_price.update_layout(
      title="Prices of Biggest Gainers and Losers",
      xaxis_title="Price (USD, Log Scale)",
      yaxis_title="Cryptos",
      xaxis_type="log",  # Logarithmic scale
      bargap=0.2
  )

  # Display the figure in Streamlit
  st.plotly_chart(fig_price)
  
  
  bruh=""
  if float(sentiment)>0.5:
    bruh="Positive"
  else:
    bruh="Negative"
  prompt = PromptTemplate(
    input_variables=["news_articles","sentiment","bruh","cryptos","cryptolist"],
    template="""  
You are Crypto Statistician and Market Analysis with extensive experience in providing real statistics on the crypto market. Given the following news article:
{news_articles}


Sentiment: {bruh}

Confidence: {sentiment}%

**Task:**

  

  
You are tasked with analyzing the impact of the news on the cryptocurrency market. You are required to provide an impact analysis based on the news article. Your analysis should include short-term, mid-term, and long-term predictions on the market, public opinion, market trends, and additional factors that could influence the market.

**Output:**

  

Please format the output in **Markdown** as follows:  

```markdown



#### Short Term


- Predictions: *In concise points, Details on how the news will affect specific cryptocurrencies or the general market in the short term and the trajectory of the numbers* Crypto List **DO NOT PRINT THIS BY ANY MEANS**: {cryptolist}
  

#### Mid Term

- Predictions: *In concise points, Details on how the news will affect specific cryptocurrencies and their trajectory or the general market in the mid term.*

  

#### Long Term

- Predictions: *In concise points, Details on how the news will affect specific cryptocurrencies or the general market in the long term.*

  

### Market Opinion Change

  

#### Public Opinion

- *In concise points, Explanation of how public opinion might shift based on the news.*

  

#### Market Trends

- *In concise points, Analysis of how market trends might change as a result of the news.*

  

### Additional Factors

  

- **Political Factors:** *Consideration of political elements that could impact the market.*

- **Economic Factors:** *Analysis of economic conditions influenced by the news.*

- **Social Factors:** *Social dynamics that might affect the cryptocurrency market based on the news.*

```

  

**Only provide the Markdown output. Do not include any additional information or text.**"""
)
  
 
  
  llm = ChatGroq(groq_api_key = st.secrets["groq_api_key"] , model="llama3-groq-70b-8192-tool-use-preview")
  chain = prompt | llm | parser 
  result = chain.invoke({"news_articles":news_articles,"sentiment":sentiment,"bruh":bruh,"cryptolist":filtered_df.to_markdown()}) 

  st.write(sentiment+ " " +bruh+ "\n"+ result)






  

