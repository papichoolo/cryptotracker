import streamlit as st
import pandas as pd
from cryptosentiment import crypto_categorizer, get_sentiment
from summarizer import summarize_news_article
from combiner import combinedscraperfunc

def safe_lower(value):
    try:
        return str(value).lower()
    except:
        return ""

def main():
    st.set_page_config(page_title="Crypto News Analyzer", page_icon=":newspaper:", layout="wide")

    st.title("Crypto News Analyzer!")

    # Button in the sidebar to trigger the scraper function
    if st.sidebar.button("Fetch Latest News"):
        with st.spinner('Fetching latest news...'):
            combinedscraperfunc()  # Run the scraping function
            st.sidebar.success("News data updated!")

    # Read the CSV file directly
    news_data = pd.read_csv("cryptocurrency_newsapi.csv")

    st.sidebar.title("Filters")
    search_term = st.sidebar.text_input("Search news")
    
    for index, row in news_data.iterrows():
        title = safe_lower(row.get('title', ''))
        description = safe_lower(row.get('description', ''))
        
        if search_term.lower() in title or search_term.lower() in description:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📰 {row.get('title', 'Untitled')}", key=f"news_{index}"):
                    with st.expander("Article Details", expanded=True):
                        st.write(f"**Source:** {row.get('source', 'Unknown')}")
                        st.write(f"**Published:** {row.get('date', 'Unknown')}")
                        st.write(f"**Link:** {row.get('url', 'No description available')}")
                        
                        sentiment = str(row.get('sentiment', ''))
                        content = str(row.get('body', ''))
                        if len(content) > 20000:
                            content = content[:20000] + "..."
                        summarized_content = summarize_news_article(content)
                        categories = crypto_categorizer(content)
                        get_sentiment(summarized_content, sentiment, categories)
                        
                        st.write("**Cryptocurrencies mentioned:**")
                        for category in categories:
                            st.write("- " + category)
            
            with col2:
                image_url = row.get('image')
                if image_url and isinstance(image_url, str):
                    st.image(image_url, use_column_width=True)
            
            st.markdown("---")

if __name__ == "__main__":
    main()