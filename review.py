#Import Packages
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
movie = input("What movie or tv shows do you want to watch? : ")

#Set the web browser
driver = webdriver.Chrome(executable_path=r"C:\KARTIK NEW\Projects\movie rating prediction\chromedriver.exe")

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
driver.find_element_by_partial_link_text('imdb').click()
# driver.find_element_by_class_name("g").click()
# driver.implicitly_wait(20)

# link = None
# while(link == None):
#     link = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "g"))
#     )
# print(link)

# link.click()


ans = driver.current_url
page = requests.get(ans)
print(ans)

