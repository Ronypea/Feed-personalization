import nltk
import pickle
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
import requests
from bs4 import BeautifulSoup
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bottle import route, run, template, request
from bottle import redirect
import math
from math import log


Base = declarative_base()

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key = True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)

class Words(Base):
    __tablename__ = "words"
    word = Column(String, primary_key = True)
    never_word = Column(Integer)
    maybe_word = Column(Integer)
    good_word = Column(Integer)


def get_news(network_page):
    news_page = BeautifulSoup(network_page.text, 'html5lib')
    news = []
    for info in zip(news_page.table.find_all('tr', class_='athing'),news_page.table.find_all('td', class_='subtext')):
        title = info[0].find('a', class_="storylink").text
        try:
            url = info[0].find('span', class_="sitestr").text
        except:
            url = 'None'
        try:
            author = info[1].find('a', class_="hnuser").text
            points = (info[1].find('span', class_="score").text)
            comments = (info[1].find_all('a')[-1].text)[:-9]
        except:
            author = 'None'
            points = '0'
            comments = '0'
        part = dict(author=author, comments=comments, points=points, title=title, url=url)
        news.append(part)
    return news


page = requests.get('https://news.ycombinator.com/')
news_list = get_news(page)

engine = create_engine("sqlite:///news.db")
Base.metadata.create_all(bind=engine)
session = sessionmaker(bind=engine)
s = session()

def add_words(new_word, label):
    never_word, maybe_word, good_word = 0, 0, 0
    if label == 'never':
        never_word = 1
    elif label == 'maybe':
        maybe_word = 1
    else:
        good_word = 1
    word = s.query(Words).filter_by(word=new_word).first()
    if type(word) == type(None):
        record = Words(word=new_word,
                       never_word=never_word,
                       maybe_word=maybe_word,
                       good_word=good_word)
        s.add(record)
    else:
        word.never_word += never_word
        word.maybe_word += maybe_word
        word.good_word += good_word
    s.commit()
    return

stop = set(stopwords.words('english'))
st = LancasterStemmer()

'''
all_news = s.query(News).filter(News.label != None).all()
for news in all_news:
    label = news.label
    title = news.title
    for symbol in '.;:-?!()':
        title = title.replace(symbol, ' ')
    title_split = title.split()
    for word in title_split:
        if word in stop:
            pass
        else:
            word = st.stem(word)
            word = word.strip().lower()
            add_words(word, label) '''


def add_news(news):
    for one_news in news:
        news = News(title=one_news['title'],
                    author=one_news['author'],
                    url=one_news['url'],
                    comments=one_news['comments'],
                    points=one_news['points'])
        s.add(news)
        s.commit()
    return

def next_page(network_page):
    page = BeautifulSoup(network_page.text, 'html5lib')
    morelink = page.find('a', attrs={'class':'morelink'})
    link = morelink['href']
    result = requests.get('{dom}/{url}'.format(dom = "https://news.ycombinator.com", url = link))
    return result

def counted():
    count_words_in_lab = [0, 0, 0]
    words = s.query(Words).all()
    for word in words:
        count_words_in_lab[0] += int(word.never_word)
        count_words_in_lab[1] += int(word.maybe_word)
        count_words_in_lab[2] += int(word.good_word)

    news = s.query(News).filter(News.label != None). all()
    labels_prob = [0,0,0]
    for one_news in news:
        if one_news.label == 'never':
            labels_prob[0] += 1
        elif one_news.label == 'maybe':
            labels_prob[1] += 1
        else:
            labels_prob[2] += 1
    labels_prob[0] = labels_prob[0]/len(news)
    labels_prob[1] = labels_prob[1]/len(news)
    labels_prob[2] = labels_prob[2]/len(news)
    return count_words_in_lab, labels_prob


def get_label(words, count_words_in_lab, labels_prob):
    result = [0, 0, 0]
    for one_word in words:
        if one_word in stop:
            pass
        else:
            one_word = st.stem(one_word)
            record = s.query(Words).filter(Words.word == one_word).first()
            if type(record) != type(None):
                try:
                    result[0] += log(int(record.never_word) / count_words_in_lab[0])
                except:
                    pass
                try:
                    result[1] += log(int(record.maybe_word) / count_words_in_lab[1])
                except:
                    pass
                try:
                    result[2] += log(int(record.good_word) / count_words_in_lab[2])
                except:
                    pass
                result[0] += log(labels_prob[0])
                result[1] += log(labels_prob[1])
                result[2] += log(labels_prob[2])
    if result[1] == max(result):
        return 'maybe'
    if result[0] == max(result):
        return 'never'
    if result[2] == max(result):
        return 'good'


@route('/')
@route('/news')
def news_list():
    count_words_in_lab, labels_prob = counted()
    news = s.query(News).filter(News.label == None).all()
    rows = []
    for one_news in news:
        title = one_news.title
        for symbol in '.;:-?!()':
            title = title.replace(symbol, ' ')
        title = title.split()
        label = get_label(title, count_words_in_lab, labels_prob)
        if label == 'never':
            color = '#999999'
        elif label == 'maybe':
            color = '#033cccc'
        else:
            color = '#ffffcc'
        rows.append((label, color, one_news))
    rows.sort(key=lambda i: i[0])

    return template('recommended_template', rows=rows)
'''
@route('/')
@route('/news')
def news_list():
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)
'''
'''
@route('/add_label/', method='GET')
def add_label():
    label = request.GET.get('label').strip()     # 1. Получить значения параметров label и id из GET-запроса
    idd = request.GET.get('id').strip()
    s = session()
    record = s.query(News).filter(News.id == idd)     # 2. Получить запись из БД с соответствующим id (такая запись только одна!)
    rec = record[0]
    rec.label = label     # 3. Изменить значение метки записи на значение label
    s.commit()     # 4. Сохранить результат в БД
    redirect('/news') '''

@route('/update_news')
def update_news():
    page = requests.get("https://news.ycombinator.com/newest")     # 1. Получить данные с новостного сайта
    news_list = get_news(page)
    s = session()
    for one_news in news_list:     # 2. Проверить каких новостей еще нет в БД
        rows = s.query(News).filter(News.author == one_news['author']).filter(News.title == one_news['title']).all()
        if rows == []:     # 3. Сохранить в БД те новости, которых там нет
            news = News(**one_news)
            s.add(news)
            s.commit()
    redirect('/news')

run(host='localhost', port=8080)
