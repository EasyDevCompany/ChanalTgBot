import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime

ua = UserAgent()

headers = {
    'user-agent': str(ua.chrome)
}

headers_for_gismeteo = {
    'X-Gismeteo-Token': '56b30cb255.3443075',
    'Accept-Encoding': 'deflate, gzip',
    'user-agent': str(ua.chrome)
}


def get_urgent_information():
    response = requests.get(
        'https://32.mchs.gov.ru/deyatelnost/press-centr/operativnaya-informaciya', headers=headers)
    result = response.content
    soup = BeautifulSoup(result, 'lxml')
    today = int(datetime.datetime.now().strftime('%d'))
    urgent_news = {}
    things_list = soup.find_all('div', class_='articles-item')
    for thing in things_list:
        thing_date = thing.find('span', class_='articles-item__date').text
        if today - int(thing_date[:2]) <= 1:
            thing_title = thing.find('a', class_='articles-item__title').text
            thing_href = 'https://32.mchs.gov.ru' + thing.find(
                'a', class_='articles-item__title').get('href')
            urgent_news[thing_title] = thing_href
    return urgent_news


# def get_weather(url):
#     response = requests.get(url, headers=headers_for_gismeteo)
#     result = response.content
#     print(result)

# get_weather('https://www.gismeteo.ru/api/')


def get_horoscope():
    horoscope = {}
    signs = {
        'aries': 'Овен',
        'taurus': 'Телец',
        'gemini': 'Близнецы',
        'cancer': 'Рак',
        'leo': 'Лев',
        'virgo': 'Дева',
        'libra': 'Весы',
        'scorpio': 'Скорпион',
        'sagittarius': 'Стрелец',
        'capricorn': 'Козерог',
        'aquarius': 'Водолей',
        'pisces': 'Рыбы',
    }
    for sign in signs.items():
        response = requests.get(
            f'https://horo.mail.ru/prediction/{sign[0]}/today/')
        result = response.content
        soup = BeautifulSoup(result, 'lxml')
        horoscope_text = soup.find(
            'div', class_=('article__item article__item_alignment_left '
                           'article__item_html')).text
        horoscope[sign[1]] = horoscope_text
    return horoscope
