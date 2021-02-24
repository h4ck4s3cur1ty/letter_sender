from bs4 import BeautifulSoup
import feedparser
import requests
import math
import time
import re

QUOTED_STRING_RE = re.compile(r"(?P<quote>['\"])(?P<string>.*?)(?<!\\)(?P=quote)")

def login(userId, userPwd):
    session = requests.session()
    data = {'state':'email-login','autoLoginYn':'N','userId':userId,'userPwd':userPwd}
    session.post('https://www.thecamp.or.kr/login/loginA.do',data=data)
    return session

def get_trainUnit():
    r = session.get('https://www.thecamp.or.kr/eduUnitCafe/viewEduUnitCafeMain.do')
    soup = BeautifulSoup(r.text, 'html.parser')
    fn_consolLetter = soup.findAll('a', class_='btn-green')[0].get('href')
    trainUnitCd = QUOTED_STRING_RE.findall(fn_consolLetter)[1][1]
    trainUnitEduSeq = QUOTED_STRING_RE.findall(fn_consolLetter)[0][1]
    return trainUnitCd, trainUnitEduSeq

def get_traineeMgrSeq(trainUnitCd, trainUnitEduSeq):
    data = {'divType':'1','trainUnitCd':trainUnitCd,'trainUnitEduSeq':trainUnitEduSeq,'enterPageType':'main'}
    r = session.post("https://www.thecamp.or.kr/consolLetter/viewConsolLetterMain.do", data=data)
    soup = BeautifulSoup(r.text, "html.parser")
    fn_selectList = soup.find('a', class_='letter-card-box on').get('href')
    traineeMgrSeq = QUOTED_STRING_RE.findall(fn_selectList)[0][1]
    return traineeMgrSeq

def send_letter(traineeMgrSeq, content, title):
    data = {'traineeMgrSeq':traineeMgrSeq, 'boardDiv':'sympathyLetter', 'sympathyLetterContent':content,'sympathyLetterSubject':title}
    r = session.post("https://www.thecamp.or.kr/consolLetter/insertConsolLetterA.do",data=data)
    print('오류발생') if r.json()['resultCd'] != '0000' else print('정상처리, 제목 : ' + title)


def get_boannews_contents(URL):
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'lxml')
    data = str(soup.find('div', itemprop='articleBody').contents[1])
    body = re.sub('<.+?>', '', data).strip()
    return body

def send_boannews(traineeMgrSeq):
    news = feedparser.parse('http://www.boannews.com/media/news_rss.xml')
    for i in range(0,len(news.entries)):
        url = news.entries[i].link
        title = news.entries[i].title
        body = get_boannews_contents(url)
        if "@boannews.com" in body: body = body[:body.find('@boannews.com')]
        pages = math.ceil(len(body) / 1500)
        body = [body[i:i+1500] for i in range(0,len(body), 1500)]
        for j in range(pages):
            send_letter(traineeMgrSeq, body[j].strip(), title + ' - ' + str(j+1))
            time.sleep(1)

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
        pages = math.ceil(len(body) / 1500)
        body = [body[i:i+1500] for i in range(0,len(body), 1500)]
        for j in range(pages):
            send_letter(traineeMgrSeq, body[j].strip(), title + ' - ' + str(j+1))
            time.sleep(1)

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
        print(body)
        pages = math.ceil(len(body) / 1500)
        body = [body[i:i+1500] for i in range(0,len(body), 1500)]
        for j in range(pages):
            send_letter(traineeMgrSeq, body[j].strip(), title + ' - ' + str(j+1))
            time.sleep(1)

session = login('', '')
trainUnitCd, trainUnitEduSeq = get_trainUnit()
traineeMgrSeq = get_traineeMgrSeq(trainUnitCd, trainUnitEduSeq)

send_jtbcnews()
send_boannews()
send_naver_baseball_sk()