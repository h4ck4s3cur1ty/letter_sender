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
        pages = math.ceil(len(body) / 1500)
        body = [body[i:i+1500] for i in range(0,len(body), 1500)]
        for j in range(pages):
            send_letter(traineeMgrSeq, body[j].strip(), title + ' - ' + str(j+1))
            time.sleep(1)

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
    send_letter(traineeMgrSeq, result, now + ' EPL 순위')
    time.sleep(1)

session = login('', '')
trainUnitCd, trainUnitEduSeq = get_trainUnit()
traineeMgrSeq = get_traineeMgrSeq(trainUnitCd, trainUnitEduSeq)

send_jtbcnews()
send_boannews()
send_naver_baseball_sk()
send_epl_rank()