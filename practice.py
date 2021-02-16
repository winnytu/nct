import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time

try: 
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    chrome = webdriver.Chrome(options=options,executable_path='../chromedriver')
    chrome.set_page_load_timeout(10)
    chrome.get('https://mbasic.facebook.com/')
    chrome.set_page_load_timeout(10)
    email = chrome.find_element_by_id("m_login_email")
    email.send_keys('winny3531@hotmail.com')
    password = chrome.find_element_by_xpath('//*[@name="pass"]')
    password.send_keys('aa22013788')
    button = chrome.find_element_by_xpath('//*[@name="login"]')
    button.click()
    time.sleep(3)
    button2 = chrome.find_element_by_xpath('//*[@value="好"]')
    button2.click()
    time.sleep(3)
    spec_url = 'https://m.facebook.com/groups/676287645867357/'
    chrome.get(spec_url)
    time.sleep(5)
    soup = BeautifulSoup(chrome.page_source,'html5lib')
    text = soup.find("div", class_="_4gur _5t8z")
    title = text.find("div",class_="_4gus").text
    content = text.find("span",class_="_li")
    for span in content.children:
        print(span.text)

    print(title)

finally:
    print('fail')
    chrome.quit()