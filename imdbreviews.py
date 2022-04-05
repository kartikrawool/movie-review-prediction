#Import Packages
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
#from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#from textblob import TextBlob
import time
import joblib
import string
import numpy as np
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from tqdm import tqdm

porter=PorterStemmer()
def tokenizer(text):
        return text.split()
def tokenizer_porter(text):
    return [porter.stem(word) for word in text.split()]

tfidf_vectorizer = joblib.load('tfidf_jlib')
m_jlib = joblib.load('model_jlib')

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

movie = input("What movie or tv shows do you want to watch? : ")

#Set the web browser
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=r"C:\KARTIK NEW\Projects\movie rating prediction\chromedriver.exe", chrome_options=chrome_options)

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
driver.get_screenshot_as_file("screenshot1.png")
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

print(table_review.Review)

#Sentiment Analysis
sentiment = get_sentiment(review)

print(f"The movie title is {film_title}")
print("")
print(sentiment)
negative = (sentiment == 0).sum()
positive = (sentiment == 1).sum()
print("Positive Review: ", positive)
print("Negative Review: ", negative)

if positive > negative:
    print('WATCH IT!')
else:
    print("DON'T WATCH IT...")

#Vadersentiment
# analyser = SentimentIntensityAnalyzer()
# sentiment1 = []
# sentiment2 = []

# for rev in review:
#     score1 = analyser.polarity_scores(rev)
#     com_score = score1.get('compound')
#     if com_score  >= 0.05:
#         sentiment1.append('positive')
#     elif com_score > -0.05 and com_score < 0.05:
#         sentiment1.append('neutral')
#     elif com_score <= -0.05:
#         sentiment1.append('negative')

# table_review['Sentiment Vader'] = sentiment1

#TextBlob
# for rev in review:
#     score2 = TextBlob(rev).sentiment.polarity
#     if score2 >= 0:
#         sentiment2.append('positive')
#     else:
#         sentiment2.append('negative')
# print(f"The movie title is {film_title}")
# print("")
# print("According to vadersentiemnt, you should :")
# if sentiment1.count('positive') > sentiment1.count('negative'):
#     print('WATCH IT!')
# else:
#     print("DON'T WATCH IT...")
# print('Positive : ', sentiment1.count('positive'))
# print('Negative : ', sentiment1.count('negative'))
# print("")
# print("According to TextBlob, you should :")
# if sentiment2.count('positive') > sentiment2.count('negative'):
#     print('WATCH IT!')
# else:
#     print("DON'T WATCH IT...")
# print('Positive : ', sentiment2.count('positive'))
# print('Negative : ', sentiment2.count('negative'))

#Close the browser
driver.close()
