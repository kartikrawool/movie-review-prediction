import streamlit as st
#Import Packages
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import joblib
import string
import numpy as np
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from tqdm import tqdm
from selenium import webdriver
import os


porter=PorterStemmer()
def tokenizer(text):
        return text.split()
def tokenizer_porter(text):
    return [porter.stem(word) for word in text.split()]

tfidf_vectorizer = joblib.load('tfidf_jlib')
m_jlib = joblib.load('model_jlib')

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage") # for heroku comment for local
chrome_options.add_argument("--no-sandbox") # for heroku comment for local
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN") # for heroku comment for local
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options) # for heroku comment for local
# for local
#driver = webdriver.Chrome(executable_path=r"C:\KARTIK NEW\Projects\movie rating prediction\chromedriver.exe", chrome_options=chrome_options)

def preprocessor(text):
    text = text.lower()
    text = ''.join([i for i in text if i in string.ascii_lowercase+' '])
    text = ' '.join([PorterStemmer().stem(word) for word in text.split()])
    text = ' '.join([word for word in text.split() if word not in stopwords.words('english')])
    return text

def vectorize(review):
#   arr = []
#   arr.append(review)
#   arr = np.array(arr)
  text_vectorized=tfidf_vectorizer.transform(review)
  return text_vectorized

def get_sentiment(review):
    # for i in tqdm(range(review.shape[0])):
    #     review.loc[i,'Review'] = preprocessor(review['Review'][i])
    for i in tqdm(range(len(review))):
        review[i] = preprocessor(review[i])

    vectorized_review = vectorize(review)    
    sentiment = m_jlib.predict(vectorized_review)
    return sentiment

def predict(movie):
    st.text("Fetching reviews from  imdb.....")
    #Go to Google
    driver.get("https://www.google.com/")

    #Enter the keyword
    driver.find_element_by_name("q").send_keys(movie + " imdb")
    time.sleep(1)

    #Click the google search button
    driver.find_element_by_name("btnK").send_keys(Keys.ENTER)
    time.sleep(1)

    #Click the link
    driver.implicitly_wait(20)
    # driver.find_element_by_class_name("g").click()
    driver.find_element_by_partial_link_text('imdb').click()
    driver.implicitly_wait(20)


    #Click the user reviews

    driver.find_element_by_xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[2]/div/div[2]/ul/li[2]/a").click()
    driver.implicitly_wait(20)

    #Scrap IMBD review
    ans = driver.current_url
    page = requests.get(ans)
    soup = BeautifulSoup(page.content, "html.parser")
    all = soup.find(id="main")

    #Get the title of the movie
    all = soup.find(id="main")
    parent = all.find(class_ ="parent")
    name = parent.find(itemprop = "name")
    url = name.find(itemprop = 'url')
    film_title = url.get_text()

    #Get the title of the review
    title_rev = all.select(".title")
    title = [t.get_text().replace("\n", "") for t in title_rev]

    #Get the review
    review_rev = all.select(".content .text")
    review = [r.get_text() for r in review_rev]

    #Make it into dataframe
    table_review = pd.DataFrame({
        "Title" : title,
        "Review" : review
    })
    st.text("Predicting sentiments of reviews.....")
    #Sentiment Analysis
    sentiment = get_sentiment(review)

    df2 = pd.DataFrame(sentiment, columns = ['Sentiment'])
    table_review['Sentiment'] = df2['Sentiment']

    st.text(f"The movie title is {film_title}")
    
    #print(sentiment)
    negative = (sentiment == 0).sum()
    positive = (sentiment == 1).sum()
    st.text(f"Positive Review: {positive}")
    st.text(f"Negative Review: {negative}")

    if positive > negative:
        st.success('WATCH IT!')
        st.balloons()
    else:
        st.error("DON'T WATCH IT...")
    st.write(table_review)
    #driver.close()

def run():
    st.title("Predicting Movie Review Sentiment")
    st.subheader('This app is created to help you decide watch a movie.')
    movie = st.text_input('Enter movie or tv show you want to watch')
    if st.button("Predict"):
        predict(movie)
if __name__ == "__main__":
    run()