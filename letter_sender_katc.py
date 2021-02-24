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

def send_letter(title, content, password):
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
            send_letter(title + ' - ' + str(j+1), body[j].strip(), letter_password)
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
            send_letter(title + ' - ' + str(j+1), body[j].strip(), letter_password)
            time.sleep(0.5)
            turnoff_alert()
            time.sleep(0.5)
            init(enlistment_date,birth,name)

def get_naver_baseball_sk_content(oid, aid):
    r = requests.get('https://sports.news.naver.com/news.nhn?oid=' + oid +'&aid=' + aid)
    soup = BeautifulSoup(r.content, 'lxml')
    data = str(soup.find('div', id='newsEndContents'))
    body = data[:data.find('<p class="source">')]
    body = re.sub('<.+?>', '', body).strip()
    return body

def send_naver_baseball_sk():
    r = requests.get('https://sports.news.naver.com/kbaseball/news/list.nhn?isphoto=N&type=team&team=SK&view=text')
    data = r.json()
    for i in range(len(data['list'])):
        title = data['list'][i]['title'].strip()
        oid = data['list'][i]['oid']
        aid = data['list'][i]['aid']
        body = get_naver_baseball_sk_content(oid, aid)
        pages = math.ceil(len(body) / 800)
        body = [body[i:i+800] for i in range(0,len(body), 800)]
        for j in range(pages):
            send_letter(title + ' - ' + str(j+1), body[j].strip(), letter_password)
            time.sleep(0.5)
            turnoff_alert()
            time.sleep(0.5)
            init(enlistment_date,birth,name)

def send_epl_rank():
    r = requests.get('https://sports.news.naver.com/wfootball/index.nhn')
    soup = BeautifulSoup(r.content, 'html.parser')

    now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    team_list = soup.find('div', id='_team_rank_epl').findAll('tr')
    result = ''
    for i in range(1,len(team_list)):
        rank = team_list[i].find('span', class_='blind').contents[0]
        team = team_list[i].find('span', class_='name').contents[0]
        score = team_list[i].findAll('span')[7].contents[0]
        result += "{} {} {}".format(rank,team,score)+' ## '
    send_letter(now + ' EPL 순위', result, letter_password)
    time.sleep(0.5)
    turnoff_alert()
    time.sleep(0.5)
    init(enlistment_date,birth,name)

URL = 'https://www.katc.mil.kr/katc/community/children.jsp'

enlistment_date = ''
birth = ''
name = ''
letter_password = ''

driver = webdriver.Chrome(executable_path='chromedriver')
driver.get(url=URL)
init(enlistment_date,birth,name)
wait_auth()

send_jtbcnews()
send_boannews()
send_naver_baseball_sk()
send_epl_rank()