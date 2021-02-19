from selenium.webdriver.support.ui import Select
from selenium import webdriver
from bs4 import BeautifulSoup
import feedparser
import requests
import math
import time
import re

def init(enlistment_date, birth, name):
    select = Select(driver.find_element_by_id('search_val1'))
    select.select_by_value(enlistment_date)

    sel_birth = driver.find_element_by_id("birthDay")
    sel_birth.send_keys(birth)
    input_name = driver.find_element_by_id("search_val3")
    input_name.send_keys(name)

    driver.find_element_by_xpath("//input[@type='submit']").click()
    press_search_btn = driver.find_element_by_id('childInfo1')
    press_search_btn.send_keys('\n')
    press_letter_btn = driver.find_element_by_id('letterBtn')
    press_letter_btn.send_keys('\n')

def wait_auth():
    press_auth_btn = driver.find_element_by_id('fn_submit')
    press_auth_btn.send_keys('\n')
    while True:
        if input('Wait for Phone Auth...If you ready, press Enter') == '':
            break
        else:
            print('no')

def write_letter(title, content, password):
    write_title = driver.find_element_by_id("article_title")
    write_title.send_keys(title)
    write_content = driver.find_element_by_id("article_text")
    write_content.send_keys(content)
    write_password = driver.find_element_by_id("writer_password")
    write_password.send_keys(password)

    driver.find_element_by_xpath("//input[@type='submit']").click()

def turnoff_alert():
    driver.switch_to_alert().accept()

def get_boannews_contents(URL):
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'lxml')
    data = str(soup.find('div', itemprop='articleBody').contents[1])
    body = re.sub('<.+?>', '', data).strip()
    return body

def send_boannews():
    news = feedparser.parse('http://www.boannews.com/media/news_rss.xml')
    for i in range(0,len(news.entries)):
        url = news.entries[i].link
        title = news.entries[i].title
        body = get_boannews_contents(url)
        if "@boannews.com" in body: body = body[:body.find('@boannews.com')]
        pages = math.ceil(len(body) / 800)
        body = [body[i:i+800] for i in range(0,len(body), 800)]
        for j in range(pages):
            write_letter(title + ' - ' + str(j), body[j].strip(), 'qwerasdf!!')
            time.sleep(0.5)
            turnoff_alert()
            time.sleep(0.5)
            init(enlistment_date,birth,name)

def get_jtbc_contents(URL):
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding='utf-8')
    data = str(soup.find('div', id='articlebody').contents[1])
    body = re.sub('<.+?>', '', data).strip()
    return body

def send_jtbcnews():
    news = feedparser.parse('http://fs.jtbc.joins.com/RSS/newsrank.xml')
    for i in range(0,len(news)):
        url = news.entries[i].link
        title = news.entries[i].title
        body = get_jtbc_contents(url)
        pages = math.ceil(len(body) / 800)
        body = [body[i:i+800] for i in range(0,len(body), 800)]
        for j in range(pages):
            write_letter(title + ' - ' + str(j), body[j].strip(), 'qwerasdf!!')
            time.sleep(0.5)
            turnoff_alert()
            time.sleep(0.5)
            init(enlistment_date,birth,name)

URL = 'https://www.katc.mil.kr/katc/community/children.jsp'
enlistment_date = ''
birth = ''
name = ''

driver = webdriver.Chrome(executable_path='chromedriver')
driver.get(url=URL)
init(enlistment_date,birth,name)
wait_auth()
send_jtbcnews()
send_boannews()